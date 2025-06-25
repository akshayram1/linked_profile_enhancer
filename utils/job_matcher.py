# Job Matching Logic
from typing import Dict, Any, List, Tuple
import re
from collections import Counter

class JobMatcher:
    """Utility class for matching LinkedIn profiles with job descriptions"""
    
    def __init__(self):
        self.weight_config = {
            'skills': 0.4,
            'experience': 0.3,
            'keywords': 0.2,
            'education': 0.1
        }
        
        self.skill_synonyms = {
            'javascript': ['js', 'ecmascript', 'node.js', 'nodejs'],
            'python': ['py', 'django', 'flask', 'fastapi'],
            'react': ['reactjs', 'react.js'],
            'angular': ['angularjs', 'angular.js'],
            'machine learning': ['ml', 'ai', 'artificial intelligence'],
            'database': ['db', 'sql', 'mysql', 'postgresql', 'mongodb']
        }
    
    def calculate_match_score(self, profile_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Calculate comprehensive match score between profile and job
        
        Args:
            profile_data (Dict[str, Any]): Cleaned profile data
            job_description (str): Job description text
            
        Returns:
            Dict[str, Any]: Match analysis with scores and details
        """
        job_requirements = self._parse_job_requirements(job_description)
        
        # Calculate individual scores
        skills_score = self._calculate_skills_match(
            profile_data.get('skills', []), 
            job_requirements['skills']
        )
        
        experience_score = self._calculate_experience_match(
            profile_data.get('experience', []), 
            job_requirements
        )
        
        keywords_score = self._calculate_keywords_match(
            profile_data, 
            job_requirements['keywords']
        )
        
        education_score = self._calculate_education_match(
            profile_data.get('education', []), 
            job_requirements
        )
        
        # Calculate weighted overall score
        overall_score = (
            skills_score['score'] * self.weight_config['skills'] +
            experience_score['score'] * self.weight_config['experience'] +
            keywords_score['score'] * self.weight_config['keywords'] +
            education_score['score'] * self.weight_config['education']
        )
        
        return {
            'overall_score': round(overall_score, 2),
            'breakdown': {
                'skills': skills_score,
                'experience': experience_score,
                'keywords': keywords_score,
                'education': education_score
            },
            'recommendations': self._generate_match_recommendations(
                skills_score, experience_score, keywords_score, education_score
            ),
            'job_requirements': job_requirements
        }
    
    def find_skill_gaps(self, profile_skills: List[str], job_requirements: List[str]) -> Dict[str, List[str]]:
        """
        Identify skill gaps between profile and job requirements
        
        Args:
            profile_skills (List[str]): Current profile skills
            job_requirements (List[str]): Required job skills
            
        Returns:
            Dict[str, List[str]]: Missing and matching skills
        """
        profile_skills_lower = [skill.lower() for skill in profile_skills]
        job_skills_lower = [skill.lower() for skill in job_requirements]
        
        # Find exact matches
        matching_skills = []
        missing_skills = []
        
        for job_skill in job_skills_lower:
            if job_skill in profile_skills_lower:
                matching_skills.append(job_skill)
            else:
                # Check for synonyms
                found_synonym = False
                for profile_skill in profile_skills_lower:
                    if self._are_skills_similar(profile_skill, job_skill):
                        matching_skills.append(job_skill)
                        found_synonym = True
                        break
                
                if not found_synonym:
                    missing_skills.append(job_skill)
        
        return {
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'match_percentage': len(matching_skills) / max(len(job_skills_lower), 1) * 100
        }
    
    def suggest_profile_improvements(self, match_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate specific improvement suggestions based on match analysis
        
        Args:
            match_analysis (Dict[str, Any]): Match analysis results
            
        Returns:
            List[str]: Improvement suggestions
        """
        suggestions = []
        breakdown = match_analysis['breakdown']
        
        # Skills suggestions
        if breakdown['skills']['score'] < 70:
            missing_skills = breakdown['skills']['details']['missing_skills'][:3]
            if missing_skills:
                suggestions.append(
                    f"Add these high-priority skills: {', '.join(missing_skills)}"
                )
        
        # Experience suggestions
        if breakdown['experience']['score'] < 60:
            suggestions.append(
                "Highlight more relevant experience in your current/previous roles"
            )
            suggestions.append(
                "Add quantified achievements that demonstrate impact"
            )
        
        # Keywords suggestions
        if breakdown['keywords']['score'] < 50:
            suggestions.append(
                "Incorporate more industry-specific keywords throughout your profile"
            )
        
        # Education suggestions
        if breakdown['education']['score'] < 40:
            suggestions.append(
                "Consider adding relevant certifications or courses"
            )
        
        return suggestions
    
    def _parse_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """Parse job description to extract requirements"""
        requirements = {
            'skills': [],
            'keywords': [],
            'experience_years': 0,
            'education_level': '',
            'industry': '',
            'role_type': ''
        }
        
        # Extract skills (common technical skills)
        skill_patterns = [
            r'\b(python|javascript|java|react|angular|node\.?js|sql|aws|docker|kubernetes)\b',
            r'\b(machine learning|ai|data science|devops|full.?stack)\b',
            r'\b(project management|agile|scrum|leadership)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            requirements['skills'].extend([match.lower() for match in matches])
        
        # Extract experience years
        exp_pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?experience'
        exp_matches = re.findall(exp_pattern, job_description, re.IGNORECASE)
        if exp_matches:
            requirements['experience_years'] = int(exp_matches[0])
        
        # Extract keywords (all meaningful words)
        keywords = re.findall(r'\b[a-zA-Z]{3,}\b', job_description)
        stop_words = {'the', 'and', 'for', 'with', 'you', 'will', 'are', 'have'}
        requirements['keywords'] = [
            word.lower() for word in keywords 
            if word.lower() not in stop_words
        ]
        
        # Remove duplicates
        requirements['skills'] = list(set(requirements['skills']))
        requirements['keywords'] = list(set(requirements['keywords']))
        
        return requirements
    
    def _calculate_skills_match(self, profile_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """Calculate skills match score"""
        if not job_skills:
            return {'score': 100, 'details': {'matching_skills': [], 'missing_skills': []}}
        
        skill_gap_analysis = self.find_skill_gaps(profile_skills, job_skills)
        
        return {
            'score': skill_gap_analysis['match_percentage'],
            'details': skill_gap_analysis
        }
    
    def _calculate_experience_match(self, profile_experience: List[Dict], job_requirements: Dict) -> Dict[str, Any]:
        """Calculate experience match score"""
        score = 0
        details = {
            'relevant_roles': 0,
            'total_experience': 0,
            'required_experience': job_requirements.get('experience_years', 0)
        }
        
        # Calculate total years of experience
        total_years = 0
        relevant_roles = 0
        
        for exp in profile_experience:
            duration_info = exp.get('duration_info', {})
            if duration_info.get('duration_months'):
                total_years += duration_info['duration_months'] / 12
            
            # Check if role is relevant (simple keyword matching)
            role_text = f"{exp.get('title', '')} {exp.get('description', '')}".lower()
            job_keywords = job_requirements.get('keywords', [])
            
            if any(keyword in role_text for keyword in job_keywords[:10]):
                relevant_roles += 1
        
        details['total_experience'] = round(total_years, 1)
        details['relevant_roles'] = relevant_roles
        
        # Calculate score based on experience and relevance
        if job_requirements.get('experience_years', 0) > 0:
            exp_ratio = min(total_years / job_requirements['experience_years'], 1.0)
            score = exp_ratio * 70 + (relevant_roles / max(len(profile_experience), 1)) * 30
        else:
            score = 80  # Default good score if no specific experience required
        
        return {
            'score': round(score, 2),
            'details': details
        }
    
    def _calculate_keywords_match(self, profile_data: Dict, job_keywords: List[str]) -> Dict[str, Any]:
        """Calculate keywords match score"""
        if not job_keywords:
            return {'score': 100, 'details': {'matched': 0, 'total': 0}}
        
        # Extract all text from profile
        profile_text = ""
        for key, value in profile_data.items():
            if isinstance(value, str):
                profile_text += f" {value}"
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        profile_text += f" {' '.join(str(v) for v in item.values())}"
                    else:
                        profile_text += f" {item}"
        
        profile_text = profile_text.lower()
        
        # Count keyword matches
        matched_keywords = 0
        for keyword in job_keywords:
            if keyword.lower() in profile_text:
                matched_keywords += 1
        
        score = (matched_keywords / len(job_keywords)) * 100
        
        return {
            'score': round(score, 2),
            'details': {
                'matched': matched_keywords,
                'total': len(job_keywords),
                'percentage': round(score, 2)
            }
        }
    
    def _calculate_education_match(self, profile_education: List[Dict], job_requirements: Dict) -> Dict[str, Any]:
        """Calculate education match score"""
        score = 70  # Default score
        details = {
            'has_degree': len(profile_education) > 0,
            'degree_count': len(profile_education)
        }
        
        if profile_education:
            score = 85  # Boost for having education
            
            # Check for relevant fields
            job_keywords = job_requirements.get('keywords', [])
            for edu in profile_education:
                edu_text = f"{edu.get('degree', '')} {edu.get('field', '')}".lower()
                if any(keyword in edu_text for keyword in job_keywords[:5]):
                    score = 95
                    break
        
        return {
            'score': score,
            'details': details
        }
    
    def _are_skills_similar(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are similar using synonyms"""
        skill1_lower = skill1.lower()
        skill2_lower = skill2.lower()
        
        # Check direct synonyms
        for main_skill, synonyms in self.skill_synonyms.items():
            if ((skill1_lower == main_skill or skill1_lower in synonyms) and
                (skill2_lower == main_skill or skill2_lower in synonyms)):
                return True
        
        # Check partial matches
        if skill1_lower in skill2_lower or skill2_lower in skill1_lower:
            return True
        
        return False
    
    def _generate_match_recommendations(self, skills_score: Dict, experience_score: Dict, 
                                      keywords_score: Dict, education_score: Dict) -> List[str]:
        """Generate recommendations based on individual scores"""
        recommendations = []
        
        if skills_score['score'] < 60:
            recommendations.append("Focus on developing missing technical skills")
        
        if experience_score['score'] < 50:
            recommendations.append("Highlight more relevant work experience")
        
        if keywords_score['score'] < 40:
            recommendations.append("Optimize profile with job-specific keywords")
        
        if education_score['score'] < 60:
            recommendations.append("Consider additional certifications or training")
        
        return recommendations
