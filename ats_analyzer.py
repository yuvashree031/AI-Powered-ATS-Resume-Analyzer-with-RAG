#imp
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from skill_extractor import SkillExtractor


@dataclass
class ATSScore:
    overall_score: float
    keyword_score: float
    format_score: float
    experience_score: float
    education_score: float
    skills_score: float
    recommendations: List[str]
    critical_issues: List[str]
    improvements: List[str]


class ATSAnalyzer:
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        
        self.action_verbs = [
            'achieved', 'administered', 'analyzed', 'architected', 'automated',
            'built', 'collaborated', 'created', 'delivered', 'designed',
            'developed', 'engineered', 'enhanced', 'established', 'executed',
            'implemented', 'improved', 'increased', 'led', 'managed',
            'optimized', 'orchestrated', 'reduced', 'scaled', 'streamlined'
        ]
        
        self.quantifiable_patterns = [
            r'\d+%', r'\$\d+[KMB]?', r'\d+[KMB]\+?', r'\d+x', r'\d+:\d+',
            r'\d+\s*(hours?|days?|weeks?|months?|years?)', r'\d+\s*(users?|customers?|clients?)',
            r'\d+\s*(million|billion|thousand)', r'reduced.*by.*\d+', r'increased.*by.*\d+'
        ]
        
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'university',
            'college', 'certification', 'certified', 'diploma'
        ]
        
        self.experience_indicators = [
            'years of experience', 'senior', 'lead', 'principal', 'staff',
            'manager', 'director', 'architect', 'expert', 'specialist'
        ]
    
    def analyze_resume(self, resume_text: str, job_description: str) -> ATSScore:
        resume_skills = self.skill_extractor.extract_skills(resume_text)
        jd_skills = self.skill_extractor.extract_skills(job_description)
        
        keyword_score = self._calculate_keyword_score(resume_text, job_description, resume_skills, jd_skills)
        format_score = self._calculate_format_score(resume_text)
        experience_score = self._calculate_experience_score(resume_text, job_description)
        education_score = self._calculate_education_score(resume_text, job_description)
        skills_score = self._calculate_skills_score(resume_skills, jd_skills)
        
        overall_score = (
            keyword_score * 0.30 +
            skills_score * 0.25 +
            experience_score * 0.20 +
            format_score * 0.15 +
            education_score * 0.10
        )
        
        recommendations = self._generate_recommendations(
            resume_text, job_description, resume_skills, jd_skills,
            keyword_score, format_score, experience_score, education_score, skills_score
        )
        
        critical_issues = self._identify_critical_issues(
            resume_text, keyword_score, format_score, skills_score
        )
        
        improvements = self._suggest_improvements(
            resume_text, job_description, resume_skills, jd_skills
        )
        
        return ATSScore(
            overall_score=round(overall_score, 1),
            keyword_score=round(keyword_score, 1),
            format_score=round(format_score, 1),
            experience_score=round(experience_score, 1),
            education_score=round(education_score, 1),
            skills_score=round(skills_score, 1),
            recommendations=recommendations,
            critical_issues=critical_issues,
            improvements=improvements
        )
    
    def _calculate_keyword_score(self, resume_text: str, job_description: str, 
                               resume_skills: Dict, jd_skills: Dict) -> float:
        resume_lower = resume_text.lower()
        jd_lower = job_description.lower()
        
        jd_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', jd_lower))
        resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_lower))
        
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        jd_keywords = jd_words - common_words
        
        matched_keywords = resume_words & jd_keywords
        keyword_match_ratio = len(matched_keywords) / len(jd_keywords) if jd_keywords else 0
        
        return min(keyword_match_ratio * 100, 100)
    
    def _calculate_format_score(self, resume_text: str) -> float:
        score = 100
        issues = []
        
        action_verb_count = sum(1 for verb in self.action_verbs if verb in resume_text.lower())
        if action_verb_count < 5:
            score -= 15
            issues.append("Insufficient action verbs")
        
        quantifiable_count = sum(1 for pattern in self.quantifiable_patterns 
                               if re.search(pattern, resume_text, re.IGNORECASE))
        if quantifiable_count < 3:
            score -= 20
            issues.append("Lack of quantifiable achievements")
        
        word_count = len(resume_text.split())
        if word_count < 300:
            score -= 15
            issues.append("Resume too short")
        elif word_count > 1000:
            score -= 10
            issues.append("Resume too long")
        
        if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
            score -= 10
            issues.append("Missing email address")
        
        return max(score, 0)
    
    def _calculate_experience_score(self, resume_text: str, job_description: str) -> float:
        resume_lower = resume_text.lower()
        jd_lower = job_description.lower()
        
        score = 50
        
        experience_matches = sum(1 for indicator in self.experience_indicators 
                               if indicator in resume_lower)
        score += min(experience_matches * 10, 30)
        
        years_pattern = r'(\d+)\+?\s*years?\s*(of\s*)?(experience|exp)'
        resume_years = re.findall(years_pattern, resume_lower)
        jd_years = re.findall(years_pattern, jd_lower)
        
        if resume_years and jd_years:
            resume_exp = max(int(year[0]) for year in resume_years)
            jd_exp = max(int(year[0]) for year in jd_years)
            
            if resume_exp >= jd_exp:
                score += 20
            elif resume_exp >= jd_exp * 0.8:
                score += 10
        
        return min(score, 100)
    
    def _calculate_education_score(self, resume_text: str, job_description: str) -> float:
        resume_lower = resume_text.lower()
        jd_lower = job_description.lower()
        
        score = 50
        
        education_matches = sum(1 for keyword in self.education_keywords 
                              if keyword in resume_lower)
        score += min(education_matches * 8, 40)
        
        if any(keyword in jd_lower for keyword in ['degree', 'bachelor', 'master', 'phd']):
            if any(keyword in resume_lower for keyword in ['degree', 'bachelor', 'master', 'phd']):
                score += 10
            else:
                score -= 20
        
        return max(min(score, 100), 0)
    
    def _calculate_skills_score(self, resume_skills: Dict, jd_skills: Dict) -> float:
        resume_skills_flat = set()
        jd_skills_flat = set()
        
        for skills_list in resume_skills.values():
            resume_skills_flat.update(skill.lower() for skill in skills_list)
        
        for skills_list in jd_skills.values():
            jd_skills_flat.update(skill.lower() for skill in skills_list)
        
        if not jd_skills_flat:
            return 75
        
        matched_skills = resume_skills_flat & jd_skills_flat
        skills_match_ratio = len(matched_skills) / len(jd_skills_flat)
        
        return min(skills_match_ratio * 100, 100)
    
    def _generate_recommendations(self, resume_text: str, job_description: str,
                                resume_skills: Dict, jd_skills: Dict,
                                keyword_score: float, format_score: float,
                                experience_score: float, education_score: float,
                                skills_score: float) -> List[str]:
        recommendations = []
        
        if keyword_score < 60:
            recommendations.append("Increase keyword density by incorporating more terms from the job description")
        
        if skills_score < 70:
            missing_skills = []
            for category, skills in jd_skills.items():
                for skill in skills:
                    if skill.lower() not in [s.lower() for s_list in resume_skills.values() for s in s_list]:
                        missing_skills.append(skill)
            
            if missing_skills:
                recommendations.append(f"Add relevant skills: {', '.join(missing_skills[:5])}")
        
        if format_score < 80:
            recommendations.append("Improve resume format with more action verbs and quantifiable achievements")
        
        if experience_score < 70:
            recommendations.append("Better highlight relevant experience and years of expertise")
        
        if education_score < 60:
            recommendations.append("Include relevant education, certifications, or training")
        
        return recommendations
    
    def _identify_critical_issues(self, resume_text: str, keyword_score: float,
                                format_score: float, skills_score: float) -> List[str]:
        issues = []
        
        if keyword_score < 40:
            issues.append("CRITICAL: Very low keyword match - resume may be filtered out")
        
        if skills_score < 50:
            issues.append("CRITICAL: Major skills gap - add required technical skills")
        
        if format_score < 60:
            issues.append("WARNING: Poor ATS format - may not parse correctly")
        
        if len(resume_text.split()) < 200:
            issues.append("WARNING: Resume too short - add more detail")
        
        return issues
    
    def _suggest_improvements(self, resume_text: str, job_description: str,
                            resume_skills: Dict, jd_skills: Dict) -> List[str]:
        improvements = []
        
        action_verb_count = sum(1 for verb in self.action_verbs if verb in resume_text.lower())
        if action_verb_count < 8:
            improvements.append("Start more bullet points with strong action verbs like 'architected', 'optimized', 'implemented'")
        
        quantifiable_count = sum(1 for pattern in self.quantifiable_patterns 
                               if re.search(pattern, resume_text, re.IGNORECASE))
        if quantifiable_count < 5:
            improvements.append("Add specific numbers, percentages, and metrics to demonstrate impact")
        
        missing_critical_skills = []
        for category in ['programming_languages', 'cloud_platforms', 'ai_ml_frameworks']:
            if category in jd_skills:
                for skill in jd_skills[category]:
                    if skill.lower() not in [s.lower() for s_list in resume_skills.values() for s in s_list]:
                        missing_critical_skills.append(skill)
        
        if missing_critical_skills:
            improvements.append(f"Consider adding these high-impact skills: {', '.join(missing_critical_skills[:3])}")
        
        return improvements
