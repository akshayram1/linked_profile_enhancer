#!/usr/bin/env python3
"""
Test script for LinkedIn Enhancer API connections
Run this to verify your API keys are working correctly
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment setup"""
    print("🔧 Testing Environment Setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    apify_token = os.getenv('APIFY_API_TOKEN')
    
    print(f"✅ OpenAI API Key: {'Found' if openai_key else 'Missing'}")
    print(f"✅ Apify API Token: {'Found' if apify_token else 'Missing'}")
    
    if not openai_key or not apify_token:
        print("\n❌ Missing API keys! Please check your .env file")
        return False
    
    return True

def test_apify():
    """Test Apify connection"""
    print("\n🔗 Testing Apify Connection...")
    
    try:
        from agents.scraper_agent import ScraperAgent
        scraper = ScraperAgent()
        
        if scraper.test_apify_connection():
            print("✅ Apify connection successful!")
            return True
        else:
            print("❌ Apify connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Apify test error: {str(e)}")
        return False

def test_openai():
    """Test OpenAI connection"""
    print("\n🤖 Testing OpenAI Connection...")
    
    try:
        from agents.content_agent import ContentAgent
        content_agent = ContentAgent()
        
        if content_agent.test_openai_connection():
            print("✅ OpenAI connection successful!")
            return True
        else:
            print("❌ OpenAI connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI test error: {str(e)}")
        return False

def test_full_workflow():
    """Test a basic workflow"""
    print("\n🚀 Testing Basic Workflow...")
    
    try:
        from agents.orchestrator import ProfileOrchestrator
        
        orchestrator = ProfileOrchestrator()
        
        # Test with Akshay's LinkedIn profile
        test_url = "https://www.linkedin.com/in/akshay-chame-b43bb8209/"
        test_job = "Software Engineer position requiring Python, React, and full-stack development skills"
        
        print(f"Testing with profile: {test_url}")
        print("Running profile enhancement test...")
        result = orchestrator.enhance_profile(test_url, test_job)        
        if result and len(result) > 100:  # Basic check for substantial output
            print("✅ Full workflow test successful!")
            print(f"📄 Generated {len(result)} characters of analysis")
            
            # Show a preview of the results
            print("\n📋 Preview of Analysis Results:")
            print("-" * 40)
            preview = result[:500] + "..." if len(result) > 500 else result
            print(preview)
            print("-" * 40)
            
            return True
        else:
            print("❌ Workflow test failed!")
            print(f"Result length: {len(result) if result else 0}")
            return False
            
    except Exception as e:
        print(f"❌ Workflow test error: {str(e)}")
        return False

def test_akshay_profile():
    """Test specifically with Akshay's LinkedIn profile"""
    print("\n👤 Testing Akshay's Profile Analysis...")
    
    try:
        from agents.scraper_agent import ScraperAgent
        from agents.analyzer_agent import AnalyzerAgent
        from agents.content_agent import ContentAgent
        
        # Test scraping
        print("📥 Scraping profile data...")
        scraper = ScraperAgent()
        profile_data = scraper.extract_profile_data("https://www.linkedin.com/in/akshay-chame-b43bb8209/")
        
        if profile_data:
            print(f"✅ Profile data extracted: {profile_data.get('name', 'Unknown')}")
            print(f"   📍 Location: {profile_data.get('location', 'N/A')}")
            print(f"   💼 Headline: {profile_data.get('headline', 'N/A')}")
            print(f"   🎯 Skills: {len(profile_data.get('skills', []))} skills found")
        
        # Test analysis
        print("\n🔍 Analyzing profile...")
        analyzer = AnalyzerAgent()
        analysis = analyzer.analyze_profile(profile_data, "Full Stack Developer with Python and React experience")
        
        if analysis:
            print(f"✅ Analysis completed:")
            print(f"   📊 Completeness Score: {analysis.get('completeness_score', 0):.1f}%")
            print(f"   💪 Strengths: {len(analysis.get('strengths', []))}")
            print(f"   🎯 Areas for improvement: {len(analysis.get('weaknesses', []))}")
        
        # Test content generation
        print("\n✍️ Generating suggestions...")
        content_agent = ContentAgent()
        suggestions = content_agent.generate_suggestions(analysis, "Full Stack Developer")
        
        if suggestions:
            print("✅ Content suggestions generated:")
            for category, items in suggestions.items():
                if isinstance(items, list) and items:
                    print(f"   📝 {category.replace('_', ' ').title()}: {len(items)} suggestions")
        
        return True
        
    except Exception as e:
        print(f"❌ Akshay profile test error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🎯 LinkedIn Profile Enhancer - API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Apify API", test_apify),
        ("OpenAI API", test_openai),
        ("Full Workflow", test_full_workflow),
        ("Akshay Profile Specific Test", test_akshay_profile)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your setup is ready to go!")
        print("Run 'python app.py' to start the application.")
    else:
        print("⚠️  Some tests failed. Please check your API keys and setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
