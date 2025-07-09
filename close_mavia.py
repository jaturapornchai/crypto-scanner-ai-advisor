#!/usr/bin/env python3
"""
ปิด MAVIA position และยกเลิก orders ที่เหลือ
"""

import ccxt
import os
from dotenv import load_dotenv

def close_mavia_position():
    load_dotenv()
    
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'sandbox': False,
        'options': {'defaultType': 'future'}
    })
    
    try:
        print("🔍 ตรวจสอบ MAVIA position...")
        
        # ตรวจสอบ position
        positions = exchange.fetch_positions()
        mavia_pos = [p for p in positions if p['symbol'] == 'MAVIA/USDT:USDT' and float(p['contracts']) != 0]
        
        if mavia_pos:
            pos = mavia_pos[0]
            print(f"📊 พบ MAVIA Position:")
            print(f"   Size: {pos['contracts']} contracts")
            print(f"   Side: {pos['side']}")
            print(f"   Entry Price: {pos['entryPrice']}")
            print(f"   Mark Price: {pos['markPrice']}")
            print(f"   PnL: {pos['unrealizedPnl']} USDT")
            print(f"   Percentage: {pos['percentage']}%")
            
            # ตรวจสอบ orders
            orders = exchange.fetch_open_orders('MAVIA/USDT')
            print(f"📋 Open Orders: {len(orders)} รายการ")
            for i, order in enumerate(orders):
                print(f"   Order {i+1}: {order['type']} {order['side']} {order['amount']} @ {order['price']}")
            
            # ปิด position
            print("\n🔄 กำลังปิด MAVIA position...")
            side = 'sell' if pos['side'] == 'long' else 'buy'
            size = abs(float(pos['contracts']))
            
            result = exchange.create_market_order(
                'MAVIA/USDT', 
                side, 
                size, 
                None, 
                None, 
                {'reduceOnly': True}
            )
            print(f"✅ ปิด position สำเร็จ: Order ID {result['id']}")
            
            # ยกเลิก orders ที่เหลือ
            if orders:
                print("🚫 กำลังยกเลิก orders ที่เหลือ...")
                for order in orders:
                    try:
                        exchange.cancel_order(order['id'], 'MAVIA/USDT')
                        print(f"   ✅ ยกเลิก Order {order['id']}")
                    except Exception as e:
                        print(f"   ⚠️ ไม่สามารถยกเลิก Order {order['id']}: {e}")
                print(f"✅ ยกเลิก orders เสร็จสิ้น")
            
            print("🎉 ปิด MAVIA position และยกเลิก orders เรียบร้อย!")
            
        else:
            print("❌ ไม่พบ MAVIA position ที่เปิดอยู่")
            
            # ตรวจสอบ orders อย่างเดียว
            orders = exchange.fetch_open_orders('MAVIA/USDT')
            if orders:
                print(f"📋 แต่พบ {len(orders)} orders ที่ยังเปิดอยู่")
                print("🚫 กำลังยกเลิก orders...")
                for order in orders:
                    try:
                        exchange.cancel_order(order['id'], 'MAVIA/USDT')
                        print(f"   ✅ ยกเลิก Order {order['id']}")
                    except Exception as e:
                        print(f"   ⚠️ ไม่สามารถยกเลิก Order {order['id']}: {e}")
                        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    close_mavia_position()
