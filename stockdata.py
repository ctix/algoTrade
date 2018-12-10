# coding: utf-8
# pysudeo code
# start from a given date , given fund amount , position management
# scan every stock in the list , caculation total gain /lose money . make it
# testable.  find a upwards trend stock, starting transacton/trading that begin
# with daily regression/downwards  perferable
#  build position in minute line , starting high frequency transaction
# according to signals and positions , fund management and position management
# till the end of the data set
# coding functions to pandas day and week data set
# basic dataset include ohlc ,cci ,mas ,bolling line
# how to compute the probabilities of close price ,Bayiesan Methods???
# write to mysql database of the whole years of day ,minutes basic features

import pandas as pd
import numpy as np

class daysDataOfStock:
    """DF hold all the datum and return value only hold latest last ndays value """
    def __init__(self, fullname):
        stockday_type = np.dtype(
            {
                'names': ['date', 'open', 'high', 'low', 'close', 'amount',
                          'vol', 'AdjClose'],
                'formats': ['i4', 'i4', 'i4', 'i4', 'i4', 'i4', 'i4', 'i4']
            },
            align=True)
        _datum1d = np.fromfile(fullname, stockday_type)
        self.DF = pd.DataFrame(_datum1d)
        dateseries = self.DF['date']
        dtstr = [str(i) for i in dateseries]
        self.DF.index = pd.to_datetime(dtstr)
        # self.DF.index.name = "date_idx"
        self.DF.loc[:, ['open', 'high', 'low', 'close', 'vol']] = \
            self.DF.loc[:, ['open', 'high', 'low', 'close', 'vol']]/100.0
        self.DF = self.DF.loc[:, ['open', 'high', 'low', 'close', 'vol']]

    def getDateRange(self):
        """the start and end  date"""
        return (self.DF.index[0], self.DF.index[-1])

    def getLatestDataFrame(self, latestNbars=60):
        return self.DF[-1*latestNbars:] #Only return last n bars
        # self.DF = self.DF[-1*latestNbars:] #Only return last n bars

    def getWeekDatum(self):
        """get items daily ,summary to Weekly Datum """
        ohlc_dict = {
            'open':'first',
            'high':'max',
            'low':'min',
            'close':'last',
            'vol':'sum'
            }
        return self.DF.resample('W-Fri', how=ohlc_dict)
         # DataFrame.resample('W-Fri', how=ohlc_dict)

class minuteOfStock:
    def __init__(self, fullname):
        """ latest number of days Bars , 1 day 240 minute bars
        default to 10 days minutes dataset """
        minute5 = np.dtype({
            'names': ['monthdate', 'hourmin', 'open', 'high', 'low', 'close',
                      'amount', 'volume', 'rev'],
            'formats': ['H', 'H', 'f', 'f', 'f', 'f', 'f', 'i', 'i']
        })
        # in case the designated file doesn't exist
        try:
            _datum1m = np.fromfile(fullname, dtype=minute5)
        except IOError as e:
            print ("IOError, file May not be Exist!!", e.args)
            return
        self.DF = pd.DataFrame(_datum1m)
        self.DF = self.convertDateMin()

    def convertDateMin(self):
        datenp = self.DF["monthdate"]
        minnp = self.DF["hourmin"]
        yearnpa = (np.floor(datenp / 2048) + 2004) * 10000
        monnpa = np.floor((datenp % 2048) / 100) * 100
        daynpa = datenp % 2048 % 100
        hourminnpa = np.floor(minnp / 60) * 100 + minnp % 60
        datetimelst = (yearnpa + monnpa + daynpa) * 10000 + hourminnpa
        # set the first col yyyymmdd
        datetime_ary = [str(i)[:12] for i in datetimelst]
        self.DF["datetime"] = pd.to_datetime(pd.Series(datetime_ary))
        # dtstr = self.dataframe["datetime"].\
            # apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        #self.dataframe.index = dtstr
        self.DF.index = self.DF["datetime"]
        return self.DF[['open', 'high', 'low', 'close', 'volume']]

    def getDatetimeRange(self):
        """the start and end  datetime of the whole dataFrame"""
        return (self.DF.index[0], self.DF.index[-1])

    def getLatestDataFrame(self,latestNbars=2400):
        """default to 10 days minutes dataset """
        return self.DF[-1*self.latestNbars:] #Only return last n bars


    def resampleNminsDatum(self,intervals='15min'):
        """resample to N minutes DataFrame,
        intervals used value 5min , 15min, 30min"""
        ohlc_dict = {
            'open':'first',
            'high':'max',
            'low':'min',
            'close':'last',
            'volume':'sum'
            }
        return self.DF.resample(intervals, how=ohlc_dict, loffset="-1s", label='right')




# first begin with byd minutes and day line for simulating
# in[13]:
if __name__ == "__main__":
    pass
    test_datum_path = "..\\tests\\datum\\"
    byd_minsfile= test_datum_path + "sz002594.lc1"
    byd_dayfile= test_datum_path + "sz002594.day"


    # in[14]:
    # get the starting date for the simulation minutes line ,
    # compute day line enter in signal
    # in[15]:
    # rtmins= minuteofstock(rtminsfn)
    # rtday = daysdataofstock(rtdayfn)
    # # in[21]:
    # # per day caculations and plot. signals refer to cci
    # # get_ipython().magic(u'pylab inline')
    # # serclose = rtday.df.close[-1200:]
    # servol = rtday.df.vol[-1200:]
    # volvals = servol.values
    # rtday.df.close.plot()

    # in[22]:
    # normvols  = autonorm(volvals)
    # fig=plt.figure()
    # mstd = pd.rolling_std(serclose,20)
    # ma = pd.rolling_mean(serclose,20)
    # mavol = pd.rolling_mean(normvols,20)
    # plt.plot(serclose.index, serclose, 'k')
    # plt.plot(serclose.index, normvols*40, 'r')
    # plt.plot(serclose.index, mavol*40, 'g')
    # plt.plot(ma.index, ma, 'b')
    # plt.fill_between(mstd.index, ma-2*mstd, ma+2*mstd, color='b', alpha=0.2)
    # plt.fill_between(mstd.index,0, normvols*40, color='y', alpha=0.2)
    #plt.plot(serclose.index, signals, 'r')


    # per minute signals per bbi
    # numtic = 720
    # serclose = rtmins.df.close[-numtic:]
    # servol = rtmins.df.vol[-numtic:]
    # volvals = servol.values
    # normvols  = autonorm(volvals)
    # mavol = pd.rolling_mean(normvols,20)
    # #mean price total amount divided by total volume traded
    # mean_price = np.cumsum(rtmins.df.amount[-numtic:])/np.cumsum(rtmins.df.vol[-numtic:]*100.0)
    # bolline = bollline(serclose)
    # bolup = bolline.bollupline[-numtic:]
#    bolup_ser = pd.series(bolup.values)
#    bolow = bolline.bolllow[-numtic:]
#    bolow_ser = pd.series(bolow.values)
#    close = serclose[-numtic:]
#    #sig = pd.series(close.values-bolup.values >0)
#    #pd.series(sig)
#    sell_signals = pd.series(bolup_ser[close.values-bolup.values > 0.01])
#    buy_signals =  pd.series(bolow_ser[close.values-bolow.values < -0.01])
#
#    # in[46]:
#
#    #rtmins.df.close.plot(use_index=false,grid=true)
#    fig=plt.figure()
#    x = np.linspace(0,numtic,numtic)
#    mstd = pd.rolling_std(serclose,20)
#    ma = pd.rolling_mean(serclose,20)
#    plt.plot(x, serclose, 'k')
#    plt.plot(x, ma, 'b')
#    plt.plot(x,mean_price, 'r')
#    plt.plot(x, normvols*5+58, 'r')
#    plt.plot(x, mavol*5+58, 'g')
#    plt.plot(sell_signals.index,sell_signals.values,'rv')
#    plt.plot(buy_signals.index,buy_signals.values,'g^')
#    plt.fill_between(x, ma-2*mstd, ma+2*mstd, color='b', alpha=0.2)
#
#
#    # in[121]:
#
#    closenp = rtday.df.close.values
#    m,c,std = caculatelstsq(closenp)
#    length = len(closenp)
#    x = np.linspace(0,length,length)
#    fig=plt.figure()
#    axes = fig.add_axes([0.1, 0.1,4.0, 4.0])
# left, bottom, width, height (range 0 to 1)
#    plt.plot(x, closenp, 'ro--')
#    plt.plot(x, x*m+c+std, 'b--')
#    plt.plot(x, x*m+c-std, 'b--')
#    plt.plot(x, x*m+c+std/2, 'g--')
#    plt.plot(x, x*m+c-std/2, 'g--')
#    plt.plot(x, x*m+c, 'b--')
#    axes.set_xlabel('daily axis')
#    axes.set_ylabel('price at')
#    print 'length==>%s  m==%s c==%s std==%s' % (length,m,c,std)
#    #closestd = closenp.std()
#    #clsstd = pd.series(closenp+2*closestd)
#    #clsstd.plot()
#
#    #y = closenp[-200:]
#    y = closenp
#    #x = np.linspace(length,200,200)
#    ymean = np.mean(y)
#    for val in y:
#        deltay = y-val
#        z = np.abs(deltay)< (ymean/100.0)
#        ncross = np.count_nonzero(z)
#        if ncross > 25 :
#            yy = np.array(length*[val])
#            plt.plot(x, yy, 'g-')
#
#
#    # in[194]:
#
#    ## minutes close
#    lg = 1920
#    closenp = rtmins.df.close.values[-lg:]
#    m,c,std = caculatelstsq(closenp)
#    length = len(closenp)
#    x = np.linspace(0,length,length)
#    fig=plt.figure()
#    axes = fig.add_axes([0.1, 0.1,4.0, 4.0])
# left, bottom, width, height (range 0 to 1)
#    plt.plot(x, closenp, 'ro--')
#    plt.plot(x, x*m+c+std/5, 'b--')
#    plt.plot(x, x*m+c-std/5, 'b--')
#    plt.plot(x, x*m+c+std/10, 'g--')
#    plt.plot(x, x*m+c-std/10, 'g--')
#    plt.plot(x, x*m+c, 'b--')
#    axes.set_xlabel('daily axis')
#    axes.set_ylabel('price at')
#    #closestd = closenp.std()
#    #clsstd = pd.series(closenp+2*closestd)
#    #clsstd.plot()
#    print  'length==>%s  m==%s c==%s std==%s' % (length,m,c,std)
#    serclose = rtmins.df.close[-lg:]
#    servol = rtmins.df.vol[-lg:]
#    volvals = servol.values
#    normvols = autonorm(volvals)
#    plt.fill_between(x, 40, 40+normvols*30, color='y', alpha=0.6)
#    mstd = pd.rolling_std(serclose,20)
#    ma = pd.rolling_mean(serclose,20)
#    plt.plot(x, serclose, 'k')
#    plt.plot(x, ma, 'b')
#    plt.fill_between(x, ma-2*mstd, ma+2*mstd, color='b', alpha=0.2)
#
#
#    # in[ ]:
#
#
#
#
#    # in[71]:
#
#    closenp = rtday.df.close.values[-500:]
#    m,c,std = caculatelstsq(closenp)
#    length = len(closenp)
#    x = np.linspace(0,length,length)
#    fig=plt.figure()
#    axes = fig.add_axes([0.1, 0.1,4.0, 4.0]) # left, bottom, width, height (range 0 to 1)
#    plt.plot(x, closenp, 'ro--')
#    plt.plot(x, x*m+c+std, 'b--')
#    plt.plot(x, x*m+c-std, 'b--')
#    plt.plot(x, x*m+c+std/2, 'g--')
#    plt.plot(x, x*m+c-std/2, 'g--')
#    plt.plot(x, x*m+c, 'b--')
#    axes.set_xlabel('daily axis')
#    axes.set_ylabel('price at')
#    #closestd = closenp.std()
#    #clsstd = pd.series(closenp+2*closestd)
#    #clsstd.plot()
#    print  'length==>%s  m==%s c==%s std==%s' % (length,m,c,std)
#
#
#    # in[20]:
#
#    # first get the previous 60 days
#    #startdate = rtmins.df.index[0].strftime("%y%m%d")
#    from datetime import timedelta
#    enddate = rtmins.df.index[0]
#    startdate = enddate.date()-timedelta(100)
#    rtdatum = rtday.df[startdate:enddate]  #previous 60 days data set
#    rtclose = rtdatum['close']
#    rtvol = rtdatum['vol']
#
#
#    # in[43]:
#
#    get_ipython().magic(u'pylab inline')
#    dayma5 = pd.rolling_mean(rtclose,5)
#    boline = bollline(rtclose)
#    boline.plot()
#
#
#    # in[44]:
#
#    daycci = cci(rtdatum,14)
#    daycci.plot()
#
#
#    # in[60]:
#
#    # finding the enter in price level  , and the period of building positions
#
#
#    # in[67]:
#
#    def builddataframe(rtdatum):
#        rtclose = rtdatum['close']
#        rtvol = rtdatum['vol']
#        rtdatum['ma5']=pd.rolling_mean(rtclose,5)
#        rtdatum['ma10']=pd.rolling_mean(rtclose,10)
#        rtdatum['ma20']=pd.rolling_mean(rtclose,20)
#        rtdatum['ma40']=pd.rolling_mean(rtclose,40)
#        rtdatum['ma60']=pd.rolling_mean(rtclose,60)
#        rtdatum['ma120']=pd.rolling_mean(rtclose,120)
#        rtdatum['skw']=pd.rolling_skew(rtclose,10)
#        rtdatum['std'] = pd.rolling_std(rtclose,10)  # 10 days std close price
#        rtdatum['stdvol'] = pd.rolling_std(rtvol,10)
#        # rtclose bolline
#        bline = bollline(rtclose,20)
#        rtdatum['blup'] = bline['blup']
#        rtdatum['blmid'] = bline['mid']
#        rtdatum['bldn'] = bline['bldn']
#        rtdatum['cci'] = cci(rtdatum.df,14)
#        rtdatum['ccisig'] =  getsignals(rtdatum.df['cci'])
#        return rtdatum
#
#
# Certain Stock history price test profit
# 1, get the stock code and search for the stock in the path
# 2, open the stockfilename and read the first 60 dealing days
# 3, caculating the  Ma5,10,20,60  of the price and Volumn moving averages
# 4, then moving forward day by day to see if the buy point certiria meet
# 4-1 buy the stock , accroding to the fund left and buy point must be falling
# into  between the day high and low ,  buy number of shares .
#    4-2 computing the cost amount of money ,and the cash left
#    4-3 put above into sqlite table stocks pools ,  write down the buy-in date
#  5, Keep moving forward from the buy date ,to see next buy or SELL point .
#  5-1 if sell point met , then sell holdings at selling price and we should
# decide to sell how many shares.
#  5-2 , when sold ,insert into table of stockpool and update the
# corresponding stocks info.   holdings left and the gain profit or the money
# lost ,against the market price of the Close of that day
#
