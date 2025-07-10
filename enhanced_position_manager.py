"""
Enhanced Position & Order Manager with Linear Regression Channel Integration
ระบบจัดการ positions และ orders ที่ใช้ Linear Regression Channel detection เท่านั้น
พร้อม Advanced Historical Data Management
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
    from linear_regression_detector import LinearRegressionChannelDetector, OHLCV
    LRC_DETECTOR_AVAILABLE = True
    print("✅ Linear Regression Channel Detector imported successfully")
except ImportError as e:
    print(f"⚠️ LRC Detector import error: {e}")
    print("🔄 Using fallback mode - will send all coins to AI")
    LRC_DETECTOR_AVAILABLE = False
except Exception as e:
    print(f"⚠️ LRC Detector error: {e}")
    print("🔄 Using fallback mode - will send all coins to AI")
    LRC_DETECTOR_AVAILABLE = False

# Import Smart TP/SL Calculator
try:
    from smart_tp_sl import SmartTPSLCalculator
    SMART_TP_SL_AVAILABLE = True
    print("✅ Smart TP/SL Calculator imported successfully")
except ImportError as e:
    print(f"⚠️ Smart TP/SL import error: {e}")
    print("🔄 Using fallback percentage TP/SL")
    SMART_TP_SL_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Smart TP/SL error: {e}")
    print("🔄 Using fallback percentage TP/SL")
    SMART_TP_SL_AVAILABLE = False

# Import Advanced Historical Data Manager
try:
    from advanced_historical_data_manager import AdvancedHistoricalDataManager
    ADVANCED_DATA_MANAGER_AVAILABLE = True
    print("✅ Advanced Historical Data Manager imported successfully")
except ImportError as e:
    print(f"⚠️ Advanced Data Manager import error: {e}")
    print("🔄 Using direct API calls")
    ADVANCED_DATA_MANAGER_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Advanced Data Manager error: {e}")
    print("🔄 Using direct API calls")
    ADVANCED_DATA_MANAGER_AVAILABLE = False

class EnhancedPositionManager:
    def __init__(self, exchange_client):
        """Initialize with exchange client"""
        self.exchange_client = exchange_client
        self.exchange = exchange_client.get_exchange()
        
        # Initialize AI Analyzer without Historical Data Manager
        self.ai_analyzer = AIAnalyzer(None)  # ไม่ส่ง exchange เพื่อไม่ให้สร้าง data manager
        
        # Initialize Advanced Historical Data Manager
        if ADVANCED_DATA_MANAGER_AVAILABLE:
            self.historical_data_manager = AdvancedHistoricalDataManager(exchange_client)
            print("📊 Advanced Historical Data Manager พร้อมใช้งาน")
        else:
            self.historical_data_manager = None
            print("⚠️ ใช้ Direct API calls แทน Historical Data Manager")
        
        # Initialize Linear Regression Channel Detector for filtering
        if LRC_DETECTOR_AVAILABLE:
            self.lrc_detector_class = LinearRegressionChannelDetector
        else:
            self.lrc_detector_class = None
        
        # Initialize Smart TP/SL Calculator
        if SMART_TP_SL_AVAILABLE:
            self.smart_tp_sl = SmartTPSLCalculator()
        else:
            self.smart_tp_sl = None
        
        # Trading parameters
        self.position_size_usdt = 20  # 20 USDT per position (เพิ่มจาก 10)
        self.leverage = 10  # 10x leverage
        self.confidence_threshold = 75  # 75% confidence threshold สำหรับ Linear Regression Channel
        self.last_signal_type = None  # Store last signal type for AI
        self.first_loop_done = False  # ติดตาม LOOP1 ครั้งแรก
        
        # Support & Resistance parameters
        self.sr_lookback_periods = 50  # จำนวน candles ที่ใช้หาแนวรับ-แนวต้าน
        self.sr_touch_threshold = 0.002  # 0.2% threshold สำหรับการนับ touch
        self.min_touches = 2  # จำนวน touch ขั้นต่ำเพื่อยืนยันแนวรับ-แนวต้าน
        
        print("🔧 Enhanced Position & Order Manager พร้อมใช้งาน")
        print("📊 ใช้ Linear Regression Channel Detection เท่านั้น")
    
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
        """
        ดึงข้อมูล OHLCV ย้อนหลัง - ใช้ Advanced Historical Data Manager
        
        ขั้นตอน:
        1. ตรวจสอบ historical_data_manager
        2. ถ้ามี -> ใช้ระบบ cache + auto update
        3. ถ้าไม่มี -> ใช้ direct API calls (fallback)
        """
        # ใช้ Advanced Historical Data Manager ถ้ามี
        if self.historical_data_manager and timeframe == '1h':
            try:
                print(f"    📊 ใช้ Advanced Historical Data Manager...")
                ohlcv_data = self.historical_data_manager.get_updated_historical_data(symbol)
                
                if ohlcv_data and len(ohlcv_data) >= limit:
                    # ตัดข้อมูลให้ตรงกับ limit ที่ต้องการ
                    final_data = ohlcv_data[-limit:] if len(ohlcv_data) > limit else ohlcv_data
                    print(f"    ✅ ได้ข้อมูลจาก Cache: {len(final_data)} records")
                    return final_data
                else:
                    print(f"    ⚠️ ข้อมูลจาก Cache ไม่เพียงพอ -> ใช้ Direct API")
                    
            except Exception as e:
                print(f"    ⚠️ ข้อผิดพลาด Historical Data Manager: {e} -> ใช้ Direct API")
        
        # Fallback: ใช้ Direct API calls
        try:
            print(f"    📊 ใช้ Direct API calls...")
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if ohlcv:
                print(f"    ✅ ได้ข้อมูลจาก API: {len(ohlcv)} records")
            return ohlcv
        except Exception as e:
            print(f"    ❌ ไม่สามารถดึงข้อมูล OHLCV สำหรับ {symbol}: {e}")
            return None
    
    def convert_ohlcv_to_detector_format(self, ohlcv_data):
        """แปลงข้อมูล OHLCV ให้เป็น format ที่ LRC detector ใช้ได้"""
        if not ohlcv_data or not LRC_DETECTOR_AVAILABLE:
            return None
        
        try:
            detector_data = []
            for candle in ohlcv_data:
                # candle format: [timestamp, open, high, low, close, volume]
                ohlcv_obj = OHLCV(
                    timestamp=int(candle[0]),
                    open=float(candle[1]),
                    high=float(candle[2]),
                    low=float(candle[3]),
                    close=float(candle[4]),
                    volume=float(candle[5])
                )
                detector_data.append(ohlcv_obj)
            
            return detector_data
            
        except Exception as e:
            print(f"    ❌ ไม่สามารถแปลง OHLCV format: {e}")
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
                    print(f"⚠️ Take Profit ({take_profit}) ต้องสูงกว่าราคาปัจจุบัน ({price}) สำหรับ LONG")
                    # Auto-fix: Set take profit to 3% above current price
                    corrected_tp = price * 1.03
                    print(f"🔧 แก้ไขอัตโนมัติ: TP = {corrected_tp:.6f} (+3% จากราคาปัจจุบัน)")
                    take_profit = corrected_tp
            else:  # SHORT position
                if stop_loss <= price:
                    print(f"❌ Stop Loss ({stop_loss}) ต้องสูงกว่าราคาปัจจุบัน ({price}) สำหรับ SHORT")
                    return False, 'validation_error'
                if take_profit >= price:
                    print(f"⚠️ Take Profit ({take_profit}) ต้องต่ำกว่าราคาปัจจุบัน ({price}) สำหรับ SHORT")
                    # Auto-fix: Set take profit to 3% below current price
                    corrected_tp = price * 0.97
                    print(f"🔧 แก้ไขอัตโนมัติ: TP = {corrected_tp:.6f} (-3% จากราคาปัจจุบัน)")
                    take_profit = corrected_tp
            
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
        """ตรวจสอบสัญญาณการเทรด - ใช้ LRC + Channel Price Validation เท่านั้น"""
        try:
            # ดึงข้อมูล OHLCV สำหรับ LRC analysis
            ohlcv = self.get_ohlcv_data(symbol, limit=144)
            if not ohlcv or len(ohlcv) < 100:
                print(f"        ❌ ข้อมูล OHLCV ไม่เพียงพอ ({len(ohlcv) if ohlcv else 0} candles)")
                return False
            
            # ใช้ LRC detector เพื่อตรวจสอบ channel breakout + price validation
            has_signal = False
            if self.lrc_detector_class:
                try:
                    # Convert OHLCV data for LRC detector
                    ohlc_objects = self.convert_ohlcv_to_detector_format(ohlcv)
                    
                    if ohlc_objects:
                        # Create LRC detector and analyze
                        lrc_detector = self.lrc_detector_class(ohlc_objects, length=100, deviation=2.0)
                        lrc_result = lrc_detector.detect_breakout_with_channel_price_check(max_lookback=5)
                        
                        if lrc_result.is_fresh_breakout and lrc_result.signal != 'NEUTRAL':
                            print(f"        ✅ พบสัญญาณ LRC + Channel Price: {lrc_result.signal}")
                            print(f"        📊 Pattern: {lrc_result.pattern_type}")
                            print(f"        📊 Confidence: {lrc_result.confidence:.1f}%")
                            print(f"        📊 Entry: {lrc_result.entry_level:.6f}")
                            print(f"        📊 Stop Loss: {lrc_result.stop_loss:.6f}")
                            
                            self.last_signal_type = lrc_result.signal
                            has_signal = True
                        else:
                            print(f"        ⚠️ ไม่ผ่านเงื่อนไข LRC + Channel Price")
                            print(f"        📊 Reason: {lrc_result.description}")
                    else:
                        print(f"        ❌ ไม่สามารถแปลงข้อมูล OHLCV")
                        
                except Exception as e:
                    print(f"        ❌ ข้อผิดพลาด LRC detector: {e}")
            else:
                print(f"        ❌ LRC detector ไม่พร้อมใช้งาน")
            
            return has_signal
            
        except Exception as e:
            print(f"        ❌ ไม่สามารถตรวจสอบสัญญาณ {symbol}: {e}")
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

    def show_positions_summary(self):
        """แสดงสรุป positions และ orders ปัจจุบัน (แบบย่อ)"""
        try:
            positions = self.get_positions()
            orders = self.get_all_orders()
            
            if positions or orders:
                print(f"� {len(positions)} positions, {len(orders)} orders")
            
        except Exception as e:
            print(f"❌ Error: {e}")

    # LOOP1: ขั้นตอนการทำงานหลักตาม step.md
    def loop1_process(self):
        """LOOP1: ขั้นตอนการทำงานหลักตาม step.md - เฉพาะดึงเหรียญที่พร้อมเทรด"""
        print("� LOOP1: ดึงรายการเหรียญที่พร้อมเทรด...")
        
        # ดึงรายการเหรียญที่พร้อมเทรด
        available_symbols = self.get_available_symbols()
        print(f"📊 พบ {len(available_symbols)} เหรียญที่พร้อมเทรด")
        
        # แสดงเหรียญที่สับไพ่แล้ว 10 อันดับแรก
        if available_symbols:
            preview_symbols = available_symbols[:10]
            print(f"🎲 เหรียญที่สับไพ่แล้ว (10 อันดับแรก): {', '.join(preview_symbols)}")
        
        return available_symbols
    
    def loop2_process(self, symbols):
        """LOOP2: วิเคราะห์และเทรดเหรียญด้วย Chart Pattern Analysis - แทน RSI"""
        print("🔄 LOOP2: วิเคราะห์เหรียญ...")
        
        if not symbols:
            return
        
        print(f"📊 สแกน {len(symbols)} เหรียญ")
        
        # ตรวจสอบ balance
        balance = self.check_available_balance()
        current_positions = self.get_positions()
        
        # ตรวจสอบ balance แทน position limit - เปิดไปเรื่อยๆ จนกว่าเงินจะหมด
        if balance < self.position_size_usdt:
            print(f"⚠️ Balance ไม่เพียงพอ: {balance:.2f} USDT")
            return
        
        # เปิด position จนกว่าเงินจะหมด (ไม่จำกัดจำนวน)
        max_positions = int(balance // self.position_size_usdt)
        print(f"📊 สามารถเปิด position ได้สูงสุด: {max_positions} รายการ")
        
        analyzed_count = 0
        ai_analyzed = 0
        skipped_count = 0
        position_opened = 0
        
        print("\n" + "="*60)
        print("🔍 เริ่มสแกนเหรียญด้วย Linear Regression Channel Detection:")
        print("⚠️ ใช้ rate limiting เพื่อหลีกเลี่ยง Binance API limit")
        print("="*60)
        
        # Rate limiting: ประมวลผลเป็น batch เพื่อลด API calls
        batch_size = 20  # ประมวลผล 20 เหรียญ แล้วหยุด 5 วินาที
        processed_in_batch = 0
        
        for i, symbol in enumerate(symbols, 1):
            try:
                # Batch rate limiting: หยุดพักหลังจากประมวลผล batch_size เหรียญ
                if processed_in_batch >= batch_size and i > batch_size:
                    print(f"\n⏸️ ประมวลผล {batch_size} เหรียญแล้ว - พักระบบ 5 วินาที...")
                    print(f"    🔄 เพื่อหลีกเลี่ยง rate limit และให้ระบบพักผ่อน")
                    time.sleep(5)  # พัก 5 วินาทีหลังจาก batch
                    processed_in_batch = 0  # รีเซ็ต counter
                    print(f"✅ เริ่มประมวลผล batch ต่อไป...")
                
                # ตรวจสอบ balance แทน position limit
                current_balance = self.check_available_balance()
                if current_balance < self.position_size_usdt:
                    print(f"⚠️ Balance หมด ({current_balance:.2f} USDT) - หยุดการเปิด position ใหม่")
                    break
                
                print(f"\n[{i:3d}/{len(symbols):3d}] 🔍 กำลังวิเคราะห์ {symbol}...")
                
                # ไม่ต้อง rate limiting เพราะใช้ Advanced Historical Data Manager
                # (ข้อมูลส่วนใหญ่มาจาก cache, ไม่ต้องเรียก API บ่อย)
                
                # ตรวจสอบ balance ก่อนเปิด position
                try:
                    current_balance = self.check_available_balance()
                    if current_balance < self.position_size_usdt:
                        print(f"    ❌ Balance ไม่เพียงพอ ({current_balance:.2f} < {self.position_size_usdt} USDT)")
                        print(f"    🔄 หยุดการเปิด position ใหม่")
                        break
                except Exception as e:
                    if "429" in str(e) or "Too Many Requests" in str(e):
                        print(f"    ⚠️ Rate limit - รอ 10 วินาที...")
                        time.sleep(10)
                        try:
                            current_balance = self.check_available_balance()
                        except Exception as e2:
                            print(f"    ❌ ไม่สามารถตรวจสอบ balance: {e2}")
                            skipped_count += 1
                            continue
                    else:
                        print(f"    ❌ ไม่สามารถตรวจสอบ balance: {e}")
                        skipped_count += 1
                        continue
                
                # ขั้นตอนที่ 1: ดึงข้อมูล OHLCV 1H สำหรับ Linear Regression Channel Analysis (120 timeframes)
                print(f"    📊 เตรียมข้อมูล OHLCV 1H (120 timeframes)...")
                
                try:
                    ohlcv_1h = self.get_ohlcv_data(symbol, timeframe='1h', limit=120)  # ใช้ Advanced Historical Data Manager
                except Exception as e:
                    print(f"    ❌ ไม่สามารถดึงข้อมูล OHLCV 1H สำหรับ {symbol}: {e}")
                    skipped_count += 1
                    continue
                
                if not ohlcv_1h or len(ohlcv_1h) < 20:
                    print(f"    ❌ ข้อมูล OHLCV 1H ไม่เพียงพอสำหรับ {symbol}")
                    skipped_count += 1
                    processed_in_batch += 1  # นับเป็น processed
                    continue
                
                print(f"    ✅ ได้ข้อมูล OHLCV 1H: {len(ohlcv_1h)} records")
                
                # ขั้นตอนที่ 2: กรองด้วย Python Linear Regression Channel detector (วิธีใหม่)
                print(f"    🔍 ขั้นตอนที่ 1: วน loop 10 รอบ หา LRC breakout...")
                print(f"    🔍 ขั้นตอนที่ 2: ถ้ามี breakout → ตรวจ Channel Price validation...")
                print(f"    🔍 ขั้นตอนที่ 3: ให้ AI คำนวณ Stop Loss และ Take Profit...")
                
                # ใช้ LRC detector เพื่อตรวจสอบ channel breakout
                lrc_result = None
                if self.lrc_detector_class:
                    try:
                        # Convert OHLCV data for LRC detector
                        ohlc_objects = self.convert_ohlcv_to_detector_format(ohlcv_1h)
                        
                        if ohlc_objects:
                            # Create LRC detector and analyze with new method
                            lrc_detector = self.lrc_detector_class(ohlc_objects, length=100, deviation=2.0)
                            lrc_result = lrc_detector.detect_breakout_with_channel_price_check(max_lookback=5)
                            
                            if not lrc_result.is_fresh_breakout or lrc_result.signal == 'NEUTRAL':
                                print(f"    ❌ ไม่ผ่านเงื่อนไข LRC + Channel Price validation ใน {symbol} - ข้าม")
                                
                                # แสดงสาเหตุที่ไม่ผ่าน
                                if hasattr(lrc_result, 'description') and 'no_lrc_breakout' in lrc_result.description:
                                    print(f"        📊 LRC Breakout: NO (ไม่พบ breakout ใน 10 timeframes)")
                                elif hasattr(lrc_result, 'description') and 'channel' in lrc_result.description.lower():
                                    print(f"        📊 LRC Breakout: YES, แต่ Channel Price validation: NO")
                                    print(f"        📊 (ราคาไม่ตรงตามเงื่อนไข channel price)")
                                
                                print(f"        📊 Signal: {lrc_result.signal}")
                                skipped_count += 1
                                processed_in_batch += 1  # นับเป็น processed
                                continue
                            
                            print(f"    ✅ ผ่านเงื่อนไข LRC + Channel Price validation ใน {symbol}!")
                            print(f"        📊 LRC Breakout: YES ({lrc_result.breakout_candles_ago} candles ago)")
                            print(f"        📊 Direction: {lrc_result.trend_direction}")
                            print(f"        📊 Channel Price Validation: YES")
                            print(f"        📊 Signal: {lrc_result.signal} (Confidence: {lrc_result.confidence:.1f}%)")
                            print(f"        📊 Pattern: {lrc_result.pattern_type}")
                            print(f"        📊 Stop Loss: {lrc_result.stop_loss:.6f}")
                            print(f"        📊 Slope: {lrc_result.slope:.6f}, Status: {lrc_result.pattern_status}")
                        else:
                            print(f"    ❌ ไม่สามารถแปลงข้อมูล OHLCV สำหรับ LRC detector")
                            skipped_count += 1
                            processed_in_batch += 1
                            continue
                        # เงื่อนไขที่ 3: ส่งให้ AI ตัดสินใจสุดท้าย (เฉพาะที่ผ่านการยืนยันแล้ว)
                        # เงื่อนไขที่ 3: ส่งให้ AI ตัดสินใจสุดท้าย (เฉพาะที่ผ่านการยืนยันแล้ว)
                        if lrc_result.signal == 'NEUTRAL':
                            print(f"    ❌ Signal เป็น NEUTRAL - ไม่มีสัญญาณการเทรดที่ชัดเจน - ข้าม {symbol}")
                            skipped_count += 1
                            continue
                        
                    except Exception as e:
                        print(f"    ❌ เกิดข้อผิดพลาดในการตรวจสอบ Linear Regression Channel pattern: {e}")
                        skipped_count += 1
                        continue
                else:
                    print(f"    ⚠️ LRC detector ไม่พร้อมใช้งาน - ส่งต่อไป AI")
                
                # ขั้นตอนที่ 3: ส่งไปยัง AI เฉพาะเหรียญที่มี fresh LRC breakout และ Signal ไม่เป็น NEUTRAL
                print(f"    🤖 ส่งข้อมูลไปยัง AI Linear Regression Channel Analyzer...")
                
                # สร้าง previous_patterns จาก LRC result พร้อมข้อมูลสำหรับ AI คำนวณ SL/TP
                previous_patterns = []
                if lrc_result:
                    current_price = ohlcv_1h[-1][4]  # ราคาปัจจุบัน
                    previous_patterns = [{
                        'type': lrc_result.pattern_type,
                        'confidence': lrc_result.confidence,
                        'breakout_candles_ago': lrc_result.breakout_candles_ago,
                        'signal': lrc_result.signal,
                        'trend_direction': lrc_result.trend_direction,
                        'slope': lrc_result.slope,
                        'upper_channel': lrc_result.upper_channel,
                        'middle_line': lrc_result.middle_line,
                        'lower_channel': lrc_result.lower_channel,
                        'entry_level': current_price,
                        'current_price': current_price,
                        'channel_reference': lrc_result.upper_channel if lrc_result.signal == 'LONG' else lrc_result.lower_channel,
                        'request_ai_sl_tp': True,  # บอก AI ให้คำนวณ SL/TP ที่เหมาะสม
                        'strength': lrc_result.strength
                    }]
                
                # ส่งเฉพาะข้อมูล 1H ไปยัง AI (ไม่ใช้ 4H)
                analysis = self.ai_analyzer.analyze_symbol(symbol, ohlcv_1h, None, previous_patterns)
                
                # ขั้นตอนที่ 3: ตรวจสอบผลลัพธ์จาก AI Linear Regression Channel Analysis
                action = analysis.get('action', 'HOLD')
                confidence = analysis.get('confidence', 0)
                pattern_detected = analysis.get('pattern_detected', 'None')
                pattern_strength = analysis.get('pattern_strength', 0)
                
                print(f"    💡 AI ผลลัพธ์: Action={action}, Pattern={pattern_detected}")
                print(f"    📊 Confidence={confidence}%, Strength={pattern_strength}")
                
                # ตรวจสอบว่า AI ให้ action ที่ชัดเจน
                if action == 'HOLD':
                    print(f"    ⚠️  AI แนะนำ HOLD - ไม่พบ Chart Pattern ที่เป็น breakout/confirmed - ข้าม {symbol}")
                    analyzed_count += 1
                    processed_in_batch += 1  # นับเป็น processed
                    continue
                
                # ตรวจสอบ confidence threshold (>75%)
                if confidence < self.confidence_threshold:
                    print(f"    ⚠️  Confidence ต่ำ ({confidence}% < {self.confidence_threshold}%) - ข้าม {symbol}")
                    analyzed_count += 1
                    processed_in_batch += 1  # นับเป็น processed
                    continue
                
                # ตรวจสอบ trend_direction ไม่เป็น "sideways" (ใหม่: ไม่เปิด position ใน sideways market)
                trend_direction = lrc_result.trend_direction if lrc_result else analysis.get('trend_direction', 'unknown')
                if trend_direction.lower() == 'sideways':
                    print(f"    ⚠️  Trend Direction เป็น 'sideways' - ไม่เปิด position ใน sideways market - ข้าม {symbol}")
                    analyzed_count += 1
                    processed_in_batch += 1  # นับเป็น processed
                    continue
                
                # ตรวจสอบ AI-calculated confidence >= 80% (ใหม่: ใช้เฉพาะ high-confidence trades)
                if confidence < 80:
                    print(f"    ⚠️  AI Confidence ต่ำกว่า 80% ({confidence}%) - ใช้เฉพาะ high-confidence trades - ข้าม {symbol}")
                    analyzed_count += 1
                    processed_in_batch += 1  # นับเป็น processed
                    continue
                
                ai_analyzed += 1
                
                # ขั้นตอนที่ 4: เปิด position เมื่อ AI ให้สัญญาณ LRC + Channel Price ที่ชัดเจน
                print(f"    ✅ พบ LRC + Channel Price pattern {pattern_detected} ที่เป็น {action}")
                print(f"    📈 Trend Direction: {trend_direction}, Confidence: {confidence}% (>= 80%)")
                print(f"    🚀 ผ่านทุกเงื่อนไข - ดำเนินการเปิด position")
                
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
                    # ใช้ Stop Loss และ Take Profit ที่ AI คำนวณให้
                    print(f"    🎯 ใช้ Stop Loss และ Take Profit ที่ AI คำนวณ...")
                    
                    # ดึงค่า SL/TP จาก AI analysis result
                    ai_stop_loss = analysis.get('stop_loss', 0)
                    ai_take_profit = analysis.get('take_profit', 0)
                    
                    if ai_stop_loss > 0 and ai_take_profit > 0:
                        stop_loss = ai_stop_loss
                        take_profit = ai_take_profit
                        print(f"    📊 AI TP/SL: TP={take_profit:.6f}, SL={stop_loss:.6f}")
                    else:
                        # Fallback: ใช้ channel reference สำหรับ SL และ percentage สำหรับ TP
                        if action.lower() == 'long':
                            # Long: SL = Upper Channel * 0.98, TP = Current Price * 1.02
                            stop_loss = lrc_result.upper_channel * 0.98 if lrc_result else current_price * 0.95
                            take_profit = current_price * 1.02
                        else:  # SHORT
                            # Short: SL = Lower Channel * 1.02, TP = Current Price * 0.98  
                            stop_loss = lrc_result.lower_channel * 1.02 if lrc_result else current_price * 1.05
                            take_profit = current_price * 0.98
                        print(f"    📊 Fallback TP/SL: TP={take_profit:.6f}, SL={stop_loss:.6f}")
                    
                    # เปิด position
                    print(f"    🚀 เปิด {action} position ตาม LRC + Channel Price {pattern_detected} (AI SL/TP)")
                    print(f"    📊 {symbol} {side.upper()} {quantity} @ {current_price}")
                    success, error_type = self.open_position_with_sl_tp(symbol, side, quantity, current_price, stop_loss, take_profit)
                    
                    if success:
                        position_opened += 1
                        balance -= self.position_size_usdt
                        processed_in_batch += 1  # นับเป็น processed เมื่อสำเร็จ
                        
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
                            processed_in_batch += 1  # นับเป็น processed แม้จะ error
                else:
                    print(f"    ❌ ไม่สามารถคำนวณ quantity ได้")
                    analyzed_count += 1
                    processed_in_batch += 1  # นับเป็น processed แม้จะ error
                
            except Exception as e:
                print(f"    ❌ เกิดข้อผิดพลาดในการวิเคราะห์ {symbol}: {e}")
                skipped_count += 1
                processed_in_batch += 1  # นับเป็น processed แม้จะ error
                continue
        
        # สรุปผลลัพธ์
        print("\n" + "="*60)
        print("📊 สรุปผล LOOP2 LRC + Channel Price Validation Analysis:")
        print(f"   📊 จำนวนเหรียญที่สแกน: {len(symbols)} เหรียญ")
        print(f"   🔍 ผ่านการกรอง LRC + Channel Price: {ai_analyzed} เหรียญ")
        print(f"   🚀 เปิด positions สำเร็จ: {position_opened} รายการ")
        print(f"   ⚠️  ข้ามไป: {skipped_count} เหรียญ")
        print(f"   💰 Balance สุดท้าย: {self.check_available_balance():.2f} USDT")
        print(f"   📌 หมายเหตุ: AI คำนวณ Stop Loss และ Take Profit ที่เหมาะสมทุก position")
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
                for prob_pos in problematic_positions:
                    symbol = prob_pos['symbol']
                    
                    # ปิดถ้า PnL เป็นลบมาก หรือมี orders เป็น 0
                    should_close = (
                        prob_pos['order_count'] == 0 or  # ไม่มี orders เลย
                        (prob_pos['pnl'] and prob_pos['pnl'] < -5)  # ขาดทุนมากกว่า 5 USDT
                    )
                    
                    if should_close:
                        print(f"🔄 ปิด position {symbol} (orders ไม่ครบ)")
                        self.close_position(symbol, prob_pos['contracts'], prob_pos['side'])
                        
                        # ยกเลิก orders ที่เหลือ
                        try:
                            remaining_orders = [o for o in all_orders if o['symbol'] == symbol]
                            for order in remaining_orders:
                                self.exchange.cancel_order(order['id'], symbol)
                        except Exception:
                            pass
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบ positions: {e}")

    def hourly_position_check(self):
        """ตรวจสอบ positions และ orders ทุกชั่วโมง"""
        print("🔍 ตรวจสอบ positions และ orders...")
        
        # ตรวจสอบและแก้ไข positions ที่มีปัญหา
        self.check_and_fix_problematic_positions()
        
        # ตรวจสอบ positions และ orders ปัจจุบัน
        positions = self.get_positions()
        all_orders = self.get_all_orders()
        
        if positions:
            print(f"📍 {len(positions)} positions เปิดอยู่")
            for pos in positions:
                symbol = pos['symbol']
                contracts = pos['contracts']
                side = pos['side']
                
                # ตรวจสอบ orders สำหรับ position นี้
                symbol_orders = self.get_orders_by_symbol(symbol)
                order_count = len(symbol_orders)
                
                if order_count != 2:
                    print(f"⚠️  {symbol}: {order_count} orders (ต้องการ 2)")
                    
                    # ยกเลิก orders และปิด position
                    self.cancel_orders_by_symbol(symbol)
                    self.close_position(symbol, contracts, side)
                    print(f"✅ ปิด position {symbol}")
                    self.cache_timestamp = 0  # Invalidate cache
        
        # ตรวจสอบ orphan orders (orders ที่ไม่มี positions)
        if all_orders and positions:
            position_symbols = {pos['symbol'] for pos in positions}
            orphan_orders = [order for order in all_orders if order['symbol'] not in position_symbols]
            
            if orphan_orders:
                print(f"🔄 ยกเลิก {len(orphan_orders)} orphan orders")
                for order in orphan_orders:
                    self.cancel_order(order['id'], order['symbol'])
                self.cache_timestamp = 0  # Invalidate cache
        
        if all_orders:
            print(f"📋 {len(all_orders)} orders รอดำเนินการ")
