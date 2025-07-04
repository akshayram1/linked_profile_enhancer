#!/usr/bin/env python3
"""
LinkedIn Profile Enhancer - Gradio Interface (app2.py)
A beautiful web interface for the LinkedIn Profile Enhancer using Gradio
"""

import sys
import os
import time
import json
from typing import Dict, Any, Tuple, Optional
import gradio as gr
from PIL import Image
import requests
from io import BytesIO

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import ProfileOrchestrator
from agents.scraper_agent import ScraperAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.content_agent import ContentAgent

class LinkedInEnhancerGradio:
    """Gradio Interface for LinkedIn Profile Enhancer"""
    
    def __init__(self):
        self.orchestrator = ProfileOrchestrator()
        self.current_profile_data = None
        self.current_analysis = None
        self.current_suggestions = None
    
    def test_api_connections(self) -> Tuple[str, str]:
        """Test API connections and return status"""
        apify_status = "❌ Failed"
        openai_status = "❌ Failed"
        
        try:
            scraper = ScraperAgent()
            if scraper.test_apify_connection():
                apify_status = "✅ Connected"
        except Exception as e:
            apify_status = f"❌ Error: {str(e)[:50]}..."
        
        try:
            content_agent = ContentAgent()
            if content_agent.test_openai_connection():
                openai_status = "✅ Connected"
        except Exception as e:
            openai_status = f"❌ Error: {str(e)[:50]}..."
        
        return apify_status, openai_status
    
    def load_profile_image(self, image_url: str) -> Optional[Image.Image]:
        """Load profile image from URL"""
        try:
            if image_url:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error loading image: {e}")
        return None
    
    def enhance_linkedin_profile(self, linkedin_url: str, job_description: str = "") -> Tuple[str, str, str, str, str, str, str, str, Optional[Image.Image]]:
        """Complete LinkedIn profile enhancement with extraction, analysis, and suggestions"""
        if not linkedin_url.strip():
            return "❌ Error", "Please enter a LinkedIn profile URL", "", "", "", "", "", "", None
        
        if not any(pattern in linkedin_url.lower() for pattern in ['linkedin.com/in/', 'www.linkedin.com/in/']):
            return "❌ Error", "Please enter a valid LinkedIn profile URL", "", "", "", "", "", "", None
        
        try:
            # Step 1: Extract profile data
            self.orchestrator.memory.session_data.clear()
            profile_data = self.orchestrator.scraper.extract_profile_data(linkedin_url)
            self.current_profile_data = profile_data
            
            # Format basic info
            basic_info = f"""
**Name:** {profile_data.get('name', 'N/A')}
**Headline:** {profile_data.get('headline', 'N/A')}
**Location:** {profile_data.get('location', 'N/A')}
**Connections:** {profile_data.get('connections', 'N/A')}
**Followers:** {profile_data.get('followers', 'N/A')}
**Email:** {profile_data.get('email', 'N/A')}
**Current Job:** {profile_data.get('job_title', 'N/A')} at {profile_data.get('company_name', 'N/A')}
            """
            
            # Format about section
            about_section = profile_data.get('about', 'No about section available')
            
            # Format experience
            experience_text = ""
            for i, exp in enumerate(profile_data.get('experience', [])[:5], 1):
                experience_text += f"""
**{i}. {exp.get('title', 'Position')}**
- Company: {exp.get('company', 'N/A')}
- Duration: {exp.get('duration', 'N/A')}
- Location: {exp.get('location', 'N/A')}
- Current: {'Yes' if exp.get('is_current') else 'No'}
"""
                if exp.get('description'):
                    experience_text += f"- Description: {exp.get('description')[:200]}...\n"
                experience_text += "\n"
            
            # Format education and skills
            education_text = ""
            for i, edu in enumerate(profile_data.get('education', []), 1):
                education_text += f"""
**{i}. {edu.get('school', 'School')}**
- Degree: {edu.get('degree', 'N/A')}
- Field: {edu.get('field', 'N/A')}
- Year: {edu.get('year', 'N/A')}
- Grade: {edu.get('grade', 'N/A')}

"""
            
            skills_text = ", ".join(profile_data.get('skills', [])[:20])
            if len(profile_data.get('skills', [])) > 20:
                skills_text += f" ... and {len(profile_data.get('skills', [])) - 20} more"
            
            details_text = f"""
## 🎓 Education
{education_text if education_text else "No education information available"}

## 🛠️ Skills
{skills_text if skills_text else "No skills information available"}

## 🏆 Certifications
{len(profile_data.get('certifications', []))} certifications found

## 📊 Additional Data
- Projects: {len(profile_data.get('projects', []))}
- Publications: {len(profile_data.get('publications', []))}
- Recommendations: {len(profile_data.get('recommendations', []))}
            """
            
            # Load profile image
            profile_image = self.load_profile_image(profile_data.get('profile_image_hq') or profile_data.get('profile_image'))
            
            # Step 2: Analyze profile automatically
            try:
                analysis = self.orchestrator.analyzer.analyze_profile(
                    self.current_profile_data, 
                    job_description
                )
                self.current_analysis = analysis
                
                # Format analysis results
                analysis_text = f"""
## 📊 Analysis Results

**Overall Rating:** {analysis.get('overall_rating', 'Unknown')}
**Completeness Score:** {analysis.get('completeness_score', 0):.1f}%
**Job Match Score:** {analysis.get('job_match_score', 0):.1f}%

### 🌟 Strengths
"""
                for strength in analysis.get('strengths', []):
                    analysis_text += f"- {strength}\n"
                
                analysis_text += "\n### ⚠️ Areas for Improvement\n"
                for weakness in analysis.get('weaknesses', []):
                    analysis_text += f"- {weakness}\n"
                
                # Keyword analysis
                keyword_analysis = analysis.get('keyword_analysis', {})
                keywords_text = ""
                if keyword_analysis:
                    found_keywords = keyword_analysis.get('found_keywords', [])
                    missing_keywords = keyword_analysis.get('missing_keywords', [])
                    
                    keywords_text = f"""
## 🔍 Keyword Analysis

**Found Keywords:** {', '.join(found_keywords[:10])}
{"..." if len(found_keywords) > 10 else ""}

**Missing Keywords:** {', '.join(missing_keywords[:5])}
{"..." if len(missing_keywords) > 5 else ""}
                    """
            except Exception as e:
                analysis_text = f"⚠️ Analysis failed: {str(e)}"
                keywords_text = ""
            
            # Step 3: Generate suggestions automatically
            try:
                suggestions = self.orchestrator.content_generator.generate_suggestions(
                    self.current_analysis, 
                    job_description
                )
                self.current_suggestions = suggestions
                
                suggestions_text = ""
                
                for category, items in suggestions.items():
                    if category == 'ai_generated_content':
                        ai_content = items if isinstance(items, dict) else {}
                        
                        # AI Headlines
                        if 'ai_headlines' in ai_content and ai_content['ai_headlines']:
                            suggestions_text += "## ✨ Professional Headlines\n\n"
                            for i, headline in enumerate(ai_content['ai_headlines'], 1):
                                cleaned_headline = headline.strip('"').replace('\\"', '"')
                                if cleaned_headline.startswith(('1.', '2.', '3.', '4.', '5.')):
                                    cleaned_headline = cleaned_headline[2:].strip()
                                suggestions_text += f"{i}. {cleaned_headline}\n\n"
                        
                        # AI About Section
                        if 'ai_about_section' in ai_content and ai_content['ai_about_section']:
                            suggestions_text += "## 📄 Enhanced About Section\n\n"
                            suggestions_text += f"```\n{ai_content['ai_about_section']}\n```\n\n"
                        
                        # AI Experience Descriptions
                        if 'ai_experience_descriptions' in ai_content and ai_content['ai_experience_descriptions']:
                            suggestions_text += "## 💼 Experience Description Ideas\n\n"
                            for desc in ai_content['ai_experience_descriptions']:
                                suggestions_text += f"- {desc}\n"
                            suggestions_text += "\n"
                    else:
                        # Standard categories
                        category_name = category.replace('_', ' ').title()
                        suggestions_text += f"## 📋 {category_name}\n\n"
                        if isinstance(items, list):
                            for item in items:
                                suggestions_text += f"- {item}\n"
                        else:
                            suggestions_text += f"- {items}\n"
                        suggestions_text += "\n"
            except Exception as e:
                suggestions_text = f"⚠️ Suggestions generation failed: {str(e)}"
            
            return "✅ Profile Enhanced Successfully", basic_info, about_section, experience_text, details_text, analysis_text, keywords_text, suggestions_text, profile_image
            
        except Exception as e:
            return "❌ Error", f"Failed to enhance profile: {str(e)}", "", "", "", "", "", "", None
    
    def analyze_profile(self, job_description: str = "") -> Tuple[str, str, str]:
        """Analyze the extracted profile data"""
        if not self.current_profile_data:
            return "❌ Error", "Please extract profile data first", ""
        
        try:
            # Analyze profile
            analysis = self.orchestrator.analyzer.analyze_profile(
                self.current_profile_data, 
                job_description
            )
            self.current_analysis = analysis
            
            # Format analysis results
            analysis_text = f"""
## 📊 Analysis Results

**Overall Rating:** {analysis.get('overall_rating', 'Unknown')}
**Completeness Score:** {analysis.get('completeness_score', 0):.1f}%
**Job Match Score:** {analysis.get('job_match_score', 0):.1f}%

### 🌟 Strengths
"""
            for strength in analysis.get('strengths', []):
                analysis_text += f"- {strength}\n"
            
            analysis_text += "\n### � Areas for Improvement\n"
            for weakness in analysis.get('weaknesses', []):
                analysis_text += f"- {weakness}\n"
            
            # Keyword analysis
            keyword_analysis = analysis.get('keyword_analysis', {})
            keywords_text = ""
            if keyword_analysis:
                found_keywords = keyword_analysis.get('found_keywords', [])
                missing_keywords = keyword_analysis.get('missing_keywords', [])
                
                keywords_text = f"""
## 🔍 Keyword Analysis

**Found Keywords:** {', '.join(found_keywords[:10])}
{"..." if len(found_keywords) > 10 else ""}

**Missing Keywords:** {', '.join(missing_keywords[:5])}
{"..." if len(missing_keywords) > 5 else ""}
                """
            
            return "✅ Success", analysis_text, keywords_text
            
        except Exception as e:
            return "❌ Error", f"Failed to analyze profile: {str(e)}", ""
    
    def generate_suggestions(self, job_description: str = "") -> Tuple[str, str]:
        """Generate enhancement suggestions"""
        if not self.current_analysis:
            return "❌ Error", "Please analyze profile first"
        
        try:
            # Generate suggestions
            suggestions = self.orchestrator.content_generator.generate_suggestions(
                self.current_analysis, 
                job_description
            )
            self.current_suggestions = suggestions
            
            suggestions_text = ""
            ai_content_text = ""
            
            for category, items in suggestions.items():
                if category == 'ai_generated_content':
                    ai_content = items if isinstance(items, dict) else {}
                    
                    # AI Headlines
                    if 'ai_headlines' in ai_content and ai_content['ai_headlines']:
                        ai_content_text += "## ✨ Professional Headlines\n\n"
                        for i, headline in enumerate(ai_content['ai_headlines'], 1):
                            cleaned_headline = headline.strip('"').replace('\\"', '"')
                            if cleaned_headline.startswith(('1.', '2.', '3.', '4.', '5.')):
                                cleaned_headline = cleaned_headline[2:].strip()
                            ai_content_text += f"{i}. {cleaned_headline}\n\n"
                    
                    # AI About Section
                    if 'ai_about_section' in ai_content and ai_content['ai_about_section']:
                        ai_content_text += "## � Enhanced About Section\n\n"
                        ai_content_text += f"```\n{ai_content['ai_about_section']}\n```\n\n"
                    
                    # AI Experience Descriptions
                    if 'ai_experience_descriptions' in ai_content and ai_content['ai_experience_descriptions']:
                        ai_content_text += "## 💼 Experience Description Ideas\n\n"
                        for desc in ai_content['ai_experience_descriptions']:
                            ai_content_text += f"- {desc}\n"
                        ai_content_text += "\n"
                else:
                    # Standard categories
                    category_name = category.replace('_', ' ').title()
                    suggestions_text += f"## 📋 {category_name}\n\n"
                    if isinstance(items, list):
                        for item in items:
                            suggestions_text += f"- {item}\n"
                    else:
                        suggestions_text += f"- {items}\n"
                    suggestions_text += "\n"
            
            return "✅ Success", suggestions_text + ai_content_text
            
        except Exception as e:
            return "❌ Error", f"Failed to generate suggestions: {str(e)}"
    
    def export_results(self, linkedin_url: str) -> str:
        """Export all results to a comprehensive downloadable file"""
        if not self.current_profile_data:
            return "❌ No data to export"
        
        try:
            # Create filename with timestamp
            profile_name = linkedin_url.split('/in/')[-1].split('/')[0] if linkedin_url else 'profile'
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"LinkedIn_Profile_Enhancement_{profile_name}_{timestamp}.md"
            
            # Compile comprehensive report
            content = f"""# 🚀 LinkedIn Profile Enhancement Report

**Generated:** {time.strftime('%B %d, %Y at %I:%M %p')}  
**Profile URL:** [{linkedin_url}]({linkedin_url})  
**Enhancement Date:** {time.strftime('%Y-%m-%d')}

---

## 📊 Executive Summary

This comprehensive report provides a detailed analysis of your LinkedIn profile along with AI-powered enhancement suggestions to improve your professional visibility and job match potential.

---

## 👤 Basic Profile Information

| Field | Current Value |
|-------|---------------|
| **Name** | {self.current_profile_data.get('name', 'N/A')} |
| **Professional Headline** | {self.current_profile_data.get('headline', 'N/A')} |
| **Location** | {self.current_profile_data.get('location', 'N/A')} |
| **Connections** | {self.current_profile_data.get('connections', 'N/A')} |
| **Followers** | {self.current_profile_data.get('followers', 'N/A')} |
| **Email** | {self.current_profile_data.get('email', 'N/A')} |
| **Current Position** | {self.current_profile_data.get('job_title', 'N/A')} at {self.current_profile_data.get('company_name', 'N/A')} |

---

## 📝 Current About Section

```
{self.current_profile_data.get('about', 'No about section available')}
```

---

## 💼 Professional Experience

"""
            # Add experience details
            for i, exp in enumerate(self.current_profile_data.get('experience', []), 1):
                content += f"""
### {i}. {exp.get('title', 'Position')} 
**Company:** {exp.get('company', 'N/A')}  
**Duration:** {exp.get('duration', 'N/A')}  
**Location:** {exp.get('location', 'N/A')}  
**Current Role:** {'Yes' if exp.get('is_current') else 'No'}

"""
                if exp.get('description'):
                    content += f"**Description:**\n```\n{exp.get('description')}\n```\n\n"
            
            # Add education
            content += "---\n\n## 🎓 Education\n\n"
            for i, edu in enumerate(self.current_profile_data.get('education', []), 1):
                content += f"""
### {i}. {edu.get('school', 'School')}
- **Degree:** {edu.get('degree', 'N/A')}
- **Field of Study:** {edu.get('field', 'N/A')}
- **Year:** {edu.get('year', 'N/A')}
- **Grade:** {edu.get('grade', 'N/A')}

"""
            
            # Add skills
            skills = self.current_profile_data.get('skills', [])
            content += f"""---

## 🛠️ Skills & Expertise

**Total Skills Listed:** {len(skills)}

"""
            if skills:
                # Group skills for better readability
                skills_per_line = 5
                for i in range(0, len(skills), skills_per_line):
                    skill_group = skills[i:i+skills_per_line]
                    content += f"- {' • '.join(skill_group)}\n"
            
            # Add certifications and additional data
            content += f"""
---

## 🏆 Additional Profile Data

| Category | Count |
|----------|-------|
| **Certifications** | {len(self.current_profile_data.get('certifications', []))} |
| **Projects** | {len(self.current_profile_data.get('projects', []))} |
| **Publications** | {len(self.current_profile_data.get('publications', []))} |
| **Recommendations** | {len(self.current_profile_data.get('recommendations', []))} |

"""
            
            # Add analysis results if available
            if self.current_analysis:
                content += f"""---

## 📈 AI Analysis Results

### Overall Assessment
- **Overall Rating:** {self.current_analysis.get('overall_rating', 'Unknown')}
- **Profile Completeness:** {self.current_analysis.get('completeness_score', 0):.1f}%
- **Job Match Score:** {self.current_analysis.get('job_match_score', 0):.1f}%

### 🌟 Identified Strengths
"""
                for strength in self.current_analysis.get('strengths', []):
                    content += f"- {strength}\n"
                
                content += "\n### ⚠️ Areas for Improvement\n"
                for weakness in self.current_analysis.get('weaknesses', []):
                    content += f"- {weakness}\n"
                
                # Add keyword analysis
                keyword_analysis = self.current_analysis.get('keyword_analysis', {})
                if keyword_analysis:
                    found_keywords = keyword_analysis.get('found_keywords', [])
                    missing_keywords = keyword_analysis.get('missing_keywords', [])
                    
                    content += f"""
### 🔍 Keyword Analysis

**Found Keywords ({len(found_keywords)}):** {', '.join(found_keywords[:15])}
{"..." if len(found_keywords) > 15 else ""}

**Missing Keywords ({len(missing_keywords)}):** {', '.join(missing_keywords[:10])}
{"..." if len(missing_keywords) > 10 else ""}
"""
            
            # Add enhancement suggestions if available
            if self.current_suggestions:
                content += "\n---\n\n## 💡 AI-Powered Enhancement Suggestions\n\n"
                
                for category, items in self.current_suggestions.items():
                    if category == 'ai_generated_content':
                        ai_content = items if isinstance(items, dict) else {}
                        
                        # AI Headlines
                        if 'ai_headlines' in ai_content and ai_content['ai_headlines']:
                            content += "### ✨ Professional Headlines (Choose Your Favorite)\n\n"
                            for i, headline in enumerate(ai_content['ai_headlines'], 1):
                                cleaned_headline = headline.strip('"').replace('\\"', '"')
                                if cleaned_headline.startswith(('1.', '2.', '3.', '4.', '5.')):
                                    cleaned_headline = cleaned_headline[2:].strip()
                                content += f"{i}. {cleaned_headline}\n\n"
                        
                        # AI About Section
                        if 'ai_about_section' in ai_content and ai_content['ai_about_section']:
                            content += "### 📄 Enhanced About Section\n\n"
                            content += f"```\n{ai_content['ai_about_section']}\n```\n\n"
                        
                        # AI Experience Descriptions
                        if 'ai_experience_descriptions' in ai_content and ai_content['ai_experience_descriptions']:
                            content += "### 💼 Experience Description Enhancements\n\n"
                            for j, desc in enumerate(ai_content['ai_experience_descriptions'], 1):
                                content += f"{j}. {desc}\n\n"
                    else:
                        # Standard categories
                        category_name = category.replace('_', ' ').title()
                        content += f"### 📋 {category_name}\n\n"
                        if isinstance(items, list):
                            for item in items:
                                content += f"- {item}\n"
                        else:
                            content += f"- {items}\n"
                        content += "\n"
            
            # Add action items and next steps
            content += """---

## 🎯 Recommended Action Items

### Immediate Actions (This Week)
1. **Update Headline:** Choose one of the AI-generated headlines that best reflects your goals
2. **Enhance About Section:** Implement the suggested about section improvements
3. **Add Missing Keywords:** Incorporate relevant missing keywords naturally into your content
4. **Complete Profile Sections:** Fill in any incomplete sections identified in the analysis

### Medium-term Goals (This Month)
1. **Experience Descriptions:** Update job descriptions using the AI-generated suggestions
2. **Skills Optimization:** Add relevant skills identified in the keyword analysis
3. **Network Growth:** Aim to increase connections in your industry
4. **Content Strategy:** Start sharing relevant professional content

### Long-term Strategy (Next 3 Months)
1. **Regular Updates:** Keep your profile current with new achievements and skills
2. **Engagement:** Actively engage with your network's content
3. **Personal Branding:** Develop a consistent professional brand across all sections
4. **Performance Monitoring:** Track profile views and connection requests

---

## 📞 Additional Resources

- **LinkedIn Profile Optimization Guide:** [LinkedIn Help Center](https://www.linkedin.com/help/linkedin)
- **Professional Photography:** Consider professional headshots for profile picture
- **Skill Assessments:** Take LinkedIn skill assessments to verify your expertise
- **Industry Groups:** Join relevant professional groups in your field



*This is an automated analysis. Results may vary based on individual goals and industry standards.*
"""
            
            # Save to file (this will be downloaded by the browser)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Report exported as {filename} - File saved for download"
            
        except Exception as e:
            return f"❌ Export failed: {str(e)}"

def create_gradio_interface():
    """Create and return the Gradio interface"""
    
    app = LinkedInEnhancerGradio()
    
    # Custom CSS for beautiful styling
    custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .header-text {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    
    .info {
        background-color: #e7f3ff;
        border: 1px solid #b3d7ff;
        color: #0c5460;
    }
    """
    
    with gr.Blocks(css=custom_css, title="🚀 LinkedIn Profile Enhancer", theme=gr.themes.Soft()) as demo:
        
        # Header
        gr.HTML("""
        <div class="header-text">
            <h1>🚀 LinkedIn Profile Enhancer</h1>
            <p style="font-size: 1.2em; margin: 1rem 0;">AI-powered LinkedIn profile analysis and enhancement suggestions</p>
            <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 2em;">🔍</div>
                    <div>Real Scraping</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2em;">🤖</div>
                    <div>AI Analysis</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2em;">🎯</div>
                    <div>Smart Suggestions</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2em;">📊</div>
                    <div>Rich Data</div>
                </div>
            </div>
        </div>
        """)
        
        # API Status Section
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 🔌 API Status")
                with gr.Row():
                    apify_status = gr.Textbox(label="📡 Apify API", interactive=False, value="Testing...")
                    openai_status = gr.Textbox(label="🤖 OpenAI API", interactive=False, value="Testing...")
                test_btn = gr.Button("🔄 Test Connections", variant="secondary")
        
        # Main Input Section
        with gr.Row():
            with gr.Column(scale=2):
                linkedin_url = gr.Textbox(
                    label="🔗 LinkedIn Profile URL",
                    placeholder="https://www.linkedin.com/in/your-profile",
                    lines=1
                )
                job_description = gr.Textbox(
                    label="🎯 Target Job Description (Optional)",
                    placeholder="Paste the job description here for tailored suggestions...",
                    lines=5
                )
            
            with gr.Column(scale=1):
                profile_image = gr.Image(
                    label="📸 Profile Picture",
                    height=200,
                    width=200
                )
        
        # Action Buttons - Single Enhanced Button
        with gr.Row():
            enhance_btn = gr.Button("� Enhance LinkedIn Profile", variant="primary", size="lg")
            export_btn = gr.Button("📁 Export Results", variant="secondary")
        
        # Results Section with Tabs
        with gr.Tabs():
            with gr.TabItem("📊 Basic Information"):
                enhance_status = gr.Textbox(label="Status", interactive=False)
                basic_info = gr.Markdown(label="Basic Information")
            
            with gr.TabItem("📝 About Section"):
                about_section = gr.Markdown(label="About Section")
            
            with gr.TabItem("💼 Experience"):
                experience_info = gr.Markdown(label="Work Experience")
            
            with gr.TabItem("🎓 Education & Skills"):
                education_skills = gr.Markdown(label="Education & Skills")
            
            with gr.TabItem("📈 Analysis Results"):
                analysis_results = gr.Markdown(label="Analysis Results")
                keyword_analysis = gr.Markdown(label="Keyword Analysis")
            
            with gr.TabItem("💡 Enhancement Suggestions"):
                suggestions_content = gr.Markdown(label="Enhancement Suggestions")
            
            with gr.TabItem("📁 Export & Download"):
                export_status = gr.Textbox(label="Download Status", interactive=False)
                gr.Markdown("""
                ### 📁 Comprehensive Report Download
                
                Click the **Export Results** button to download a complete markdown report containing:
                
                #### 📊 **Complete Profile Analysis**
                - Basic profile information and current content
                - Detailed experience and education sections
                - Skills analysis and completeness scoring
                
                #### 🤖 **AI Enhancement Suggestions**
                - Professional headline options
                - Enhanced about section recommendations
                - Experience description improvements
                - Keyword optimization suggestions
                
                #### 🎯 **Action Plan**
                - Immediate action items (this week)
                - Medium-term goals (this month) 
                - Long-term strategy (next 3 months)
                - Additional resources and tips
                
                **File Format:** Markdown (.md) - Compatible with GitHub, Notion, and most text editors
                """)
        
        # Event Handlers
        def on_test_connections():
            apify, openai = app.test_api_connections()
            return apify, openai
        
        def on_enhance_profile(url, job_desc):
            status, basic, about, exp, details, analysis, keywords, suggestions, image = app.enhance_linkedin_profile(url, job_desc)
            return status, basic, about, exp, details, analysis, keywords, suggestions, image
        
        def on_export_results(url):
            return app.export_results(url)
        
        # Connect events
        test_btn.click(
            fn=on_test_connections,
            outputs=[apify_status, openai_status]
        )
        
        enhance_btn.click(
            fn=on_enhance_profile,
            inputs=[linkedin_url, job_description],
            outputs=[enhance_status, basic_info, about_section, experience_info, education_skills, analysis_results, keyword_analysis, suggestions_content, profile_image]
        )
        
        export_btn.click(
            fn=on_export_results,
            inputs=[linkedin_url],
            outputs=[export_status]
        )
        
        # Auto-test connections on load
        demo.load(
            fn=on_test_connections,
            outputs=[apify_status, openai_status]
        )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; border-top: 1px solid #eee;">
            <p>🚀 <strong>LinkedIn Profile Enhancer</strong> | Powered by AI | Built with ❤️ using Gradio</p>
            <p>Data scraped with respect to LinkedIn's ToS | Uses OpenAI GPT-4o-mini and Apify</p>
        </div>
        """)
    
    return demo

def main():
    """Main function"""
    
    # Check if running with command line arguments (for backward compatibility)
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("""
LinkedIn Profile Enhancer - Gradio Interface

Usage:
    python app2.py                      # Launch Gradio web interface
    python app2.py --help               # Show this help
    
Web Interface Features:
    - Beautiful modern UI
    - Real-time profile extraction
    - AI-powered analysis
    - Enhancement suggestions
    - Export functionality
    - Profile image display
            """)
            return
        else:
            print("❌ Unknown argument. Use --help for usage information.")
            return
    
    # Launch Gradio interface
    print("🚀 Starting LinkedIn Profile Enhancer...")
    print("📱 Launching Gradio interface...")
    
    demo = create_gradio_interface()
    demo.launch(
        server_name="localhost",
        server_port=7860,
        share=True,  # Creates a public link
        show_error=True
    )

if __name__ == "__main__":
    main()
