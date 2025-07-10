#!/usr/bin/env python3
"""
ทดสอบการสร้างโครงสร้างโฟลเดอร์อัตโนมัติ
"""

import os
from linear_regression_detector import ensure_all_required_folders, create_sample_log_structure, create_readme_files

def test_folder_structure():
    """ทดสอบการสร้างโครงสร้างโฟลเดอร์"""
    print("🧪 ทดสอบการสร้างโครงสร้างโฟลเดอร์อัตโนมัติ")
    print("="*60)
    
    # ลบโฟลเดอร์ทดสอบถ้ามี
    test_folders = ["test_temp", "test_logs", "test_configs"]
    for folder in test_folders:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
    
    print("🔧 สร้างโครงสร้างโฟลเดอร์ทั้งหมด...")
    cache_file = ensure_all_required_folders()
    create_sample_log_structure()
    create_readme_files()
    
    print("\n📁 ตรวจสอบโฟลเดอร์ที่สร้างแล้ว:")
    required_folders = [
        "historical_data_cache",
        "historical_data", 
        "logs",
        "backups",
        "temp",
        "models",
        "configs",
        "reports"
    ]
    
    for folder in required_folders:
        if os.path.exists(folder):
            files_count = len(os.listdir(folder))
            print(f"  ✅ {folder} ({files_count} ไฟล์)")
        else:
            print(f"  ❌ {folder} (ไม่มี)")
    
    print("\n📄 ตรวจสอบไฟล์ config:")
    config_files = [
        "configs/trading_config.json",
        "configs/symbols_config.json", 
        "configs/ai_config.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            size = os.path.getsize(config_file)
            print(f"  ✅ {config_file} ({size} bytes)")
        else:
            print(f"  ❌ {config_file} (ไม่มี)")
    
    print("\n📝 ตรวจสอบไฟล์ log:")
    log_files = [
        "logs/trading.log",
        "logs/ai_analysis.log",
        "logs/errors.log", 
        "logs/performance.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"  ✅ {log_file} ({size} bytes)")
        else:
            print(f"  ❌ {log_file} (ไม่มี)")
    
    print("\n📖 ตรวจสอบไฟล์ README:")
    readme_files = [
        "historical_data_cache/README.md",
        "logs/README.md",
        "configs/README.md",
        "reports/README.md"
    ]
    
    for readme_file in readme_files:
        if os.path.exists(readme_file):
            size = os.path.getsize(readme_file)
            print(f"  ✅ {readme_file} ({size} bytes)")
        else:
            print(f"  ❌ {readme_file} (ไม่มี)")
    
    print(f"\n📊 ไฟล์ข้อมูลทดสอบ: {cache_file}")
    if os.path.exists(cache_file):
        size = os.path.getsize(cache_file)
        print(f"  ✅ ขนาด: {size} bytes")
        
        # แสดงจำนวนข้อมูล
        import json
        with open(cache_file, 'r') as f:
            data = json.load(f)
        print(f"  📈 จำนวนแท่งเทียน: {len(data)}")
    else:
        print(f"  ❌ ไม่พบไฟล์")
    
    print("\n✅ การทดสอบเสร็จสิ้น!")
    print("🎯 ระบบสามารถสร้างโครงสร้างโฟลเดอร์อัตโนมัติได้สมบูรณ์")

if __name__ == "__main__":
    test_folder_structure()
