"""
Enhanced Position & Order Manager with Line Breakout + EMA7 Integration
ระบบจัดการ positions และ orders ที่ใช้ Line Breakout + EMA7 detection เท่านั้น
"""

import time
import datetime
import random
from ai_analyzer import AIAnalyzer
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from pattern_detector import PatternDetector
    PATTERN_DETECTOR_AVAILABLE = True
    print("✅ Pattern Detector imported successfully")
except ImportError as e:
    print(f"⚠️ PatternDetector import error: {e}")
    print("🔄 Using fallback mode - will send all coins to AI")
    PATTERN_DETECTOR_AVAILABLE = False
except Exception as e:
    print(f"⚠️ PatternDetector error: {e}")
    print("🔄 Using fallback mode - will send all coins to AI")
    PATTERN_DETECTOR_AVAILABLE = False

class EnhancedPositionManager:
    def __init__(self, exchange_client):
        """Initialize with exchange client"""
        self.exchange_client = exchange_client
        self.exchange = exchange_client.get_exchange()
        
        # Initialize AI Analyzer without Historical Data Manager
        self.ai_analyzer = AIAnalyzer(None)  # ไม่ส่ง exchange เพื่อไม่ให้สร้าง data manager
        
        # Initialize Pattern Detector for Line Breakout + EMA7 filtering
        if PATTERN_DETECTOR_AVAILABLE:
            self.pattern_detector = PatternDetector()
        else:
            self.pattern_detector = None
        
        # Trading parameters
        self.position_size_usdt = 20  # 20 USDT per position (เพิ่มจาก 10)
        self.leverage = 10  # 10x leverage
        self.confidence_threshold = 75  # 75% confidence threshold สำหรับ Line Breakout + EMA7
        self.last_signal_type = None  # Store last signal type for AI
        self.first_loop_done = False  # ติดตาม LOOP1 ครั้งแรก
        
        print("🔧 Enhanced Position & Order Manager พร้อมใช้งาน")
        print("📊 ใช้ Line Breakout + EMA7 Detection เท่านั้น")
    
    # LOOP1 Methods - Direct API calls (no cache)
    def get_positions(self):
        """ดึงข้อมูล positions ที่เปิดอยู่ (Direct API - no cache)"""
        try:
            positions = self.exchange.fetch_positions()
            open_positions = [pos for pos in positions if pos['contracts'] != 0]
            return open_positions
        except Exception as e:
            print(f"❌ ไม่สามารถดึงข้อมูล positions: {e}")
            return []
    
    def get_orders_by_symbol(self, symbol):
        """ดึงข้อมูล orders ของ symbol ที่กำหนด (Direct API - no cache)"""
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            print(f"❌ ไม่สามารถดึงข้อมูล orders สำหรับ {symbol}: {e}")
            return []
    
    def get_all_orders(self):
        """ดึงข้อมูล orders ทั้งหมด (Direct API - no cache)"""
        try:
            orders = self.exchange.fetch_open_orders()
            return orders
        except Exception as e:
            print(f"❌ ไม่สามารถดึงข้อมูล orders ทั้งหมด: {e}")
            return []
    
    def close_position(self, symbol, contracts, side):
        """ปิด position ด้วย market order"""
        try:
            print(f"🔄 กำลังปิด position {symbol} ({side}) ขนาด {abs(contracts)}")
            
            close_side = 'sell' if side == 'long' else 'buy'
            
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=close_side,
                amount=abs(contracts),
                params={'reduceOnly': True}
            )
            
            print(f"✅ ปิด position {symbol} สำเร็จ - Order ID: {order['id']}")
            return True
            
        except Exception as e:
            print(f"❌ ไม่สามารถปิด position {symbol}: {e}")
            return False
    
    def cancel_orders_by_symbol(self, symbol):
        """ยกเลิก orders ทั้งหมดของ symbol ที่กำหนด"""
        try:
            print(f"🔄 กำลังยกเลิก orders ทั้งหมดของ {symbol}")
            
            orders = self.get_orders_by_symbol(symbol)
            if not orders:
                print(f"✅ ไม่มี orders ที่ต้องยกเลิกสำหรับ {symbol}")
                return True
            
            success_count = 0
            for order in orders:
                try:
                    self.exchange.cancel_order(order['id'], symbol)
                    print(f"✅ ยกเลิก order {order['id']} สำเร็จ")
                    success_count += 1
                except Exception as e:
                    print(f"❌ ไม่สามารถยกเลิก order {order['id']}: {e}")
            
            print(f"📊 ยกเลิก {success_count}/{len(orders)} orders สำหรับ {symbol}")
            return success_count == len(orders)
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการยกเลิก orders {symbol}: {e}")
            return False
    
    def cancel_order(self, order_id, symbol):
        """ยกเลิก order เดี่ยว"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            print(f"✅ ยกเลิก order {order_id} ({symbol}) สำเร็จ")
            return True
        except Exception as e:
            print(f"❌ ไม่สามารถยกเลิก order {order_id}: {e}")
            return False
    
    # New LOOP1 methods
    def get_available_symbols(self):
        """ดึงรายการเหรียญที่สามารถเทรดได้"""
        try:
            markets = self.exchange.markets
            positions = self.get_positions()
            
            # สร้างรายการ symbols ที่มี positions
            position_symbols = {pos['symbol'] for pos in positions}
            
            # กรองเฉพาะเหรียญที่มี USDT เป็น quote asset และไม่มี position
            available_symbols = []
            for symbol, market in markets.items():
                if (market['quote'] == 'USDT' and 
                    market['type'] == 'swap' and 
                    market['active'] and 
                    symbol not in position_symbols):
                    available_symbols.append(symbol)
            
            print(f"🔍 พบเหรียญ candidate: {len(available_symbols)} เหรียญ")
            
            # สลับตำแหน่ง (สับไพ่) เพื่อให้กระจาย
            random.shuffle(available_symbols)
            
            print(f"🎲 สับไพ่เหรียญทั้งหมด: {len(available_symbols)} เหรียญ")
            
            return available_symbols
            
        except Exception as e:
            print(f"❌ ไม่สามารถดึงรายการเหรียญ: {e}")
            return []
    
    def set_leverage(self, symbol, leverage):
        """ตั้งค่า leverage สำหรับ symbol"""
        try:
            self.exchange.set_leverage(leverage, symbol)
            print(f"✅ ตั้ง leverage {leverage}x สำหรับ {symbol}")
            return True
        except Exception as e:
            print(f"❌ ไม่สามารถตั้ง leverage สำหรับ {symbol}: {e}")
            return False
    
    def set_margin_mode(self, symbol, margin_mode='isolated'):
        """ตั้งค่า margin mode สำหรับ symbol"""
        try:
            self.exchange.set_margin_mode(margin_mode, symbol)
            print(f"✅ ตั้ง margin mode {margin_mode} สำหรับ {symbol}")
            return True
        except Exception as e:
            print(f"❌ ไม่สามารถตั้ง margin mode สำหรับ {symbol}: {e}")
            return False
    
    # LOOP2 Methods
    def get_ohlcv_data(self, symbol, timeframe='1h', limit=200):
        """ดึงข้อมูล OHLCV ย้อนหลัง"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            print(f"❌ ไม่สามารถดึงข้อมูล OHLCV สำหรับ {symbol}: {e}")
            return None
    
    def check_available_balance(self):
        """ตรวจสอบเงินที่พร้อมใช้ (Direct API - no cache)"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            return usdt_balance
        except Exception as e:
            print(f"❌ ไม่สามารถตรวจสอบ balance: {e}")
            return 0
    
    def calculate_position_quantity(self, symbol, side, price):
        """คำนวณ quantity สำหรับ position"""
        try:
            # คำนวณ quantity จาก position size
            position_value = self.position_size_usdt * self.leverage
            quantity = position_value / price
            
            # ปรับ quantity ให้ตรงกับ precision ของ symbol
            market = self.exchange.markets[symbol]
            precision = market['precision']['amount']
            
            if precision:
                quantity = round(quantity, precision)
            
            return quantity
            
        except Exception as e:
            print(f"❌ ไม่สามารถคำนวณ quantity สำหรับ {symbol}: {e}")
            return 0
    
    def open_position_with_sl_tp(self, symbol, side, quantity, price, stop_loss, take_profit):
        """เปิด position พร้อม stop loss และ take profit
        
        Returns:
            tuple: (success: bool, error_type: str)
            error_type: 'insufficient_funds', 'validation_error', 'network_error', 'other_error'
        """
        try:
            # ตรวจสอบว่า SL/TP ไม่เป็น 0 หรือ None
            if not stop_loss or stop_loss <= 0:
                print(f"❌ Stop Loss ไม่ถูกต้อง: {stop_loss} - ยกเลิกการเปิด position")
                return False, 'validation_error'
                
            if not take_profit or take_profit <= 0:
                print(f"❌ Take Profit ไม่ถูกต้อง: {take_profit} - ยกเลิกการเปิด position") 
                return False, 'validation_error'
            
            # ตรวจสอบความสมเหตุสมผลของ SL/TP กับราคาปัจจุบัน
            if side == 'buy':  # LONG position
                if stop_loss >= price:
                    print(f"❌ Stop Loss ({stop_loss}) ต้องต่ำกว่าราคาปัจจุบัน ({price}) สำหรับ LONG")
                    return False, 'validation_error'
                if take_profit <= price:
                    print(f"❌ Take Profit ({take_profit}) ต้องสูงกว่าราคาปัจจุบัน ({price}) สำหรับ LONG")
                    return False, 'validation_error'
            else:  # SHORT position
                if stop_loss <= price:
                    print(f"❌ Stop Loss ({stop_loss}) ต้องสูงกว่าราคาปัจจุบัน ({price}) สำหรับ SHORT")
                    return False, 'validation_error'
                if take_profit >= price:
                    print(f"❌ Take Profit ({take_profit}) ต้องต่ำกว่าราคาปัจจุบัน ({price}) สำหรับ SHORT")
                    return False, 'validation_error'
            
            print(f"✅ SL/TP ผ่านการตรวจสอบ: SL={stop_loss}, TP={take_profit}")
            print(f"🔄 เปิด position {symbol} {side.upper()} quantity: {quantity}")
            
            # ตั้งค่า leverage และ margin mode ก่อนเปิด position
            print(f"🔧 ตั้งค่า leverage 10x และ margin isolated สำหรับ {symbol}")
            try:
                self.set_leverage(symbol, self.leverage)
                self.set_margin_mode(symbol, 'isolated')
            except Exception as e:
                print(f"⚠️ ไม่สามารถตั้งค่า leverage/margin: {e} (ดำเนินการต่อ)")
            
            # เปิด position หลัก
            main_order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=quantity
            )
            
            print(f"✅ เปิด position {symbol} สำเร็จ - Order ID: {main_order['id']}")
            
            # Invalidate cache หลังจากเปิด position
            self.cache_timestamp = 0
            
            # ตั้ง stop loss
            sl_side = 'sell' if side == 'buy' else 'buy'
            try:
                sl_order = self.exchange.create_order(
                    symbol=symbol,
                    type='stop_market',
                    side=sl_side,
                    amount=quantity,
                    params={
                        'stopPrice': stop_loss,
                        'reduceOnly': True
                    }
                )
                print(f"✅ ตั้ง stop loss {stop_loss} สำเร็จ - Order ID: {sl_order['id']}")
            except Exception as e:
                print(f"❌ ไม่สามารถตั้ง stop loss: {e}")
            
            # ตั้ง take profit
            tp_side = 'sell' if side == 'buy' else 'buy'
            try:
                tp_order = self.exchange.create_order(
                    symbol=symbol,
                    type='take_profit_market',
                    side=tp_side,
                    amount=quantity,
                    params={
                        'stopPrice': take_profit,
                        'reduceOnly': True
                    }
                )
                print(f"✅ ตั้ง take profit {take_profit} สำเร็จ - Order ID: {tp_order['id']}")
            except Exception as e:
                print(f"❌ ไม่สามารถตั้ง take profit: {e}")
            
            return True, 'success'
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"❌ ไม่สามารถเปิด position {symbol}: {e}")
            
            # ตรวจสอบประเภทของ error
            if any(keyword in error_msg for keyword in ['insufficient', 'balance', 'funds', 'margin', 'money']):
                return False, 'insufficient_funds'
            elif any(keyword in error_msg for keyword in ['network', 'timeout', 'connection']):
                return False, 'network_error'
            else:
                return False, 'other_error'
    
    def check_trading_signals(self, symbol):
        """ตรวจสอบสัญญาณการเทรด - เทรดตามเทรนด์ (ไม่เอาจุดกลับตัว)"""
        try:
            # ดึงข้อมูล OHLCV สำหรับการคำนวณ indicators
            ohlcv = self.get_ohlcv_data(symbol, limit=144)
            if not ohlcv or len(ohlcv) < 50:
                print(f"        ❌ ข้อมูล OHLCV ไม่เพียงพอ ({len(ohlcv) if ohlcv else 0} candles)")
                return False
            
            # แปลงข้อมูลเป็น lists
            closes = [candle[4] for candle in ohlcv]
            highs = [candle[2] for candle in ohlcv]
            lows = [candle[3] for candle in ohlcv]
            volumes = [candle[5] for candle in ohlcv]
            
            # คำนวณ indicators สำหรับเทรดตามเทรนด์
            ema_20 = self.calculate_ema(closes, 20)
            ema_50 = self.calculate_ema(closes, 50)
            ema_100 = self.calculate_ema(closes, 100)
            rsi = self.calculate_rsi(closes)
            macd_line, signal_line = self.calculate_macd_simple(closes)
            
            current_price = closes[-1]
            current_volume = volumes[-1]
            avg_volume = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else current_volume
            
            # เทรดตามเทรนด์ - Trend Following Strategy
            # 1. ระบุเทรนด์ที่ชัดเจน
            strong_uptrend = (ema_20 > ema_50 > ema_100 and 
                             current_price > ema_20 and 
                             current_price > closes[-2])  # ราคาเพิ่มขึ้น
            
            strong_downtrend = (ema_20 < ema_50 < ema_100 and 
                               current_price < ema_20 and 
                               current_price < closes[-2])  # ราคาลดลง
            
            # 2. ยืนยันเทรนด์ด้วย RSI และ MACD
            bullish_momentum = (rsi > 50 and rsi < 80 and  # RSI ในเขตบวกแต่ยังไม่ overbought
                               macd_line > signal_line and macd_line > 0)  # MACD บวกและเหนือ signal
            
            bearish_momentum = (rsi < 50 and rsi > 20 and  # RSI ในเขตลบแต่ยังไม่ oversold
                               macd_line < signal_line and macd_line < 0)  # MACD ลบและใต้ signal
            
            # 3. ยืนยันด้วย volume
            volume_confirmation = current_volume > avg_volume * 1.1  # volume เพิ่มขึ้น
            
            # สัญญาณเทรดตามเทรนด์
            # Long Signal: เทรนด์ขึ้นแรง + momentum บวก + volume สนับสนุน
            trend_long_signal = (strong_uptrend and 
                                bullish_momentum and 
                                volume_confirmation)
            
            # Short Signal: เทรนด์ลงแรง + momentum ลบ + volume สนับสนุน
            trend_short_signal = (strong_downtrend and 
                                 bearish_momentum and 
                                 volume_confirmation)
            
            # แสดงรายละเอียด
            print(f"        📊 Price: {current_price:.6f}")
            print(f"        📊 EMA20: {ema_20:.6f}, EMA50: {ema_50:.6f}, EMA100: {ema_100:.6f}")
            print(f"        📊 RSI: {rsi:.1f}, MACD: {macd_line:.6f}, Volume: {current_volume/avg_volume:.1f}x")
            
            # ระบุเทรนด์
            if strong_uptrend:
                trend_type = "STRONG_UPTREND"
            elif strong_downtrend:
                trend_type = "STRONG_DOWNTREND"
            else:
                trend_type = "SIDEWAYS"
            
            print(f"        📊 Trend: {trend_type}")
            
            has_trend_signal = trend_long_signal or trend_short_signal
            signal_type = "LONG" if trend_long_signal else "SHORT" if trend_short_signal else "NONE"
            
            if has_trend_signal:
                print(f"        ✅ พบสัญญาณเทรดตามเทรนด์: {signal_type}")
                self.last_signal_type = signal_type
            else:
                print(f"        ⚠️  ไม่พบสัญญาณเทรดตามเทรนด์")
            
            return has_trend_signal
            
        except Exception as e:
            print(f"        ❌ ไม่สามารถตรวจสอบสัญญาณเทรดตามเทรนด์สำหรับ {symbol}: {e}")
            return False
        try:
            # ดึงข้อมูล OHLCV สำหรับการคำนวณ RSI divergence
            ohlcv = self.get_ohlcv_data(symbol, limit=144)  # ใช้ 144 candles สำหรับ divergence
            if not ohlcv or len(ohlcv) < 50:
                print(f"        ❌ ข้อมูล OHLCV ไม่เพียงพอ ({len(ohlcv) if ohlcv else 0} candles)")
                return False
            
            # แปลงข้อมูลเป็น lists
            closes = [candle[4] for candle in ohlcv]  # close prices
            highs = [candle[2] for candle in ohlcv]   # high prices
            lows = [candle[3] for candle in ohlcv]    # low prices
            
            # คำนวณ RSI สำหรับทุก candle ที่เป็นไปได้
            rsi_values = []
            for i in range(14, len(closes)):
                rsi = self.calculate_rsi(closes[:i+1])
                rsi_values.append(rsi)
            
            # หา divergence (ต้องมีอย่างน้อย 20 RSI values)
            if len(rsi_values) < 20:
                print(f"        ❌ RSI values ไม่เพียงพอสำหรับ divergence")
                return False
            
            # ตรวจสอบ Bullish Divergence (ราคาทำ lower low แต่ RSI ทำ higher low)
            bullish_divergence = self.check_bullish_divergence(lows[-50:], rsi_values[-36:])
            
            # ตรวจสอบ Bearish Divergence (ราคาทำ higher high แต่ RSI ทำ lower high)
            bearish_divergence = self.check_bearish_divergence(highs[-50:], rsi_values[-36:])
            
            current_price = closes[-1]
            current_rsi = rsi_values[-1]
            
            # แสดงรายละเอียด
            print(f"        📊 ราคาปัจจุบัน: {current_price:.6f}, RSI: {current_rsi:.1f}")
            
            divergence_found = False
            divergence_type = None
            
            if bullish_divergence:
                print(f"        🟢 พบ Bullish Divergence (ราคา↓ RSI↑) - สัญญาณซื้อ")
                divergence_found = True
                divergence_type = "BULLISH"
            elif bearish_divergence:
                print(f"        🔴 พบ Bearish Divergence (ราคา↑ RSI↓) - สัญญาณขาย")
                divergence_found = True
                divergence_type = "BEARISH"
            else:
                print(f"        ⚠️  ไม่พบ RSI Divergence")
            
            # เก็บ divergence type ไว้ใช้ใน AI analysis
            if divergence_found:
                self.last_divergence_type = divergence_type
            
            return divergence_found
            
        except Exception as e:
            print(f"        ❌ ไม่สามารถตรวจสอบ RSI Divergence สำหรับ {symbol}: {e}")
            return False

    def calculate_rsi(self, prices, period=14):
        """คำนวณ RSI"""
        if len(prices) < period + 1:
            return 50  # return neutral value
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_ema(self, prices, period):
        """คำนวณ EMA"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        # Simple EMA calculation
        alpha = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema
    
    def calculate_macd_simple(self, prices):
        """คำนวณ MACD แบบง่าย"""
        if len(prices) < 26:
            return 0, 0
        
        # EMA 12 และ 26
        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)
        
        # MACD line
        macd_line = ema_12 - ema_26
        
        # Signal line (EMA 9 ของ MACD)
        # สำหรับความง่าย ใช้ค่าคงที่
        signal_line = macd_line * 0.9
        
        return macd_line, signal_line

    def show_positions_summary(self):
        """แสดงสรุป positions และ orders ปัจจุบัน"""
        try:
            print("\n📊 สรุป Positions และ Orders ปัจจุบัน:")
            print("="*60)
            
            # ดึงข้อมูล positions
            positions = self.get_positions()
            total_pnl = 0
            
            if positions:
                print(f"📍 Positions: {len(positions)} รายการ")
                for pos in positions:
                    symbol = pos['symbol']
                    side = pos['side'].upper()
                    contracts = abs(pos['contracts'])
                    pnl = pos.get('unrealizedPnl', 0) or 0
                    total_pnl += pnl
                    
                    print(f"   {symbol} - {side} {contracts:,.4f} (PnL: {pnl:+.2f})")
                
                print(f"💰 Total PnL: {total_pnl:+.2f} USDT")
            else:
                print("📍 Positions: 0 รายการ")
            
            # ดึงข้อมูล orders
            all_orders = self.get_all_orders()
            if all_orders:
                print(f"📋 Orders: {len(all_orders)} รายการ")
                
                # จัดกลุ่ม orders ตาม symbol
                orders_by_symbol = {}
                for order in all_orders:
                    symbol = order['symbol']
                    if symbol not in orders_by_symbol:
                        orders_by_symbol[symbol] = 0
                    orders_by_symbol[symbol] += 1
                
                for symbol, count in orders_by_symbol.items():
                    print(f"   {symbol}: {count} orders")
            else:
                print("📋 Orders: 0 รายการ")
            
            print("="*60)
            
        except Exception as e:
            print(f"❌ ไม่สามารถแสดงสรุป positions: {e}")

    # LOOP1: ขั้นตอนการทำงานหลักตาม step.md
    def loop1_process(self):
        """LOOP1: ขั้นตอนการทำงานหลักตาม step.md"""
        print("🔄 เริ่ม LOOP1 Process...")
        print("="*60)
        
        # แสดงสรุป positions และ orders ก่อนเริ่มการทำงาน
        self.show_positions_summary()
        
        # ตรวจสอบและแก้ไข positions ที่มีปัญหา
        self.check_and_fix_problematic_positions()
        
        # ขั้นตอนที่ 1: ตรวจสอบ positions และ orders
        print("📍 ขั้นตอนที่ 1: ตรวจสอบ positions และจำนวน orders")
        print("🔍 กำลังดึงข้อมูล positions ที่เปิดอยู่...")
        
        positions = self.get_positions()
        if not positions:
            print("✅ ไม่มี positions ที่เปิดอยู่")
        else:
            print(f"📊 พบ {len(positions)} positions ที่เปิดอยู่:")
            
            for i, pos in enumerate(positions, 1):
                symbol = pos['symbol']
                contracts = pos['contracts']
                side = pos['side']
                unrealized_pnl = pos['unrealizedPnl'] or 0
                
                print(f"\n  [{i}] 🔍 ตรวจสอบ {symbol}")
                print(f"      📊 Position: {side.upper()} {abs(contracts)}")
                print(f"      💰 PnL: {unrealized_pnl:+.2f} USDT")
                
                print(f"      🔍 ค้นหา orders สำหรับ {symbol}...")
                orders = self.get_orders_by_symbol(symbol)
                order_count = len(orders)
                
                print(f"      📋 พบ {order_count} orders สำหรับ {symbol}")
                
                if order_count != 2:
                    print(f"      ⚠️  {symbol} มี {order_count} orders (ต้องการ 2 orders)")
                    print(f"      🔧 กำลังดำเนินการ: ปิด position และยกเลิก orders")
                    
                    # ยกเลิก orders ก่อน
                    cancel_result = self.cancel_orders_by_symbol(symbol)
                    if cancel_result:
                        print(f"      ✅ ยกเลิก orders {symbol} สำเร็จ")
                    else:
                        print(f"      ❌ ยกเลิก orders {symbol} ไม่สำเร็จ")
                    
                    # ปิด position
                    close_result = self.close_position(symbol, contracts, side)
                    if close_result:
                        print(f"      ✅ ปิด position {symbol} สำเร็จ")
                        # Invalidate cache หลังจากมีการเปลี่ยนแปลง
                        self.cache_timestamp = 0
                    else:
                        print(f"      ❌ ปิด position {symbol} ไม่สำเร็จ")
                else:
                    print(f"      ✅ {symbol} มี orders ครบ 2 orders แล้ว")
                    # แสดงรายละเอียด orders
                    for j, order in enumerate(orders, 1):
                        order_type = order.get('type', 'unknown')
                        order_side = order.get('side', 'unknown')
                        order_amount = order.get('amount', 0)
                        print(f"          [{j}] {order_type} {order_side} {order_amount}")
        
        print("\n" + "="*60)
        
        # ขั้นตอนที่ 2: ค้นหา orders ที่ไม่มี positions
        print("📋 ขั้นตอนที่ 2: ค้นหา orders ที่ไม่มี positions")
        print("🔍 กำลังดึงข้อมูล orders ทั้งหมด...")
        
        all_orders = self.get_all_orders()
        if not all_orders:
            print("✅ ไม่มี orders ที่เปิดอยู่")
        else:
            print(f"📊 พบ {len(all_orders)} orders ทั้งหมด")
            
            position_symbols = {pos['symbol'] for pos in positions}
            orphan_orders = [order for order in all_orders if order['symbol'] not in position_symbols]
            
            if not orphan_orders:
                print("✅ ไม่มี orders ที่ไม่มี positions")
            else:
                print(f"⚠️  พบ {len(orphan_orders)} orders ที่ไม่มี positions:")
                
                for i, order in enumerate(orphan_orders, 1):
                    symbol = order['symbol']
                    order_id = order['id']
                    side = order['side']
                    amount = order['amount']
                    order_type = order.get('type', 'unknown')
                    
                    print(f"  [{i}] 🔄 ยกเลิก orphan order: {symbol} {order_type} {side.upper()} {amount}")
                    cancel_result = self.cancel_order(order_id, symbol)
                    if cancel_result:
                        print(f"      ✅ ยกเลิก order {order_id} สำเร็จ")
                        # Invalidate cache หลังจากมีการเปลี่ยนแปลง
                        self.cache_timestamp = 0
                    else:
                        print(f"      ❌ ยกเลิก order {order_id} ไม่สำเร็จ")
        
        print("\n" + "="*60)
        
        # ขั้นตอนที่ 3: ดึงรายการเหรียญที่พร้อมเทรด
        print("📋 ขั้นตอนที่ 3: ดึงรายการเหรียญที่พร้อมเทรด")
        print("🔍 กำลังค้นหาเหรียญ USDT ที่พร้อมเทรด...")
        
        available_symbols = self.get_available_symbols()
        print(f"📊 พบ {len(available_symbols)} เหรียญที่พร้อมเทรด")
        
        # แสดงเหรียญที่สับไพ่แล้ว 10 อันดับแรก
        if available_symbols:
            preview_symbols = available_symbols[:10]
            print(f"🎲 เหรียญที่สับไพ่แล้ว (10 อันดับแรก): {', '.join(preview_symbols)}")
        
        # ขั้นตอนที่ 4: ข้ามการตั้งค่า leverage และ margin mode (ตั้งค่าตอนเทรดจริง)
        print("📋 ขั้นตอนที่ 4: ข้ามการตั้งค่า leverage/margin (ตั้งค่าตอนเทรดจริง)")
        print("⚡ ประหยัดเวลา - ตั้งค่าจะทำตอนเปิด position จริงเท่านั้น")
        
        print("\n✅ เสร็จสิ้น LOOP1 Process")
        print("="*60)
        
        return available_symbols
    
    def loop2_process(self, symbols):
        """LOOP2: วิเคราะห์และเทรดเหรียญด้วย Chart Pattern Analysis - แทน RSI"""
        print("🔄 เริ่ม LOOP2 Process...")
        print("📊 ใช้ Chart Pattern Analysis แทน RSI")
        print("🎯 เทรด LONG/SHORT ตามคำแนะนำ AI Chart Pattern")
        print("="*60)
        
        if not symbols:
            print("✅ ไม่มีเหรียญที่ต้องวิเคราะห์")
            return
        
        print(f"📊 จำนวนเหรียญที่ต้องสแกน: {len(symbols)} เหรียญ")
        print(f"📈 กรองด้วย Chart Pattern Breakout/Confirmed")
        print(f"🤖 เทรด LONG/SHORT ตามคำแนะนำ AI Chart Pattern")
        print(f"💰 เปิด position จนกว่าเงินจะหมด (Position Size: {self.position_size_usdt} USDT/position)")
        
        # ตรวจสอบจำนวน positions และ balance ตาม step.md
        balance = self.check_available_balance()
        current_positions = self.get_positions()
        position_count = len(current_positions)
        print(f"💰 Balance เริ่มต้น: {balance:.2f} USDT")
        print(f"📊 จำนวน Positions ปัจจุบัน: {position_count}")
        
        # ตรวจสอบ balance แทน position limit - เปิดไปเรื่อยๆ จนกว่าเงินจะหมด
        if balance < self.position_size_usdt:
            print(f"⚠️ Balance ({balance:.2f} USDT) ไม่เพียงพอสำหรับ position ใหม่ (ต้องการ {self.position_size_usdt} USDT)")
            return
        
        # เปิด position จนกว่าเงินจะหมด (ไม่จำกัดจำนวน)
        max_positions = int(balance // self.position_size_usdt)
        print(f"📊 สามารถเปิด position ได้สูงสุด: {max_positions} รายการ")
        
        analyzed_count = 0
        ai_analyzed = 0
        skipped_count = 0
        position_opened = 0
        
        print("\n" + "="*60)
        print("🔍 เริ่มสแกนเหรียญด้วย Line Breakout + EMA7 Detection:")
        print("="*60)
        
        for i, symbol in enumerate(symbols, 1):
            try:
                # ตรวจสอบ balance แทน position limit
                current_balance = self.check_available_balance()
                if current_balance < self.position_size_usdt:
                    print(f"⚠️ Balance หมด ({current_balance:.2f} USDT) - หยุดการเปิด position ใหม่")
                    break
                
                print(f"\n[{i:3d}/{len(symbols):3d}] 🔍 กำลังวิเคราะห์ {symbol}...")
                
                # ตรวจสอบ balance ก่อนเปิด position
                current_balance = self.check_available_balance()
                if current_balance < self.position_size_usdt:
                    print(f"    ❌ Balance ไม่เพียงพอ ({current_balance:.2f} < {self.position_size_usdt} USDT)")
                    print(f"    🔄 หยุดการเปิด position ใหม่")
                    break
                
                # ขั้นตอนที่ 1: ดึงข้อมูล OHLCV 1H สำหรับ Line Breakout + EMA7 Analysis (จาก API ใหม่ทุกครั้ง)
                print(f"    📊 ดึงข้อมูล OHLCV 1H ใหม่จาก Binance API...")
                ohlcv_1h = self.get_ohlcv_data(symbol, timeframe='1h', limit=20)  # ดึง 20 candles สำหรับ Line Breakout + EMA7
                
                if not ohlcv_1h or len(ohlcv_1h) < 20:
                    print(f"    ❌ ไม่สามารถดึงข้อมูล OHLCV 1H สำหรับ {symbol}")
                    skipped_count += 1
                    continue
                
                print(f"    ✅ ได้ข้อมูล OHLCV 1H: {len(ohlcv_1h)} records (ใหม่จาก API)")
                
                # ขั้นตอนที่ 2: กรองด้วย Python Line Breakout + EMA7 detector ก่อนส่งไป AI
                print(f"    🔍 ตรวจสอบ Line Breakout + EMA7 ด้วย Python detector...")
                
                # ใช้ pattern_detector เพื่อตรวจสอบ Line Breakout + EMA7
                pattern_result = None
                if self.pattern_detector:
                    try:
                        # Convert OHLCV data for pattern detector
                        ohlc_data = []
                        for candle in ohlcv_1h:
                            ohlc_data.append({
                                'timestamp': int(candle[0]),
                                'open': float(candle[1]),
                                'high': float(candle[2]),
                                'low': float(candle[3]),
                                'close': float(candle[4]),
                                'volume': float(candle[5])
                            })
                        
                        # ตรวจสอบ Line Breakout + EMA7 pattern
                        pattern_result = self.pattern_detector.detect_patterns(ohlc_data)
                        
                        if not pattern_result.get('pattern_detected', False):
                            print(f"    ❌ ไม่พบ fresh Line Breakout + EMA7 ใน {symbol} - ข้าม")
                            print(f"        📊 Breakout candles ago: {pattern_result.get('breakout_candles_ago', 999)}")
                            skipped_count += 1
                            continue
                        
                        print(f"    ✅ พบ fresh Line Breakout + EMA7 ใน {symbol}!")
                        print(f"        📊 Pattern: {pattern_result.get('pattern_type', 'Unknown')}")
                        print(f"        📊 Confidence: {pattern_result.get('confidence', 0):.1f}%")
                        print(f"        📊 Breakout: {pattern_result.get('breakout_candles_ago', 999)} candles ago")
                        print(f"        📊 Signal: {pattern_result.get('signal', 'NEUTRAL')}")
                        print(f"        📊 Candle Color: {pattern_result.get('candle_color', '')} vs EMA7: {pattern_result.get('candle_vs_ema7', '')}")
                        
                    except Exception as e:
                        print(f"    ❌ เกิดข้อผิดพลาดในการตรวจสอบ Line Breakout + EMA7 pattern: {e}")
                        skipped_count += 1
                        continue
                else:
                    print(f"    ⚠️ Pattern detector ไม่พร้อมใช้งาน - ส่งต่อไป AI")
                
                # ขั้นตอนที่ 3: ส่งไปยัง AI เฉพาะเหรียญที่มี fresh Line Breakout + EMA7
                print(f"    🤖 ส่งข้อมูลไปยัง AI Line Breakout + EMA7 Analyzer...")
                
                # สร้าง previous_patterns จาก Line Breakout + EMA7 result
                previous_patterns = []
                if pattern_result:
                    previous_patterns = [{
                        'type': pattern_result.get('pattern_type', 'Unknown'),
                        'confidence': pattern_result.get('confidence', 0),
                        'breakout_candles_ago': pattern_result.get('breakout_candles_ago', 999),
                        'signal': pattern_result.get('signal', 'NEUTRAL'),
                        'candle_color': pattern_result.get('candle_color', ''),
                        'candle_vs_ema7': pattern_result.get('candle_vs_ema7', ''),
                        'ema7_value': pattern_result.get('ema7_value', 0)
                    }]
                
                # ส่งเฉพาะข้อมูล 1H ไปยัง AI (ไม่ใช้ 4H)
                analysis = self.ai_analyzer.analyze_symbol(symbol, ohlcv_1h, None, previous_patterns)
                
                # ขั้นตอนที่ 3: ตรวจสอบผลลัพธ์จาก AI Line Breakout + EMA7 Analysis
                action = analysis.get('action', 'HOLD')
                confidence = analysis.get('confidence', 0)
                stop_loss = analysis.get('stop_loss', 0)
                take_profit = analysis.get('take_profit', 0)
                pattern_detected = analysis.get('pattern_detected', 'None')
                pattern_strength = analysis.get('pattern_strength', 0)
                
                print(f"    💡 AI ผลลัพธ์: Action={action}, Pattern={pattern_detected}")
                print(f"    📊 Confidence={confidence}%, Strength={pattern_strength}, SL={stop_loss}, TP={take_profit}")
                
                # ตรวจสอบว่า AI ให้ action ที่ชัดเจน
                if action == 'HOLD':
                    print(f"    ⚠️  AI แนะนำ HOLD - ไม่พบ Chart Pattern ที่เป็น breakout/confirmed - ข้าม {symbol}")
                    analyzed_count += 1
                    continue
                
                # ตรวจสอบ confidence threshold (>80%)
                if confidence < self.confidence_threshold:
                    print(f"    ⚠️  Confidence ต่ำ ({confidence}% < 80%) - ข้าม {symbol}")
                    analyzed_count += 1
                    continue
                
                # ตรวจสอบว่า AI ให้ SL/TP ที่ชัดเจน
                if not stop_loss or stop_loss <= 0:
                    print(f"    ❌ AI ไม่ได้ระบุ Stop Loss ที่ชัดเจน (SL={stop_loss}) - ข้าม {symbol}")
                    analyzed_count += 1
                    continue
                    
                if not take_profit or take_profit <= 0:
                    print(f"    ❌ AI ไม่ได้ระบุ Take Profit ที่ชัดเจน (TP={take_profit}) - ข้าม {symbol}")
                    analyzed_count += 1
                    continue
                
                ai_analyzed += 1
                
                # ขั้นตอนที่ 4: เปิด position เมื่อ AI ให้สัญญาณ Line Breakout + EMA7 ที่ชัดเจน
                print(f"    ✅ พบ Line Breakout + EMA7 pattern {pattern_detected} ที่เป็น {action} - ดำเนินการเปิด position")
                
                # ตรวจสอบว่าเหรียญนี้มี position เปิดอยู่แล้วหรือไม่
                existing_positions = self.get_positions()
                existing_symbols = {pos['symbol'] for pos in existing_positions}
                
                if symbol in existing_symbols:
                    print(f"    ⚠️  {symbol} มี position เปิดอยู่แล้ว - ข้ามการเปิด position ซ้ำ")
                    analyzed_count += 1
                    continue
                
                # ตรวจสอบ balance (อัปเดตแบบ realtime)
                current_balance = self.check_available_balance()
                balance = current_balance
                
                if balance < self.position_size_usdt:
                    print(f"    ❌ Balance ไม่พอ: {balance:.2f} < {self.position_size_usdt}")
                    print(f"    💰 เงินหมดแล้ว - หยุดการเปิด position")
                    break
                
                # ดึงราคาปัจจุบัน (ใช้ข้อมูลจาก OHLCV ล่าสุด)
                current_price = ohlcv_1h[-1][4]  # Close price ล่าสุด
                print(f"    💰 ราคาปัจจุบัน: {current_price}")
                
                # กำหนด side จาก AI action
                if action == 'LONG':
                    side = 'buy'
                elif action == 'SHORT':
                    side = 'sell'
                else:
                    print(f"    ❌ AI action ไม่ชัดเจน: {action}")
                    analyzed_count += 1
                    continue
                
                # คำนวณ quantity
                quantity = self.calculate_position_quantity(symbol, side, current_price)
                print(f"    📏 คำนวณ quantity: {quantity}")
                
                if quantity > 0:
                    # เปิด position
                    print(f"    🚀 เปิด {action} position ตาม Line Breakout + EMA7 {pattern_detected}")
                    print(f"    📊 {symbol} {side.upper()} {quantity} @ {current_price}")
                    success, error_type = self.open_position_with_sl_tp(symbol, side, quantity, current_price, stop_loss, take_profit)
                    
                    if success:
                        position_opened += 1
                        balance -= self.position_size_usdt
                        
                        print(f"    ✅ เปิด position {symbol} สำเร็จ")
                        print(f"    💰 Balance เหลือ: {balance:.2f} USDT")
                        
                        # ตรวจสอบว่ายังมีเงินเหลือหรือไม่
                        if balance < self.position_size_usdt:
                            print(f"\n💰 เงินเหลือไม่พอเปิด position ถัดไป ({balance:.2f} USDT)")
                            print(f"🔄 หยุดการวิเคราะห์ - รอรอบถัดไป")
                            break
                    else:
                        print(f"    ❌ เปิด position {symbol} ไม่สำเร็จ - Error type: {error_type}")
                        
                        # จัดการ error ตามประเภท
                        if error_type == 'insufficient_funds':
                            print(f"    💰 เงินหมด - หยุดการทำงานและรอจนถึงชั่วโมงถัดไป")
                            self.wait_until_next_hour_first_minute()
                            return  # หยุด loop2_process ทันที
                        else:
                            print(f"    ⚠️  Error อื่นๆ - ดำเนินการต่อ")
                            analyzed_count += 1
                else:
                    print(f"    ❌ ไม่สามารถคำนวณ quantity ได้")
                    analyzed_count += 1
                
            except Exception as e:
                print(f"    ❌ เกิดข้อผิดพลาดในการวิเคราะห์ {symbol}: {e}")
                skipped_count += 1
                continue
        
        # สรุปผลลัพธ์
        print("\n" + "="*60)
        print("📊 สรุปผล LOOP2 Line Breakout + EMA7 Analysis:")
        print(f"   📊 จำนวนเหรียญที่สแกน: {len(symbols)} เหรียญ")
        print(f"   🔍 ผ่านการกรอง Line Breakout + EMA7: {ai_analyzed} เหรียญ")
        print(f"   🚀 เปิด positions สำเร็จ: {position_opened} รายการ")
        print(f"   ⚠️  ข้ามไป: {skipped_count} เหรียญ")
        print(f"   💰 Balance สุดท้าย: {self.check_available_balance():.2f} USDT")
        print("="*60)
    
    def show_summary(self):
        """แสดงสรุปข้อมูล positions และ orders"""
        print("📊 สรุปข้อมูลปัจจุบัน:")
        print("-" * 40)
        
        positions = self.get_positions()
        print(f"📍 Positions: {len(positions)} รายการ")
        for pos in positions:
            symbol = pos['symbol']
            side = pos['side']
            contracts = abs(pos['contracts'])
            pnl = pos['unrealizedPnl'] or 0
            print(f"   {symbol} - {side.upper()} {contracts:,.4f} (PnL: {pnl:+.2f})")
        
        orders = self.get_all_orders()
        print(f"📋 Orders: {len(orders)} รายการ")
        
        if orders:
            order_by_symbol = {}
            for order in orders:
                symbol = order['symbol']
                if symbol not in order_by_symbol:
                    order_by_symbol[symbol] = 0
                order_by_symbol[symbol] += 1
            
            for symbol, count in order_by_symbol.items():
                print(f"   {symbol}: {count} orders")
    
    def wait_for_next_hour(self):
        """รอจนถึงนาทีแรกของชั่วโมงถัดไป"""
        now = datetime.datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        
        wait_seconds = (next_hour - now).total_seconds()
        wait_minutes = wait_seconds / 60
        
        print(f"⏰ รอจนถึงนาทีแรกของชั่วโมงถัดไป: {next_hour.strftime('%H:%M:%S')}")
        print(f"⏱️ รอ {wait_minutes:.1f} นาที ({wait_seconds:.0f} วินาที)")
        
        # แสดงการนับถอยหลังทุก ๆ 5 นาที
        while wait_seconds > 0:
            if wait_seconds > 300:  # ถ้าเหลือมากกว่า 5 นาที
                time.sleep(300)  # รอ 5 นาที
                wait_seconds -= 300
                remaining_minutes = wait_seconds / 60
                print(f"⏳ เหลืออีก {remaining_minutes:.1f} นาที...")
            else:
                time.sleep(wait_seconds)
                break
        
        print(f"✅ ถึงเวลาแล้ว - {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    def wait_until_next_hour_first_minute(self):
        """รอจนถึงนาทีแรกของชั่วโมงถัดไปเมื่อเกิด error หลังเปิด position"""
        now = datetime.datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        
        wait_seconds = (next_hour - now).total_seconds()
        wait_minutes = wait_seconds / 60
        
        print(f"⏰ เกิด error หลังเปิด position - รอจนถึงชั่วโมงถัดไป")
        print(f"🕒 รอจนถึง {next_hour.strftime('%H:%M:%S')} (รอ {wait_minutes:.1f} นาที)")
        
        time.sleep(wait_seconds)
        print(f"✅ ถึงเวลาแล้ว - {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    def check_and_fix_problematic_positions(self):
        """ตรวจสอบและแก้ไข positions ที่มีปัญหา (orders ไม่ครบ)"""
        try:
            print("🔍 ตรวจสอบ positions ที่มีปัญหา...")
            
            # ดึงข้อมูล positions และ orders
            positions = self.get_positions()
            all_orders = self.get_all_orders()
            
            # นับจำนวน orders แต่ละ symbol
            order_counts = {}
            for order in all_orders:
                symbol = order['symbol']
                order_counts[symbol] = order_counts.get(symbol, 0) + 1
            
            problematic_positions = []
            
            for pos in positions:
                symbol = pos['symbol']
                contracts = float(pos['contracts'])
                
                if contracts != 0:  # มี position
                    order_count = order_counts.get(symbol, 0)
                    
                    # ตรวจสอบว่ามี orders น้อยกว่า 2 (ควรมี SL + TP)
                    if order_count < 2:
                        problematic_positions.append({
                            'symbol': symbol,
                            'contracts': contracts,
                            'side': pos['side'],
                            'order_count': order_count,
                            'pnl': pos['unrealizedPnl']
                        })
            
            if problematic_positions:
                print(f"⚠️  พบ positions ที่มีปัญหา {len(problematic_positions)} รายการ:")
                
                for prob_pos in problematic_positions:
                    symbol = prob_pos['symbol']
                    print(f"   📊 {symbol}: {prob_pos['order_count']} orders (ควรมี 2)")
                    print(f"      Size: {prob_pos['contracts']}, PnL: {prob_pos['pnl']}")
                    
                    # ถามผู้ใช้หรือปิดอัตโนมัติตามเงื่อนไข
                    # ปิดถ้า PnL เป็นลบมาก หรือมี orders เป็น 0
                    should_close = (
                        prob_pos['order_count'] == 0 or  # ไม่มี orders เลย
                        (prob_pos['pnl'] and prob_pos['pnl'] < -5)  # ขาดทุนมากกว่า 5 USDT
                    )
                    
                    if should_close:
                        print(f"🔄 ปิด position {symbol} (เหตุผล: orders ไม่ครบ/ขาดทุนมาก)")
                        success = self.close_position(symbol, prob_pos['contracts'], prob_pos['side'])
                        
                        if success:
                            # ยกเลิก orders ที่เหลือ
                            try:
                                remaining_orders = [o for o in all_orders if o['symbol'] == symbol]
                                for order in remaining_orders:
                                    self.exchange.cancel_order(order['id'], symbol)
                                    print(f"   🚫 ยกเลิก order {order['id']}")
                            except Exception as e:
                                print(f"   ⚠️ ไม่สามารถยกเลิก orders: {e}")
                    else:
                        print(f"   ⏳ เก็บ position {symbol} ไว้ (PnL: {prob_pos['pnl']})")
                        
            else:
                print("✅ ไม่พบ positions ที่มีปัญหา")
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบ positions: {e}")

    # ...existing code...
