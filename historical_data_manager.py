"""
Historical Data Manager - จัดการข้อมูลย้อนหลังและ Chart Pattern Analysis
โมดูลสำหรับจัดเก็บข้อมูล OHLCV และลดการใช้ Binance API
"""

import os
import json
import ccxt
from datetime import datetime, timedelta
from pathlib import Path

class HistoricalDataManager:
    """Class สำหรับจัดการข้อมูลย้อนหลังและประหยัด API"""
    
    def __init__(self, exchange):
        """Initialize Historical Data Manager"""
        self.exchange = exchange
        self.base_path = Path("historical_data")
        self.symbols_path = self.base_path / "symbols"
        self.patterns_path = self.base_path / "patterns"
        self.analysis_path = self.base_path / "analysis"
        self.cache_path = self.base_path / "cache"
        
        # สร้าง folders อัตโนมัติ
        self._create_folders()
        
        # โหลด API usage tracking
        self.api_usage = self._load_api_usage()
        
        print("📁 Historical Data Manager พร้อมใช้งาน")
    
    def _create_folders(self):
        """สร้าง folders อัตโนมัติถ้าไม่มี"""
        for path in [self.base_path, self.symbols_path, self.patterns_path, 
                     self.analysis_path, self.cache_path]:
            path.mkdir(exist_ok=True)
        print("📁 สร้าง folders อัตโนมัติเรียบร้อย")
    
    def _load_api_usage(self):
        """โหลดข้อมูลการใช้ API"""
        usage_file = self.analysis_path / "api_usage.json"
        today = datetime.now().strftime("%Y-%m-%d")
        
        if usage_file.exists():
            with open(usage_file, 'r') as f:
                data = json.load(f)
                if data.get("date") == today:
                    return data
        
        # สร้างใหม่สำหรับวันนี้
        return {
            "date": today,
            "total_calls": 0,
            "calls_by_symbol": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "efficiency_rate": "0%"
        }
    
    def _save_api_usage(self):
        """บันทึกข้อมูลการใช้ API"""
        usage_file = self.analysis_path / "api_usage.json"
        
        # คำนวณ efficiency rate
        total = self.api_usage["cache_hits"] + self.api_usage["cache_misses"]
        if total > 0:
            efficiency = (self.api_usage["cache_hits"] / total) * 100
            self.api_usage["efficiency_rate"] = f"{efficiency:.1f}%"
        
        with open(usage_file, 'w') as f:
            json.dump(self.api_usage, f, indent=2)
    
    def get_ohlcv_data(self, symbol, timeframe, limit=1000):
        """ดึงข้อมูล OHLCV พร้อม Smart Caching"""
        try:
            # แปลง symbol format
            clean_symbol = symbol.replace("/", "").replace(":USDT", "")
            filename = f"{clean_symbol}_{timeframe}.json"
            file_path = self.symbols_path / filename
            
            # เช็คข้อมูลที่มีอยู่
            current_time = datetime.now()
            cache_valid = False
            existing_data = None
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
                
                # เช็ค cache validity (1 ชั่วโมง)
                last_update = datetime.fromisoformat(existing_data.get("last_update", "2000-01-01T00:00:00"))
                cache_valid = (current_time - last_update).total_seconds() < 3600
                
                if cache_valid:
                    self.api_usage["cache_hits"] += 1
                    self._save_api_usage()
                    print(f"📊 ใช้ cache สำหรับ {symbol} {timeframe}")
                    return existing_data["data"][-limit:]  # คืนข้อมูลล่าสุด
            
            # ดึงข้อมูลใหม่จาก API
            print(f"📡 ดึงข้อมูล {symbol} {timeframe} จาก Binance API")
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # อัปเดต API usage
            self.api_usage["cache_misses"] += 1
            self.api_usage["total_calls"] += 1
            symbol_key = clean_symbol
            self.api_usage["calls_by_symbol"][symbol_key] = self.api_usage["calls_by_symbol"].get(symbol_key, 0) + 1
            
            # เตรียมข้อมูลสำหรับบันทึก
            data_to_save = {
                "symbol": clean_symbol,
                "timeframe": timeframe,
                "last_update": current_time.isoformat(),
                "last_api_call": current_time.isoformat(),
                "data_source": "binance_api",
                "cache_valid_until": (current_time + timedelta(hours=1)).isoformat(),
                "total_candles": len(ohlcv),
                "api_calls_today": self.api_usage["calls_by_symbol"].get(symbol_key, 0),
                "data": ohlcv
            }
            
            # บันทึกข้อมูล
            with open(file_path, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            self._save_api_usage()
            
            return ohlcv
            
        except Exception as e:
            print(f"❌ Error getting OHLCV for {symbol}: {e}")
            return []
    
    def save_pattern_analysis(self, symbol, analysis_result):
        """บันทึกผลการวิเคราะห์ Chart Pattern"""
        try:
            clean_symbol = symbol.replace("/", "").replace(":USDT", "")
            filename = f"{clean_symbol}_patterns.json"
            file_path = self.patterns_path / filename
            
            # โหลดข้อมูลเดิม
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {"symbol": clean_symbol, "analyses": []}
            
            # เพิ่มผลการวิเคราะห์ใหม่
            analysis_entry = {
                "timestamp": datetime.now().isoformat(),
                **analysis_result
            }
            data["analyses"].append(analysis_entry)
            
            # เก็บเฉพาะ 100 records ล่าสุด
            if len(data["analyses"]) > 100:
                data["analyses"] = data["analyses"][-100:]
            
            # บันทึก
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            print(f"❌ Error saving pattern analysis for {symbol}: {e}")
    
    def get_pattern_history(self, symbol):
        """ดึงประวัติการวิเคราะห์ Pattern"""
        try:
            clean_symbol = symbol.replace("/", "").replace(":USDT", "")
            filename = f"{clean_symbol}_patterns.json"
            file_path = self.patterns_path / filename
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                return data.get("analyses", [])
            
            return []
            
        except Exception as e:
            print(f"❌ Error loading pattern history for {symbol}: {e}")
            return []
    
    def get_api_stats(self):
        """ดึงสถิติการใช้ API"""
        return self.api_usage
