# Profile Analysis Agent
import re
from typing import Dict, Any, List
from collections import Counter

class AnalyzerAgent:
    """Agent responsible for analyzing LinkedIn profiles and providing insights"""
    
    def __init__(self):
        self.action_words = [
            'led', 'managed', 'developed', 'created', 'implemented', 'designed',
            'built', 'improved', 'increased', 'reduced', 'optimized', 'delivered',
            'achieved', 'launched', 'established', 'coordinated', 'executed'
        ]
    
    def analyze_profile(self, profile_data: Dict[str, Any], job_description: str = "") -> Dict[str, Any]:
        """
        Analyze a LinkedIn profile and provide comprehensive insights
        
        Args:
            profile_data (Dict[str, Any]): Extracted profile data
            job_description (str): Optional job description for matching analysis
            
        Returns:
            Dict[str, Any]: Analysis results with scores and recommendations
        """
        if not profile_data:
            return self._empty_analysis()
        
        try:
            # Calculate completeness score
            completeness_score = self._calculate_completeness(profile_data)
            
            # Analyze keywords
            keyword_analysis = self._analyze_keywords(profile_data, job_description)
            
            # Assess content quality
            content_quality = self._assess_content_quality(profile_data)
            
            # Identify strengths and weaknesses
            strengths = self._identify_strengths(profile_data)
            weaknesses = self._identify_weaknesses(profile_data)
            
            # Calculate job match if job description provided
            job_match_score = 0
            if job_description:
                job_match_score = self._calculate_job_match(profile_data, job_description)
            
            return {
                'completeness_score': completeness_score,
                'keyword_analysis': keyword_analysis,
                'content_quality': content_quality,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'job_match_score': job_match_score,
                'recommendations': self._generate_recommendations(profile_data, weaknesses),
                'overall_rating': self._calculate_overall_rating(completeness_score, content_quality, job_match_score)
            }
            
        except Exception as e:
            print(f"Error in profile analysis: {str(e)}")
            return self._empty_analysis()
    
    def _calculate_completeness(self, profile_data: Dict[str, Any]) -> float:
        """Calculate profile completeness percentage"""
        score = 0
        total_points = 10
        
        # Basic information (2 points)
        if profile_data.get('name'): score += 1
        if profile_data.get('headline'): score += 1
        
        # About section (2 points)
        about = profile_data.get('about', '')
        if about and len(about) > 50: score += 1
        if about and len(about) > 200: score += 1
        
        # Experience (2 points)
        experience = profile_data.get('experience', [])
        if len(experience) >= 1: score += 1
        if len(experience) >= 2: score += 1
        
        # Education (1 point)
        if profile_data.get('education'): score += 1
        
        # Skills (2 points)
        skills = profile_data.get('skills', [])
        if len(skills) >= 5: score += 1
        if len(skills) >= 10: score += 1
        
        # Location (1 point)
        if profile_data.get('location'): score += 1
        
        return (score / total_points) * 100
    
    def _analyze_keywords(self, profile_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Analyze keywords in profile vs job description"""
        profile_text = self._extract_all_text(profile_data).lower()
        
        # Extract common tech keywords
        tech_keywords = [
            'python', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
            'aws', 'docker', 'kubernetes', 'git', 'agile', 'scrum'
        ]
        
        found_keywords = []
        for keyword in tech_keywords:
            if keyword.lower() in profile_text:
                found_keywords.append(keyword)
        
        # Analyze job description keywords if provided
        missing_keywords = []
        if job_description:
            job_keywords = re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower())
            job_keyword_freq = Counter(job_keywords)
            
            for keyword, freq in job_keyword_freq.most_common(10):
                if keyword not in profile_text and len(keyword) > 3:
                    missing_keywords.append(keyword)
        
        return {
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords[:5],  # Top 5 missing
            'keyword_density': len(found_keywords)
        }
    
    def _assess_content_quality(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of content"""
        about_section = profile_data.get('about', '')
        headline = profile_data.get('headline', '')
        
        return {
            'headline_length': len(headline),
            'about_length': len(about_section),
            'has_quantified_achievements': self._has_numbers(about_section),
            'uses_action_words': self._has_action_words(about_section)
        }
    
    def _identify_strengths(self, profile_data: Dict[str, Any]) -> List[str]:
        """Identify profile strengths"""
        strengths = []
        
        if len(profile_data.get('experience', [])) >= 3:
            strengths.append("Good work experience history")
        
        if len(profile_data.get('skills', [])) >= 10:
            strengths.append("Comprehensive skills list")
        
        if len(profile_data.get('about', '')) > 200:
            strengths.append("Detailed about section")
        
        return strengths
    
    def _identify_weaknesses(self, profile_data: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement"""
        weaknesses = []
        
        if not profile_data.get('about') or len(profile_data.get('about', '')) < 100:
            weaknesses.append("About section needs improvement")
        
        if len(profile_data.get('skills', [])) < 5:
            weaknesses.append("Limited skills listed")
        
        if not self._has_numbers(profile_data.get('about', '')):
            weaknesses.append("Lacks quantified achievements")
        
        return weaknesses
    
    def _calculate_job_match(self, profile_data: Dict[str, Any], job_description: str) -> float:
        """Calculate how well profile matches job description"""
        if not job_description:
            return 0
        
        profile_text = self._extract_all_text(profile_data).lower()
        job_text = job_description.lower()
        
        # Extract keywords from job description
        job_keywords = set(re.findall(r'\b[a-zA-Z]{4,}\b', job_text))
        
        # Count matches
        matches = 0
        for keyword in job_keywords:
            if keyword in profile_text:
                matches += 1
        
        return min((matches / len(job_keywords)) * 100, 100) if job_keywords else 0
    
    def _extract_all_text(self, profile_data: Dict[str, Any]) -> str:
        """Extract all text from profile for analysis"""
        text_parts = []
        
        # Add basic info
        text_parts.append(profile_data.get('headline', ''))
        text_parts.append(profile_data.get('about', ''))
        
        # Add experience descriptions
        for exp in profile_data.get('experience', []):
            text_parts.append(exp.get('description', ''))
            text_parts.append(exp.get('title', ''))
        
        # Add skills
        text_parts.extend(profile_data.get('skills', []))
        
        return ' '.join(text_parts)
    
    def _has_numbers(self, text: str) -> bool:
        """Check if text contains numbers/metrics"""
        return bool(re.search(r'\d+', text))
    
    def _has_action_words(self, text: str) -> bool:
        """Check if text contains action words"""
        text_lower = text.lower()
        return any(word in text_lower for word in self.action_words)
    
    def _generate_recommendations(self, profile_data: Dict[str, Any], weaknesses: List[str]) -> List[str]:
        """Generate specific recommendations based on analysis"""
        recommendations = []
        
        for weakness in weaknesses:
            if "about section" in weakness.lower():
                recommendations.append("Add a compelling about section with 150-300 words describing your expertise")
            elif "skills" in weakness.lower():
                recommendations.append("Add more relevant skills to reach at least 10 skills")
            elif "quantified" in weakness.lower():
                recommendations.append("Include specific numbers and metrics in your descriptions")
        
        return recommendations
    
    def _calculate_overall_rating(self, completeness: float, content_quality: Dict[str, Any], job_match: float) -> str:
        """Calculate overall profile rating"""
        score = completeness * 0.4
        
        # Add content quality score
        if content_quality.get('has_quantified_achievements'):
            score += 10
        if content_quality.get('uses_action_words'):
            score += 10
        if content_quality.get('about_length', 0) > 150:
            score += 10
        
        # Add job match if available
        if job_match > 0:
            score += job_match * 0.3
        
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'completeness_score': 0,
            'keyword_analysis': {'found_keywords': [], 'missing_keywords': [], 'keyword_density': 0},
            'content_quality': {'headline_length': 0, 'about_length': 0, 'has_quantified_achievements': False, 'uses_action_words': False},
            'strengths': [],
            'weaknesses': ['Profile data not available'],
            'job_match_score': 0,
            'recommendations': ['Please provide valid profile data'],
            'overall_rating': 'Unknown'
        }
