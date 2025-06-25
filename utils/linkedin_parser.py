# LinkedIn Data Parser
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

class LinkedInParser:
    """Utility class for parsing and cleaning LinkedIn profile data"""
    
    def __init__(self):
        self.skill_categories = {
            'technical': ['python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker'],
            'management': ['leadership', 'project management', 'team management', 'agile', 'scrum'],
            'marketing': ['seo', 'social media', 'content marketing', 'digital marketing', 'analytics'],
            'design': ['ui/ux', 'photoshop', 'figma', 'adobe', 'design thinking']
        }
    
    def clean_profile_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and standardize raw profile data
        
        Args:
            raw_data (Dict[str, Any]): Raw scraped data
            
        Returns:
            Dict[str, Any]: Cleaned profile data
        """
        cleaned_data = {}
        
        # Clean basic info
        cleaned_data['name'] = self._clean_text(raw_data.get('name', ''))
        cleaned_data['headline'] = self._clean_text(raw_data.get('headline', ''))
        cleaned_data['location'] = self._clean_text(raw_data.get('location', ''))
        cleaned_data['about'] = self._clean_text(raw_data.get('about', ''))
        
        # Clean experience
        cleaned_data['experience'] = self._clean_experience_list(
            raw_data.get('experience', [])
        )
        
        # Clean education
        cleaned_data['education'] = self._clean_education_list(
            raw_data.get('education', [])
        )
        
        # Clean and categorize skills
        cleaned_data['skills'] = self._clean_skills_list(
            raw_data.get('skills', [])
        )
        
        # Parse additional info
        cleaned_data['connections'] = self._parse_connections(
            raw_data.get('connections', '')
        )
        
        cleaned_data['url'] = raw_data.get('url', '')
        cleaned_data['parsed_at'] = datetime.now().isoformat()
        
        return cleaned_data
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract meaningful keywords from text
        
        Args:
            text (str): Input text
            min_length (int): Minimum keyword length
            
        Returns:
            List[str]: Extracted keywords
        """
        # Remove special characters and convert to lowercase
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words and filter
        words = clean_text.split()
        
        # Common stop words to exclude
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'within', 'without',
            'under', 'over', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Filter keywords
        keywords = [
            word for word in words 
            if len(word) >= min_length and word not in stop_words
        ]
        
        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            if keyword not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword)
        
        return unique_keywords
    
    def parse_duration(self, duration_str: str) -> Dict[str, Any]:
        """
        Parse duration strings like "2020 - Present" or "Jan 2020 - Dec 2022"
        
        Args:
            duration_str (str): Duration string
            
        Returns:
            Dict[str, Any]: Parsed duration info
        """
        duration_info = {
            'raw': duration_str,
            'start_date': None,
            'end_date': None,
            'is_current': False,
            'duration_months': 0
        }
        
        if not duration_str:
            return duration_info
        
        # Check if current position
        if 'present' in duration_str.lower():
            duration_info['is_current'] = True
        
        # Extract years using regex
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, duration_str)
        
        if years:
            duration_info['start_date'] = years[0] if len(years) > 0 else None
            duration_info['end_date'] = years[1] if len(years) > 1 else None
        
        return duration_info
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize skills into different types
        
        Args:
            skills (List[str]): List of skills
            
        Returns:
            Dict[str, List[str]]: Categorized skills
        """
        categorized = {
            'technical': [],
            'management': [],
            'marketing': [],
            'design': [],
            'other': []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized_flag = False
            
            for category, keywords in self.skill_categories.items():
                if any(keyword in skill_lower for keyword in keywords):
                    categorized[category].append(skill)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized['other'].append(skill)
        
        return categorized
    
    def extract_achievements(self, text: str) -> List[str]:
        """
        Extract achievements with numbers/metrics from text
        
        Args:
            text (str): Input text
            
        Returns:
            List[str]: List of achievements
        """
        achievements = []
        
        # Patterns for achievements with numbers
        patterns = [
            r'[^.]*\b\d+%[^.]*',  # Percentage achievements
            r'[^.]*\b\d+[kK]\+?[^.]*',  # Numbers with K (thousands)
            r'[^.]*\b\d+[mM]\+?[^.]*',  # Numbers with M (millions)
            r'[^.]*\$\d+[^.]*',  # Money amounts
            r'[^.]*\b\d+\s*(years?|months?)[^.]*',  # Time periods
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            achievements.extend([match.strip() for match in matches])
        
        return achievements
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,!?()&/]', '', text)
        
        return text
    
    def _clean_experience_list(self, experience_list: List[Dict]) -> List[Dict]:
        """Clean experience entries"""
        cleaned_experience = []
        
        for exp in experience_list:
            if isinstance(exp, dict):
                cleaned_exp = {
                    'title': self._clean_text(exp.get('title', '')),
                    'company': self._clean_text(exp.get('company', '')),
                    'duration': self._clean_text(exp.get('duration', '')),
                    'description': self._clean_text(exp.get('description', '')),
                    'location': self._clean_text(exp.get('location', '')),
                }
                
                # Parse duration
                cleaned_exp['duration_info'] = self.parse_duration(cleaned_exp['duration'])
                
                # Extract achievements
                cleaned_exp['achievements'] = self.extract_achievements(
                    cleaned_exp['description']
                )
                
                cleaned_experience.append(cleaned_exp)
        
        return cleaned_experience
    
    def _clean_education_list(self, education_list: List[Dict]) -> List[Dict]:
        """Clean education entries"""
        cleaned_education = []
        
        for edu in education_list:
            if isinstance(edu, dict):
                cleaned_edu = {
                    'degree': self._clean_text(edu.get('degree', '')),
                    'school': self._clean_text(edu.get('school', '')),
                    'year': self._clean_text(edu.get('year', '')),
                    'field': self._clean_text(edu.get('field', '')),
                }
                cleaned_education.append(cleaned_edu)
        
        return cleaned_education
    
    def _clean_skills_list(self, skills_list: List[str]) -> List[str]:
        """Clean and deduplicate skills"""
        if not skills_list:
            return []
        
        cleaned_skills = []
        seen_skills = set()
        
        for skill in skills_list:
            cleaned_skill = self._clean_text(str(skill))
            skill_lower = cleaned_skill.lower()
            
            if cleaned_skill and skill_lower not in seen_skills:
                cleaned_skills.append(cleaned_skill)
                seen_skills.add(skill_lower)
        
        return cleaned_skills
    
    def _parse_connections(self, connections_str: str) -> int:
        """Parse connection count from string"""
        if not connections_str:
            return 0
        
        # Extract numbers from connection string
        numbers = re.findall(r'\d+', connections_str)
        
        if numbers:
            return int(numbers[0])
        
        # Handle "500+" format
        if '500+' in connections_str:
            return 500
        
        return 0
