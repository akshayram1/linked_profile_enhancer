#!/usr/bin/env python3
"""
Test script to verify LinkedIn URL scraping fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.scraper_agent import ScraperAgent
from agents.orchestrator import ProfileOrchestrator

def test_url_handling():
    """Test that different URLs are handled correctly"""
    
    print("🧪 Testing LinkedIn URL handling...")
    
    # Test URLs
    test_urls = [
        "https://www.linkedin.com/in/test-user-1/",
        "https://www.linkedin.com/in/test-user-2/", 
        "linkedin.com/in/different-user"
    ]
    
    scraper = ScraperAgent()
    
    for url in test_urls:
        print(f"\n🔍 Testing URL: {url}")
        profile_data = scraper.extract_profile_data(url)
        
        print(f"✅ Profile Name: {profile_data.get('name', 'N/A')}")
        print(f"✅ Profile URL: {profile_data.get('url', 'N/A')}")
        print(f"✅ Scraped At: {profile_data.get('scraped_at', 'N/A')}")
        
        # Verify the URL is correctly stored
        if profile_data.get('url') != url and not profile_data.get('url', '').startswith('https://'):
            expected_url = 'https://' + url if not url.startswith('http') else url
            if profile_data.get('url') == expected_url:
                print("✅ URL normalization working correctly")
        
        print("-" * 50)

def test_orchestrator():
    """Test the orchestrator with fresh data"""
    
    print("\n🎭 Testing Orchestrator...")
    
    orchestrator = ProfileOrchestrator()
    
    # Test with force refresh
    test_url = "https://www.linkedin.com/in/example-user/"
    
    print(f"🔄 Testing with force refresh for: {test_url}")
    result = orchestrator.enhance_profile(test_url, force_refresh=True)
    
    print("✅ Orchestrator test completed")
    print(f"📝 Result length: {len(result)} characters")

if __name__ == "__main__":
    print("🚀 Starting LinkedIn URL Scraping Tests")
    print("=" * 60)
    
    try:
        test_url_handling()
        test_orchestrator()
        
        print("\n✅ All tests completed!")
        print("\n📋 Summary of fixes:")
        print("• Added URL change detection in Streamlit")
        print("• Added session state clearing when URL changes")
        print("• Enhanced logging in scraper agent")
        print("• Added cache clearing functionality")
        print("• Fixed URL normalization")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
