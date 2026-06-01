#import
import json
import pickle
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


try: #try catch block
    from langchain_groq import ChatGroq
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
from dotenv import load_dotenv
import os

load_dotenv()


class RAGPipeline:
    def __init__(
        self, 
        resume_bullets_path: str = "data/resume_bullets.json",
        vectorstore_path: str = "vectorstore",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.resume_bullets_path = resume_bullets_path
        self.vectorstore_path = vectorstore_path
        self.model = SentenceTransformer(model_name)
        
        if GROQ_AVAILABLE and os.getenv("GROQ_API_KEY"):
            self.llm = ChatGroq(
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name="llama-3.1-8b-instant",
                temperature=0.3
            )
        else:
            self.llm = None
        
        self.index, self.bullets_data = self._load_or_create_index()
        
        self.prompt_template = PromptTemplate(
            input_variables=["original_bullet", "missing_skills", "retrieved_examples"],
            template="""You are an expert ATS resume writer and career coach. Your task is to transform the given resume bullet point into a compelling, ATS-optimized achievement statement.

ORIGINAL BULLET POINT:
{original_bullet}

MISSING SKILLS TO INCORPORATE (if relevant):
{missing_skills}

HIGH-PERFORMING EXAMPLES FOR REFERENCE:
{retrieved_examples}

IMPROVEMENT GUIDELINES:
1. START with a strong action verb (Developed, Implemented, Architected, Optimized, etc.)
2. INCLUDE quantifiable metrics and impact (percentages, time saved, team size, etc.)
3. NATURALLY INTEGRATE relevant missing skills where they fit contextually
4. FOCUS on business impact and technical achievements
5. USE industry-standard terminology and keywords
6. KEEP it concise but impactful (1-2 lines maximum)
7. ENSURE it's ATS-friendly with relevant keywords
8. AVOID generic phrases and weak language

ENHANCED BULLET POINT:"""
        )
    
    def _load_or_create_index(self) -> tuple:
        index_path = os.path.join(self.vectorstore_path, "faiss_index.bin")
        data_path = os.path.join(self.vectorstore_path, "bullets_data.pkl")
        
        if os.path.exists(index_path) and os.path.exists(data_path):
            index = faiss.read_index(index_path)
            with open(data_path, 'rb') as f:
                bullets_data = pickle.load(f)
            return index, bullets_data
        else:
            return self._create_index()
    
    def _create_index(self) -> tuple:
        with open(self.resume_bullets_path, 'r') as f:
            bullets_data = json.load(f)
        
        bullet_texts = [item["bullet"] for item in bullets_data]
        
        embeddings = self.model.encode(bullet_texts)
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        
        faiss.normalize_L2(embeddings)
        index.add(embeddings.astype('float32'))
        
        os.makedirs(self.vectorstore_path, exist_ok=True)
        faiss.write_index(index, os.path.join(self.vectorstore_path, "faiss_index.bin"))
        with open(os.path.join(self.vectorstore_path, "bullets_data.pkl"), 'wb') as f:
            pickle.dump(bullets_data, f)
        
        return index, bullets_data
    
    def retrieve_similar_bullets(self, query_text: str, k: int = 3) -> List[Dict]:
        query_embedding = self.model.encode([query_text])
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        similar_bullets = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.bullets_data):
                bullet_data = self.bullets_data[idx].copy()
                bullet_data['similarity_score'] = float(scores[0][i])
                similar_bullets.append(bullet_data)
        
        return similar_bullets
    
    def improve_resume_bullets(self, resume_text: str, missing_skills: List[str]) -> List[Dict]:
        bullets = self._extract_bullets(resume_text)
        
        if not bullets:
            return []
        
        improved_bullets = []
        
        for i, original_bullet in enumerate(bullets):
            if len(original_bullet.strip()) < 10:
                continue
                
            try:
                similar_bullets = self.retrieve_similar_bullets(original_bullet, k=3)
            except Exception as e:
                similar_bullets = []
            
            retrieved_examples = "\n".join([
                f"- {bullet['bullet']}" for bullet in similar_bullets
            ])
            
            missing_skills_text = ", ".join(missing_skills[:5])
            
            improved_bullet = None
            error_msg = None
            
            if self.llm:
                try:
                    prompt = self.prompt_template.format(
                        original_bullet=original_bullet,
                        missing_skills=missing_skills_text,
                        retrieved_examples=retrieved_examples
                    )
                    
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    improved_bullet = response.content.strip()
                    
                except Exception as e:
                    error_msg = f"LLM error: {str(e)}"
            
            if not improved_bullet or improved_bullet.strip() == "":
                try:
                    improved_bullet = self._improve_bullet_fallback(original_bullet, missing_skills[:3])
                except Exception as e:
                    improved_bullet = original_bullet
                    error_msg = f"Both LLM and fallback failed: {str(e)}"
            
            improvement_entry = {
                "original": original_bullet,
                "improved": improved_bullet,
                "similar_examples": [b["bullet"] for b in similar_bullets]
            }
            
            if error_msg:
                improvement_entry["error"] = error_msg
            
            improved_bullets.append(improvement_entry)
        
        return improved_bullets
    
    def _extract_bullets(self, resume_text: str) -> List[str]:
        lines = resume_text.split('\n')
        bullets = []
        
        bullet_indicators = [
            '•', '-', '*', '◦', '▪', '▫', '‣',
            'developed', 'implemented', 'created', 'designed', 'built', 'managed', 'led',
            'optimized', 'enhanced', 'improved', 'automated', 'streamlined', 'coordinated',
            'collaborated', 'architected', 'engineered', 'delivered', 'executed', 'achieved',
            'increased', 'reduced', 'maintained', 'supported', 'integrated', 'deployed'
        ]
        
        for line in lines:
            line = line.strip()
            
            if len(line) < 15:
                continue
                
            skip_sections = [
                'education', 'skills', 'contact', 'objective', 'summary', 
                'certifications', 'languages', 'references', 'awards'
            ]
            if any(section in line.lower() for section in skip_sections):
                continue
            
            line_lower = line.lower()
            
            if any(line.startswith(symbol) for symbol in ['•', '-', '*', '◦', '▪', '▫', '‣']):
                cleaned_line = line.lstrip('•-*◦▪▫‣ ').strip()
                if len(cleaned_line) > 20:
                    bullets.append(cleaned_line)
            
            elif any(line_lower.startswith(verb) for verb in [
                'developed', 'implemented', 'created', 'designed', 'built', 'managed', 'led',
                'optimized', 'enhanced', 'improved', 'automated', 'streamlined', 'coordinated',
                'collaborated', 'architected', 'engineered', 'delivered', 'executed'
            ]):
                if len(line) > 25:
                    bullets.append(line)
            
            elif any(indicator in line_lower for indicator in [
                'increased', 'reduced', 'improved', 'achieved', 'saved', 'generated',
                '%', 'percent', 'million', 'thousand', 'hours', 'days', 'weeks'
            ]) and len(line) > 20:
                bullets.append(line)
        
        seen = set()
        unique_bullets = []
        for bullet in bullets:
            if bullet not in seen:
                seen.add(bullet)
                unique_bullets.append(bullet)
        
        return unique_bullets[:10]
    
    def _improve_bullet_fallback(self, original_bullet: str, missing_skills: List[str]) -> str:
        improved = original_bullet.strip()
        
        weak_to_strong_verbs = {
            'worked on': 'developed',
            'worked with': 'utilized',
            'used': 'leveraged',
            'helped': 'collaborated to',
            'made': 'created',
            'did': 'executed',
            'was responsible for': 'managed',
            'handled': 'orchestrated',
            'assisted': 'supported',
            'participated': 'contributed to',
            'involved in': 'spearheaded',
            'created': 'architected',
            'built': 'engineered'
        }
        
        improved_lower = improved.lower()
        for weak, strong in weak_to_strong_verbs.items():
            if improved_lower.startswith(weak):
                improved = strong.capitalize() + improved[len(weak):]
                break
        
        if not any(char.isdigit() for char in improved):
            if any(word in improved_lower for word in ['develop', 'build', 'create', 'implement']):
                improved += ", improving system performance by 25%"
            elif any(word in improved_lower for word in ['manage', 'lead', 'coordinate']):
                improved += ", leading a team of 5+ members"
            elif any(word in improved_lower for word in ['optimize', 'enhance', 'improve']):
                improved += ", reducing processing time by 30%"
            elif any(word in improved_lower for word in ['automate', 'streamline']):
                improved += ", saving 15+ hours per week"
        
        if missing_skills:
            relevant_skills = []
            
            for skill in missing_skills[:3]:
                skill_lower = skill.lower()
                
                if any(word in improved_lower for word in ['api', 'backend', 'server', 'service']):
                    if skill_lower in ['docker', 'kubernetes', 'microservices', 'rest api', 'graphql']:
                        relevant_skills.append(skill)
                
                elif any(word in improved_lower for word in ['frontend', 'ui', 'interface', 'web']):
                    if skill_lower in ['react', 'angular', 'vue.js', 'typescript', 'css']:
                        relevant_skills.append(skill)
                
                elif any(word in improved_lower for word in ['database', 'data', 'storage']):
                    if skill_lower in ['postgresql', 'mongodb', 'redis', 'sql']:
                        relevant_skills.append(skill)
                
                elif any(word in improved_lower for word in ['deploy', 'infrastructure', 'cloud']):
                    if skill_lower in ['aws', 'docker', 'kubernetes', 'ci/cd', 'terraform']:
                        relevant_skills.append(skill)
                
                elif any(word in improved_lower for word in ['model', 'algorithm', 'analysis', 'prediction']):
                    if skill_lower in ['tensorflow', 'pytorch', 'machine learning', 'python']:
                        relevant_skills.append(skill)
            
            if relevant_skills:
                if len(relevant_skills) == 1:
                    improved = improved.rstrip('.') + f" using {relevant_skills[0]}"
                else:
                    improved = improved.rstrip('.') + f" leveraging {', '.join(relevant_skills[:-1])} and {relevant_skills[-1]}"
        
        impact_phrases = [
            "resulting in enhanced system reliability",
            "contributing to improved user experience", 
            "leading to increased operational efficiency",
            "ensuring scalable and maintainable solutions",
            "delivering high-quality, production-ready code"
        ]
        
        if not any(phrase in improved_lower for phrase in ['improving', 'increasing', 'reducing', 'enhancing', 'resulting']):
            import random
            impact = random.choice(impact_phrases)
            improved = improved.rstrip('.') + f", {impact}"
        
        if not improved.endswith('.'):
            improved += '.'
            
        return improved
