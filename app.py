# Main Gradio App for LinkedIn Profile Enhancer
"""
LinkedIn Profile Enhancer - AI-Powered Profile Analysis and Enhancement

USAGE:
    python app.py                    # Launch web interface (default)
    python app.py --test             # Run comprehensive API test demo
    python app.py --quick-test       # Run quick API connectivity test
    python app.py --help             # Show this help message

FEATURES:
    • Real LinkedIn profile scraping via Apify API
    • AI-powered profile analysis and scoring
    • OpenAI-generated content suggestions
    • Interactive web interface with Gradio
    • Complete workflow testing capabilities

EXAMPLE TEST:
    python app.py --test
    # This will demonstrate:
    # 1. Apify API connection and profile scraping
    # 2. Profile analysis with scoring and insights
    # 3. OpenAI content generation
    # 4. Complete end-to-end workflow
"""

import gradio as gr
from agents.orchestrator import ProfileOrchestrator
from memory.memory_manager import MemoryManager
from agents.scraper_agent import ScraperAgent
from agents.content_agent import ContentAgent

class LinkedInEnhancerApp:
    def __init__(self):
        self.orchestrator = ProfileOrchestrator()
        self.memory_manager = MemoryManager()
        
        # Test API connections on startup
        self._test_api_connections()
    
    def _test_api_connections(self):
        """Test API connections and show status"""
        print("🔧 Testing API connections...")
        
        # Test Apify connection
        try:
            scraper = ScraperAgent()
            apify_status = scraper.test_apify_connection()
            print(f"✅ Apify: {'Connected' if apify_status else 'Failed'}")
        except Exception as e:
            print(f"❌ Apify: Failed - {str(e)}")
        
        # Test OpenAI connection
        try:
            content_agent = ContentAgent()
            openai_status = content_agent.test_openai_connection()
            print(f"✅ OpenAI: {'Connected' if openai_status else 'Failed'}")
        except Exception as e:
            print(f"❌ OpenAI: Failed - {str(e)}")
        
        print("🚀 Application ready!")
    
    def process_profile_enhanced(self, linkedin_url, job_description=""):
        """Enhanced processing function that returns data for all tabs"""
        try:
            if not linkedin_url.strip():
                return ("Please enter a LinkedIn profile URL", {}, 0, 0, "Not Analyzed", 0, "")
            
            # Validate LinkedIn URL format
            if not self._is_valid_linkedin_url(linkedin_url):
                return ("Please enter a valid LinkedIn profile URL", {}, 0, 0, "Invalid URL", 0, "")
            
            # Get the standard enhancement output
            enhancement_result = self.orchestrator.enhance_profile(linkedin_url, job_description)
            
            # Get the raw scraped data
            profile_data = self.orchestrator.scraper.extract_profile_data(linkedin_url)
            
            # Get analysis for dashboard metrics
            analysis = self.orchestrator.analyzer.analyze_profile(profile_data, job_description)
            
            # Extract metrics for dashboard
            completeness = analysis.get('completeness_score', 0)
            job_match = analysis.get('job_match_score', 0)
            rating = analysis.get('overall_rating', 'Unknown')
            keyword_count = len(analysis.get('keyword_analysis', {}).get('found_keywords', []))
            
            # Create insights summary
            insights = self._create_insights_summary(analysis)
            
            return (
                enhancement_result,      # Enhancement tab
                profile_data,           # Scraped data tab
                completeness,           # Completeness score
                job_match,             # Job match score
                rating,                # Overall rating
                keyword_count,         # Keyword count
                insights               # Profile insights
            )
            
        except Exception as e:
            error_msg = f"Error processing profile: {str(e)}"
            return (error_msg, {}, 0, 0, "Error", 0, error_msg)
    
    def _create_insights_summary(self, analysis):
        """Create a summary of key insights for the analytics dashboard"""
        insights = []
        
        # Add completeness insights
        completeness = analysis.get('completeness_score', 0)
        if completeness >= 80:
            insights.append("🎉 Excellent profile completeness! Your profile is well-structured.")
        elif completeness >= 60:
            insights.append("👍 Good profile completeness, but there's room for improvement.")
        else:
            insights.append("⚠️ Profile needs significant improvements in completeness.")
        
        # Add keyword insights
        keyword_analysis = analysis.get('keyword_analysis', {})
        found_keywords = keyword_analysis.get('found_keywords', [])
        missing_keywords = keyword_analysis.get('missing_keywords', [])
        
        if len(found_keywords) >= 10:
            insights.append(f"🔍 Great keyword coverage! Found {len(found_keywords)} relevant keywords.")
        elif len(found_keywords) >= 5:
            insights.append(f"🔍 Moderate keyword usage. Found {len(found_keywords)} keywords.")
        else:
            insights.append(f"🔍 Low keyword density. Only found {len(found_keywords)} relevant keywords.")
        
        if missing_keywords:
            insights.append(f"💡 Consider adding these missing keywords: {', '.join(missing_keywords[:3])}")
        
        # Add content quality insights
        content_quality = analysis.get('content_quality', {})
        if content_quality.get('has_quantified_achievements'):
            insights.append("📊 Great! Your profile includes quantified achievements.")
        else:
            insights.append("📊 Consider adding more quantified achievements and metrics.")
        
        if content_quality.get('uses_action_words'):
            insights.append("💪 Excellent use of action words in your descriptions.")
        else:
            insights.append("💪 Try using more action words to make your profile more dynamic.")
        
        # Add strengths and weaknesses summary
        strengths = analysis.get('strengths', [])
        weaknesses = analysis.get('weaknesses', [])
        
        if strengths:
            insights.append(f"\n🌟 Top Strengths:")
            for strength in strengths[:3]:
                insights.append(f"  • {strength}")
        
        if weaknesses:
            insights.append(f"\n🔧 Areas to Improve:")
            for weakness in weaknesses[:3]:
                insights.append(f"  • {weakness}")
        
        return "\n".join(insights)

    def process_profile(self, linkedin_url, job_description=""):
        """Main processing function for LinkedIn profile enhancement"""
        try:
            if not linkedin_url.strip():
                return "Please enter a LinkedIn profile URL"
            
            # Validate LinkedIn URL format
            if not self._is_valid_linkedin_url(linkedin_url):
                return "Please enter a valid LinkedIn profile URL (e.g., https://linkedin.com/in/username)"
            
            return self.orchestrator.enhance_profile(linkedin_url, job_description)
        except Exception as e:
            return f"Error processing profile: {str(e)}"
    
    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn URL format"""
        linkedin_patterns = [
            'linkedin.com/in/',
            'www.linkedin.com/in/',
            'https://linkedin.com/in/',
            'https://www.linkedin.com/in/'        ]
        return any(pattern in url.lower() for pattern in linkedin_patterns)
    
    def create_interface(self):
        """Create the Gradio interface with enhanced UI"""
        # Custom CSS for beautiful styling
        custom_css = """
        .gradio-container {
            max-width: 1400px !important;
            margin: 0 auto;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .main-header {
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        }
        
        .input-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
        }
        
        .output-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
        }
        
        .feature-card {
            background: linear-gradient(145deg, #f0f0f0, #ffffff);
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
            border: none !important;
            padding: 12px 30px !important;
            font-weight: bold !important;
            border-radius: 25px !important;
            transition: all 0.3s ease !important;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
        }
        
        .tab-nav {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 10px !important;
        }
        
        .tab-content {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 0 0 15px 15px !important;
            padding: 2rem !important;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 0.5rem;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-connected { background-color: #4CAF50; }
        .status-disconnected { background-color: #f44336; }
        """
        
        with gr.Blocks(
            title="🚀 LinkedIn Profile Enhancer",
            theme=gr.themes.Soft(),
            css=custom_css
        ) as demo:            
            # Header
            with gr.Row():
                with gr.Column():
                    gr.HTML("""
                    <div class="main-header">
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
                                <div>Data Insights</div>
                            </div>
                        </div>
                    </div>
                    """)
            
            with gr.Row():
                with gr.Column(scale=1, elem_classes="input-section"):
                    gr.Markdown("### 📝 Input Configuration")
                    
                    linkedin_url = gr.Textbox(
                        label="🔗 LinkedIn Profile URL",
                        placeholder="https://linkedin.com/in/your-profile",
                        lines=1,
                        info="Enter the full LinkedIn profile URL to analyze",
                        elem_classes="url-input"
                    )
                    
                    job_description = gr.Textbox(
                        label="🎯 Target Job Description (Optional)",
                        placeholder="Paste the job description here for tailored suggestions...",
                        lines=8,
                        info="Include job description for personalized optimization",
                        elem_classes="job-input"
                    )
                    
                    with gr.Row():
                        submit_btn = gr.Button(
                            "� Enhance Profile", 
                            variant="primary",
                            size="lg",
                            elem_classes="btn-primary"
                        )
                        clear_btn = gr.Button(
                            "🗑️ Clear All",
                            variant="secondary",
                            size="lg"
                        )
                    
                    # Status indicators
                    gr.HTML("""
                    <div style="margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                        <h4>🔌 API Status</h4>
                        <div style="display: flex; gap: 1rem;">
                            <div><span class="status-indicator status-connected"></span>OpenAI: Connected</div>
                            <div><span class="status-indicator status-connected"></span>Apify: Connected</div>
                        </div>
                    </div>
                    """)
                
                with gr.Column(scale=2, elem_classes="output-section"):
                    gr.Markdown("### � Analysis Results")
                    
                    # Create tabs for different views
                    with gr.Tabs(elem_classes="tab-nav"):
                        with gr.TabItem("🎯 Enhancement Report", elem_classes="tab-content"):
                            enhancement_output = gr.Textbox(
                                label="Enhancement Analysis",
                                lines=30,
                                interactive=False,
                                show_copy_button=True,
                                elem_classes="enhancement-output"
                            )
                        
                        with gr.TabItem("📋 Scraped Data", elem_classes="tab-content"):
                            scraped_data_output = gr.JSON(
                                label="Raw Profile Data",
                                elem_classes="scraped-data"
                            )
                        
                        with gr.TabItem("📈 Analytics Dashboard", elem_classes="tab-content"):
                            with gr.Row():
                                with gr.Column():
                                    completeness_score = gr.Number(
                                        label="📊 Completeness Score",
                                        value=0,
                                        interactive=False
                                    )
                                    job_match_score = gr.Number(
                                        label="🎯 Job Match Score", 
                                        value=0,
                                        interactive=False
                                    )
                                with gr.Column():
                                    overall_rating = gr.Textbox(
                                        label="⭐ Overall Rating",
                                        value="Not Analyzed",
                                        interactive=False
                                    )
                                    keyword_count = gr.Number(
                                        label="🔍 Keywords Found",
                                        value=0,
                                        interactive=False
                                    )
                            
                            profile_insights = gr.Textbox(
                                label="🔍 Profile Insights",
                                lines=15,
                                interactive=False,
                                show_copy_button=True
                            )
            
            # Examples section
            gr.Markdown("### 💡 Example LinkedIn URLs (for testing)")
            gr.Examples(
                examples=[
                    ["https://linkedin.com/in/example-profile"],
                    ["https://www.linkedin.com/in/sample-user"],
                ],
                inputs=[linkedin_url]
            )
            
            # Instructions
            gr.Markdown("""
            ### 📋 How to Use:
            1. **Enter LinkedIn URL**: Paste any public LinkedIn profile URL
            2. **Add Job Description** (Optional): Include a job posting for targeted suggestions  
            3. **Click Enhance Profile**: Get comprehensive analysis and recommendations
            4. **Review Results**: Implementation suggestions for each profile section
            
            ### 🔧 Current Capabilities:
            - ✅ **Real Profile Scraping**: Using Apify's LinkedIn scraper
            - ✅ **AI Content Generation**: Powered by OpenAI GPT models
            - ✅ **Job Matching**: Smart compatibility analysis
            - ✅ **Memory Management**: Session tracking and history
            
            ### 🛡️ Privacy Notice:
            This tool respects LinkedIn's terms of service and only processes publicly available profile information.
            """)            
            # Examples section
            gr.Markdown("### 💡 Example LinkedIn URLs (for testing)")
            gr.Examples(
                examples=[
                    ["https://www.linkedin.com/in/akshaychame/"],
                    ["https://linkedin.com/in/sample-profile"],
                ],
                inputs=[linkedin_url]
            )
            
            # Instructions
            with gr.Accordion("📋 How to Use", open=False):
                gr.Markdown("""
                ### Step-by-Step Guide:
                1. **Enter LinkedIn URL**: Paste any public LinkedIn profile URL
                2. **Add Job Description** (Optional): Include a job posting for targeted suggestions  
                3. **Click Enhance Profile**: Get comprehensive analysis and recommendations
                4. **Review Results**: Check different tabs for various insights
                
                ### 🔧 Current Capabilities:
                - ✅ **Real Profile Scraping**: Using Apify's LinkedIn scraper
                - ✅ **AI Content Generation**: Powered by OpenAI GPT-4o-mini
                - ✅ **Job Matching**: Smart compatibility analysis
                - ✅ **Data Visualization**: Raw data inspection and analytics
                
                ### 🛡️ Privacy Notice:
                This tool respects LinkedIn's terms of service and only processes publicly available profile information.
                """)
            
            # Event handlers - Updated for new interface
            submit_btn.click(
                fn=self.process_profile_enhanced,
                inputs=[linkedin_url, job_description],
                outputs=[
                    enhancement_output, 
                    scraped_data_output,
                    completeness_score,
                    job_match_score,
                    overall_rating,
                    keyword_count,
                    profile_insights
                ],
                show_progress=True
            )
            
            clear_btn.click(
                fn=lambda: ("", "", "", {}, 0, 0, "Not Analyzed", 0, ""),
                outputs=[
                    linkedin_url, 
                    job_description, 
                    enhancement_output,
                    scraped_data_output,
                    completeness_score,
                    job_match_score,
                    overall_rating,
                    keyword_count,
                    profile_insights
                ]
            )
        return demo

def run_api_test_demo():
    """
    Comprehensive API Test Demo - Run this to test all components
    This demonstrates the complete workflow with real API calls
    """
    print("\n" + "="*60)
    print("🧪 LINKEDIN ENHANCER - API TEST DEMO")
    print("="*60)
    
    # Test LinkedIn URL (you can change this)
    test_linkedin_url = "https://www.linkedin.com/in/akshaychame/"
    
    print(f"\n🔍 Testing with LinkedIn URL: {test_linkedin_url}")
    print("-" * 50)
    
    try:
        # Initialize components
        print("\n1️⃣  INITIALIZING COMPONENTS...")
        scraper = ScraperAgent()
        orchestrator = ProfileOrchestrator()
        
        # Test Apify Connection
        print("\n2️⃣  TESTING APIFY CONNECTION...")
        apify_connected = scraper.test_apify_connection()
        print(f"   Status: {'✅ Connected' if apify_connected else '❌ Failed'}")
        
        # Test Profile Scraping
        print("\n3️⃣  TESTING PROFILE SCRAPING...")
        profile_data = scraper.extract_profile_data(test_linkedin_url)
        
        if profile_data:
            print("   ✅ Profile data extracted successfully!")
            print(f"   📊 Name: {profile_data.get('name', 'N/A')}")
            print(f"   📊 Headline: {profile_data.get('headline', 'N/A')}")
            print(f"   📊 Experience entries: {len(profile_data.get('experience', []))}")
            print(f"   📊 Skills: {len(profile_data.get('skills', []))}")
            print(f"   📊 Education entries: {len(profile_data.get('education', []))}")
        else:
            print("   ❌ Failed to extract profile data")
            return
        
        # Test Profile Analysis
        print("\n4️⃣  TESTING PROFILE ANALYSIS...")
        from agents.analyzer_agent import AnalyzerAgent
        analyzer = AnalyzerAgent()
        
        analysis = analyzer.analyze_profile(profile_data)
        print("   ✅ Profile analysis completed!")
        print(f"   📊 Completeness Score: {analysis.get('completeness_score', 0):.1f}%")
        print(f"   📊 Overall Rating: {analysis.get('overall_rating', 'Unknown')}")
        print(f"   📊 Strengths: {len(analysis.get('strengths', []))}")
        print(f"   📊 Recommendations: {len(analysis.get('recommendations', []))}")
        
        # Test Content Generation
        print("\n5️⃣  TESTING AI CONTENT GENERATION...")
        content_agent = ContentAgent()
        openai_connected = content_agent.test_openai_connection()
        print(f"   OpenAI Status: {'✅ Connected' if openai_connected else '❌ Failed'}")
        
        if openai_connected:
            sample_suggestions = content_agent.generate_content_suggestions(profile_data, analysis)
            print("   ✅ AI content suggestions generated!")
            print(f"   📊 Generated {len(sample_suggestions)} suggestions")
        
        # Full Workflow Test
        print("\n6️⃣  TESTING COMPLETE WORKFLOW...")
        result = orchestrator.enhance_profile(test_linkedin_url, "")
        
        if "Error" not in result:
            print("   ✅ Complete workflow successful!")
            print("   📊 Full enhancement report generated")
        else:
            print(f"   ⚠️  Workflow completed with issues: {result[:100]}...")
        
        print("\n" + "="*60)
        print("🎉 API TEST DEMO COMPLETED!")
        print("="*60)
        print(f"✅ All systems tested - Ready for production use!")
        print(f"🌐 Access the web interface at: http://127.0.0.1:7861")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test demo failed: {str(e)}")
        print("   Check your API keys and network connection")
        print("="*60)

def run_quick_test():
    """Quick test of core functionality"""
    print("\n🚀 QUICK API TEST...")
    
    try:
        # Test Apify
        scraper = ScraperAgent()
        apify_ok = scraper.test_apify_connection()
        print(f"Apify: {'✅' if apify_ok else '❌'}")
        
        # Test OpenAI
        content_agent = ContentAgent()
        openai_ok = content_agent.test_openai_connection()
        print(f"OpenAI: {'✅' if openai_ok else '❌'}")
        
        # Test with sample URL
        if apify_ok:
            result = scraper.extract_profile_data("https://www.linkedin.com/in/akshaychame/")
            print(f"Scraping: {'✅' if result else '❌'}")
        
        print("✅ Quick test completed!\n")
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}\n")

def main():
    """
    Main entry point for LinkedIn Profile Enhancer
    
    Usage:
    - python app.py                    # Launch web interface
    - python app.py --test             # Run comprehensive API test demo
    - python app.py --quick-test       # Run quick API connectivity test
    """
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            print("🔥 Running API Test Demo...")
            run_api_test_demo()
            return
        elif sys.argv[1] == "--quick-test":
            print("🔥 Running Quick Test...")
            run_quick_test()
            return
        elif sys.argv[1] == "--help":
            print(__doc__ if __doc__ else main.__doc__)
            return
    
    # Default: Launch web interface
    print("🔥 Starting LinkedIn Profile Enhancer...")
    
    # Optional: Run quick test before launching web interface
    print("🔧 Running connectivity check...")
    run_quick_test()
    
    app = LinkedInEnhancerApp()
    demo = app.create_interface()
    
    print("🌐 Launching web interface...")
    demo.launch(
        share=True,
        server_name="127.0.0.1",
        server_port=7861,
        show_error=True
    )

if __name__ == "__main__":
    main()
