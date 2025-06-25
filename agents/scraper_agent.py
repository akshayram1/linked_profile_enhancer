import os
import time
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ScraperAgent:
    """Agent responsible for extracting data from LinkedIn profiles using Apify REST API"""
    
    def __init__(self):
        self.apify_token = os.getenv('APIFY_API_TOKEN')
        if not self.apify_token:
            raise ValueError("APIFY_API_TOKEN not found in environment variables")
        
        # Use the task-based API endpoint you provided
        self.api_url = "https://api.apify.com/v2/actor-tasks/proactive_quantifier~linkedin-profile-scraper-task/run-sync-get-dataset-items?token=apify_api_4y5Vilfl2GDDlMSY1M2JhdJxowJPg01SpbH1&method=POST"
    
    def extract_profile_data(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Extract profile data from LinkedIn URL using Apify REST API
        
        Args:
            linkedin_url (str): LinkedIn profile URL
            
        Returns:
            Dict[str, Any]: Extracted profile data
        """
        try:
            print(f"🔍 Starting scraping for: {linkedin_url}")
            print(f"🔗 URL being processed: {linkedin_url}")
            
            # Clean and validate URL
            linkedin_url = linkedin_url.strip()
            if not linkedin_url.startswith('http'):
                linkedin_url = 'https://' + linkedin_url
            
            print(f"🧹 Cleaned URL: {linkedin_url}")
            
            # Configure the run input with fresh URL
            run_input = {
                "profileUrls": [linkedin_url],
                "slowDown": True,  # To avoid being blocked
                "includeSkills": True,
                "includeExperience": True,
                "includeEducation": True,
                "includeRecommendations": False,  # Optional, can be slow
                "saveHtml": False,
                "saveMarkdown": False
            }
            
            print(f"📋 Apify input: {json.dumps(run_input, indent=2)}")
            
            # Make the API request
            print("🚀 Running Apify scraper via REST API...")
            response = requests.post(                self.api_url,
                json=run_input,
                headers={'Content-Type': 'application/json'},
                timeout=180  # 3 minutes timeout
            )
            
            if response.status_code in [200, 201]:  # 201 is also success for Apify
                results = response.json()
                print(f"✅ API Response received: {len(results)} items")
                
                if results and len(results) > 0:
                    # Process the first result (since we're scraping one profile)
                    raw_data = results[0]
                    processed_data = self._process_apify_data(raw_data, linkedin_url)
                    print("✅ Successfully extracted and processed profile data")
                    return processed_data
                else:
                    print("⚠️ No data in API response, falling back to mock data")
                    return self._mock_profile_data(linkedin_url)
            else:
                print(f"❌ API request failed: {response.status_code} - {response.text}")
                print("⚠️ Falling back to mock data")
                return self._mock_profile_data(linkedin_url)
                
        except requests.Timeout:
            print("⏰ Request timed out, falling back to mock data")
            return self._mock_profile_data(linkedin_url)
        except Exception as e:
            print(f"❌ Error extracting profile data: {str(e)}")
            print("⚠️ Falling back to mock data for demonstration")
            return self._mock_profile_data(linkedin_url)
    
    def test_apify_connection(self) -> bool:
        """Test if Apify connection is working"""
        try:
            # Test with the task endpoint
            test_url = "https://api.apify.com/v2/actor-tasks/proactive_quantifier~linkedin-profile-scraper-task?token=apify_api_4y5Vilfl2GDDlMSY1M2JhdJxowJPg01SpbH1"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                task_info = response.json()
                print(f"✅ Successfully connected to Apify task: {task_info.get('name', 'LinkedIn Profile Scraper Task')}")
                return True
            else:
                print(f"❌ Failed to connect to Apify: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to Apify: {str(e)}")
            return False
    
    def _process_apify_data(self, raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Process raw Apify data into standardized format"""
        
        print(f"📊 Processing data for URL: {url}")
        print(f"📋 Raw data keys: {list(raw_data.keys())}")
        
        # Extract basic information
        profile_data = {
            'name': raw_data.get('fullName', ''),
            'headline': raw_data.get('headline', ''),
            'location': raw_data.get('location', ''),
            'about': raw_data.get('summary', ''),
            'connections': raw_data.get('connectionsCount', 0),
            'url': url,  # Use the URL that was actually requested
            'profile_image': raw_data.get('profilePicture', ''),
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"✅ Extracted profile for: {profile_data.get('name', 'Unknown')}")
        print(f"🔗 Profile URL stored: {profile_data['url']}")
        
        # Process experience
        experience_list = []
        for exp in raw_data.get('experience', []):
            experience_item = {
                'title': exp.get('title', ''),
                'company': exp.get('companyName', ''),
                'duration': f"{exp.get('startDate', '')} - {exp.get('endDate', 'Present')}",
                'description': exp.get('description', ''),
                'location': exp.get('location', ''),
                'start_date': exp.get('startDate', ''),
                'end_date': exp.get('endDate', ''),
                'is_current': exp.get('endDate') is None or exp.get('endDate') == ''
            }
            experience_list.append(experience_item)
        profile_data['experience'] = experience_list
        
        # Process education
        education_list = []
        for edu in raw_data.get('education', []):
            education_item = {
                'degree': edu.get('degreeName', ''),
                'school': edu.get('schoolName', ''),
                'field': edu.get('fieldOfStudy', ''),
                'year': edu.get('startDate', '') + ' - ' + edu.get('endDate', ''),
                'start_date': edu.get('startDate', ''),
                'end_date': edu.get('endDate', '')
            }
            education_list.append(education_item)
        profile_data['education'] = education_list
        
        # Process skills
        skills_list = []
        for skill in raw_data.get('skills', []):
            if isinstance(skill, dict):
                skills_list.append(skill.get('name', ''))
            else:
                skills_list.append(str(skill))
        profile_data['skills'] = skills_list
        
        # Additional information
        profile_data['languages'] = raw_data.get('languages', [])
        profile_data['certifications'] = raw_data.get('certifications', [])
        profile_data['volunteer_experience'] = raw_data.get('volunteerExperience', [])
        
        return profile_data
    
    def _mock_profile_data(self, url: str) -> Dict[str, Any]:
        """Mock profile data for demonstration purposes"""
        print(f"⚠️ Using mock data for URL: {url}")
        
        # Extract potential name from URL for more realistic mock data
        profile_name = "Demo User"
        if "/in/" in url:
            profile_slug = url.split("/in/")[-1].split("/")[0].replace("-", " ").title()
            if profile_slug and len(profile_slug) > 2:
                profile_name = profile_slug
        
        return {
            'name': profile_name,
            'headline': 'Software Engineer | Full Stack Developer | React & Node.js',
            'location': 'India',
            'about': f'Passionate software engineer with expertise in full-stack development. This is mock data for demonstration purposes since the actual LinkedIn profile at {url} could not be scraped.',
            'experience': [
                {
                    'title': 'Software Engineer',
                    'company': 'Tech Solutions',
                    'duration': '2022 - Present',
                    'description': 'Developed full-stack web applications using React and Node.js. Improved application performance by 40% and led a team of 3 developers.',
                    'location': 'India',
                    'start_date': '2022-01',
                    'end_date': None,
                    'is_current': True
                },
                {
                    'title': 'Junior Developer',
                    'company': 'Startup Inc',
                    'duration': '2021 - 2022',
                    'description': 'Built responsive web interfaces and REST APIs. Collaborated with cross-functional teams to deliver high-quality software solutions.',
                    'location': 'India',
                    'start_date': '2021-06',
                    'end_date': '2022-01',
                    'is_current': False
                }
            ],
            'education': [
                {
                    'degree': 'Bachelor of Engineering',
                    'school': 'Engineering College',
                    'field': 'Computer Science',
                    'year': '2017 - 2021',
                    'start_date': '2017',
                    'end_date': '2021'
                }
            ],
            'skills': [
                'JavaScript', 'React', 'Node.js', 'Python', 'HTML/CSS', 
                'MongoDB', 'SQL', 'Git', 'AWS', 'Express.js', 'TypeScript'
            ],
            'connections': 500,
            'url': url,
            'languages': ['English', 'Hindi'],
            'certifications': [],
            'volunteer_experience': [],
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
