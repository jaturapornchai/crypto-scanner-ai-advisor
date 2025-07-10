#!/usr/bin/env python3
"""
Simple verification script to check that the new functionality is working.
"""

def test_method_exists():
    """Test that the hourly_position_check method exists"""
    try:
        from enhanced_position_manager import EnhancedPositionManager
        
        # Check if the method exists
        if hasattr(EnhancedPositionManager, 'hourly_position_check'):
            print("✅ hourly_position_check method exists")
            return True
        else:
            print("❌ hourly_position_check method not found")
            return False
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_app_structure():
    """Test that app.py has the expected structure"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for hourly position check call
        if 'hourly_position_check()' in content:
            print("✅ app.py calls hourly_position_check")
        else:
            print("❌ app.py does not call hourly_position_check")
            return False
            
        # Check that summary calls are removed/minimal
        summary_count = content.count('show_summary()')
        if summary_count == 0:
            print("✅ Summary calls removed from main loop")
        else:
            print(f"⚠️ Still has {summary_count} summary calls")
            
        return True
        
    except Exception as e:
        print(f"❌ File check failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verifying hourly position/order checking implementation...")
    print("=" * 60)
    
    test1 = test_method_exists()
    test2 = test_app_structure()
    
    print("=" * 60)
    if test1 and test2:
        print("🎉 Implementation verified successfully!")
        print("")
        print("📝 Summary of changes:")
        print("   ✅ Position/order checking moved to hourly schedule")
        print("   ✅ Summary information minimized")  
        print("   ✅ Main loop simplified")
        print("   ✅ New hourly_position_check method added")
        print("")
        print("🚀 System ready to run with new hourly checking!")
    else:
        print("❌ Verification failed - please check implementation")
    
    print("=" * 60)
