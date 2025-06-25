import streamlit as st
import json
import pandas as pd
from agents.orchestrator import ProfileOrchestrator
from agents.scraper_agent import ScraperAgent
from agents.content_agent import ContentAgent
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="🚀 LinkedIn Profile Enhancer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .success-card {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .warning-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    
    .info-card {
        background: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 0.5rem 0;
    }
    
    .stTabs > div > div > div > div {
        padding: 1rem;
    }
    
    .profile-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = ProfileOrchestrator()
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'profile_data' not in st.session_state:
        st.session_state.profile_data = None
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = None
    if 'current_url' not in st.session_state:
        st.session_state.current_url = None

def clear_results_if_url_changed(linkedin_url):
    """Clear cached results if URL has changed"""
    if st.session_state.current_url != linkedin_url:
        st.session_state.analysis_results = None
        st.session_state.profile_data = None
        st.session_state.suggestions = None
        st.session_state.current_url = linkedin_url
        st.cache_data.clear()  # Clear any Streamlit cache
        print(f"🔄 URL changed to: {linkedin_url} - Clearing cached data")

def create_header():
    """Create the main header"""
    st.markdown("""
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
    """, unsafe_allow_html=True)

def create_sidebar():
    """Create the sidebar with input controls"""
    with st.sidebar:
        st.header("📝 Configuration")
        
        # LinkedIn URL input
        linkedin_url = st.text_input(
            "🔗 LinkedIn Profile URL",
            placeholder="https://linkedin.com/in/your-profile",
            help="Enter the full LinkedIn profile URL to analyze"
        )
        
        # Job description input
        job_description = st.text_area(
            "🎯 Target Job Description (Optional)",
            placeholder="Paste the job description here for tailored suggestions...",
            height=150,
            help="Include job description for personalized optimization"
        )
        
        # API Status
        st.subheader("🔌 API Status")
        
        # Test API connections
        if st.button("🔄 Test Connections"):
            with st.spinner("Testing API connections..."):
                # Test Apify
                try:
                    scraper = ScraperAgent()
                    apify_status = scraper.test_apify_connection()
                    if apify_status:
                        st.success("✅ Apify: Connected")
                    else:
                        st.error("❌ Apify: Failed")
                except Exception as e:
                    st.error(f"❌ Apify: Error - {str(e)}")
                
                # Test OpenAI
                try:
                    content_agent = ContentAgent()
                    openai_status = content_agent.test_openai_connection()
                    if openai_status:
                        st.success("✅ OpenAI: Connected")
                    else:
                        st.error("❌ OpenAI: Failed")
                except Exception as e:
                    st.error(f"❌ OpenAI: Error - {str(e)}")
        
        # Examples
        st.subheader("💡 Example URLs")
        example_urls = [
            "https://linkedin.com/in/example-profile",
            "https://www.linkedin.com/in/sample-user"
        ]
        
        for url in example_urls:
            if st.button(f"📋 {url.split('/')[-1]}", key=url):
                st.session_state.example_url = url
        
        return linkedin_url, job_description

def create_metrics_display(analysis):
    """Create metrics display"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📈 Completeness Score",
            f"{analysis.get('completeness_score', 0):.1f}%",
            delta=None
        )
    
    with col2:
        rating = analysis.get('overall_rating', 'Unknown')
        st.metric(
            "⭐ Overall Rating",
            rating,
            delta=None
        )
    
    with col3:
        st.metric(
            "🎯 Job Match Score",
            f"{analysis.get('job_match_score', 0):.1f}%",
            delta=None
        )
    
    with col4:
        keywords = analysis.get('keyword_analysis', {})
        found_count = len(keywords.get('found_keywords', []))
        st.metric(
            "🔍 Keywords Found",
            found_count,
            delta=None
        )

def create_analysis_charts(analysis):
    """Create analysis charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Completeness breakdown
        scores = {
            'Profile Info': 20,
            'About Section': 25,
            'Experience': 25,
            'Skills': 15,
            'Education': 15
        }
        
        fig_pie = px.pie(
            values=list(scores.values()),
            names=list(scores.keys()),
            title="Profile Section Weights",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Score comparison
        current_score = analysis.get('completeness_score', 0)
        target_score = 90
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = current_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Profile Completeness"},
            delta = {'reference': target_score, 'increasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)

def display_profile_data(profile_data):
    """Display scraped profile data in a structured format"""
    if not profile_data:
        st.warning("No profile data available")
        return
    
    # Profile Header with Image
    st.subheader("👤 Profile Overview")
    
    # Create columns for profile image and basic info
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        # Display profile image
        profile_image = profile_data.get('profile_image_hq') or profile_data.get('profile_image')
        if profile_image:
            st.image(profile_image, width=150, caption="Profile Picture")
        else:
            st.markdown("""
            <div style="width: 150px; height: 150px; background-color: #f0f0f0; border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center; font-size: 48px;">
                👤
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card">
            <strong>Name:</strong> {profile_data.get('name', 'N/A')}<br>
            <strong>Headline:</strong> {profile_data.get('headline', 'N/A')}<br>
            <strong>Location:</strong> {profile_data.get('location', 'N/A')}<br>
            <strong>Connections:</strong> {profile_data.get('connections', 'N/A')}<br>
            <strong>Followers:</strong> {profile_data.get('followers', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="info-card">
            <strong>Current Job:</strong> {profile_data.get('job_title', 'N/A')}<br>
            <strong>Company:</strong> {profile_data.get('company_name', 'N/A')}<br>
            <strong>Industry:</strong> {profile_data.get('company_industry', 'N/A')}<br>
            <strong>Email:</strong> {profile_data.get('email', 'N/A')}<br>
            <strong>Profile URL:</strong> <a href="{profile_data.get('url', '#')}" target="_blank">View Profile</a>
        </div>
        """, unsafe_allow_html=True)
    
    # About Section
    if profile_data.get('about'):
        st.subheader("📝 About Section")
        st.markdown(f"""
        <div class="profile-section">
            {profile_data.get('about', 'No about section available')}
        </div>
        """, unsafe_allow_html=True)
    
    # Experience
    if profile_data.get('experience'):
        st.subheader("💼 Experience")
        for i, exp in enumerate(profile_data.get('experience', [])):
            with st.expander(f"{exp.get('title', 'Position')} at {exp.get('company', 'Company')}", expanded=i==0):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Duration:** {exp.get('duration', 'N/A')}")
                    st.write(f"**Location:** {exp.get('location', 'N/A')}")
                    if exp.get('description'):
                        st.write("**Description:**")
                        st.write(exp.get('description'))
                with col2:
                    st.write(f"**Current Role:** {'Yes' if exp.get('is_current') else 'No'}")
    
    # Skills
    if profile_data.get('skills'):
        st.subheader("🛠️ Skills")
        skills = profile_data.get('skills', [])
        if skills:
            # Create a DataFrame for better display
            skills_df = pd.DataFrame({'Skills': skills})
            st.dataframe(skills_df, use_container_width=True)
    
    # Education
    if profile_data.get('education'):
        st.subheader("🎓 Education")
        for edu in profile_data.get('education', []):
            st.markdown(f"""
            <div class="info-card">
                <strong>{edu.get('degree', 'Degree')}</strong><br>
                {edu.get('school', 'School')} | {edu.get('field', 'Field')}<br>
                <em>{edu.get('year', 'Year')}</em>
            </div>
            """, unsafe_allow_html=True)
    
    # Raw Data (collapsible)
    with st.expander("🔍 Raw JSON Data"):
        st.json(profile_data)

def display_analysis_results(analysis):
    """Display analysis results"""
    if not analysis:
        st.warning("No analysis results available")
        return
    
    # Metrics
    create_metrics_display(analysis)
    
    # Charts
    st.subheader("📊 Analysis Visualization")
    create_analysis_charts(analysis)
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌟 Profile Strengths")
        strengths = analysis.get('strengths', [])
        if strengths:
            for strength in strengths:
                st.markdown(f"""
                <div class="success-card">
                    ✅ {strength}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific strengths identified")
    
    with col2:
        st.subheader("🔧 Areas for Improvement")
        weaknesses = analysis.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                st.markdown(f"""
                <div class="warning-card">
                    🔸 {weakness}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No major areas for improvement identified")
    
    # Keyword Analysis
    keyword_analysis = analysis.get('keyword_analysis', {})
    if keyword_analysis:
        st.subheader("🔍 Keyword Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            found_keywords = keyword_analysis.get('found_keywords', [])
            if found_keywords:
                st.write("**Keywords Found:**")
                st.write(", ".join(found_keywords[:10]))
        
        with col2:
            missing_keywords = keyword_analysis.get('missing_keywords', [])
            if missing_keywords:
                st.write("**Missing Keywords:**")
                st.write(", ".join(missing_keywords[:5]))

def display_suggestions(suggestions):
    """Display enhancement suggestions"""
    if not suggestions:
        st.warning("No suggestions available")
        return
    
    for category, items in suggestions.items():
        if category == 'ai_generated_content':
            st.subheader("🤖 AI-Generated Content Suggestions")
            ai_content = items if isinstance(items, dict) else {}
            
            # Headlines
            if 'ai_headlines' in ai_content and ai_content['ai_headlines']:
                st.write("**✨ Professional Headlines:**")
                for i, headline in enumerate(ai_content['ai_headlines'], 1):
                    cleaned_headline = headline.strip('"').replace('\\"', '"')
                    if cleaned_headline.startswith(('1.', '2.', '3.', '4.', '5.')):
                        cleaned_headline = cleaned_headline[2:].strip()
                    st.write(f"{i}. {cleaned_headline}")
                st.write("")
            
            # About Section
            if 'ai_about_section' in ai_content and ai_content['ai_about_section']:
                st.write("**📝 Enhanced About Section:**")
                st.code(ai_content['ai_about_section'], language='text')
                st.write("")
            
            # Experience Descriptions
            if 'ai_experience_descriptions' in ai_content and ai_content['ai_experience_descriptions']:
                st.write("**💼 Experience Description Ideas:**")
                for desc in ai_content['ai_experience_descriptions']:
                    st.write(f"• {desc}")
                st.write("")
        else:
            # Standard categories
            category_name = category.replace('_', ' ').title()
            st.subheader(f"📋 {category_name}")
            if isinstance(items, list):
                for item in items:
                    st.write(f"• {item}")
            else:
                st.write(f"• {items}")
            st.write("")

def main():
    """Main Streamlit application"""
    initialize_session_state()
    create_header()
    
    # Sidebar
    linkedin_url, job_description = create_sidebar()
    
    # Main content
    if st.button("🚀 Enhance Profile", type="primary", use_container_width=True):
        if not linkedin_url.strip():
            st.error("Please enter a LinkedIn profile URL")
        elif not any(pattern in linkedin_url.lower() for pattern in ['linkedin.com/in/', 'www.linkedin.com/in/']):
            st.error("Please enter a valid LinkedIn profile URL")
        else:
            # Clear cached data if URL has changed
            clear_results_if_url_changed(linkedin_url)
            
            with st.spinner("🔍 Analyzing LinkedIn profile..."):
                try:
                    st.info(f"🔍 Extracting data from: {linkedin_url}")
                    
                    # Get profile data and analysis (force fresh extraction)
                    profile_data = st.session_state.orchestrator.scraper.extract_profile_data(linkedin_url)
                    
                    st.info(f"✅ Profile data extracted for: {profile_data.get('name', 'Unknown')}")
                    
                    analysis = st.session_state.orchestrator.analyzer.analyze_profile(profile_data, job_description)
                    suggestions = st.session_state.orchestrator.content_generator.generate_suggestions(analysis, job_description)
                    
                    # Store in session state
                    st.session_state.profile_data = profile_data
                    st.session_state.analysis_results = analysis
                    st.session_state.suggestions = suggestions
                    
                    st.success("✅ Profile analysis completed!")
                    
                except Exception as e:
                    st.error(f"❌ Error analyzing profile: {str(e)}")
    
    # Display results if available
    if st.session_state.profile_data or st.session_state.analysis_results:
        st.markdown("---")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "🔍 Scraped Data", "🎯 Suggestions", "📈 Implementation"])
        
        with tab1:
            st.header("📊 Profile Analysis")
            if st.session_state.analysis_results:
                display_analysis_results(st.session_state.analysis_results)
            else:
                st.info("No analysis results available yet")
        
        with tab2:
            st.header("🔍 Scraped Profile Data")
            if st.session_state.profile_data:
                display_profile_data(st.session_state.profile_data)
            else:
                st.info("No profile data available yet")
        
        with tab3:
            st.header("🎯 Enhancement Suggestions")
            if st.session_state.suggestions:
                display_suggestions(st.session_state.suggestions)
            else:
                st.info("No suggestions available yet")
        
        with tab4:
            st.header("📈 Implementation Roadmap")
            if st.session_state.analysis_results:
                recommendations = st.session_state.analysis_results.get('recommendations', [])
                if recommendations:
                    st.subheader("🎯 Priority Actions")
                    for i, rec in enumerate(recommendations[:5], 1):
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>{i}.</strong> {rec}
                        </div>
                        """, unsafe_allow_html=True)
                
                st.subheader("📊 General Best Practices")
                best_practices = [
                    "Update your profile regularly with new achievements",
                    "Use professional keywords relevant to your industry",
                    "Engage with your network by sharing valuable content",
                    "Ask for recommendations from colleagues and clients",
                    "Monitor profile views and connection requests"
                ]
                
                for practice in best_practices:
                    st.markdown(f"""
                    <div class="info-card">
                        🔸 {practice}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Complete the analysis first to see implementation suggestions")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🚀 <strong>LinkedIn Profile Enhancer</strong> | Powered by AI | Data scraped with respect to LinkedIn's ToS</p>
        <p>Built with ❤️ using Streamlit, OpenAI GPT-4o-mini, and Apify</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
