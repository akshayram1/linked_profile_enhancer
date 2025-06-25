# Content Generation Agent
import os
from typing import Dict, Any, List
from prompts.agent_prompts import ContentPrompts
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ContentAgent:
    """Agent responsible for generating content suggestions and improvements using OpenAI"""
    
    def __init__(self):
        self.prompts = ContentPrompts()
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. Using fallback content generation.")
            self.openai_client = None
        else:
            self.openai_client = OpenAI(api_key=api_key)
    
    def generate_suggestions(self, analysis: Dict[str, Any], job_description: str = "") -> Dict[str, Any]:
        """
        Generate enhancement suggestions based on analysis
        
        Args:
            analysis (Dict[str, Any]): Profile analysis results
            job_description (str): Optional job description for tailored suggestions
            
        Returns:
            Dict[str, Any]: Enhancement suggestions
        """
        try:
            suggestions = {
                'headline_improvements': self._suggest_headline_improvements(analysis, job_description),
                'about_section': self._suggest_about_improvements(analysis, job_description),
                'experience_optimization': self._suggest_experience_improvements(analysis),
                'skills_enhancement': self._suggest_skills_improvements(analysis, job_description),
                'keyword_optimization': self._suggest_keyword_improvements(analysis),
                'content_quality': self._suggest_content_quality_improvements(analysis)
            }
            
            # Add AI-generated content if OpenAI is available
            if self.openai_client:
                suggestions['ai_generated_content'] = self._generate_ai_content(analysis, job_description)
            
            return suggestions
            
        except Exception as e:
            raise Exception(f"Failed to generate suggestions: {str(e)}")
    
    def _generate_ai_content(self, analysis: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Generate AI-powered content using OpenAI"""
        ai_content = {}
        
        try:
            # Generate AI headline suggestions
            ai_content['ai_headlines'] = self._generate_ai_headlines(analysis, job_description)
            
            # Generate AI about section
            ai_content['ai_about_section'] = self._generate_ai_about_section(analysis, job_description)
            
            # Generate AI experience descriptions
            ai_content['ai_experience_descriptions'] = self._generate_ai_experience_descriptions(analysis)
            
        except Exception as e:
            print(f"Error generating AI content: {str(e)}")
            ai_content['error'] = "AI content generation temporarily unavailable"
        
        return ai_content
    
    def _generate_ai_headlines(self, analysis: Dict[str, Any], job_description: str) -> List[str]:
        """Generate AI-powered headline suggestions"""
        if not self.openai_client:
            return []
        
        prompt = f"""
        Generate 5 compelling LinkedIn headlines for this professional profile:
        
        Current analysis: {analysis.get('summary', 'No analysis available')}
        Target job (if any): {job_description[:200] if job_description else 'General optimization'}
        
        Requirements:
        - Maximum 120 characters each
        - Include relevant keywords
        - Professional and engaging tone        - Show value proposition
        - Vary the style (some formal, some creative)
        
        Return only the headlines, numbered 1-5:
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            headlines = response.choices[0].message.content.strip().split('\n')
            return [h.strip() for h in headlines if h.strip()][:5]
            
        except Exception as e:
            print(f"Error generating AI headlines: {str(e)}")
            return []
    
    def _generate_ai_about_section(self, analysis: Dict[str, Any], job_description: str) -> str:
        """Generate AI-powered about section"""
        if not self.openai_client:
            return ""
        
        prompt = f"""
        Write a compelling LinkedIn About section for this professional:
        
        Profile Analysis: {analysis.get('summary', 'No analysis available')}
        Strengths: {', '.join(analysis.get('strengths', []))}
        Target Role: {job_description[:300] if job_description else 'Career advancement'}
        
        Requirements:
        - 150-300 words
        - Professional yet personable tone
        - Include quantified achievements
        - Strong opening hook
        - Clear value proposition
        - Call to action at the end
        - Use bullet points for key skills/achievements        
        Write the complete About section:
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating AI about section: {str(e)}")
            return ""
    
    def _generate_ai_experience_descriptions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate AI-powered experience descriptions"""
        if not self.openai_client:
            return []
        
        # This would ideally take specific experience entries
        # For now, return general improvement suggestions
        
        prompt = """
        Generate 3 example bullet points for LinkedIn experience descriptions that:
        - Start with strong action verbs
        - Include quantified achievements
        - Show business impact        - Are relevant for tech professionals
        
        Format: Return only the bullet points, one per line with • prefix
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            descriptions = response.choices[0].message.content.strip().split('\n')
            return [d.strip() for d in descriptions if d.strip()]
            
        except Exception as e:
            print(f"Error generating AI experience descriptions: {str(e)}")
            return []
    
    def _suggest_headline_improvements(self, analysis: Dict[str, Any], job_description: str = "") -> List[str]:
        """Generate headline improvement suggestions"""
        suggestions = []
        
        content_quality = analysis.get('content_quality', {})
        headline_length = content_quality.get('headline_length', 0)
        
        if headline_length < 50:
            suggestions.append("Expand your headline to include more keywords and value proposition")
        elif headline_length > 120:
            suggestions.append("Shorten your headline to be more concise and impactful")
        
        suggestions.extend([
            "Include specific technologies or skills you specialize in",
            "Mention your years of experience or seniority level",
            "Add a unique value proposition that sets you apart",
            "Use action-oriented language to show what you do"
        ])
        
        return suggestions
    
    def _suggest_about_improvements(self, analysis: Dict[str, Any], job_description: str = "") -> List[str]:
        """Generate about section improvement suggestions"""
        suggestions = []
        
        content_quality = analysis.get('content_quality', {})
        about_length = content_quality.get('about_length', 0)
        has_numbers = content_quality.get('has_quantified_achievements', False)
        has_action_words = content_quality.get('uses_action_words', False)
        
        if about_length < 100:
            suggestions.append("Expand your about section to at least 2-3 paragraphs")
        
        if not has_numbers:
            suggestions.append("Add quantified achievements (e.g., 'Increased sales by 30%')")
        
        if not has_action_words:
            suggestions.append("Use more action verbs to describe your accomplishments")
        
        suggestions.extend([
            "Start with a compelling hook that grabs attention",
            "Include your professional mission or passion",
            "Mention specific technologies, tools, or methodologies you use",
            "End with a call-to-action for potential connections"
        ])
        
        return suggestions
    
    def _suggest_experience_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate experience section improvement suggestions"""
        suggestions = [
            "Use bullet points to highlight key achievements in each role",
            "Start each bullet point with an action verb",
            "Include metrics and numbers to quantify your impact",
            "Focus on results rather than just responsibilities",
            "Tailor descriptions to align with your target role"
        ]
        
        return suggestions
    
    def _suggest_skills_improvements(self, analysis: Dict[str, Any], job_description: str) -> List[str]:
        """Generate skills section improvement suggestions"""
        suggestions = []
        
        keyword_analysis = analysis.get('keyword_analysis', {})
        missing_keywords = keyword_analysis.get('missing_keywords', [])
        
        if missing_keywords and job_description:
            suggestions.append(f"Consider adding these relevant skills: {', '.join(missing_keywords[:5])}")
        
        suggestions.extend([
            "Prioritize your most relevant skills at the top",
            "Include both technical and soft skills",
            "Get endorsements from colleagues for your key skills",
            "Add skills that are trending in your industry"
        ])
        
        return suggestions
    
    def _suggest_keyword_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate keyword optimization suggestions"""
        suggestions = []
        
        keyword_analysis = analysis.get('keyword_analysis', {})
        keyword_density = keyword_analysis.get('keyword_density', 0)
        missing_keywords = keyword_analysis.get('missing_keywords', [])
        
        if keyword_density < 50:
            suggestions.append("Increase keyword density by incorporating more relevant terms")
        
        if missing_keywords:
            suggestions.append(f"Consider adding these keywords: {', '.join(missing_keywords[:3])}")
        
        suggestions.extend([
            "Use industry-specific terminology naturally throughout your profile",
            "Include location-based keywords if relevant",
            "Add keywords related to your target roles"
        ])
        
        return suggestions
    
    def _suggest_content_quality_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate general content quality improvement suggestions"""
        completeness_score = analysis.get('completeness_score', 0)
        
        suggestions = []
        
        if completeness_score < 80:
            suggestions.append("Complete all sections of your profile for better visibility")
        
        suggestions.extend([
            "Use a professional headshot as your profile photo",
            "Add a background image that reflects your industry",
            "Keep your profile updated with recent achievements",
            "Engage regularly by posting and commenting on relevant content",
            "Ask for recommendations from colleagues and clients"
        ])
        
        return suggestions
    
    def generate_headline_examples(self, current_headline: str, job_description: str = "") -> List[str]:
        """Generate example headlines"""
        examples = [
            "Senior Software Engineer | Full-Stack Developer | React & Node.js Expert",
            "Data Scientist | Machine Learning Engineer | Python & AI Specialist",
            "Digital Marketing Manager | SEO Expert | Growth Hacker",
            "Product Manager | Agile Expert | B2B SaaS Specialist"
        ]
        
        return examples
    
    def generate_about_template(self, analysis: Dict[str, Any]) -> str:
        """Generate an about section template"""
        template = """
🚀 [Opening Hook - What makes you unique]

💼 [Years] years of experience in [Industry/Field], specializing in [Key Skills/Technologies]. I'm passionate about [What drives you professionally].

🎯 **What I do:**
• [Key responsibility/achievement 1]
• [Key responsibility/achievement 2] 
• [Key responsibility/achievement 3]

📊 **Recent achievements:**
• [Quantified achievement 1]
• [Quantified achievement 2]
• [Quantified achievement 3]

🛠️ **Technical expertise:** [List 5-8 key skills/technologies]

🤝 **Let's connect** if you're interested in [collaboration opportunity/your goals]        """
        
        return template.strip()
    
    def test_openai_connection(self) -> bool:
        """Test if OpenAI connection is working"""
        if not self.openai_client:
            return False
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"OpenAI connection test failed: {str(e)}")
            return False
