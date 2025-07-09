#!/usr/bin/env python3
"""
ทดสอบฟังก์ชันตรวจสอบ positions ที่มีปัญหา
"""

print("✅ Pattern Detector imported successfully")

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_position_manager import EnhancedPositionManager
import ccxt
from dotenv import load_dotenv

def test_problematic_positions():
    try:
        load_dotenv()
        
        exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'sandbox': False,
            'options': {'defaultType': 'future'}
        })
        
        print("🚀 สร้าง Enhanced Position Manager...")
        manager = EnhancedPositionManager(exchange)
        
        print("🔍 ตรวจสอบ positions ที่มีปัญหา...")
        manager.check_and_fix_problematic_positions()
        
        print("✅ การตรวจสอบเสร็จสิ้น")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_problematic_positions()
