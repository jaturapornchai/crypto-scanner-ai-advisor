#!/usr/bin/env python3
"""
Simple Linear Regression Channel Test
ทดสอบพื้นฐานของระบบ LRC
"""

def test_basic_imports():
    """ทดสอบการ import พื้นฐาน"""
    print("🧪 Testing basic imports...")
    
    try:
        import ccxt
        print(f"✅ CCXT: {ccxt.__version__}")
        
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv: OK")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_lrc_calculation():
    """ทดสอบการคำนวณ Linear Regression Channel"""
    print("\n🧪 Testing LRC calculation...")
    
    try:
        import numpy as np
        
        # สร้างข้อมูลทดสอบ
        # แนวโน้มขึ้น พร้อม breakout ในตอนท้าย
        prices = []
        for i in range(100):
            if i < 95:
                price = 45000 + (i * 10)  # แนวโน้มขึ้นช้าๆ
            else:
                price = 45000 + (95 * 10) + ((i - 95) * 100)  # breakout ขึ้นแรง
            prices.append(price)
        
        # คำนวณ Linear Regression
        x = np.arange(len(prices))
        slope, intercept = np.polyfit(x, prices, 1)
        
        # คำนวณ deviation
        lr_line = slope * x + intercept
        deviations = np.abs(np.array(prices) - lr_line)
        std_dev = np.std(deviations)
        
        # คำนวณ channel boundaries
        upper_channel = lr_line + (2.0 * std_dev)
        lower_channel = lr_line - (2.0 * std_dev)
        
        print(f"✅ Linear Regression calculation completed!")
        print(f"📊 Slope: {slope:.4f}")
        print(f"📊 Last Upper Channel: {upper_channel[-1]:.2f}")
        print(f"📊 Last Middle Line: {lr_line[-1]:.2f}")
        print(f"📊 Last Lower Channel: {lower_channel[-1]:.2f}")
        print(f"📊 Last Price: {prices[-1]:.2f}")
        
        # ตรวจสอบ breakout
        last_price = prices[-1]
        last_upper = upper_channel[-1]
        last_lower = lower_channel[-1]
        
        if last_price > last_upper:
            print(f"🚀 BREAKOUT UP detected! Price {last_price:.2f} > Upper {last_upper:.2f}")
        elif last_price < last_lower:
            print(f"📉 BREAKOUT DOWN detected! Price {last_price:.2f} < Lower {last_lower:.2f}")
        else:
            print(f"📊 Price within channel: {last_lower:.2f} < {last_price:.2f} < {last_upper:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ LRC calculation error: {e}")
        return False

def test_exchange_basic():
    """ทดสอบการเชื่อมต่อ exchange พื้นฐาน"""
    print("\n🧪 Testing exchange connection...")
    
    try:
        import ccxt
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_SECRET_KEY')
        
        if not api_key or not api_secret:
            print("❌ Missing API credentials in .env file")
            return False
        
        print(f"✅ API Key found: {api_key[:8]}...")
        print(f"✅ API Secret found: {api_secret[:8]}...")
        
        # สร้าง exchange instance
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'sandbox': False,  # ใช้ live trading
            'options': {
                'defaultType': 'future',
            },
        })
        
        print("✅ Exchange instance created!")
        
        # ทดสอบการเรียก API
        try:
            exchange.load_markets()
            print("✅ Markets loaded successfully!")
            
            # นับ USDT futures symbols
            futures_symbols = [s for s in exchange.symbols if 'USDT' in s and '/USDT:USDT' in s]
            print(f"📊 Found {len(futures_symbols)} USDT futures symbols")
            
            return True
            
        except Exception as api_e:
            print(f"❌ API call failed: {api_e}")
            return False
        
    except Exception as e:
        print(f"❌ Exchange test error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Linear Regression Channel - Basic System Test")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("LRC Calculation", test_lrc_calculation),
        ("Exchange Connection", test_exchange_basic),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print("="*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 Test Summary")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 Basic system is ready!")
        print("🚀 You can run: python app.py")
        print("\n⚠️  WARNING: This system uses REAL MONEY for trading!")
        print("⚠️  Make sure to test with small amounts first!")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running the main system.")

if __name__ == "__main__":
    main()
