# Main Agent Coordinator
import time
from .scraper_agent import ScraperAgent
from .analyzer_agent import AnalyzerAgent
from .content_agent import ContentAgent
from memory.memory_manager import MemoryManager

class ProfileOrchestrator:
    """Main coordinator for all LinkedIn profile enhancement agents"""
    
    def __init__(self):
        self.scraper = ScraperAgent()
        self.analyzer = AnalyzerAgent()
        self.content_generator = ContentAgent()
        self.memory = MemoryManager()
    
    def enhance_profile(self, linkedin_url, job_description="", force_refresh=True):
        """
        Main workflow for enhancing a LinkedIn profile
        
        Args:
            linkedin_url (str): LinkedIn profile URL
            job_description (str): Optional job description for tailored suggestions
            force_refresh (bool): Force fresh scraping instead of using cache
            
        Returns:
            str: Enhancement suggestions and analysis
        """
        try:
            print(f"🎯 Starting profile enhancement for: {linkedin_url}")
            
            # Always clear cache for fresh data extraction
            if force_refresh:
                print("🗑️ Clearing all cached data...")
                self.memory.force_refresh_session(linkedin_url)
                # Clear any session data for this URL
                self.memory.clear_session_cache(linkedin_url)
                # Also clear any general cache
                self.memory.clear_session_cache()  # Clear all sessions
            
            # Step 1: Scrape LinkedIn profile data
            print("📡 Step 1: Scraping profile data...")
            print(f"🔗 Target URL: {linkedin_url}")
            profile_data = self.scraper.extract_profile_data(linkedin_url)
            
            # Verify we got data for the correct URL
            if profile_data.get('url') != linkedin_url:
                print(f"⚠️ URL mismatch detected!")
                print(f"   Expected: {linkedin_url}")
                print(f"   Got: {profile_data.get('url', 'Unknown')}")
            
            # Step 2: Analyze the profile
            print("🔍 Step 2: Analyzing profile...")
            analysis = self.analyzer.analyze_profile(profile_data, job_description)
            
            # Step 3: Generate enhancement suggestions
            print("💡 Step 3: Generating suggestions...")
            suggestions = self.content_generator.generate_suggestions(analysis, job_description)
            
            # Step 4: Store in memory for future reference
            session_data = {
                'profile_data': profile_data,
                'analysis': analysis,
                'suggestions': suggestions,
                'job_description': job_description,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.memory.store_session(linkedin_url, session_data)
            
            print("✅ Profile enhancement completed!")
            return self._format_output(analysis, suggestions)
            
        except Exception as e:
            return f"Error in orchestration: {str(e)}"
    
    def _format_output(self, analysis, suggestions):
        """Format the final output for display"""
        output = []
        
        # Profile Analysis Section
        output.append("## 📊 Profile Analysis")
        output.append("")
        output.append(f"**📈 Completeness Score:** {analysis.get('completeness_score', 0):.1f}%")
        output.append(f"**⭐ Overall Rating:** {analysis.get('overall_rating', 'Unknown')}")
        output.append(f"**🎯 Job Match Score:** {analysis.get('job_match_score', 0):.1f}%")
        output.append("")
        
        # Strengths
        strengths = analysis.get('strengths', [])
        if strengths:
            output.append("### 🌟 Profile Strengths")
            for strength in strengths:
                output.append(f"✅ {strength}")
            output.append("")
        
        # Areas for Improvement
        weaknesses = analysis.get('weaknesses', [])
        if weaknesses:
            output.append("### 🔧 Areas for Improvement")
            for weakness in weaknesses:
                output.append(f"🔸 {weakness}")
            output.append("")
        
        # Keyword Analysis
        keyword_analysis = analysis.get('keyword_analysis', {})
        if keyword_analysis:
            found_keywords = keyword_analysis.get('found_keywords', [])
            missing_keywords = keyword_analysis.get('missing_keywords', [])
            
            output.append("### � Keyword Analysis")
            output.append(f"**Keywords Found ({len(found_keywords)}):** {', '.join(found_keywords[:10])}")
            if missing_keywords:
                output.append(f"**Missing Keywords:** {', '.join(missing_keywords[:5])}")
            output.append("")
        
        # Enhancement Suggestions Section
        output.append("## 🎯 Enhancement Suggestions")
        output.append("")
        
        for category, items in suggestions.items():
            if category == 'ai_generated_content':
                # Special formatting for AI content
                output.append("### 🤖 AI-Generated Content Suggestions")
                ai_content = items if isinstance(items, dict) else {}
                
                if 'ai_headlines' in ai_content and ai_content['ai_headlines']:
                    output.append("")
                    output.append("#### ✨ Professional Headlines")
                    for i, headline in enumerate(ai_content['ai_headlines'], 1):
                        # Clean up the headline format
                        cleaned_headline = headline.strip('"').replace('\\"', '"')
                        if cleaned_headline.startswith(('1.', '2.', '3.', '4.', '5.')):
                            cleaned_headline = cleaned_headline[2:].strip()
                        output.append(f"{i}. {cleaned_headline}")
                    output.append("")
                
                if 'ai_about_section' in ai_content and ai_content['ai_about_section']:
                    output.append("#### 📝 Enhanced About Section")
                    output.append("```")
                    about_content = ai_content['ai_about_section']
                    # Clean up the about section
                    about_lines = about_content.split('\n')
                    for line in about_lines:
                        if line.strip():
                            output.append(line.strip())
                    output.append("```")
                    output.append("")
                
                if 'ai_experience_descriptions' in ai_content and ai_content['ai_experience_descriptions']:
                    output.append("#### 💼 Experience Description Ideas")
                    for desc in ai_content['ai_experience_descriptions']:
                        output.append(f"• {desc}")
                    output.append("")
            else:
                # Standard formatting for other categories
                category_name = category.replace('_', ' ').title()
                output.append(f"### {category_name}")
                if isinstance(items, list):
                    for item in items:
                        output.append(f"• {item}")
                else:
                    output.append(f"• {items}")
                output.append("")
        
        # Next Steps Section
        output.append("## 📈 Implementation Roadmap")
        output.append("")
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            output.append("### 🎯 Priority Actions")
            for i, rec in enumerate(recommendations[:5], 1):
                output.append(f"{i}. {rec}")
            output.append("")
        
        output.append("### 📊 General Best Practices")
        output.append("🔸 Update your profile regularly with new achievements")
        output.append("🔸 Use professional keywords relevant to your industry")
        output.append("🔸 Engage with your network by sharing valuable content")
        output.append("🔸 Ask for recommendations from colleagues and clients")
        output.append("🔸 Monitor profile views and connection requests")
        output.append("")
        
        output.append("---")
        output.append("*Analysis powered by AI • Data scraped with respect to LinkedIn's ToS*")
        
        return "\n".join(output)
