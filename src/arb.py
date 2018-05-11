from forex_python.converter import CurrencyRates
import ccxt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from time import sleep as sleep
import datetime
import contextlib


def get_zar_usd():
    CR = CurrencyRates().get_rate('USD', 'ZAR')
    return (CR)


def get_ticker_rates(ex=ccxt.bitstamp(), tickers=np.array(['BTC/USD', 'LTC/USD'])):
    rates = []
    for ticker in tickers:
        rate =ex.fetch_ticker(ticker)
        rates.append(rate.copy())
        rate.clear()
        sleep(2)
    return rates


def get_crypto_arb(bitstamp, luno, ice3x, AMT=30000,  plt_results=False, plt_rev_arb=False):
    CT = datetime.datetime.now()

    zarusd = get_zar_usd()
    usdzar = 1 / zarusd

    luno_tickers = np.array(['BTC/ZAR'])
    bitstamp_tickers = np.array(['BTC/USD', 'LTC/USD'])
    ice3x_tickers = np.array(['BTC/ZAR', 'LTC/ZAR'])

    #luno = ccxt.luno()
    #bitstamp = ccxt.bitstamp()
    #ice3x = ccxt.ice3x()

    luno_rates = get_ticker_rates(luno, luno_tickers)
    bitstamp_rates = get_ticker_rates(bitstamp, bitstamp_tickers)
    ice3x_rates = get_ticker_rates(ice3x, ice3x_tickers)

    luno_btc_arb = calc_arb(AMT, luno_rates[0]['bid'], bitstamp_rates[0]['ask'], usdzar)

    ice3x_btc_arb = calc_arb(AMT, ice3x_rates[0]['last'], bitstamp_rates[0]['ask'], usdzar)
    ice3x_ltc_arb = calc_arb(AMT, ice3x_rates[1]['last'], bitstamp_rates[1]['ask'], usdzar)

    luno_btc_revarb = calc_rev_arb(ASK=luno_rates[0]['ask'], BID=bitstamp_rates[0]['bid'], BASE=zarusd)
    ice3x_btc_revarb = calc_rev_arb(ASK=ice3x_rates[0]['last'], BID=bitstamp_rates[0]['bid'], BASE=zarusd)
    ice3x_ltc_revarb = calc_rev_arb(ASK=ice3x_rates[1]['last'], BID=bitstamp_rates[1]['bid'], BASE=zarusd)

    # print('The ARB ratio is: {}'.format(luno_btc_arb))
    # print luno_btc_arb, ice3x_btc_arb, ice3x_ltc_arb, luno_btc_revarb, ice3x_btc_revarb, ice3x_ltc_revarb

    if plt_results:
        AMT_VEC = range(0, 35000, 100)

        LUNO_BTC_VEC = [calc_arb(float(x), luno_rates[0]['bid'], bitstamp_rates[0]['ask'], usdzar) for x in AMT_VEC]
        ICE3X_BTC_VEC = [calc_arb(float(x), ice3x_rates[0]['last'], bitstamp_rates[0]['ask'], usdzar) for x in AMT_VEC]
        ICE3X_LTC_VEC = [calc_arb(float(x), ice3x_rates[1]['last'], bitstamp_rates[1]['ask'], usdzar) for x in AMT_VEC]

        ymax = np.max([luno_btc_arb, ice3x_btc_arb, ice3x_ltc_arb])
        ymin = np.min([luno_btc_arb, ice3x_btc_arb, ice3x_ltc_arb])

        plt.clf()
        plt.plot(AMT_VEC, LUNO_BTC_VEC)
        plt.plot(AMT_VEC, ICE3X_BTC_VEC)
        plt.plot(AMT_VEC, ICE3X_LTC_VEC)
        plt.axhline(y=0, color='dimgrey')
        plt.axvline(x=0, color='dimgrey')
        plt.legend(['LUNO_BTC: ' + str(np.round(luno_btc_arb * 100, 4)) + '%',
                    'ICE3X_BTC: ' + str(np.round(ice3x_btc_arb * 100, 4)) + '%',
                    'ICE3X_LTC: ' + str(np.round(ice3x_ltc_arb * 100, 4)) + '%'],
                   loc='lower right')
        plt.ylim((ymin - 0.03, ymax + 0.02))
        plt.text(35000 / 2, ymax + 0.015, str(CT.strftime('%Y-%m-%d %H:%M')), fontsize=12,
                 bbox=dict(facecolor='red', alpha=0.5), horizontalalignment='center',
                 verticalalignment='center')
        plt.title('ARB Comparison')
        plt.xlabel('ZAR')
        plt.ylabel('Arb %')
        plt.grid(which='both')
        # plt.show()
        plt.savefig('images/ARB.png')
        plt.close()

    if plt_rev_arb:
        AMT_VEC = range(0, 35000, 100)

        LUNO_BTC_REV_VEC = [calc_rev_arb(ASK=luno_rates[0]['ask'], BID=bitstamp_rates[0]['bid'], AMT=x, BASE=zarusd) for
                            x in AMT_VEC]
        ICE3X_BTC_REV_VEC = [calc_rev_arb(ASK=ice3x_rates[0]['last'], BID=bitstamp_rates[0]['bid'], AMT=x, BASE=zarusd)
                             for x in AMT_VEC]
        ICE3X_LTC_REV_VEC = [calc_rev_arb(ASK=ice3x_rates[1]['last'], BID=bitstamp_rates[1]['bid'], AMT=x, BASE=zarusd)
                             for x in AMT_VEC]

        ymax = np.max([luno_btc_revarb, ice3x_btc_revarb, ice3x_ltc_revarb])
        ymin = np.min([luno_btc_revarb, ice3x_btc_revarb, ice3x_ltc_revarb])

        plt.clf()
        plt.plot(AMT_VEC, LUNO_BTC_REV_VEC)
        plt.plot(AMT_VEC, ICE3X_BTC_REV_VEC)
        plt.plot(AMT_VEC, ICE3X_LTC_REV_VEC)
        plt.axhline(y=0, color='dimgray')
        plt.axvline(x=0, color='dimgray')
        plt.legend(['LUNO_BTC: ' + str(np.round(luno_btc_revarb * 100, 4)) + '%',
                    'ICE3X_BTC: ' + str(np.round(ice3x_btc_revarb * 100, 4)) + '%',
                    'ICE3X_LTC: ' + str(np.round(ice3x_ltc_revarb * 100, 4)) + '%'],
                   loc='lower right')
        plt.title('Reverse ARB Comparison')
        plt.text(35000 / 2, ymax + 0.015, str(CT.strftime('%Y-%m-%d %H:%M')), fontsize=12,
                 bbox=dict(facecolor='red', alpha=0.5), horizontalalignment='center',
                 verticalalignment='center')
        plt.xlabel('ZAR')
        plt.ylabel('Arb %')
        plt.ylim((ymin - 0.03, ymax + 0.02))
        plt.grid(which='both')
        # plt.show()
        plt.savefig('images/REV_ARB.png')
        plt.close()

    return luno_btc_arb, ice3x_btc_arb, ice3x_ltc_arb, luno_btc_revarb, ice3x_btc_revarb, ice3x_ltc_revarb, zarusd


def get_btc_rates():
    luno = ccxt.luno()
    bitstamp = ccxt.bitstamp()
    ice3x = ccxt.ice3x()

    luno_btc = luno.fetch_ticker('BTC/ZAR')
    bs_btc = bitstamp.fetch_ticker('BTC/USD')
    ice_btc = ice3x.fetch_ticker('BTC/ZAR')
    return luno_btc, bs_btc, ice_btc


def calc_diff(AMT, BID, ASK, BASE, PEN1=0.9998, PEN2=0.99, ZAR_WITHDRAW_COST=8.5, USD_DEP_COST=7.5):
    DIFF = PEN1 * PEN2 * BID * (BASE * AMT * (1 / ASK) - USD_DEP_COST * (1 / ASK)) - ZAR_WITHDRAW_COST
    return (DIFF)


def calc_arb(AMT, BID, ASK, BASE, PEN1=0.9998, PEN2=0.99, ZAR_WITHDRAW_COST=8.5, USD_DEP_COST=7.5):
    VAL = PEN1 * PEN2 * BID * (BASE * AMT * (1 / ASK) - USD_DEP_COST * (1 / ASK)) - ZAR_WITHDRAW_COST
    DIFF = VAL - AMT
    try:
        ARB = DIFF / AMT
    except:
        ARB = -1000
    return (ARB)


def calc_rev_arb(ASK, BID, AMT=10000.00, BASE=12.00, PEN=0.99):
    base_dollars = AMT / BASE
    bought = AMT * (1 / ASK) * BID * PEN * PEN * PEN
    diff = bought - base_dollars
    try:
        rev_arb = diff / base_dollars
    except:
        rev_arb = -1
    return (rev_arb)


def get_btc_arb(AMT=30000, graph=False):
    zarusd = get_zar_usd()
    usdzar = 1 / zarusd
    luno_btc, bs_btc, ice_btc = get_btc_rates()
    AMT_D = calc_diff(AMT, luno_btc['bid'], bs_btc['ask'], usdzar)
    DIFF = AMT_D - AMT
    ARB = DIFF / AMT
    rev_arb = calc_rev_arb(ASK=luno_btc['ask'], BID=bs_btc['bid'], BASE=zarusd)
    print('The ARB ratio is: {}'.format(ARB))

    if (graph):
        AMT_VEC = range(0, 55000, 1000)
        AMT_D_VEC = [calc_diff(float(x), luno_btc['bid'], bs_btc['ask'], usdzar) for x in AMT_VEC]
        DIFF_VEC = np.array(AMT_D_VEC) - np.array(AMT_VEC)
        ARB_VEC = DIFF_VEC / AMT_VEC

        # ARB2 = [calc_arb(x, BID = luno_btc['bid'], ASK=bs_btc['ask'], BASE=usdzar) for x in AMT_VEC]

        plt.plot(AMT_VEC, ARB_VEC)
        plt.ylim((-0.2, 0.2))
        # plt.plot(AMT_VEC, ARB2)
        # plt.savefig('images/ARB_BTC.png')
        plt.show()
    return ARB, zarusd, rev_arb


def plt_last_24_hours(db):
    CT = datetime.datetime.now()

    df = db.get_last_24_hours()
    df['time'] = pd.to_datetime(df['time'])
    df['time'] = df['time'].apply(lambda x: datetime.datetime.time(x))
    df = df.sort_values(by=['time'])
    minx = df['time'].min()
    maxx = df['time'].max()

    midx = datetime.time(hour=minx.hour + (maxx.hour-minx.hour)/2,minute = minx.minute + (maxx.minute-minx.minute)/2 )

    miny = df[['luno_btc_arb','luno_btc_revarb']].min().min()
    maxy = df[['luno_btc_arb', 'luno_btc_revarb']].max().max()

    plt.clf()
    arbplt, = plt.plot(df['time'], df['luno_btc_arb'])
    plt.plot(df['time'], df['luno_btc_arb'], 'p', label=None)

    revarbplt, = plt.plot(df['time'], df['luno_btc_revarb'])
    plt.plot(df['time'], df['luno_btc_revarb'], 'p', label=None)

    plt.axhline(y=0, color='dimgray')
    plt.text(midx, maxy + 0.012, str(CT.strftime('%Y-%m-%d %H:%M')), fontsize=12,
             bbox=dict(facecolor='red', alpha=0.5), horizontalalignment='center',
             verticalalignment='center')
    plt.ylim((miny - 0.025, maxy + 0.025))
    plt.xlabel('Time')
    plt.ylabel('ARB')
    plt.legend([arbplt, revarbplt],['ARB','REV ARB'])
    plt.grid(which='both')

    # plt.show()
    plt.savefig('images/LAST_24.png')

    plt.close()
