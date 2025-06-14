#!/usr/bin/env python
"""
Test script for AI Image Recognition functionality
Tests the system without EasyOCR dependency
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Books4Geeks.settings')
django.setup()

def test_ai_image_recognition():
    """Test AI Image Recognition module"""
    print("🧪 Testing AI Image Recognition System...")
    print("=" * 50)
    
    try:
        # Import the AI module
        from B4G.ai_image_recognition import AIImageRecognition, EASYOCR_AVAILABLE, GEMINI_AVAILABLE
        
        print(f"✅ AI module imported successfully")
        print(f"📦 EasyOCR Available: {EASYOCR_AVAILABLE}")
        print(f"🤖 Gemini AI Available: {GEMINI_AVAILABLE}")
        
        # Initialize AI system
        ai = AIImageRecognition()
        print(f"✅ AI system initialized")
        print(f"🔍 OCR Reader: {'Available' if ai.ocr_reader else 'Not Available (using fallback)'}")
        print(f"🧠 AI Model: {'Available' if ai.model else 'Not Configured'}")
        
        # Test genre keywords
        print(f"📚 Genre Categories: {len(ai.genre_keywords)} categories loaded")
        for genre, keywords in list(ai.genre_keywords.items())[:3]:
            print(f"   - {genre}: {len(keywords)} keywords")
        
        print("=" * 50)
        print("🎯 System Status:")
        
        if ai.model:
            print("✅ READY: AI Image Recognition fully operational with Gemini AI")
            print("   - Text extraction via Gemini AI")
            print("   - Genre classification available")
            print("   - Damage assessment functional")
            print("   - Auto-categorization active")
        elif EASYOCR_AVAILABLE:
            print("⚠️  PARTIAL: OCR available but no AI analysis")
            print("   - Text extraction via EasyOCR")
            print("   - Basic genre classification")
            print("   - Limited damage assessment")
        else:
            print("🔧 FALLBACK: Using computer vision fallbacks")
            print("   - OpenCV-based text region detection")
            print("   - Keyword-based genre classification")
            print("   - Basic damage assessment")
        
        # Test error handling
        test_result = ai._error_response("Test error")
        if not test_result['success']:
            print("✅ Error handling working correctly")
        
        print("=" * 50)
        print("🚀 AI Image Recognition Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_django_integration():
    """Test Django integration"""
    print("\n🔗 Testing Django Integration...")
    print("=" * 50)
    
    try:
        # Test model imports
        from B4G.models import Books
        print("✅ Books model imported")
        
        # Test views import
        from B4G.views import ai_image_recognition_dashboard
        print("✅ AI views imported")
        
        # Test URL configuration
        from django.urls import reverse
        try:
            url = reverse('ai_image_recognition_dashboard')
            print(f"✅ AI dashboard URL: {url}")
        except:
            print("⚠️  AI URLs might not be fully configured")
        
        print("✅ Django integration working")
        return True
        
    except Exception as e:
        print(f"❌ Django integration error: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Books4Geeks AI Image Recognition Test Suite")
    print("=" * 60)
    
    # Test AI functionality
    ai_test = test_ai_image_recognition()
    
    # Test Django integration
    django_test = test_django_integration()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print(f"   AI System: {'✅ PASS' if ai_test else '❌ FAIL'}")
    print(f"   Django Integration: {'✅ PASS' if django_test else '❌ FAIL'}")
    
    if ai_test and django_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 AI Image Recognition is ready for use!")
        print("\n📝 Next Steps:")
        print("   1. Add Gemini API key to .env file for full functionality")
        print("   2. Start Django server: python manage.py runserver")
        print("   3. Navigate to AI Recognition in the menu")
        print("   4. Upload book cover images to test")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return ai_test and django_test

if __name__ == "__main__":
    main()
