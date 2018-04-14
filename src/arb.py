from forex_python.converter import CurrencyRates
import ccxt
import matplotlib.pyplot as plt
import numpy as np

def get_zar_usd():
    c = CurrencyRates()
    return(c.get_rate('USD','ZAR'))

def get_btc_rates():
    luno = ccxt.luno()
    bitstamp = ccxt.bitstamp()
    ice3x = ccxt.ice3x()
    luno_btc = luno.fetch_ticker('BTC/ZAR')
    bs_btc = bitstamp.fetch_ticker('BTC/USD')
    ice_btc = ice3x.fetch_ticker('BTC/ZAR')
    return luno_btc, bs_btc, ice_btc

def calc_diff(AMT, BID, ASK, BASE, PEN1 = 0.9998, PEN2 = 0.99, ZAR_WITHDRAW_COST = 8.5, USD_DEP_COST = 7.5):
    DIFF = PEN1 * PEN2* BID * (BASE * AMT * (1 / ASK) - USD_DEP_COST* (1 / ASK)) - ZAR_WITHDRAW_COST
    return(DIFF)

def get_btc_arb(AMT = 30000, graph = False):

    zarusd = get_zar_usd()
    usdzar = 1/zarusd
    luno_btc, bs_btc, ice_btc = get_btc_rates()
    AMT_D = calc_diff(AMT, luno_btc['bid'], bs_btc['ask'], usdzar)
    DIFF = AMT_D-AMT
    ARB = DIFF/AMT

    if(graph):
        AMT_VEC = range(0, 55000, 1000)
        AMT_D_VEC = [calc_diff(x, luno_btc['bid'], bs_btc['ask'], usdzar) for x in AMT_VEC]
        DIFF_VEC = np.array(AMT_D_VEC) - np.array(AMT_VEC)
        ARB_VEC = DIFF_VEC / AMT_VEC
        plt.plot(AMT_VEC, ARB_VEC)
        plt.savefig('images/ARB_BTC')
    return(ARB)
