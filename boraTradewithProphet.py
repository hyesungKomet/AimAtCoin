import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

access = "your-access"
secret = "your-secret"
coin = "KRW-BORA"


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


predicted_close_price = 0


def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=500)
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds', 'y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] ==
                       forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] ==
                           data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue


predict_price(coin)
schedule.every().hour.do(lambda: predict_price(coin))

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
buy_price = 0

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(coin)
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price(coin, 0.3)
            current_price = get_current_price(coin)
            if target_price < current_price and current_price < predicted_close_price:
                krw = get_balance("KRW")
                if krw > 10000:
                    buy_price = upbit.buy_market_order(coin, krw*0.5)

                elif krw > 2000:
                    buy_price = upbit.buy_market_order(coin, krw*0.999)

            # 3%이상의 수익을 봤을 때는 매도
            if buy_price * 1.03 <= current_price:
                upbit.sell_market_order(coin, get_balance("BORA"))

        else:
            btc = get_balance("BORA")
            if btc > 5:
                upbit.sell_market_order(coin, btc)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
