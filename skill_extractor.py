import json
import re
from typing import Dict, List, Set


class SkillExtractor:
    def __init__(self, skill_keywords_path: str = "data/skill_keywords.json"):
        with open(skill_keywords_path, 'r') as f:
            self.skill_keywords = json.load(f)
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        if not text:
            return {category: [] for category in self.skill_keywords.keys()}
        
        text_lower = text.lower()
        extracted_skills = {}
        
        for category, keywords in self.skill_keywords.items():
            found_skills = []
            
            for skill in keywords:
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
            
            extracted_skills[category] = found_skills
        
        return extracted_skills
    
    def get_all_skills_flat(self, skills_dict: Dict[str, List[str]]) -> Set[str]:
        all_skills = set()
        for skills_list in skills_dict.values():
            all_skills.update(skills_list)
        return all_skills