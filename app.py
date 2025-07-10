"""
Crypto Trading System - Main Application
ระบบเทรดคริปโตที่ใช้ CCXT เชื่อมต่อ Binance Futures
ทำงานตามขั้นตอนใน step.md พร้อม AI Integration
"""

import time
from exchange_client import ExchangeClient
from enhanced_position_manager import EnhancedPositionManager

def main():
    """Main application entry point"""
    try:
        print("🚀 เริ่มต้นระบบ Crypto Trading System with AI")
        print("="*60)
        print("💰 ระบบใช้เงินจริงในการเทรด - ทำงานอัตโนมัติ")
        print("💰 System uses REAL MONEY - Automated Trading")
        print("="*60)
        
        # เชื่อมต่อ exchange
        print("📡 กำลังเชื่อมต่อ Binance Futures...")
        exchange_client = ExchangeClient()
        
        # ทดสอบการเชื่อมต่อ
        if not exchange_client.test_connection():
            print("❌ ไม่สามารถเชื่อมต่อ exchange ได้")
            return
        
        print("="*60)
        
        # สร้าง Enhanced Position & Order Manager
        print("🔧 เริ่มต้น Enhanced Position & Order Manager...")
        manager = EnhancedPositionManager(exchange_client)
        
        # Main trading loop
        while True:
            try:
                print(f"\n🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)
                
                # ทำการตรวจสอบ positions และ orders ทุกชั่วโมง
                manager.hourly_position_check()
                
                # รัน LOOP1 Process (ดึงเหรียญที่ไม่มี position)
                available_symbols = manager.loop1_process()
                
                # รัน LOOP2 Process (วิเคราะห์เหรียญใหม่)
                if available_symbols:
                    print(f"📊 วิเคราะห์เหรียญ: {len(available_symbols)} เหรียญ")
                    manager.loop2_process(available_symbols)
                
                print("✅ เสร็จสิ้นรอบนี้")
                print("="*60)
                
                # รอจนถึงชั่วโมงถัดไป
                manager.wait_for_next_hour()
                
            except KeyboardInterrupt:
                print("\n🛑 ระบบถูกยกเลิกโดยผู้ใช้")
                break
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในรอบนี้: {e}")
                print("⏰ รอ 5 นาทีก่อนเริ่มรอบใหม่...")
                time.sleep(300)  # รอ 5 นาที
                continue
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในระบบ: {e}")
        print("🔧 ลองตรวจสอบ:")
        print("   - ไฟล์ .env มี API Key และ Secret ถูกต้อง")
        print("   - API มี permission สำหรับ Futures")
        print("   - DeepSeek API Key ถูกต้อง")
        print("   - เครือข่ายอินเทอร์เน็ตเสถียร")

if __name__ == "__main__":
    main()
