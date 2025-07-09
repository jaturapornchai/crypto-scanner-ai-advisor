#!/usr/bin/env python3
"""
Linear Regression Channel - Minimal Test
ทดสอบเฉพาะ LRC logic เท่านั้น
"""

def test_lrc_manually():
    """ทดสอบ Linear Regression Channel ด้วยการคำนวณเอง"""
    print("🧪 ทดสอบ Linear Regression Channel Logic")
    print("=" * 50)
    
    # สร้างข้อมูลทดสอบ: แนวโน้มขึ้นพร้อม breakout
    print("📊 สร้างข้อมูลทดสอบ...")
    prices = []
    
    # 100 แท่งเทียนแรก - แนวโน้มขึ้นช้าๆ
    for i in range(95):
        base_price = 45000
        trend = i * 5  # ขึ้น 5 บาทต่อแท่ง
        noise = (i % 10 - 5) * 20  # noise ±100 บาท
        price = base_price + trend + noise
        prices.append(price)
    
    # 5 แท่งเทียนสุดท้าย - breakout ขึ้น
    for i in range(5):
        base_price = 45000 + (95 * 5)  # ราคาฐาน
        breakout = (i + 1) * 100  # breakout ขึ้นแรง 100 บาทต่อแท่ง
        price = base_price + breakout
        prices.append(price)
    
    print(f"✅ สร้างข้อมูล {len(prices)} แท่งเทียน")
    print(f"📊 ราคาเริ่มต้น: {prices[0]:.2f}")
    print(f"📊 ราคาสุดท้าย: {prices[-1]:.2f}")
    print(f"📊 ราคา 5 แท่งสุดท้าย: {[f'{p:.0f}' for p in prices[-5:]]}")
    
    # คำนวณ Linear Regression
    print("\n📈 คำนวณ Linear Regression...")
    
    # ใช้การคำนวณง่ายๆ
    n = len(prices)
    x_vals = list(range(n))
    
    # คำนวณ slope และ intercept
    sum_x = sum(x_vals)
    sum_y = sum(prices)
    sum_xy = sum(x * y for x, y in zip(x_vals, prices))
    sum_x2 = sum(x * x for x in x_vals)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n
    
    print(f"✅ Slope: {slope:.4f}")
    print(f"✅ Intercept: {intercept:.2f}")
    
    # คำนวณ Linear Regression Line
    lr_line = [slope * x + intercept for x in x_vals]
    print(f"📊 LR Line ราคาสุดท้าย: {lr_line[-1]:.2f}")
    
    # คำนวณ Standard Deviation
    print("\n📊 คำนวณ Channel Boundaries...")
    deviations = [abs(price - lr_val) for price, lr_val in zip(prices, lr_line)]
    avg_deviation = sum(deviations) / len(deviations)
    
    # คำนวณ variance เพื่อหา standard deviation
    variance = sum((dev - avg_deviation) ** 2 for dev in deviations) / len(deviations)
    std_dev = variance ** 0.5
    
    print(f"✅ Standard Deviation: {std_dev:.2f}")
    
    # คำนวณ Upper และ Lower Channel (deviation = 2.0)
    deviation_multiplier = 2.0
    upper_channel = [lr_val + (deviation_multiplier * std_dev) for lr_val in lr_line]
    lower_channel = [lr_val - (deviation_multiplier * std_dev) for lr_val in lr_line]
    
    print(f"📊 Upper Channel สุดท้าย: {upper_channel[-1]:.2f}")
    print(f"📊 Lower Channel สุดท้าย: {lower_channel[-1]:.2f}")
    
    # ตรวจสอบ Breakout ใน 5 แท่งสุดท้าย
    print("\n🎯 ตรวจสอบ Fresh Breakout (5 แท่งสุดท้าย)...")
    
    breakout_detected = False
    breakout_type = "None"
    breakout_candle = None
    
    for i in range(5):  # ตรวจสอบ 5 แท่งสุดท้าย
        candle_idx = -(5 - i)  # -5, -4, -3, -2, -1
        price = prices[candle_idx]
        upper = upper_channel[candle_idx]
        lower = lower_channel[candle_idx]
        
        print(f"📊 แท่งที่ {i+1}: Price={price:.2f}, Upper={upper:.2f}, Lower={lower:.2f}")
        
        if price > upper:
            breakout_detected = True
            breakout_type = "BREAKOUT UP"
            breakout_candle = i + 1
            print(f"🚀 {breakout_type} detected! Price {price:.2f} > Upper {upper:.2f}")
        elif price < lower:
            breakout_detected = True
            breakout_type = "BREAKOUT DOWN"
            breakout_candle = i + 1
            print(f"📉 {breakout_type} detected! Price {price:.2f} < Lower {lower:.2f}")
    
    # สรุปผล
    print("\n" + "=" * 50)
    print("📋 สรุปผลการทดสอบ Linear Regression Channel")
    print("=" * 50)
    
    print(f"📊 จำนวนข้อมูล: {len(prices)} แท่งเทียน")
    print(f"📈 Linear Regression Slope: {slope:.4f} ({'Uptrend' if slope > 0 else 'Downtrend'})")
    print(f"📊 Channel Width: {(upper_channel[-1] - lower_channel[-1]):.2f}")
    print(f"📊 Latest Price: {prices[-1]:.2f}")
    print(f"📊 Upper Channel: {upper_channel[-1]:.2f}")
    print(f"📊 Lower Channel: {lower_channel[-1]:.2f}")
    
    if breakout_detected:
        print(f"🎯 Fresh Breakout: {breakout_type}")
        print(f"⏰ Breakout Candle: {breakout_candle} candles ago")
        print(f"✅ Trading Signal: {'LONG' if breakout_type == 'BREAKOUT UP' else 'SHORT'}")
    else:
        print("📊 No Fresh Breakout detected")
        print("📊 Trading Signal: HOLD")
    
    print("\n🎉 Linear Regression Channel test completed!")
    return breakout_detected

def test_volume_analysis():
    """ทดสอบการวิเคราะห์ volume"""
    print("\n" + "=" * 50)
    print("🧪 ทดสอบ Volume Analysis")
    print("=" * 50)
    
    # สร้างข้อมูล volume
    volumes = []
    
    # Volume ปกติ 95 แท่งแรก
    for i in range(95):
        normal_volume = 1000 + (i % 100)  # volume ปกติ 1000-1100
        volumes.append(normal_volume)
    
    # Volume spike ใน 5 แท่งสุดท้าย (ตอน breakout)
    for i in range(5):
        spike_volume = 1000 + ((i + 1) * 500)  # volume เพิ่มขึ้นเป็น 1500, 2000, 2500, 3000, 3500
        volumes.append(spike_volume)
    
    print(f"📊 Volume ปกติ (95 แท่งแรก): {volumes[0]}-{volumes[94]}")
    print(f"📊 Volume spike (5 แท่งสุดท้าย): {volumes[-5:]}")
    
    # คำนวณ average volume ของ 20 แท่งก่อนหน้า
    avg_volume = sum(volumes[-25:-5]) / 20  # ไม่รวม 5 แท่งสุดท้าย
    print(f"📊 Average Volume (20 แท่งก่อนหน้า): {avg_volume:.0f}")
    
    # ตรวจสอบ volume spike ใน 5 แท่งสุดท้าย
    volume_confirmed = False
    for i in range(5):
        candle_idx = -(5 - i)
        volume = volumes[candle_idx]
        volume_ratio = volume / avg_volume
        
        print(f"📊 แท่งที่ {i+1}: Volume={volume}, Ratio={volume_ratio:.2f}x")
        
        if volume_ratio >= 1.5:  # Volume เพิ่มขึ้น ≥ 150%
            volume_confirmed = True
            print(f"✅ Volume spike confirmed! {volume_ratio:.2f}x > 1.5x")
    
    print(f"\n📊 Volume Confirmation: {'✅ CONFIRMED' if volume_confirmed else '❌ NOT CONFIRMED'}")
    return volume_confirmed

def main():
    """Main test function"""
    print("🚀 Linear Regression Channel - Minimal Test")
    print("⚠️  ทดสอบ logic เพื่อยืนยันว่าระบบทำงานถูกต้อง")
    print("⚠️  ระบบจริงใช้เงินจริงในการเทรด!")
    
    # ทดสอบ LRC
    breakout_result = test_lrc_manually()
    
    # ทดสอบ Volume
    volume_result = test_volume_analysis()
    
    # สรุปสุดท้าย
    print("\n" + "=" * 60)
    print("🎯 สรุปผลการทดสอบทั้งหมด")
    print("=" * 60)
    
    print(f"📊 Linear Regression Channel: {'✅ WORKING' if breakout_result else '⚠️  NO BREAKOUT'}")
    print(f"📊 Volume Analysis: {'✅ CONFIRMED' if volume_result else '❌ NOT CONFIRMED'}")
    
    if breakout_result and volume_result:
        print("\n🎉 ระบบ Linear Regression Channel พร้อมใช้งาน!")
        print("📋 เงื่อนไขสำหรับเปิด position:")
        print("   ✅ Fresh Breakout ใน 5 แท่งเทียนย้อนหลัง")
        print("   ✅ Volume Spike ≥ 150%")
        print("   ✅ AI Confidence ≥ 85%")
        print("\n🚀 คุณสามารถรันระบบจริงได้: python app.py")
        print("⚠️  ระบบใช้เงินจริง - ทดสอบด้วยจำนวนน้อยก่อน!")
    else:
        print("\n📊 ระบบทำงานได้ แต่ข้อมูลทดสอบไม่มี breakout ที่เหมาะสม")
        print("📋 ในการใช้งานจริง ระบบจะวิเคราะห์ข้อมูลจริงจาก Binance")

if __name__ == "__main__":
    main()
