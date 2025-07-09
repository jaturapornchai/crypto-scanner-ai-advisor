#!/usr/bin/env python3
"""
สคริปต์เฉพาะกิจสำหรับปิด MAVIA position
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_position_manager import EnhancedPositionManager

def close_mavia_now():
    """ปิด MAVIA position ทันที"""
    try:
        print("🚀 เริ่มต้นระบบเพื่อปิด MAVIA position...")
        
        # สร้าง manager
        import ccxt
        from dotenv import load_dotenv
        load_dotenv()
        
        exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'sandbox': False,
            'options': {'defaultType': 'future'}
        })
        
        manager = EnhancedPositionManager(exchange)
        
        # ดึงข้อมูล positions
        positions = manager.get_positions()
        mavia_position = None
        
        for pos in positions:
            if pos['symbol'] == 'MAVIA/USDT:USDT' and float(pos['contracts']) != 0:
                mavia_position = pos
                break
        
        if mavia_position:
            print(f"📊 พบ MAVIA Position:")
            print(f"   Symbol: {mavia_position['symbol']}")
            print(f"   Size: {mavia_position['contracts']}")
            print(f"   Side: {mavia_position['side']}")
            print(f"   PnL: {mavia_position['unrealizedPnl']} USDT")
            
            # ตรวจสอบ orders
            orders = manager.get_all_orders()
            mavia_orders = [o for o in orders if o['symbol'] == 'MAVIA/USDT:USDT']
            print(f"📋 MAVIA Orders: {len(mavia_orders)} รายการ")
            
            for order in mavia_orders:
                print(f"   - {order['type']} {order['side']} {order['amount']} @ {order['price']}")
            
            # ปิด position
            print("\n🔄 กำลังปิด MAVIA position...")
            success = manager.close_position(
                'MAVIA/USDT:USDT', 
                float(mavia_position['contracts']), 
                mavia_position['side']
            )
            
            if success:
                # ยกเลิก orders ที่เหลือ
                if mavia_orders:
                    print("🚫 กำลังยกเลิก MAVIA orders ที่เหลือ...")
                    for order in mavia_orders:
                        try:
                            manager.exchange.cancel_order(order['id'], 'MAVIA/USDT:USDT')
                            print(f"   ✅ ยกเลิก order {order['id']}")
                        except Exception as e:
                            print(f"   ⚠️ ไม่สามารถยกเลิก order {order['id']}: {e}")
                
                print("🎉 ปิด MAVIA position เรียบร้อยแล้ว!")
            else:
                print("❌ ไม่สามารถปิด MAVIA position ได้")
                
        else:
            print("❌ ไม่พบ MAVIA position ที่เปิดอยู่")
            
            # ตรวจสอบ orders อย่างเดียว
            orders = manager.get_all_orders()
            mavia_orders = [o for o in orders if o['symbol'] == 'MAVIA/USDT:USDT']
            
            if mavia_orders:
                print(f"📋 แต่พบ MAVIA orders {len(mavia_orders)} รายการ")
                print("🚫 กำลังยกเลิก...")
                for order in mavia_orders:
                    try:
                        manager.exchange.cancel_order(order['id'], 'MAVIA/USDT:USDT')
                        print(f"   ✅ ยกเลิก order {order['id']}")
                    except Exception as e:
                        print(f"   ⚠️ ไม่สามารถยกเลิก order {order['id']}: {e}")
                        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    close_mavia_now()
