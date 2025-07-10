# Historical Data Cache

โฟลเดอร์นี้เก็บข้อมูล OHLCV ที่ดึงมาจาก Exchange

## โครงสร้างไฟล์:
- `{SYMBOL}_USDT_{TIMEFRAME}.json` - ข้อมูล OHLCV ของเหรียญแต่ละตัว

## รูปแบบข้อมูล:
```json
[
  [timestamp, open, high, low, close, volume],
  ...
]
```
