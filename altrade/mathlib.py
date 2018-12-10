#coding=gbk

import numpy as np
import pandas as pd
#from stockdata import *
from scipy import stats

## TODO 1, complete the unittest by fix date range and replace print with assert equels !
## TODO 2 ,  add the method : MovingAverage_ rolling_windows, using pd.rolling_windows()


def rolling_ma(values, win_size):
    #print("========>", type(values))
    assert len(
        values) >= win_size  # assert that have enough elements to caculate average
    #print("rolling values", values[0:4])
    valseries = pd.Series(values)
    ma = pd.rolling_mean(valseries, win_size)
    #print(valseries[:6])
    #print(type(ma.values))
    return ma.values[win_size - 1:]  # first servals is Nan, must take off


def getEMAs(dailyList, Ndays):
    """ get EMA on CLOSE of daily list   CLOSE= 4  VOL=6"""
    EMA_np = np.array([])
    #dailyList = self.getColumnArray(4)/100.0
    #print dailyList
    EMA_np = caculateEMAs(dailyList, Ndays)
    return EMA_np


def caculateEMAs(dataList, Ndays):
    """ get EMA on data list ,return number of values equals Length-Ndays """
    EMAList = np.array([])
    dataLength = len(dataList)
    #EMA =MAlatest = round(np.mean(dataList[:Ndays]),2)
    #EMA =MAlatest = dataList[Ndays-1]  #first ema = previous Close
    prevNdays_tot = sum(dataList[:Ndays - 1])
    ndays = len(dataList[:Ndays - 1])  #first ema = previous Close
    EMA = 1.0 * prevNdays_tot / ndays  # use an average for first ema
    K = round(1.0 / (Ndays + 1), 4)
    EMAList = np.append(EMAList, EMA)
    for i in range(Ndays, dataLength):
        #todayClose, preClose = dataList[i], dataList[i - 1]
        #EMA = (2.0*dataList[i]+EMA*(Ndays-1))*K
        EMA = 2.0 * (dataList[i] - EMA) * K + EMA
        #EMA = 2.0*K*(todayClose+preClose)+(1-2*K)*EMA
        EMAList = np.append(EMAList, EMA)
    #EMAList.append(EMA)
    return np.round(EMAList, 2)


def MACD(dataList, lastN):
    """ caculate MACD  , return last N values"""
    print("Math module MACD ------yep!!")
    ema26 = getEMAs(dataList, 26)
    ema12 = getEMAs(dataList, 12)
    #print "ema12" ,ema12
    length = len(ema26)  # make its same shape
    DIF = ema12[-1 * length:] - ema26
    #DEA =  self.caculateEMAs(DIF,9)
    DEA = caculateEMAs(DIF, 9)
    length = len(DEA)
    MACD = (DIF[-1 * length:] - DEA) * 2  #BAR
    if length > lastN:
        MACD_np = np.vstack([DIF[-1 * lastN:], DEA[-1 * lastN:], MACD[-1 *
                                                                      lastN:]])
    else:
        MACD_np = np.vstack([DIF[-1 * length:], DEA[-1 * length:], MACD])
    return np.round(MACD_np, 2)


def MovingAverage(interval, window_size):
    """interval is the array ,window_size is the number of N for MA
	Usage : MovingAverage(Array,Number), return is np array. first and last
	servals should be deleted for mapping cause,see also MAper functions"""
    window = np.ones(int(window_size)) / float(window_size)
    return np.convolve(interval, window, 'same')


def MAper(Input_np, win_s):
    """Moving average of the Input array ,win_s default 20 ,size adjusted!
	the last is the moving average , others not"""
    MA_np = MovingAverage(Input_np, win_s)
    if win_s % 2 == 0:
        ifrom = win_s / 2
        iend = -1 * (ifrom - 1)
    else:
        ifrom = (win_s - 1) / 2
        iend = -1 * ifrom
    PerMA_np = MA_np[ifrom:iend]  # per Input_np[ifrom:]
    return PerMA_np

#def BollLine(minClose_np, win_s=20):
#    """Computing Boll Lines ,mid line, upper and lower line
#	win_s default 20   """
#    #MID_np = MAper(minClose_np, 20)  #MID:=MA(C,N);
#    MID_np = rolling_ma(minClose_np, 20)  #MID:=MA(C,N);
#    mid_len = len(MID_np)  #if len(MID_np) < 20 else 20
#    MIDdiff_np = minClose_np[-1 * mid_len:] - MID_np  #VART1:=POW((C-MID),2);
#    # stdMa = np.std(MIDdiff_np[-20:]) if mid_len < 20 else np.std(MIDdiff_np[-1 * mid_len:])
#    VART1_np = MIDdiff_np * MIDdiff_np
#    # VART2:=MA(VART1,N);
#    # VART3:=SQRT(VART2);
#    var3_ = rolling_ma(VART1_np, 20)
#    VART3_np = np.sqrt(var3_)
#    # print "VART3_np ======> ",VART3_np
#    # VART3_np = appendMake_np(priceMean_np,mid_len)
#    # UPPER:=MID+2*VART3;
#    # LOWER:=MID-2*VART3;
#    MID_np = MID_np[-1 * len(VART3_np):]
#    BolUp = MID_np + 2 * VART3_np
#    BolLow = MID_np - 2 * VART3_np
#    tmp_vstack = np.vstack((BolUp, MID_np))
#    Boll3Lines_np = np.vstack((tmp_vstack, BolLow))
#    return Boll3Lines_np


def getWavingRange(
        datumLast):  # should be tested ,be with moving average  20130122
    """Waving Range percentage: (High-Low)/CLOSE X 100%"""
    closeP = datumLast.T[4]
    diff_highlow = datumLast.T[2] - datumLast.T[3]
    wavingNp = 1.0 * diff_highlow / closeP * 100.0
    return np.round(wavingNp, 2)[-10:]

def getDailyWaveRange(df): # parameter is pandas DataFrame
    """ Daily Wave Range of the stock, should less than 10.99% """
    waverg_ser = (df.high - df.low)/(100.0*df.close)
    return waverg_ser

# def getDataFrameDescribe(df): # parameter is pandas DataFrame
    # df.describe()

def getVCOHL(datumLast):  # should be tested ,be with moving average  20130122
    """Accumulations vers Distributions index  daily
	vol*(Close-Open)/(High-Low)"""
    closeOpen = datumLast.T[4] - datumLast.T[1]
    highLow = datumLast.T[2] - datumLast.T[3]
    VolumnOfDay = datumLast.T[6] / 100.0 / 10000  # 10K hands
    return np.round(VolumnOfDay * closeOpen / highLow, 2)


def getFluxPare(datumLast, lastN):
    """caculate trading volumn and Up and down rate in a 2D array
	fluxrate : (Close-Open)/Open , volrate : VOL / 100/1000.0"""
    fluxrate_np = np.round(
        (1.0 * datumLast.T[4] - datumLast.T[1]) / datumLast.T[1] * 100.0, 2)
    VolumnOfDay = np.round(datumLast.T[6] / 100.0 / 10000, 2)  # 10K hands
    return np.vstack([fluxrate_np[-lastN:], VolumnOfDay[-lastN:]])


def XSchannel(datumLast, ndays):
    """
    :param datumLast: numpy ndarray
    :param ndays:  intervals count
    :return: 4-dim np arrays
    """
    #assert type(datumLast) == np.object()
    Close_np, Vol_np = datumLast.T[4] / 100.0, datumLast.T[6] / 100000.0
    var2_np = np.round(Close_np * Vol_np, 2)  #VAR2:=CLOSE*VOL;
    #VAR3:=EMA((EXPMA(VAR2,3)/EXPMA(VOL,3)+EXPMA(VAR2,6)/EXPMA(VOL,6)+
    #       EXPMA(VAR2,12)/EXPMA(VOL,12)+EXPMA(VAR2,24)/EXPMA(VOL,24))/4,13);
    ema3 = caculateEMAs(var2_np, 3) / caculateEMAs(Vol_np, 3)
    ema6 = caculateEMAs(var2_np, 6) / caculateEMAs(Vol_np, 6)
    ema12 = caculateEMAs(var2_np, 12) / caculateEMAs(Vol_np, 12)
    ema24 = caculateEMAs(var2_np, 24) / caculateEMAs(Vol_np, 24
                                                     )  # with shortest length
    #print len(ema3),len(ema6),len(ema12),len(ema24)
    trimlen = len(ema24)  # below trim the np array with the same elements
    #print "the shortest length of ema24===>",trimlen
    var3_np = caculateEMAs(
        (ema3[-trimlen:] + ema6[-trimlen:] + ema12[-trimlen:] + ema24) / 4, 13)
    shortest = len(var3_np)
    ndays = shortest - 1 if ndays > shortest else ndays
    sup_np = np.round(1.06 * var3_np, 2)  # SUP:1.06*VAR3;
    sdn_np = np.round(0.94 * var3_np, 2)  #SDN:VAR3*0.94;
    var4_np = caculateEMAs(Close_np, 9)  #VAR4:=EXPMA(CLOSE,9);
    lup_np = caculateEMAs(1.14 * var4_np, 5)  #LUP:EXPMA(VAR4*1.14,5);
    ldn_np = caculateEMAs(0.86 * var4_np, 5)  #LDN:EXPMA(VAR4*0.86,5);
    #print "the shortest length of lup_np===>",len(lup_np),len(ldn_np),len(var3_np),len(sup_np),len(sdn_np),len(var3_np)
    #lchn_np =  np.vstack(lup_np,ldn_np)  # long channel
    #schn_np =  np.vstack(lup_np,ldn_np)
    return np.vstack((lup_np[-ndays:], sup_np[-ndays:], sdn_np[-ndays:],
                      ldn_np[-ndays:]))


def TrendSlope(npval):
    """
    :param npval:  numpy array
    :return: slope rate , >0 uptrend <0 down trend
    """
    slope = 0.0
    x = np.arange(len(npval))
    mat = np.vstack([x, np.ones(len(x))]).T
    slope, c = np.linalg.lstsq(mat, npval)[0]
    #print "Slopes ==> %s , c ==> %s" % (slope, c)
    return slope


def LinearRegression(ValueList):
    """Linear regression using stats.linregress
    :param ValueList:
    :return:
    """
    np_ilst = np.arange(len(ValueList))
    np_vls = np.array(ValueList, float)
    (a_s, b_s, r, tt, stderr) = stats.linregress(np_ilst, np_vls)
    a_s, b_s, stderr = round(a_s, 3), round(b_s, 3), round(stderr, 3)
    return (a_s, b_s, stderr)

#def AveDev(typ_np, ndays):
#    mean_np = MAper(typ_np, ndays)
#    length = len(mean_np)
#    last = np.sum(np.abs(typ_np[-ndays:] - mean_np[-1]))
#    sum_list = [np.sum(np.abs(typ_np[-i - ndays + 1:-i + 1] - mean_np[-i])) for i in range(2, length + 1)]
#    sum_list.reverse()
#    sum_list.append(last)
#    avedev_np = np.array(sum_list) / ndays * 1.0
#    return np.round(avedev_np, 2)
#
#
def CCI_np(datumLast, ndays=14):
   """TYP:=(HIGH+LOW+CLOSE)/3;
   CCI:(TYP-MA(TYP,N))/(0.015*AVEDEV(TYP,N)); N default 14 """
   typ_np = (datumLast.T[4] + datumLast.T[2] + datumLast.T[3]) / 300.0  # specify for daily *.day
   ma_typ = MAper(typ_np, ndays)
   avedev_np = AveDev(typ_np, ndays)
   #print avedev_np
   length = len(avedev_np)
   # max caculated elements length
   cci = (typ_np[-length:] - ma_typ[-length:]) / (0.015 * avedev_np[-length:])
   #numelements = len(cci)
   return np.round(cci, 2)


#def Bayesian(datumLast,ndays):
def ADLine(datumLast, ndays):
    """ -OLD---CLV = [(Close-Low)-(High-Close)] / (High-Low)
	====AD = previousAD + CLV * VOL   ========   instead ========
	A:=SUM(((CLOSE-LOW)-(HIGH-CLOSE))*VOL/10000/(HIGH-LOW),0);
	ADVOL:A;     MA1:MA(A,30);   MA2:MA(MA1,100);
	just cumsum 100 days ,not since the initiating date"""
    #ADlist = []
    datumLast = datumLast[-ndays:]
    #decreInx = ndays-1
    diff_np = (datumLast.T[4] - datumLast.T[3]) - (datumLast.T[2] -
                                                   datumLast.T[4])
    diffhl_np = (datumLast.T[2] -
                 datumLast.T[3]) + 0.00001  #high-low  not zero
    CLV_np = diff_np / diffhl_np * datumLast.T[6] / 1000000.0
    AD_np = np.round(np.cumsum(CLV_np), 2)
    return AD_np


def BollLine(minClose_ser, win_s=20):
    """Computing Boll Lines ,mid line, upper and lower line win_s default 20   """
    dtindx = minClose_ser.index
    print("minClose series range %s<===>%s " %
          (minClose_ser[:1], minClose_ser[-1:]))
    MID_np = pd.rolling_mean(minClose_ser, win_s)  #MID:=MA(C,N);
    minClose_np = np.round(minClose_ser.values, 2)
    mid_len = len(MID_np)  #if len(MID_np) < 20 else 20
    MIDdiff_np = minClose_np[-1 * mid_len:] - MID_np  #VART1:=POW((C-MID),2);
    #stdMa = np.std(MIDdiff_np[-20:]) if mid_len < 20 else np.std(MIDdiff_np[-1 * mid_len:])
    VART1_np = MIDdiff_np * MIDdiff_np
    vart1_se = pd.Series(VART1_np, index=dtindx)
    VART3_np = np.sqrt(pd.rolling_mean(vart1_se, win_s))
    MID_np = MID_np[-1 * len(VART3_np):]
    BolUp = MID_np + 2 * VART3_np
    BolLow = MID_np - 2 * VART3_np
    BollDF = pd.DataFrame(
        {'MinClose': minClose_np,
         'Bollupline': BolUp,
         'MidLine': MID_np,
         'BollLow': BolLow},
        index=dtindx)
    #tmp_vstack = np.vstack((BolUp, MID_np))
    #Boll3Lines_np = np.vstack((tmp_vstack, BolLow))
    return BollDF


def AveDev(typ_np, ndays):
    mean_np = pd.rolling_mean(typ_np, ndays)
    length = len(mean_np)
    last = np.sum(np.abs(typ_np[-ndays:] - mean_np[-1]))
    sum_list = [np.sum(np.abs(typ_np[-i - ndays + 1:-i + 1] - mean_np[-i]))
                for i in range(2, length + 1)]
    sum_list.reverse()
    sum_list.append(last)
    avedev_np = np.array(sum_list) / ndays * 1.0
    return np.round(avedev_np, 2)


def CCI_df(df, ndays=14):
    """TYP:=(HIGH+LOW+CLOSE)/3;
    CCI:(TYP-MA(TYP,N))/(0.015*AVEDEV(TYP,N)); N default 14 """
    typ = (df.high + df.low + df.close) / 3.0  # specify for daily *.day
    ma_typ = pd.rolling_mean(typ, ndays)
    avedev_np = AveDev(typ, ndays)
    #print avedev_np
    length = len(avedev_np)
    # max caculated elements length
    cci = (typ[-length:] - ma_typ[-length:]) / (0.015 * avedev_np[-length:])
    #numelements = len(cci)
    return np.round(cci, 2)

# In[9]:


def getSignals(cci_np):  # if CCI got a signal
    signals_array = ['trend']

    for i in range(1, len(cci_np)):
        j = i - 1
        if (cci_np[j] >= 100) and (cci_np[i] < 100):
            signals_array.append('dec'
                                 )  # this's going weak signal,decrease pos
        elif (cci_np[j] < 100) and (cci_np[i] >= 100):
            signals_array.append('inc')  #going strong, increase pos
        elif (cci_np[j] <= -100) and (cci_np[i] > -100):
            signals_array.append('buy'
                                 )  #maybe reverting ,buy some ,starting buying
        elif (cci_np[j] > 10) and (
                cci_np[i] < 10):  #maybe slump ,go under zero
            signals_array.append('sell')  #maybe slump ,go under zero
        elif (cci_np[i] < cci_np[j]):
            signals_array.append('down')
        elif (cci_np[i] > cci_np[j]):
            signals_array.append('up')
        else:
            signals_array.append('trend')
    return pd.Series(signals_array, index=cci_np.index)


def caculateLstsq(values_np):
    """ cacluate lest squre and regression up and down line """
    length = len(values_np)
    x = np.linspace(0, length, length)
    y = values_np
    #x=np.linspace(0,99,99)
    #y = CloseList/100.0
    #plt.plot(x, y, 'ro--')
    Ax = np.vstack([x, np.ones(len(x))]).T
    s = np.linalg.lstsq(Ax, y)
    #plt.plot(x, x*m+c, 'b--')
    m, c, = s[0]
    xx, std = s[3]
    return m, c, std


def autoNorm(dataSet):
    """ Normalizing numpy array to 0-1 """
    minVals = dataSet.min(0)
    maxVals = dataSet.max(0)
    ranges = maxVals - minVals
    #normDataSet = np.zeros(np.shape(dataSet))
    #m = dataSet.shape[0]
    #print "dataSet shape[0] ==%s" % m
    #normDataSet = dataSet - np.tile(minVals, (m,1))
    normDataSet = (dataSet - minVals) / ranges
    return normDataSet


#测试代码
if __name__ == "__main__":
    pass
    #unittest.main()
