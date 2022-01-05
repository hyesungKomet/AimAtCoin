import pyupbit
import numpy as np

# ohlcv: open high low close volumn -> 당일 시가 고가 저가 종가 거래량 데이터
# count=7: 7일 동안의 ohlcv!
df = pyupbit.get_ohlcv("KRW-BTC", count=7)
print(df)

# 변동성 돌파 기준 범위 계산: (고가-저가) * k값(처음에는 0.5로 잡음)
df['range'] = (df['high'] - df['low']) * 0.5
# 타겟이 되는 가격은 당일 시가에 전날의 변동폭 * k값 -> 해당하면 매수 진행
df['target'] = df['open'] + df['range'].shift(1)

# fee = 0.0032   #수수료 일단 제외
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'],  # - fee,
                     1)
# numpy의 where(조건문, 참일 때의 값, 거짓일 때의 값)
# 고가가 타겟값보다 높다면 참이므로 수익률은 종가 / 타겟값이고 낮다면 거짓이므로 수익률은 그대로 1

df['hpr'] = df['ror'].cumprod()  # 누적곱계산 -> 누적수익률

# Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

# MDD 계산(Max Draw Down)
print("MDD(%): ", df['dd'].max())
df.to_excel("dd.xlsx")
