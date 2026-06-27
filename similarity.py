from typing import Dict, List, Set, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing

class SimilarityAnalyzer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def analyze_similarity(
        self, 
        resume_text: str, 
        jd_text: str, 
        resume_skills: Dict[str, List[str]],
        jd_skills: Dict[str, List[str]]
    ) -> Dict:
        resume_embedding = self.model.encode([resume_text])
        jd_embedding = self.model.encode([jd_text])
        
        similarity_matrix = cosine_similarity(resume_embedding, jd_embedding)
        similarity_score = float(similarity_matrix[0][0])
        
        similarity_percentage = round(similarity_score * 100, 2)
        
        resume_skills_flat = self._get_flat_skills(resume_skills)
        jd_skills_flat = self._get_flat_skills(jd_skills)
        
        missing_skills = list(jd_skills_flat - resume_skills_flat)
        
        return {
            "similarity_score": similarity_percentage,
            "missing_skills": missing_skills,
            "resume_skills_count": len(resume_skills_flat),
            "jd_skills_count": len(jd_skills_flat),
            "matched_skills": list(resume_skills_flat & jd_skills_flat)
        }
    
    def _get_flat_skills(self, skills_dict: Dict[str, List[str]]) -> Set[str]:
        flat_skills = set()
        for skills_list in skills_dict.values():
            flat_skills.update(skills_list)
        return flat_skills
