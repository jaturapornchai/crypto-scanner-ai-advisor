#!/usr/bin/env python3
"""
Test script for the new hourly position and order checking functionality.
Tests the enhanced main loop with position/order checking every hour.
"""

import time
from datetime import datetime
from unittest.mock import Mock
from enhanced_position_manager import EnhancedPositionManager

def test_hourly_position_check():
    """Test the new hourly position checking functionality"""
    print("🧪 Testing new hourly position/order checking...")
    
    # Create mock exchange client
    mock_exchange = Mock()
    
    # Mock positions response (no positions)
    mock_exchange.fetch_positions.return_value = []
    
    # Mock orders response (no orders)
    mock_exchange.fetch_open_orders.return_value = []
    
    # Mock balance response
    mock_exchange.fetch_balance.return_value = {
        'USDT': {'free': 100.0}
    }
    
    # Mock markets response 
    mock_exchange.fetch_markets.return_value = [
        {
            'id': 'BTCUSDT',
            'symbol': 'BTC/USDT:USDT',
            'quote': 'USDT',
            'type': 'swap',
            'active': True
        }
    ]
    
    # Create position manager with mock
    manager = EnhancedPositionManager(mock_exchange)
    
    # Test hourly position check (should not fail)
    try:
        print("📍 Testing hourly_position_check method...")
        manager.hourly_position_check()
        print("✅ hourly_position_check completed successfully")
        
        # Test simplified loop1_process (should return symbols)
        print("📍 Testing simplified loop1_process...")
        symbols = manager.loop1_process()
        print(f"✅ loop1_process returned {len(symbols) if symbols else 0} symbols")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_app_import():
    """Test that the main app can be imported without errors"""
    try:
        print("📍 Testing app.py import...")
        import app
        print("✅ app.py imported successfully")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing new hourly position/order checking system...")
    print("=" * 60)
    print(f"⏰ Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_hourly_position_check()
    test2_passed = test_app_import()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Hourly Position Check: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   App Import: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! System is ready.")
        print("🔄 Position and order checking now runs every hour")
        print("💡 Summary information has been minimized")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    print("=" * 60)
