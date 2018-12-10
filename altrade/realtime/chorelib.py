import time
import datetime
import sqlite3
from urllib import urlopen


def getStockData(stockCode):
    """At the Market time use urllib to open and get real time stock
    biddin gand pricing ,delay exist ,alway keep alarm to it """
    HqString = "http://hq.sinajs.cn/list=" + stockCode
    # from the url return data, retrive the data items ,return the price List
    # reading realtime bidding info from sina
    while True:  # if IOError wait 30seconds to retry
        try:
            begin_t = time.time()
            hqList = urlopen(HqString).read()
            consume_t = time.time() - begin_t
            # print "getting from remote hq.sina,consumes %f seconds....." % consume_t
            # logger.info("Check if the HqString changed!!==> \n %s" % hqList)
            break
        except IOError:
            print "IOError ,sleep 20 second,then fetch again"
            time.sleep(20)

    hqList = hqList.split(',')
    # print "====retrieved Hq from sina ,the length ===>", len(hqList)
    if len(hqList) != 33:
        print "Length Error != 33 Hqlist is invalid!!!!!!!!!!! return 0  \n"
        print "Error List contains===>", hqList
        return 0
    todayOpen, yesClose, atTime = hqList[1], hqList[2], hqList[31].split('"')[0]
    # tmpHigh,tmpLow, tmpVol ,tmpMoney =  hqList[4], hqList[5], hqList[8] , hqList[9]
    # nowPrice = hqList[3]
    valList = map(float, hqList[1:30]) + [hqList[30]] + [atTime]
    return valList


def AtTransactionTime():
    """ Transaction duration definition,and return NOW is in which time span/segments """
    # print "Enter AtTransactionTime..."
    amStarttime, noonEndtime = datetime.time(9, 00), datetime.time(11, 30)
    pmStarttime, pmEndtime = datetime.time(13, 00), datetime.time(15, 00)
    nowtime = datetime.datetime.now().time()
    beforetime = nowtime < amStarttime
    AmDealtime = (nowtime > amStarttime) and (nowtime < noonEndtime)
    Noontime = (nowtime > noonEndtime) and (nowtime < pmStarttime)
    PmDealtime = (nowtime > pmStarttime) and (nowtime < pmEndtime)
    aftertime = (nowtime > pmEndtime)
    if beforetime:
        return "before"
    elif AmDealtime:
        return "amdeal"
    elif Noontime:
        return "noon"
    elif PmDealtime:
        return "pmdeal"
    elif aftertime:
        return "after"


def DueTime(duetime_hour, duetime_min):
    """ scheduled time ,input due time hour ,min Output Should return duetime ,
    used by scheduled task enterabs """
    nowtime = time.localtime()
    # if AtTransactionTime() in ["amdeal"]:
    #     return nowtime  # in trading time
    yr, mo, dy = nowtime.tm_year, nowtime.tm_mon, nowtime.tm_mday  # get now date
    dealstart_sec = time.mktime([yr, mo, dy, duetime_hour, duetime_min, 0, 0, 0, 0])
    now_sec = time.mktime(nowtime)
    if AtTransactionTime() not in ["before", "noon", "after"]:
        due_sec = now_sec if dealstart_sec < now_sec else dealstart_sec
    return due_sec


def SaveRec2db(SegmentData):
    if len(SegmentData) < 1:  # nothing in Array
        return
    conn = sqlite3.connect('stocks.db')
    curs = conn.cursor()
    query = 'INSERT INTO Hq1min(stockname, Dealdetails, Timestamp) VALUES(?,?,?)'
    for datline in SegmentData:
        stock, timestamp = datline[0], " ".join(datline[30:])
        details = ', '.join(str(x) for x in datline[1:30])
        print "the data line ==>", datline
        # stock, details, timestamp = datline[0], " ".join(datline[1]), " ".join(datline[2])
        vals = [stock, details, timestamp]
        print "Values to save to sqlite!!==>", vals
        curs.execute(query, vals)
    conn.commit()
    conn.close()
