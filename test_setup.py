#!/usr/bin/env python
"""Quick test to verify the app can start"""
import sys
import traceback
import os

def test_imports():
    """Test all imports work"""
    try:
        from main import app
        print("[PASS] Main app imports successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to import app: {e}")
        traceback.print_exc()
        return False

def test_templates():
    """Test templates directory exists"""
    if os.path.exists("templates"):
        print("[PASS] Templates directory exists")
        templates = os.listdir("templates")
        print(f"  Templates: {', '.join(templates)}")
        return True
    else:
        print("[FAIL] Templates directory missing")
        return False

def test_static():
    """Test static directory exists"""
    if os.path.exists("static"):
        print("[PASS] Static directory exists")
        css = os.path.exists("static/css/styles.css")
        js = os.path.exists("static/js/main.js")
        print(f"  CSS: {'found' if css else 'missing'}, JS: {'found' if js else 'missing'}")
        return css and js
    else:
        print("[FAIL] Static directory missing")
        return False

def main():
    print("Testing FastAPI Pro UI setup...\n")
    results = []
    
    results.append(test_imports())
    results.append(test_templates())
    results.append(test_static())
    
    print(f"\n{'='*50}")
    if all(results):
        print("[SUCCESS] All tests passed!")
        print("\nTo start the server:")
        print("  uvicorn main:app --reload")
        print("\nThen visit:")
        print("  http://127.0.0.1:8000/dashboard")
        return 0
    else:
        print("[FAILED] Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
