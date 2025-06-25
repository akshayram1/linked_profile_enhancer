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
        
        # Validate token format
        if not self.apify_token.startswith('apify_api_'):
            print(f"⚠️ Warning: Token doesn't start with 'apify_api_'. Current token starts with: {self.apify_token[:10]}...")
        
        # Use the new actor API endpoint
        self.api_url = f"https://api.apify.com/v2/acts/dev_fusion~linkedin-profile-scraper/run-sync-get-dataset-items?token={self.apify_token}"
        
        print(f"🔑 Using Apify token: {self.apify_token[:15]}...")  # Show first 15 chars for debugging
    
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
            print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Clean and validate URL
            original_url = linkedin_url
            linkedin_url = linkedin_url.strip()
            if not linkedin_url.startswith('http'):
                linkedin_url = 'https://' + linkedin_url
            
            print(f"🧹 Cleaned URL: {linkedin_url}")
            
            # Verify URL consistency
            if original_url != linkedin_url:
                print(f"🔄 URL normalized: {original_url} → {linkedin_url}")
            
            # Configure the run input with fresh URL
            run_input = {
                "profileUrls": [linkedin_url],  # This actor expects profileUrls, not startUrls
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
            response = requests.post(
                self.api_url,
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
                    error_msg = "No data returned from Apify API. The profile may be private or the scraper encountered an issue."
                    print(f"❌ {error_msg}")
                    raise ValueError(error_msg)
            else:
                error_details = ""
                try:
                    error_response = response.json()
                    error_details = f" - {error_response.get('error', {}).get('message', response.text)}"
                except:
                    error_details = f" - {response.text}"
                
                if response.status_code == 401:
                    error_msg = f"Authentication failed (401): Invalid or expired API token{error_details}"
                    print(f"❌ {error_msg}")
                    print(f"🔑 Token being used: {self.apify_token[:15]}...")
                    print(f"💡 Please check your APIFY_API_TOKEN in your .env file")
                elif response.status_code == 404:
                    error_msg = f"Actor not found (404): The actor 'dev_fusion~linkedin-profile-scraper' may not exist{error_details}"
                    print(f"❌ {error_msg}")
                elif response.status_code == 429:
                    error_msg = f"Rate limit exceeded (429): Too many requests{error_details}"
                    print(f"❌ {error_msg}")
                else:
                    error_msg = f"API request failed with status {response.status_code}{error_details}"
                    print(f"❌ {error_msg}")
                
                raise requests.RequestException(error_msg)
                
        except requests.Timeout:
            error_msg = "Request timed out. The scraping operation took too long to complete."
            print(f"⏰ {error_msg}")
            raise requests.Timeout(error_msg)
        except Exception as e:
            error_msg = f"Error extracting profile data: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def test_apify_connection(self) -> bool:
        """Test if Apify connection is working"""
        try:
            # Test with the actor endpoint
            test_url = f"https://api.apify.com/v2/acts/dev_fusion~linkedin-profile-scraper?token={self.apify_token}"
            print(f"🔗 Testing connection to: {test_url[:50]}...")
            
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                actor_info = response.json()
                print(f"✅ Successfully connected to Apify actor: {actor_info.get('name', 'LinkedIn Profile Scraper')}")
                return True
            elif response.status_code == 401:
                print(f"❌ Authentication failed (401): Invalid or expired API token")
                print(f"🔑 Token being used: {self.apify_token[:15]}...")
                print(f"💡 Please check your APIFY_API_TOKEN in your .env file")
                return False
            elif response.status_code == 404:
                print(f"❌ Actor not found (404): The actor 'dev_fusion~linkedin-profile-scraper' may not exist or be accessible")
                return False
            else:
                print(f"❌ Failed to connect to Apify: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to Apify: {str(e)}")
            return False
    
    def _process_apify_data(self, raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Process raw Apify data into standardized format"""
        
        print(f"📊 Processing data for URL: {url}")
        print(f"📋 Raw data keys: {list(raw_data.keys())}")
        
        # Extract basic information - using the correct field names from API
        profile_data = {
            'name': raw_data.get('fullName', ''),
            'headline': raw_data.get('headline', ''),
            'location': raw_data.get('addressWithCountry', raw_data.get('addressWithoutCountry', '')),
            'about': raw_data.get('about', ''),  # API uses 'about' not 'summary'
            'connections': raw_data.get('connections', 0),
            'followers': raw_data.get('followers', 0),
            'email': raw_data.get('email', ''),
            'url': url,  # Use the URL that was actually requested
            'profile_image': raw_data.get('profilePic', ''),
            'profile_image_hq': raw_data.get('profilePicHighQuality', ''),
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'job_title': raw_data.get('jobTitle', ''),
            'company_name': raw_data.get('companyName', ''),
            'company_industry': raw_data.get('companyIndustry', ''),
            'company_website': raw_data.get('companyWebsite', ''),
            'company_size': raw_data.get('companySize', ''),
            'current_job_duration': raw_data.get('currentJobDuration', ''),
            'top_skills': raw_data.get('topSkillsByEndorsements', '')
        }
        
        print(f"✅ Extracted profile for: {profile_data.get('name', 'Unknown')}")
        print(f"🔗 Profile URL stored: {profile_data['url']}")
        
        # Process experience - API uses 'experiences' array
        experience_list = []
        for exp in raw_data.get('experiences', []):
            experience_item = {
                'title': exp.get('title', ''),
                'company': exp.get('subtitle', '').replace(' · Full-time', '').replace(' · Part-time', ''),
                'duration': exp.get('caption', ''),
                'description': '',  # Extract from subComponents if available
                'location': exp.get('metadata', ''),
                'company_logo': exp.get('logo', ''),
                'is_current': 'Present' in exp.get('caption', '') or '·' not in exp.get('caption', '')
            }
            
            # Extract description from subComponents
            if 'subComponents' in exp and exp['subComponents']:
                for sub in exp['subComponents']:
                    if 'description' in sub and sub['description']:
                        descriptions = []
                        for desc in sub['description']:
                            if isinstance(desc, dict) and desc.get('text'):
                                descriptions.append(desc['text'])
                        experience_item['description'] = ' '.join(descriptions)
            
            experience_list.append(experience_item)
        profile_data['experience'] = experience_list
        
        # Process education - API uses 'educations' array
        education_list = []
        for edu in raw_data.get('educations', []):
            education_item = {
                'degree': edu.get('subtitle', ''),
                'school': edu.get('title', ''),
                'field': '',  # Extract from subtitle
                'year': edu.get('caption', ''),
                'logo': edu.get('logo', ''),
                'grade': ''  # Extract from subComponents if available
            }
            
            # Split degree and field from subtitle
            subtitle = edu.get('subtitle', '')
            if ' - ' in subtitle:
                parts = subtitle.split(' - ', 1)
                education_item['degree'] = parts[0]
                education_item['field'] = parts[1] if len(parts) > 1 else ''
            elif ', ' in subtitle:
                parts = subtitle.split(', ', 1)
                education_item['degree'] = parts[0]
                education_item['field'] = parts[1] if len(parts) > 1 else ''
            
            # Extract grade from subComponents
            if 'subComponents' in edu and edu['subComponents']:
                for sub in edu['subComponents']:
                    if 'description' in sub and sub['description']:
                        for desc in sub['description']:
                            if isinstance(desc, dict) and desc.get('text', '').startswith('Grade:'):
                                education_item['grade'] = desc['text']
            
            education_list.append(education_item)
        profile_data['education'] = education_list
        
        # Process skills - API uses 'skills' array with title
        skills_list = []
        for skill in raw_data.get('skills', []):
            if isinstance(skill, dict) and 'title' in skill:
                skills_list.append(skill['title'])
            elif isinstance(skill, str):
                skills_list.append(skill)
        profile_data['skills'] = skills_list
        
        # Process certifications - API uses 'licenseAndCertificates'
        certifications_list = []
        for cert in raw_data.get('licenseAndCertificates', []):
            cert_item = {
                'title': cert.get('title', ''),
                'issuer': cert.get('subtitle', ''),
                'date': cert.get('caption', ''),
                'credential_id': cert.get('metadata', ''),
                'logo': cert.get('logo', '')
            }
            certifications_list.append(cert_item)
        profile_data['certifications'] = certifications_list
        
        # Process languages (if available)
        profile_data['languages'] = raw_data.get('languages', [])
        
        # Process volunteer experience (if available)
        volunteer_list = []
        for vol in raw_data.get('volunteerAndAwards', []):
            if isinstance(vol, dict):
                volunteer_list.append(vol)
        profile_data['volunteer_experience'] = volunteer_list
        
        # Additional rich data
        profile_data['honors_awards'] = raw_data.get('honorsAndAwards', [])
        profile_data['projects'] = raw_data.get('projects', [])
        profile_data['publications'] = raw_data.get('publications', [])
        profile_data['recommendations'] = raw_data.get('recommendations', [])
        profile_data['interests'] = raw_data.get('interests', [])
        
        return profile_data
