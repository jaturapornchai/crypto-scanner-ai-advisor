
import os
import ccxt
from dotenv import load_dotenv

class ExchangeClient:
    """Class สำหรับจัดการการเชื่อมต่อ Binance Futures"""
    
    def __init__(self):
        """Initialize CCXT Binance Futures connection"""
        load_dotenv()
        
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_SECRET_KEY')
        self.use_testnet = os.getenv('USE_TESTNET', 'false').lower() == 'true'
        
        if not self.api_key or not self.api_secret:
            raise ValueError("❌ กรุณาตั้งค่า BINANCE_API_KEY และ BINANCE_SECRET_KEY ใน .env")
        
        # เชื่อมต่อ Binance Futures ด้วย CCXT
        self.exchange = ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'sandbox': self.use_testnet,
            'options': {
                'defaultType': 'future',  # ใช้ futures trading
                'warnOnFetchOpenOrdersWithoutSymbol': False,  # ปิด warning
            },
        })
        
        # โหลด markets
        self.exchange.load_markets()
        print(f"🚀 เชื่อมต่อ Binance Futures สำเร็จ!")
        mode = 'Testnet' if self.use_testnet else '💰 LIVE TRADING (เงินจริง)'
        print(f"📊 Mode: {mode}")
        
        if not self.use_testnet:
            print("⚠️  ระบบกำลังใช้เงินจริงในการเทรด!")
            print("⚠️  System is using REAL MONEY for trading!")
    
    def get_exchange(self):
        """ส่งคืน exchange object"""
        return self.exchange
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ"""
        try:
            balance = self.exchange.fetch_balance()
            total_balance = balance['USDT']['total'] if 'USDT' in balance else 0
            print(f"💰 USDT Balance: {total_balance:,.2f} USDT")
            return True
        except Exception as e:
            print(f"❌ การเชื่อมต่อล้มเหลว: {e}")
            return False
