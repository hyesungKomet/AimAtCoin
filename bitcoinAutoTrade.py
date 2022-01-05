import time
import pyupbit
import datetime
import requests

access = "your key"
secret = "your key"
myToken = "your slack key"
coin = "KRW-BTC"


def post_message(token, channel, text):
    # 슬랙 메세지 전송
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "bearer" + token},
                             data={"channel": channel, "text": text}
                             )


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + \
        (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_ma15(ticker):
    # 15일 이동 평균선 조회
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15


def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


def get_ror(k=0.5):
    df = pyupbit.get_ohlcv(coin)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    #fee = 0.0032
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],  # - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror


def get_bestk():
    kdict = {}
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k)
        kdict[k] = ror
        #print("%.1f %f" % (k, ror))
    # print(kdict)
    for key, value in kdict.items():
        if value == max(kdict.values()):
            k = key
    print("k value: " + str(k))
    return k


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken, "#auto-coin-trade", "autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()  # 현재 시간
        start_time = get_start_time(coin)  # 시작시간 9:00
        end_time = start_time + datetime.timedelta(days=1)  # 9:00 + 1일

        # 8:59:50초
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price(coin, get_bestk())
            post_message(myToken, "#auto-coin-trade",
                         "best k: "+str(get_bestk()))
            ma15 = get_ma15(coin)
            current_price = get_current_price(coin)
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order(coin, krw*0.9995)
                    post_message(myToken, "#auto-coin-trade",
                                 "BTC buy: "+str(buy_result))
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order(coin, btc*0.9995)
                post_message(myToken, "#auto-coin-trade",
                             "BTC sell: "+str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken, "#auto-coin-trade", e)
        time.sleep(1)
