"""
Smart Take Profit & Stop Loss Calculator
คำนวณ TP/SL ตามแนวรับ-แนวต้าน (Support & Resistance)
"""

class SmartTPSLCalculator:
    def __init__(self):
        """Initialize Smart TP/SL Calculator"""
        # Parameters ตาม documentation
        self.lookback_period = 50          # 50 candles lookback
        self.pivot_window = 5              # 5-candle window รอบ pivot
        self.touch_threshold = 0.002       # 0.2% threshold
        self.min_touches = 2               # minimum 2 touches
        self.relevance_range = 0.10        # 10% จากราคาปัจจุบัน
        self.execution_buffer = 0.005      # 0.5% buffer for execution
        
    def find_pivot_points(self, highs, lows):
        """
        หา pivot points (จุดสูง/ต่ำ) จากข้อมูลราคา
        
        Returns:
            tuple: (resistance_candidates, support_candidates)
        """
        resistance_candidates = []
        support_candidates = []
        
        # ค้นหา pivot highs (แนวต้าน)
        for i in range(self.pivot_window, len(highs) - self.pivot_window):
            is_pivot_high = True
            current_high = highs[i]
            
            # ตรวจสอบว่าจุดนี้สูงกว่าจุดรอบๆ
            for j in range(i - self.pivot_window, i + self.pivot_window + 1):
                if j != i and highs[j] >= current_high:
                    is_pivot_high = False
                    break
            
            if is_pivot_high:
                resistance_candidates.append(current_high)
        
        # ค้นหา pivot lows (แนวรับ)
        for i in range(self.pivot_window, len(lows) - self.pivot_window):
            is_pivot_low = True
            current_low = lows[i]
            
            # ตรวจสอบว่าจุดนี้ต่ำกว่าจุดรอบๆ
            for j in range(i - self.pivot_window, i + self.pivot_window + 1):
                if j != i and lows[j] <= current_low:
                    is_pivot_low = False
                    break
            
            if is_pivot_low:
                support_candidates.append(current_low)
        
        return resistance_candidates, support_candidates
    
    def count_touches(self, price_list, level):
        """
        นับจำนวนครั้งที่ราคาแตะแนวรับ-แนวต้าน
        """
        touches = 0
        for price in price_list:
            if abs(price - level) / level <= self.touch_threshold:
                touches += 1
        return touches
    
    def filter_valid_levels(self, candidates, price_list, current_price, is_resistance=True):
        """
        กรองแนวรับ-แนวต้านที่ valid
        """
        valid_levels = []
        
        for level in candidates:
            # ตรวจสอบ relevance range
            if is_resistance:
                # แนวต้าน: ต้องสูงกว่าราคาปัจจุบันและไม่เกิน relevance_range
                if level > current_price * (1 + self.relevance_range):
                    continue
                if level < current_price * (1 + self.execution_buffer):
                    continue
            else:
                # แนวรับ: ต้องต่ำกว่าราคาปัจจุบันและไม่เกิน relevance_range
                if level < current_price * (1 - self.relevance_range):
                    continue
                if level > current_price * (1 - self.execution_buffer):
                    continue
            
            # นับ touches
            touches = self.count_touches(price_list, level)
            
            if touches >= self.min_touches:
                distance = abs(level - current_price) / current_price
                valid_levels.append({
                    'level': level,
                    'touches': touches,
                    'distance': distance
                })
        
        # เรียงตามจำนวน touches และระยะห่าง
        valid_levels.sort(key=lambda x: (x['touches'], -x['distance']), reverse=True)
        
        return [level['level'] for level in valid_levels[:3]]  # เอา 3 อันดับแรก
    
    def calculate_support_resistance(self, ohlcv_data, current_price):
        """
        คำนวณแนวรับ-แนวต้านจากข้อมูล OHLCV
        
        Args:
            ohlcv_data: ข้อมูล OHLCV [[timestamp, open, high, low, close, volume], ...]
            current_price: ราคาปัจจุบัน
            
        Returns:
            dict: {'support_levels': [...], 'resistance_levels': [...]}
        """
        try:
            if len(ohlcv_data) < self.lookback_period:
                print(f"⚠️ ข้อมูลไม่เพียงพอสำหรับ S/R: {len(ohlcv_data)} แท่ง (ต้องการ {self.lookback_period})")
                return {'support_levels': [], 'resistance_levels': []}
            
            # ใช้ข้อมูล lookback_period แท่งล่าสุด
            recent_data = ohlcv_data[-self.lookback_period:]
            
            # แปลงข้อมูล OHLCV
            highs = [float(candle[2]) for candle in recent_data]
            lows = [float(candle[3]) for candle in recent_data]
            
            # หา pivot points
            resistance_candidates, support_candidates = self.find_pivot_points(highs, lows)
            
            # กรองแนวรับ-แนวต้านที่ valid
            valid_resistance = self.filter_valid_levels(
                resistance_candidates, highs, current_price, is_resistance=True
            )
            valid_support = self.filter_valid_levels(
                support_candidates, lows, current_price, is_resistance=False
            )
            
            return {
                'support_levels': valid_support,
                'resistance_levels': valid_resistance
            }
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการคำนวณ S/R: {e}")
            return {'support_levels': [], 'resistance_levels': []}
    
    def calculate_smart_tp_sl(self, entry_price, side, support_levels, resistance_levels):
        """
        คำนวณ Smart TP/SL จากแนวรับ-แนวต้าน
        
        Args:
            entry_price: ราคา entry
            side: 'long' หรือ 'short'
            support_levels: list ของแนวรับ
            resistance_levels: list ของแนวต้าน
            
        Returns:
            dict: {'take_profit': price, 'stop_loss': price, 'method': 'smart/fallback'}
        """
        try:
            if side.lower() == 'long':
                return self._calculate_long_tp_sl(entry_price, support_levels, resistance_levels)
            else:  # SHORT
                return self._calculate_short_tp_sl(entry_price, support_levels, resistance_levels)
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการคำนวณ Smart TP/SL: {e}")
            return self._calculate_fallback_tp_sl(entry_price, side)
    
    def _calculate_long_tp_sl(self, entry_price, support_levels, resistance_levels):
        """คำนวณ TP/SL สำหรับ LONG position"""
        take_profit = None
        stop_loss = None
        
        # หา Take Profit จากแนวต้าน
        for resistance in resistance_levels:
            if resistance > entry_price * 1.02:  # อย่างน้อย 2% กำไร
                take_profit = resistance * (1 - self.execution_buffer)  # -0.5% buffer
                break
        
        # หา Stop Loss จากแนวรับ
        for support in support_levels:
            if support < entry_price * 0.98:  # อย่างมาก 2% ขาดทุน
                stop_loss = support * (1 - self.execution_buffer)  # -0.5% buffer
                break
        
        # ใช้ fallback ถ้าไม่พบ
        if take_profit is None:
            take_profit = entry_price * 1.15  # +15% fallback
            
        if stop_loss is None:
            stop_loss = entry_price * 0.95   # -5% fallback
        
        # ตรวจสอบ validation
        if take_profit <= entry_price or stop_loss >= entry_price:
            return self._calculate_fallback_tp_sl(entry_price, 'long')
        
        method = 'smart' if (take_profit != entry_price * 1.15 or stop_loss != entry_price * 0.95) else 'fallback'
        
        return {
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'method': method
        }
    
    def _calculate_short_tp_sl(self, entry_price, support_levels, resistance_levels):
        """คำนวณ TP/SL สำหรับ SHORT position"""
        take_profit = None
        stop_loss = None
        
        # หา Take Profit จากแนวรับ
        for support in support_levels:
            if support < entry_price * 0.98:  # อย่างน้อย 2% กำไร
                take_profit = support * (1 + self.execution_buffer)  # +0.5% buffer
                break
        
        # หา Stop Loss จากแนวต้าน
        for resistance in resistance_levels:
            if resistance > entry_price * 1.02:  # อย่างมาก 2% ขาดทุน
                stop_loss = resistance * (1 + self.execution_buffer)  # +0.5% buffer
                break
        
        # ใช้ fallback ถ้าไม่พบ
        if take_profit is None:
            take_profit = entry_price * 0.85  # -15% fallback
            
        if stop_loss is None:
            stop_loss = entry_price * 1.05   # +5% fallback
        
        # ตรวจสอบ validation
        if take_profit >= entry_price or stop_loss <= entry_price:
            return self._calculate_fallback_tp_sl(entry_price, 'short')
        
        method = 'smart' if (take_profit != entry_price * 0.85 or stop_loss != entry_price * 1.05) else 'fallback'
        
        return {
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'method': method
        }
    
    def _calculate_fallback_tp_sl(self, entry_price, side):
        """คำนวณ TP/SL แบบ fallback (percentage-based)"""
        if side.lower() == 'long':
            take_profit = entry_price * 1.15  # +15%
            stop_loss = entry_price * 0.95    # -5%
        else:  # SHORT
            take_profit = entry_price * 0.85  # -15%
            stop_loss = entry_price * 1.05    # +5%
        
        return {
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'method': 'fallback'
        }
    
    def get_smart_tp_sl_from_ohlcv(self, symbol, entry_price, side, ohlcv_data):
        """
        Main function: คำนวณ Smart TP/SL จากข้อมูล OHLCV
        
        Args:
            symbol: symbol ของเหรียญ
            entry_price: ราคา entry
            side: 'long' หรือ 'short'
            ohlcv_data: ข้อมูล OHLCV
            
        Returns:
            dict: {'take_profit': price, 'stop_loss': price, 'method': 'smart/fallback'}
        """
        print(f"🔍 คำนวณ Smart TP/SL สำหรับ {symbol} ({side.upper()})")
        
        # คำนวณแนวรับ-แนวต้าน
        sr_data = self.calculate_support_resistance(ohlcv_data, entry_price)
        support_levels = sr_data['support_levels']
        resistance_levels = sr_data['resistance_levels']
        
        print(f"📊 {symbol} - Support: {len(support_levels)} levels, Resistance: {len(resistance_levels)} levels")
        if support_levels:
            print(f"   📉 Support levels: {[f'{s:.6f}' for s in support_levels[:3]]}")
        if resistance_levels:
            print(f"   📈 Resistance levels: {[f'{r:.6f}' for r in resistance_levels[:3]]}")
        
        # คำนวณ Smart TP/SL
        result = self.calculate_smart_tp_sl(entry_price, side, support_levels, resistance_levels)
        
        print(f"🎯 Smart TP/SL ({result['method']}): TP={result['take_profit']:.6f}, SL={result['stop_loss']:.6f}")
        
        return result

if __name__ == "__main__":
    # ทดสอบ Smart TP/SL Calculator
    print("🧪 ทดสอบ Smart TP/SL Calculator...")
    
    calculator = SmartTPSLCalculator()
    
    # สร้างข้อมูลทดสอบ (fake OHLCV data)
    fake_ohlcv = []
    base_price = 50000
    
    # สร้างข้อมูล 50 แท่งเทียน
    for i in range(50):
        timestamp = 1640995200000 + (i * 3600000)  # 1 hour intervals
        
        # สร้างราคาที่มีแนวรับ-แนวต้าน
        if i % 10 == 0:  # resistance level
            high = base_price + 1000 + (i * 10)
            low = base_price - 500 + (i * 10)
        elif i % 5 == 0:  # support level  
            high = base_price + 500 + (i * 10)
            low = base_price - 1000 + (i * 10)
        else:
            high = base_price + 300 + (i * 10)
            low = base_price - 300 + (i * 10)
        
        open_price = (high + low) / 2
        close_price = open_price + (i % 3 - 1) * 100  # random variation
        volume = 100 + i
        
        fake_ohlcv.append([timestamp, open_price, high, low, close_price, volume])
    
    current_price = fake_ohlcv[-1][4]  # last close price
    
    print(f"💰 ราคาปัจจุบัน: {current_price:.2f}")
    
    # ทดสอบ LONG position
    print("\n📈 ทดสอบ LONG Position:")
    result_long = calculator.get_smart_tp_sl_from_ohlcv("TEST/USDT", current_price, "long", fake_ohlcv)
    
    # ทดสอบ SHORT position
    print("\n📉 ทดสอบ SHORT Position:")
    result_short = calculator.get_smart_tp_sl_from_ohlcv("TEST/USDT", current_price, "short", fake_ohlcv)
    
    print("\n✅ Smart TP/SL Calculator ทดสอบเสร็จสิ้น!")
