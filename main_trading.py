#!/usr/bin/env python3
"""
Main Trading Application
รันระบบเทรดอัตโนมัติด้วย Chart Pattern Analysis
"""

import sys
import os
from exchange_client import ExchangeClient
from enhanced_position_manager import EnhancedPositionManager

def main():
    """Main function สำหรับรันระบบเทรด"""
    print("🚀 เริ่มต้นระบบเทรดอัตโนมัติ")
    print("📊 ใช้ Chart Pattern Analysis")
    print("💰 เปิด positions จนกว่าเงินจะหมด (ไม่จำกัด 20 positions)")
    print("⏰ LOOP1: ครั้งแรกรันทันที ครั้งต่อไปรอนาทีแรกของชั่วโมงต่อไป")
    print("="*60)
    
    try:
        # Initialize exchange client
        print("🔗 เชื่อมต่อ exchange...")
        exchange_client = ExchangeClient()
        
        # Initialize position manager
        print("🔧 เริ่มต้น Position Manager...")
        position_manager = EnhancedPositionManager(exchange_client)
        
        # แสดงข้อมูลเริ่มต้น
        print("\n📊 ข้อมูลเริ่มต้น:")
        balance = position_manager.check_available_balance()
        positions = position_manager.get_positions()
        orders = position_manager.get_all_orders()
        
        print(f"💰 Balance: {balance:.2f} USDT")
        print(f"📍 Positions: {len(positions)} รายการ")
        print(f"📋 Orders: {len(orders)} รายการ")
        
        max_possible_positions = int(balance // position_manager.position_size_usdt)
        print(f"📊 สามารถเปิด position ได้สูงสุด: {max_possible_positions} รายการ")
        print("🎯 จะเปิดไปเรื่อยๆ จนกว่าเงินจะหมด")
        
        print("\n✅ พร้อมเริ่มต้นการเทรด!")
        print("=" * 60)
        
        # เริ่ม main loop
        position_manager.main_loop()
        
    except KeyboardInterrupt:
        print("\n👋 หยุดการทำงานด้วย Ctrl+C")
        sys.exit(0)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        print("📞 กรุณาตรวจสอบการตั้งค่า API key และการเชื่อมต่อ")
        sys.exit(1)

if __name__ == "__main__":
    main()
