import pyupbit

access = "your key"          # 본인 값으로 변경
secret = "your key"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-APENFT"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회

from pyupbit import WebSocketManager

if __name__ == "__main__":
    wm = WebSocketManager("ticker", ["KRW-BTC"])
    for i in range(10):
        data = wm.get()
        print(data)
    wm.terminate()
