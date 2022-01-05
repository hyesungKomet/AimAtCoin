import pyupbit
import numpy as np


def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-BTC")
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    #fee = 0.0032
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],  # - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror


kdict = {}
for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    kdict[k] = ror
    #print("%.1f %f" % (k, ror))
print(kdict)
for key, value in kdict.items():
    if value == max(kdict.values()):
        k = key
print(k)
