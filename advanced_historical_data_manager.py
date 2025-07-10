#!/usr/bin/env python3
"""
Historical Data Manager - Advanced Version
จัดการข้อมูล OHLCV ย้อนหลังของเหรียญต่างๆ แบบ Local Storage
- ตรวจสอบและสร้าง JSON files สำหรับแต่ละเหรียญ
- อัปเดตข้อมูลให้เป็นปัจจุบันก่อนวิเคราะห์
- ไม่มี rate limit เพื่อความเร็วสูงสุด
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import ccxt
from pathlib import Path

class AdvancedHistoricalDataManager:
    """Advanced Historical Data Manager with local JSON storage"""
    
    def __init__(self, exchange_client, data_dir: str = "historical_data_cache"):
        """Initialize with exchange client and data directory"""
        self.exchange_client = exchange_client
        self.exchange = exchange_client.exchange if exchange_client else None
        self.data_dir = Path(data_dir)
        
        # สร้างโฟลเดอร์สำหรับเก็บข้อมูล
        self.data_dir.mkdir(exist_ok=True)
        
        # กำหนดจำนวน timeframes ที่ต้องการ (120 สำหรับ LRC analysis)
        self.required_timeframes = 120
        self.timeframe = '1h'
        
        print(f"📊 Advanced Historical Data Manager เริ่มต้นแล้ว")
        print(f"📁 ข้อมูลจะถูกเก็บใน: {self.data_dir.absolute()}")
        print(f"⏰ ดึงข้อมูล: {self.required_timeframes} timeframes ({self.timeframe})")
    
    def get_data_file_path(self, symbol: str) -> Path:
        """สร้าง path สำหรับไฟล์ข้อมูลของเหรียญ"""
        safe_symbol = symbol.replace('/', '_').replace(':', '_')
        return self.data_dir / f"{safe_symbol}_{self.timeframe}.json"
    
    def load_existing_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """โหลดข้อมูลที่มีอยู่จากไฟล์ JSON"""
        file_path = self.get_data_file_path(symbol)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"    ⚠️ ไม่สามารถอ่านไฟล์ {file_path}: {e}")
            return None
    
    def save_data_to_file(self, symbol: str, ohlcv_data: List[List], metadata: Dict[str, Any] = None):
        """บันทึกข้อมูลลงไฟล์ JSON"""
        file_path = self.get_data_file_path(symbol)
        
        # สร้างข้อมูลที่จะบันทึก
        data_to_save = {
            'symbol': symbol,
            'timeframe': self.timeframe,
            'last_update': datetime.now().isoformat(),
            'total_records': len(ohlcv_data),
            'data': ohlcv_data,
            'metadata': metadata or {}
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2)
            return True
        except Exception as e:
            print(f"    ❌ ไม่สามารถบันทึกไฟล์ {file_path}: {e}")
            return False
    
    def get_latest_timestamp_from_data(self, ohlcv_data: List[List]) -> Optional[int]:
        """หา timestamp ล่าสุดจากข้อมูล OHLCV"""
        if not ohlcv_data:
            return None
        
        # ข้อมูล OHLCV format: [timestamp, open, high, low, close, volume]
        return max(candle[0] for candle in ohlcv_data)
    
    def calculate_missing_timeframes(self, latest_timestamp: int) -> int:
        """คำนวณจำนวน timeframes ที่ขาดหายไป"""
        now = datetime.now()
        latest_time = datetime.fromtimestamp(latest_timestamp / 1000)
        
        # คำนวณความต่างเป็นชั่วโมง
        time_diff = now - latest_time
        hours_diff = int(time_diff.total_seconds() / 3600)
        
        # ต้องการข้อมูลอย่างน้อย 1 timeframe ใหม่
        return max(1, hours_diff)
    
    def fetch_fresh_data(self, symbol: str, limit: int = None) -> Optional[List[List]]:
        """ดึงข้อมูลใหม่จาก Binance API"""
        if not self.exchange:
            print(f"    ❌ ไม่มี exchange client")
            return None
        
        try:
            limit = limit or self.required_timeframes
            print(f"    📊 ดึงข้อมูลใหม่จาก API: {limit} timeframes...")
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, self.timeframe, limit=limit)
            
            if ohlcv and len(ohlcv) > 0:
                print(f"    ✅ ได้ข้อมูลใหม่: {len(ohlcv)} records")
                return ohlcv
            else:
                print(f"    ❌ ไม่ได้ข้อมูลจาก API")
                return None
                
        except Exception as e:
            print(f"    ❌ ข้อผิดพลาดในการดึงข้อมูล: {e}")
            return None
    
    def fetch_incremental_data(self, symbol: str, since_timestamp: int, limit: int) -> Optional[List[List]]:
        """ดึงข้อมูลเพิ่มเติมตั้งแต่ timestamp ที่กำหนด"""
        if not self.exchange:
            return None
        
        try:
            print(f"    📊 ดึงข้อมูลเพิ่มเติม: {limit} timeframes ตั้งแต่ {datetime.fromtimestamp(since_timestamp/1000)}")
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, self.timeframe, since=since_timestamp, limit=limit)
            
            if ohlcv and len(ohlcv) > 0:
                print(f"    ✅ ได้ข้อมูลเพิ่มเติม: {len(ohlcv)} records")
                return ohlcv
            else:
                return None
                
        except Exception as e:
            print(f"    ❌ ข้อผิดพลาดในการดึงข้อมูลเพิ่มเติม: {e}")
            return None
    
    def merge_ohlcv_data(self, existing_data: List[List], new_data: List[List]) -> List[List]:
        """รวมข้อมูลเก่าและใหม่ โดยไม่ให้ซ้ำกัน"""
        if not existing_data:
            return new_data
        
        if not new_data:
            return existing_data
        
        # สร้าง dict จาก existing data สำหรับเช็ค timestamp ที่ซ้ำ
        existing_timestamps = {candle[0]: candle for candle in existing_data}
        
        # เพิ่มข้อมูลใหม่ที่ไม่ซ้ำ
        for candle in new_data:
            timestamp = candle[0]
            existing_timestamps[timestamp] = candle  # อัปเดตถ้ามีแล้ว หรือเพิ่มใหม่
        
        # เรียงลำดับตาม timestamp และเอาแค่จำนวนที่ต้องการ
        merged_data = sorted(existing_timestamps.values(), key=lambda x: x[0])
        
        # เก็บแค่ required_timeframes ล่าสุด
        if len(merged_data) > self.required_timeframes:
            merged_data = merged_data[-self.required_timeframes:]
        
        return merged_data
    
    def get_updated_historical_data(self, symbol: str) -> Optional[List[List]]:
        """
        หลักฟังก์ชัน: ดึงข้อมูลประวัติศาสตร์ที่อัปเดตแล้วสำหรับเหรียญ
        
        ขั้นตอน:
        1. ตรวจสอบไฟล์ JSON ที่มีอยู่
        2. ถ้าไม่มี -> ดึงข้อมูลใหม่ทั้งหมด
        3. ถ้ามีแล้ว -> ตรวจสอบความเป็นปัจจุบัน
        4. อัปเดตข้อมูลที่ขาดหายไป
        5. คืนค่าข้อมูลที่พร้อมใช้
        """
        print(f"    🔍 กำลังเตรียมข้อมูลประวัติศาสตร์สำหรับ {symbol}...")
        
        # ขั้นตอนที่ 1: ตรวจสอบไฟล์ที่มีอยู่
        existing_data_file = self.load_existing_data(symbol)
        
        if not existing_data_file:
            # ขั้นตอนที่ 2: ไม่มีไฟล์ -> ดึงข้อมูลใหม่ทั้งหมด
            print(f"    📁 ไม่พบไฟล์ข้อมูลสำหรับ {symbol} -> ดึงข้อมูลใหม่")
            fresh_data = self.fetch_fresh_data(symbol, self.required_timeframes)
            
            if fresh_data:
                # บันทึกข้อมูลใหม่
                if self.save_data_to_file(symbol, fresh_data):
                    print(f"    ✅ สร้างไฟล์ข้อมูลใหม่: {len(fresh_data)} records")
                    return fresh_data
                else:
                    print(f"    ❌ ไม่สามารถบันทึกไฟล์ข้อมูล")
                    return fresh_data  # คืนค่าข้อมูลแม้บันทึกไม่ได้
            else:
                print(f"    ❌ ไม่สามารถดึงข้อมูลใหม่ได้")
                return None
        
        # ขั้นตอนที่ 3: มีไฟล์แล้ว -> ตรวจสอบความเป็นปัจจุบัน
        existing_ohlcv = existing_data_file.get('data', [])
        
        if not existing_ohlcv:
            print(f"    ⚠️ ไฟล์ข้อมูลว่างเปล่า -> ดึงข้อมูลใหม่")
            fresh_data = self.fetch_fresh_data(symbol, self.required_timeframes)
            if fresh_data:
                self.save_data_to_file(symbol, fresh_data)
                return fresh_data
            return None
        
        # หา timestamp ล่าสุดจากข้อมูลที่มี
        latest_timestamp = self.get_latest_timestamp_from_data(existing_ohlcv)
        
        if not latest_timestamp:
            print(f"    ⚠️ ไม่สามารถหา timestamp ล่าสุด -> ดึงข้อมูลใหม่")
            fresh_data = self.fetch_fresh_data(symbol, self.required_timeframes)
            if fresh_data:
                self.save_data_to_file(symbol, fresh_data)
                return fresh_data
            return existing_ohlcv
        
        # ขั้นตอนที่ 4: คำนวณข้อมูลที่ขาดหายไป
        missing_timeframes = self.calculate_missing_timeframes(latest_timestamp)
        
        if missing_timeframes <= 1:
            print(f"    ✅ ข้อมูลเป็นปัจจุบันแล้ว ({len(existing_ohlcv)} records)")
            return existing_ohlcv
        
        print(f"    🔄 ข้อมูลล้าสมัย {missing_timeframes} timeframes -> อัปเดต")
        
        # ดึงข้อมูลเพิ่มเติม
        since_timestamp = latest_timestamp + (60 * 60 * 1000)  # +1 hour in milliseconds
        new_data = self.fetch_incremental_data(symbol, since_timestamp, missing_timeframes + 5)  # +5 buffer
        
        if new_data:
            # รวมข้อมูลเก่าและใหม่
            updated_data = self.merge_ohlcv_data(existing_ohlcv, new_data)
            
            # บันทึกข้อมูลที่อัปเดตแล้ว
            if self.save_data_to_file(symbol, updated_data):
                print(f"    ✅ อัปเดตข้อมูลสำเร็จ: {len(updated_data)} records (เพิ่ม {len(new_data)} records)")
            else:
                print(f"    ⚠️ อัปเดตข้อมูลได้แต่บันทึกไฟล์ไม่สำเร็จ")
            
            return updated_data
        else:
            print(f"    ⚠️ ไม่สามารถดึงข้อมูลเพิ่มเติมได้ -> ใช้ข้อมูลเก่า")
            return existing_ohlcv
    
    def cleanup_old_files(self, days_old: int = 7):
        """ลบไฟล์ข้อมูลที่เก่ามากเกินไป"""
        print(f"🧹 ล้างไฟล์ข้อมูลที่เก่ากว่า {days_old} วัน...")
        
        cutoff_time = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        for file_path in self.data_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            except Exception as e:
                print(f"    ⚠️ ไม่สามารถลบไฟล์ {file_path}: {e}")
        
        if deleted_count > 0:
            print(f"✅ ลบไฟล์เก่า {deleted_count} ไฟล์")
        else:
            print(f"✅ ไม่มีไฟล์เก่าที่ต้องลบ")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """แสดงสถิติของ cache"""
        json_files = list(self.data_dir.glob("*.json"))
        total_files = len(json_files)
        total_size = sum(f.stat().st_size for f in json_files)
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.data_dir.absolute())
        }
    
    def print_cache_stats(self):
        """แสดงสถิติ cache"""
        stats = self.get_cache_stats()
        print(f"📊 สถิติ Historical Data Cache:")
        print(f"    📁 ไฟล์ทั้งหมด: {stats['total_files']} ไฟล์")
        print(f"    💾 ขนาดรวม: {stats['total_size_mb']} MB")
        print(f"    📂 ตำแหน่ง: {stats['cache_dir']}")
