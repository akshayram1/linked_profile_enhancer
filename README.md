# LinkedIn Profile Enhancer

An AI-powered tool that analyzes LinkedIn profiles and provides personalized enhancement suggestions to improve professional visibility and job matching.

## Features

- 🔍 **Profile Analysis**: Comprehensive analysis of LinkedIn profile completeness and quality
- 🎯 **Job Matching**: Smart matching against job descriptions with skill gap analysis
- ✍️ **Content Generation**: AI-powered suggestions for headlines, about sections, and experience descriptions
- 💾 **Memory Management**: Session and persistent storage for tracking improvements over time
- 🌐 **Web Interface**: User-friendly Gradio interface for easy interaction

## Project Structure

```
linkedin_enhancer/
├── app.py                 # Main Gradio application
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py    # Main agent coordinator
│   ├── scraper_agent.py   # LinkedIn data extraction
│   ├── analyzer_agent.py  # Profile analysis
│   └── content_agent.py   # Content generation
├── memory/
│   ├── __init__.py
│   └── memory_manager.py  # Session & persistent memory
├── utils/
│   ├── __init__.py
│   ├── linkedin_parser.py # Parse scraped data
│   └── job_matcher.py     # Job matching logic
├── prompts/
│   └── agent_prompts.py   # All agent prompts
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd linkedin_enhancer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with your API keys
OPENAI_API_KEY=your_openai_key_here
APIFY_API_TOKEN=your_apify_token_here
```

## API Keys Setup

### Required Services:

1. **OpenAI API** (for AI content generation):
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Create an API key in your dashboard
   - Add to `.env` file: `OPENAI_API_KEY=sk-...`

2. **Apify API** (for LinkedIn scraping):
   - Sign up at [Apify](https://apify.com/)
   - Rent the "curious_coder/linkedin-profile-scraper" actor
   - Get your API token from account settings
   - Add to `.env` file: `APIFY_API_TOKEN=apify_api_...`

## Usage

### Running the Application

Start the Gradio interface:
```bash
python app.py
```

The application will launch a web interface where you can:
1. Input a LinkedIn profile URL
2. Optionally provide a job description for tailored suggestions
3. Get comprehensive analysis and enhancement recommendations

### Core Components

#### 1. Profile Orchestrator (`agents/orchestrator.py`)
The main coordinator that manages the entire enhancement workflow:
- Coordinates between scraper, analyzer, and content generation agents
- Manages data flow and session storage
- Formats final output for user presentation

#### 2. Scraper Agent (`agents/scraper_agent.py`)
Handles LinkedIn profile data extraction using Apify:
- **Real LinkedIn Scraping**: Uses Apify's `curious_coder/linkedin-profile-scraper`
- **Comprehensive Data**: Extracts experience, education, skills, connections, etc.
- **Fallback Support**: Uses mock data if scraping fails
- **Rate Limiting**: Built-in delays to respect LinkedIn's terms

#### 3. Analyzer Agent (`agents/analyzer_agent.py`)
Performs comprehensive profile analysis:
- Calculates profile completeness score
- Analyzes keyword optimization
- Identifies strengths and weaknesses
- Assesses content quality
- Provides job matching scores

#### 4. Content Agent (`agents/content_agent.py`)
Generates enhancement suggestions using AI:
- **AI-Powered Content**: Uses OpenAI GPT models for content generation
- **Smart Headlines**: AI-generated LinkedIn headline suggestions
- **About Section**: AI-crafted professional summaries
- **Experience Optimization**: Enhanced job descriptions with metrics
- **Fallback Logic**: Traditional rule-based suggestions if AI unavailable

#### 5. Memory Manager (`memory/memory_manager.py`)
Handles data persistence:
- Session data storage
- User preferences
- Analysis history tracking
- Data export functionality

#### 6. Utility Classes
- **LinkedIn Parser** (`utils/linkedin_parser.py`): Cleans and standardizes profile data
- **Job Matcher** (`utils/job_matcher.py`): Calculates job compatibility scores

## Key Features

### Profile Analysis
- **Completeness Score**: Measures profile completeness (0-100%)
- **Keyword Analysis**: Identifies missing keywords for target roles
- **Content Quality**: Assesses use of action words and quantified achievements
- **Strengths/Weaknesses**: Identifies areas of improvement

### Job Matching
- **Skills Gap Analysis**: Compares profile skills with job requirements
- **Match Scoring**: Weighted scoring across skills, experience, keywords, and education
- **Improvement Recommendations**: Specific suggestions to increase match scores

### Content Enhancement
- **Smart Suggestions**: Context-aware recommendations for each profile section
- **Template Generation**: Provides templates and examples for better content
- **Keyword Optimization**: Natural integration of relevant keywords

## Development

### Adding New Features

1. **New Analysis Criteria**: Extend `AnalyzerAgent` with additional analysis methods
2. **Enhanced Scraping**: Improve `ScraperAgent` with better data extraction (requires LinkedIn API setup)
3. **AI Integration**: Add LLM calls in `ContentAgent` for more sophisticated suggestions
4. **Additional Matching Logic**: Extend `JobMatcher` with more sophisticated algorithms

### Configuration

The system uses configurable weights for job matching in `utils/job_matcher.py`:
```python
weight_config = {
    'skills': 0.4,
    'experience': 0.3, 
    'keywords': 0.2,
    'education': 0.1
}
```

## Limitations & Considerations

### Current Capabilities
- ✅ **Real LinkedIn Scraping**: Uses Apify's professional scraper
- ✅ **AI Content Generation**: OpenAI GPT-powered suggestions
- ✅ **Job Matching**: Advanced compatibility scoring
- ✅ **Memory Management**: Session tracking and persistent storage

### Production Ready Features
- **API Integration**: Full OpenAI and Apify integration
- **Error Handling**: Graceful fallbacks and error recovery
- **Rate Limiting**: Respects API limits and LinkedIn terms
- **Data Validation**: Input validation and sanitization

### Production Considerations
- **Rate Limiting**: Built-in API rate limiting and respect for service terms
- **Data Privacy**: Secure handling of profile data and API keys
- **Scalability**: Modular architecture supports high-volume usage
- **Monitoring**: API connection testing and error tracking

## Testing the Setup

After setting up your API keys, test the connections:

```python
# Test Apify connection
python -c "from agents.scraper_agent import ScraperAgent; ScraperAgent().test_apify_connection()"

# Test OpenAI connection  
python -c "from agents.content_agent import ContentAgent; ContentAgent().test_openai_connection()"
```

## Future Enhancements

- 📊 **Analytics Dashboard**: Track improvement metrics over time
- 🔄 **A/B Testing**: Test different enhancement strategies
- 🌐 **Multi-language Support**: Support for profiles in different languages
- 📱 **Mobile App**: React Native or Flutter mobile application
- 🔗 **LinkedIn Integration**: Direct LinkedIn API partnership for real-time updates
- 🎯 **Industry-specific Templates**: Tailored suggestions for different industries
- 📈 **Performance Tracking**: Monitor profile view increases after optimizations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or support, please open an issue in the repository or contact the development team.

---

**Note**: This tool is for educational and professional development purposes. Always respect LinkedIn's terms of service and data privacy regulations when using profile data.
# linked_profile_enhancer
