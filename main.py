import io
import os
from typing import Dict, Any, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from datetime import datetime


from utils.text_loader import extract_pdf_text, extract_docx_text
from utils.preprocessing import preprocess_text
from skill_extractor import SkillExtractor
from similarity import SimilarityAnalyzer
from rag_pipeline import RAGPipeline
from ats_analyzer import ATSAnalyzer

app = FastAPI(
    title="AI-Powered ATS Resume Analyzer with RAG",
    description="AI-powered resume analysis using RAG architecture and FAISS vector retrieval",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

skill_extractor = SkillExtractor()
similarity_analyzer = SimilarityAnalyzer()
rag_pipeline = RAGPipeline()
ats_analyzer = ATSAnalyzer()

analytics_data = []


class AnalysisRequest(BaseModel):
    job_description: str
    target_role: str = "Software Engineer"
    experience_level: str = "Mid"


class QuickAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str


@app.post("/api/analyze")
async def analyze_resume_comprehensive(
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    target_role: str = Form("Software Engineer"),
    experience_level: str = Form("Mid")
) -> Dict[str, Any]:
    try:
        if not resume.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and DOCX files are supported"
            )
        
        file_content = await resume.read()
        file_stream = io.BytesIO(file_content)
        
        try:
            if resume.filename.lower().endswith('.pdf'):
                resume_text = extract_pdf_text(file_stream)
            else:
                resume_text = extract_docx_text(file_stream)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful text from resume file"
            )
        
        processed_resume = preprocess_text(resume_text)
        processed_jd = preprocess_text(job_description)
        
        resume_skills = skill_extractor.extract_skills(resume_text)
        jd_skills = skill_extractor.extract_skills(job_description)
        
        similarity_results = similarity_analyzer.analyze_similarity(
            processed_resume, processed_jd, resume_skills, jd_skills
        )
        
        ats_score = ats_analyzer.analyze_resume(resume_text, job_description)
        
        improved_bullets = rag_pipeline.improve_resume_bullets(
            resume_text, similarity_results["missing_skills"]
        )
        
        role_recommendations = _generate_role_recommendations(
            target_role, experience_level, resume_skills, jd_skills
        )
        
        career_insights = _generate_career_insights(
            resume_text, resume_skills, target_role, experience_level
        )
        
        response = {
            "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            
            "similarity_score": similarity_results["similarity_score"],
            "ats_score": {
                "overall_score": ats_score.overall_score,
                "keyword_score": ats_score.keyword_score,
                "format_score": ats_score.format_score,
                "experience_score": ats_score.experience_score,
                "education_score": ats_score.education_score,
                "skills_score": ats_score.skills_score
            },
            
            "skills_analysis": {
                "resume_skills": resume_skills,
                "jd_skills": jd_skills,
                "missing_skills": similarity_results["missing_skills"],
                "matched_skills": similarity_results["matched_skills"],
                "skills_gap_percentage": round((len(similarity_results["missing_skills"]) / 
                                              max(len(similarity_results["missing_skills"]) + len(similarity_results["matched_skills"]), 1)) * 100, 1)
            },
            
            "bullet_improvements": improved_bullets,
            "ats_recommendations": ats_score.recommendations,
            "critical_issues": ats_score.critical_issues,
            "improvement_suggestions": ats_score.improvements,
            
            "role_recommendations": role_recommendations,
            "career_insights": career_insights,
            
            "target_role": target_role,
            "experience_level": experience_level,
            "resume_stats": {
                "word_count": len(resume_text.split()),
                "skills_count": similarity_results["resume_skills_count"],
                "bullets_improved": len(improved_bullets)
            }
        }
        
        background_tasks.add_task(
            _store_analytics, 
            response["analysis_id"], 
            target_role, 
            experience_level, 
            ats_score.overall_score,
            similarity_results["similarity_score"]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/quick-analyze")
async def quick_analyze(request: QuickAnalysisRequest) -> Dict[str, Any]:
    try:
        resume_skills = skill_extractor.extract_skills(request.resume_text)
        jd_skills = skill_extractor.extract_skills(request.job_description)
        
        similarity_results = similarity_analyzer.analyze_similarity(
            request.resume_text, request.job_description, resume_skills, jd_skills
        )
        
        ats_score = ats_analyzer.analyze_resume(request.resume_text, request.job_description)
        
        return {
            "similarity_score": similarity_results["similarity_score"],
            "ats_score": ats_score.overall_score,
            "missing_skills": similarity_results["missing_skills"][:10],
            "matched_skills": similarity_results["matched_skills"][:10],
            "top_recommendations": ats_score.recommendations[:5]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")


@app.get("/api/skill-suggestions/{role}")
async def get_skill_suggestions(role: str, level: str = "Mid") -> Dict[str, List[str]]:
    try:
        role_skills = {
            "Software Engineer": {
                "Junior": ["Python", "JavaScript", "Git", "SQL", "HTML/CSS"],
                "Mid": ["React", "Node.js", "Docker", "AWS", "PostgreSQL", "REST API"],
                "Senior": ["Kubernetes", "Microservices", "System Design", "Terraform", "GraphQL"],
                "Principal": ["Architecture Design", "Technical Leadership", "Distributed Systems"]
            },
            "Data Scientist": {
                "Junior": ["Python", "Pandas", "NumPy", "SQL", "Statistics"],
                "Mid": ["Machine Learning", "TensorFlow", "Scikit-learn", "Jupyter", "Data Visualization"],
                "Senior": ["Deep Learning", "MLOps", "Feature Engineering", "A/B Testing"],
                "Principal": ["Research", "Technical Leadership", "Model Architecture"]
            },
            "DevOps Engineer": {
                "Junior": ["Linux", "Docker", "Git", "Bash", "CI/CD"],
                "Mid": ["Kubernetes", "Terraform", "AWS", "Jenkins", "Monitoring"],
                "Senior": ["Infrastructure as Code", "Service Mesh", "Security", "Cost Optimization"],
                "Principal": ["Platform Engineering", "Technical Strategy", "Team Leadership"]
            }
        }
        
        return {
            "recommended_skills": role_skills.get(role, {}).get(level, []),
            "trending_skills": ["AI/ML", "Cloud Native", "Kubernetes", "TypeScript", "GraphQL"],
            "emerging_skills": ["WebAssembly", "Edge Computing", "Quantum Computing", "Blockchain"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill suggestions failed: {str(e)}")


@app.get("/api/analytics/summary")
async def get_analytics_summary() -> Dict[str, Any]:
    if not analytics_data:
        return {
            "total_analyses": 0,
            "average_ats_score": 0,
            "average_similarity_score": 0,
            "popular_roles": [],
            "common_issues": []
        }
    
    return {
        "total_analyses": len(analytics_data),
        "average_ats_score": sum(a["ats_score"] for a in analytics_data) / len(analytics_data),
        "average_similarity_score": sum(a["similarity_score"] for a in analytics_data) / len(analytics_data),
        "popular_roles": ["Software Engineer", "Data Scientist", "DevOps Engineer"],
        "common_issues": [
            "Lack of quantifiable achievements",
            "Missing technical keywords",
            "Insufficient action verbs"
        ]
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "AI-Powered ATS Resume Analyzer with RAG is running",
        "version": "2.0.0",
        "features": [
            "ATS Scoring",
            "RAG-powered Improvements", 
            "Real-time Analysis",
            "Career Insights"
        ],
        "uptime": "Available"
    }


def _generate_role_recommendations(target_role: str, experience_level: str, 
                                 resume_skills: Dict, jd_skills: Dict) -> List[str]:
    recommendations = []
    
    if target_role.lower() in ["software engineer", "developer"]:
        if experience_level == "Junior":
            recommendations.append("Focus on building a strong foundation in core programming languages")
            recommendations.append("Create personal projects to demonstrate practical skills")
        elif experience_level == "Senior":
            recommendations.append("Highlight system design and architecture experience")
            recommendations.append("Emphasize leadership and mentoring capabilities")
    
    elif target_role.lower() in ["data scientist", "ml engineer"]:
        recommendations.append("Showcase end-to-end ML project experience")
        recommendations.append("Highlight experience with production ML systems")
    
    elif target_role.lower() in ["devops", "sre", "platform engineer"]:
        recommendations.append("Emphasize infrastructure automation and monitoring experience")
        recommendations.append("Highlight experience with cloud platforms and containerization")
    
    return recommendations


def _generate_career_insights(resume_text: str, resume_skills: Dict, 
                            target_role: str, experience_level: str) -> Dict[str, Any]:
    total_skills = sum(len(skills) for skills in resume_skills.values())
    
    next_level_skills = {
        "Junior": ["System Design", "Architecture", "Leadership"],
        "Mid": ["Technical Leadership", "Mentoring", "Strategic Planning"],
        "Senior": ["Executive Leadership", "Business Strategy", "Innovation"],
        "Principal": ["Industry Expertise", "Thought Leadership", "Vision Setting"]
    }
    
    return {
        "current_level_assessment": f"Based on skills analysis, you appear to be at {experience_level} level",
        "skill_diversity_score": min(len(resume_skills.keys()) * 10, 100),
        "next_level_skills": next_level_skills.get(experience_level, []),
        "career_growth_areas": [
            "Technical depth in core competencies",
            "Cross-functional collaboration",
            "Industry knowledge and trends"
        ],
        "certification_suggestions": [
            "AWS Certified Solutions Architect",
            "Kubernetes Administrator",
            "Certified Scrum Master"
        ]
    }


async def _store_analytics(analysis_id: str, target_role: str, experience_level: str, 
                          ats_score: float, similarity_score: float):
    analytics_data.append({
        "analysis_id": analysis_id,
        "timestamp": datetime.now().isoformat(),
        "target_role": target_role,
        "experience_level": experience_level,
        "ats_score": ats_score,
        "similarity_score": similarity_score
    })
    
    if len(analytics_data) > 1000:
        analytics_data.pop(0)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
