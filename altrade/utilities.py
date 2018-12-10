#coding=gbk
import glob
import os
import time
from urllib import urlopen

from daysDataOfStock import *
import mathlib

CLOSE = 4


def getStockData(stockCode):
    """use urllib to open and get real time stock pricing but delays exist
    from the url return data, retrive the data items ,return the price List
    reading realtime bidding info from sina """
    import time
    HqString = "http://hq.sinajs.cn/list=" + stockCode
    while True:  # if IOError wait 30seconds to retry
        try:
            hqList = urlopen(HqString).read()
            #print "getting from remote hq.sina,consumes %f seconds....." % consume_t
            #logger.info("Check if the HqString changed!!==> \n %s" % hqList)
            break
        except IOError:
            print "IOError ,sleep 20 second,then fetch again"
            time.sleep(20)
    hqList = hqList.split(',')
    #print "====retrieved Hq from sina ,the length ===>", len(hqList)
    if len(hqList) != 33:
        #BeepNote(150, 100, 2)
        print "Length Error != 33 Hqlist is invalid!!!!!!!!!!! return 0  \n"
        print "Error List contains===>", hqList
        return 0
    #todayOpen, yesClose, atTime = hqList[1], hqList[2], hqList[31].split('"')[0]
    #tmpHigh,tmpLow, tmpVol ,tmpMoney =  hqList[4], hqList[5], hqList[8] , hqList[9]
    #nowPrice = hqList[3]
    valList = map(float, hqList[1:30]) + [hqList[30]] + [atTime]
    return valList

def time_consumed(start):
    #start = time.clock()
    end = time.clock()
    print "time consumed : %f s in loading" % (end - start)
    #read: 6.760052 s

def findDataDir(filename):
    """ find the newest date daily data in existed dirs """
    title = filename[:2]
    tail = filename[-3:]

    if title == 'sz':
        stDir = "\\Vipdoc\\sz"
    elif title == 'sh':
        stDir = "\\Vipdoc\\sh"
    else:
        print " Err in filename  "
        return 0
    if tail == 'day':
        endDir = "\\lday\\"
    elif tail == 'lc5':
        endDir = "\\fzline\\"
    elif tail == 'lc1':
        endDir = "\\minline\\"
    else:
        print " Err in stock datum type  "
        return 0

    dataDir = stDir + endDir
    # 2014-04-16 vipdoc shared in Z:\\
    #dataDir = "\\sz\\lday" if title == 'sz' else "\\sh\\lday"
    pathDirlst = ["e:\\mytools\\jcb_sina", "e:\\mytools\\jcb_sina", "D:\\mytools\\new_ztzq_v6",
                  "E:\\Stocks\\jcb_sina", "D:\\MyApps\\jcb_sina"]
    filepath = ""
    for ndir in pathDirlst:
        newdir = ndir + dataDir
        if os.path.exists(newdir):
            print "path exist==>"
            filepath = newdir
            print "Found dir !!!", filepath
            break
        else:
            print "Not a valid path"
            newdir = ""
            continue
    print "filepath Contains the stocks files==>", filepath
    return filepath


def getStocklist(datadir):
    """get all stock available ,from below directory """
    # datadir = "E:\\mytools\\jcb_sina\\vipdoc"
    # datadir = "D:\\jcb_sina\\vipdoc"
    dirname_sh = datadir + '\\sh\\lday'
    dirname_sz = datadir + '\\sz\\lday'
    filelst_sh = list(all_files('sh60*.day', dirname_sh))
    filelst_sz = list(all_files('sz00*.day', dirname_sz))
    filelst_ns = list(all_files('sz300*.day', dirname_sz))
    return filelst_sz + filelst_sh + filelst_ns


def checkMarketIndex(market, atDate):
    """ check if the Market fit to deal with """
    PathName = findDataDir(market)
    if market == "sh":
        indexName = "sh999999.day"  # ShangHai stock market index
    elif market == "sz":
        indexName = "sz399001.day"   # ShenZhen stock index
    else:
        return ""
    indexFullname = PathName + "\\" + indexName
    marketIdx = daysDataOfStock(indexFullname, 100)
    hisDateMitrix = marketIdx.getPrevDateDatum(atDate, 30)
    return hisDateMitrix


# marketIdxClose = hisDateMitrix.T[CLOSE]
# health = marketMAHealth(marketIdxClose)
# return health

def marketMAHealth(marketIdxClose):
    """need to modify ,to fix the classfication ,change to the quantifications and digitals ,exact numberous figures!!"""
    assert len(marketIdxClose) == 100
    todayIndexClose = marketIdxClose[-1]
    indexMA20s = mathlib.getMovingAverages(marketIdxClose, 20)
    fiveUp = (indexMA20s[0] > indexMA20s[5])  # need modify to see y=kx+b
    tenUp = (indexMA20s[5] > indexMA20s[15])  # need modify to see y=kx+b
    Ma20up = fiveUp and tenUp
    indexMA60s = mathlib.getMovingAverages(marketIdxClose, 60)
    tenUp = (indexMA60s[0] > indexMA60s[10])  # need modify to see y=kx+b
    twentyUp = (indexMA60s[10] > indexMA60s[-1])  # need modify to see y=kx+b
    Ma60up = twentyUp and tenUp

    if (todayIndexClose > indexMA20s[0]) and Ma20up:
        MarketIndexHealth = "best"
    elif todayIndexClose > indexMA60s[0] and Ma60up:
        MarketIndexHealth = "good"
    elif todayIndexClose < indexMA60s[0] and not Ma60up:
        MarketIndexHealth = "worse"
    else:
        MarketIndexHealth = "OK"

    return MarketIndexHealth


def prepareStock(filename, days):
    filepath = findDataDir(filename[:2])
    fullname = filepath + "\\" + filename
    return daysDataOfStock(fullname, latestNDays=days)


def stackNpArray(dimN, dimNstocks):
    """ insert a numpy array to make a multi dimension numpy array """
    dimNstocks = np.vstack([dimN, dimNstocks])
    return dimNstocks


#  for row in dimNstocks:
#      print row

def getDailyDataOfStock(stockfilename, dayslength):
    """ get numpy list of stocks days price and volumn """
    filepath = findDataDir()
    fullpathname = filepath + "\\" + stockfilename
    msele = daysDataOfStock(fullpathname, dayslength)
    nptmpArray = msele.datumLast
    #print nptmpArray.T
    closeList = nptmpArray.T[4]
    closeList = np.vstack([closeList, msele.getTA(6) / 9000.0])  #volumn
    dayslst = closeList.tolist()


def all_files(pattern, search_path, pathsep=os.pathsep):
    """ Given a search path, yield all files matching the pattern. """
    for path in search_path.split(pathsep):
        for match in glob.glob(os.path.join(path, pattern)):
            yield match


def checkLastDateOK(lastdate, deltaDays=20):
    """  check if the Last Date is vaild , Last Date is  20 days Less than    the current date will be ignored!  """
    lastdate = str(lastdate)
    todaydate = datetime.date.today()
    mdate = datetime.date(int(lastdate[0:4]), int(lastdate[4:6]), int(lastdate[6:8]))
    #~ print (Todate - mdate).days
    return 1 if (todaydate - mdate).days < deltaDays else 0


def checkDateSpan(lastdate, tilldate):
    """  check if the Last Date is vaild , Last Date is  20 days Less than the current date will be ignored!  """
    if lastdate > tilldate:
        print "Error !! first arg date must less than second"
        return -1
    lastdate, tilldate = str(lastdate), str(tilldate)
    tdate = datetime.date(int(tilldate[0:4]), int(tilldate[4:6]), int(tilldate[6:8]))
    ldate = datetime.date(int(lastdate[0:4]), int(lastdate[4:6]), int(lastdate[6:8]))
    return (tdate - ldate).days


#    return  1 if (tdate - ldate).days < deltaDays else 0

def validDate(date):
    """ if found date is a valid one!! """
    strDate = str(date)
    yyyy, mm, dd = int(strDate[0:4]), int(strDate[4:6]), int(strDate[6:8])
    yearOK = yyyy in range(1997, 2015)
    monthOK = mm in range(1, 13)
    dayOK = dd in range(1, 32)
    return yearOK and monthOK and dayOK


import datetime
import dateutil.parser


def DateParse(date):
    # dateutil.parser needs a string argument: let's make one from our
    # `date' argument, according to a few reasonable conventions...:
    kwargs = {}  # assume no named-args
    if isinstance(date, (tuple, list)):
        date = ' '.join([str(x) for x in date])  # join up sequences
    elif isinstance(date, int):
        date = str(date)  # stringify integers
    elif isinstance(date, dict):
        kwargs = date  # accept named-args dicts
        date = kwargs.pop('date')  # with a 'date' str
    try:
        try:
            parsedate = dateutil.parser.parse(date, **kwargs)
            print 'Sharp %r -> %s' % (date, parsedate)
            return parsedate
        except ValueError:
            parsedate = dateutil.parser.parse(date, fuzzy=True, **kwargs)
            print 'Fuzzy %r -> %s' % (date, parsedate)
            return ''
    except Exception, err:
        print 'Try as I may, I cannot parse %r (%s)' % (date, err)
        return ''


def caculateCoeff(valueList):
    """ Return correlation coefficients of valueList ,give serials of number of days"""
    serialNos = np.arange(0, len(valueList))
    d2Array = np.vstack([serialNos, valueList])
    coeff = np.corrcoef(d2Array)
    return round(coeff[0][1], 2)


def getHulls(dataList):
    ' Graham scan to find upper and lower convex hulls of a set of 2D points '
    U = []
    L = []
    #Points = [(dataList.index(cl),cl) for cl in dataList]  #make the 2D point (x,y)
    #Points = [(i,dataList[i]) for i  in range(len(dataList))]  #make the 2D point (x,y)
    Points = [(i, cl) for i, cl in enumerate(dataList)]  #make the 2D point (x,y)
    for p in Points:
        if (7, 1039) == p:
            pass
        while len(U) > 1 and orientation(U[-2], U[-1], p) <= 0:
            if (U[-1][0] - U[-2][0]) <= 30:  #should replaed by a more accurate algorithem
                U.pop()
            else:
                break
        while len(L) > 1 and orientation(L[-2], L[-1], p) >= 0:
            if (L[-1][0] - L[-2][0]) <= 30:
                L.pop()
            else:
                break
        U.append(p)
        L.append(p)
    return U, L


def orientation(p, q, r):
    """ >0 if p-q-r are clockwise, <0 if counterclockwise, 0 if colinear. """
    return (q[1] - p[1]) * (r[0] - p[0]) - (q[0] - p[0]) * (r[1] - p[1])


def initlog():
    import logging
    logger = logging.getLogger()
    #TODO: logfilename default to 'test.log',should be improved!!
    #as a parameter
    logfilename = 'test.log'
    hdlr = logging.FileHandler(logfilename)
    #formatter = logging.Formatter('%(levelname)s %(funcName)s %(message)s\n')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger


try:
    set
except NameError:
    from sets import Set as set
# f defines an equivalence relation among items of sequence seq, and
# f(x) must be hashable for each item x of seq
def uniquer(seq, f=None):
    """ Keeps earliest occurring item of each f-defined equivalence class """
    if f is None:  # f's default is the identity function f(x) -> x
        def f(x): return x
    already_seen = set()
    result = []
    for item in seq:
        marker = f(item)
        if marker not in already_seen:
            already_seen.add(marker)
            result.append(item)
        #~ else:
        #~ result.remove(item)
    return result

#def filterNearVal(seq, max=1):
#pass
def filterNearVal(seq, max=1):
    """filter out the date of  near  less than 5 days  max =1 ,hold max value , else max = 0 ,find lowest"""
    assert len(seq) >= 3
    result = []
    lastloc = len(seq) - 1
    loc = 0
    while loc < lastloc:
        idx, val = seq[loc]
        #print "loc --->",loc
        #if idx == 123 :
        #print "----------------"
        #if loc > lastloc :  break
        maxit = minit = seq[loc]
        nextIdx, nextVal = seq[loc + 1]
        val, nextVal = float(val), float(nextVal)
        assert (nextIdx - idx) >= 0
        while (nextIdx - idx) < 5:
            #maxit =(idx,str(val))  if  val > nextVal  else (nextIdx,str(nextVal))
            #minit =(idx,str(val))  if  val < nextVal   else (nextIdx,str(nextVal))
            maxit = maxit if val > nextVal  else seq[loc + 1]
            minit = minit if val < nextVal   else seq[loc + 1]
            idx, val = nextIdx, nextVal
            if loc + 2 <= lastloc:
                nextIdx, nextVal = seq[loc + 2]
                nextVal = float(nextVal)
                loc += 1
            else:
                break
            if loc + 1 > lastloc:
                break
        if max == 1: result.append(maxit)
        if max == 0: result.append(minit)
        loc += 1
    result.append(seq[lastloc])
    return result


def percentValue(nowprice, prehighprice):
    """ current price is how much higher or lower than previous high """
    nowprice, prehighprice = float(nowprice), float(prehighprice)
    percent = round((nowprice - prehighprice) / prehighprice * 100.0, 2)
    return percent


def closePriceHulls(CloseList):
    todayClose = CloseList[-1]
    length = len(CloseList)
    upPercent = percentValue(todayClose, CloseList[0])
    if upPercent < 6.18:  #if current close is not over 6.18% than ndays before
        return 0  # then neglect this stock!!
    topList, lowList = getHulls(CloseList)
    if len(topList) < 3:
        return 0
    assert len(topList) >= 3
    topList.sort()
    loc = -2
    idx, maxClose = topList[-2]  # the second last, exclude first [0] and last [-1]
    LastIdx = length
    #maxClose,minClose = max(CloseList),min(CloseList)
    while (LastIdx - idx) <= 5:  #seek previous High ,at least 5 days before
        loc -= 1
        LastIdx = idx  # previous idx
        idx, maxClose = topList[loc]
    upPercent = percentValue(todayClose, maxClose)
    deltaDays = length - idx - 1
    assert deltaDays <> 0
    if upPercent < -1.0:
        return 0
    #very good, price climbs close to previous high in 6weeks
    elif upPercent < 10.18:
        return upPercent, deltaDays
    else:
        return 0


def getApex(dataList):
    """ return max and min apex list """
    Points = [(i, cl) for i, cl in enumerate(dataList)]  #make the 2D point (x,y)
    Values = [(val, index) for index, val in Points]
    Values.sort()
    orderPoints = [(index, val) for val, index in Values]
    minApex, maxApex = orderPoints[:30], orderPoints[-30:]
    minls = filterOut(minApex)
    maxApex.reverse()
    maxls = filterOut(maxApex)
    return maxls, minls


def filterOut(Points):
    loc = 0
    while loc <= 4:  #at least we need 4 Apex
        indexlist = [i for i, v in Points]
        delPts = []
        dellist = []
        if loc >= len(indexlist): break  #out of range exception rise up!!
        nplist = np.array(indexlist)
        npdelta = nplist - indexlist[loc]
        for j, delta in enumerate(npdelta):
            if abs(delta) <= 4 and delta <> 0:  # days span more than 4
                dellist.append(j)
        if not dellist:
            loc += 1
            continue
        for di in dellist:
            delPts.append(Points[di])
        for p in delPts:
            Points.remove(p)
        loc += 1
    Points.sort()
    return Points


def NumOfWeekInYear(specDate):
    """ check if a specified date like "yyyymmdd" in same week of a year ,retun No. of weeks in a year"""
    specDate = str(specDate)
    mdate = datetime.date(int(specDate[0:4]), int(specDate[4:6]), int(specDate[6:8]))
    return int(mdate.strftime('%W'))


def weekIndexList(dateList):
    """same week date seperated by index  """
    weekindexlist = []
    numWeekYear = [NumOfWeekInYear(specdate) for specdate in dateList]
    previousValue = -1
    for numofweek in numWeekYear:
        if previousValue <> numofweek:
            weekindexlist.append(numWeekYear.index(numofweek))
            previousValue = numofweek
        else:
            continue
    return weekindexlist


def dateLastfix(prefix):
    """ generate the date lastfix ,append to the prefix string"""
    tdate = datetime.date.today()
    datestr = tdate.strftime("%Y%m%d")
    filename_saved = prefix + datestr
    return filename_saved


def today2int():
    """ convert today date to integer"""
    sdate = datetime.datetime.today().date()
    str_date = sdate.strftime('%Y%m%d')
    int_date = int(str_date)
    return int_date


def getListCol(inputList, col):
    """ get the list No.column,return a new column list"""
    list_zip = zip(*inputList)
    return list_zip[col]


def epochTime(due_hour, due_min):
    """ input duetime hour ,minutes ,output epochTime of seconds"""
    nowtime = time.localtime()
    yr, mo, dy = nowtime.tm_year, nowtime.tm_mon, nowtime.tm_mday
    duetime = time.mktime([yr, mo, dy, due_hour, due_min, 0, 0, 0, 0])
    #sec2Run = duetime- start
    return duetime


def epcoh2DateTime(epoch_t):
    """ convert epoch_t integer number type time to datetime yyyymmdd hhmmss """
    strDatetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_t))
    return strDatetime


def ifLineCross(line2p, Line2p):
    """ if two line crossed , has a point of cross return 0 not cross , 1 upcross  -1 down cross"""
    downCrs = (line2p[0] > Line2p[0]) and (line2p[1] < Line2p[1])
    upCrs = (line2p[0] < Line2p[0]) and (line2p[1] > Line2p[1])
    if downCrs:
        return -1  # line2p down cross Line2p
    elif upCrs:
        return 1  # line2p up cross Line2p
    else:
        return 0


def getMAs(Close_np, lastN):  # 4, 10,40,60 MAs
    """get MA lines  """
    MA4lst = mathlib.getMovingAverages(Close_np, 4)
    MA10lst = mathlib.getMovingAverages(Close_np, 10)
    MA40lst = mathlib.getMovingAverages(Close_np, 40)
    MA60lst = mathlib.getMovingAverages(Close_np, 60)
    return [MA4lst[-lastN:], MA10lst[-lastN:], MA40lst[-lastN:], MA60lst[-lastN:]]


def seconds4Now2DueMoment(duetime_hour, duetime_min):
    """ input duetime to run ,output the deta seconds from now Should return duetime ,used by enterabs NO USE NOW!!!!"""
    start = time.time()
    duetime = epochTime(duetime_hour, duetime_min)
    deltaT = duetime - start
    return deltaT



def getTurtlePos(closeprice_list):
    """ get 20 data set of price , return 20 high and low """
    high = round(max(closeprice_list[-20:]), 2)
    low = round(min(closeprice_list[-20:]), 2)
    return high, low


def DueTime(duetime_hour, duetime_min):
    """ input duetime hour ,min Output Should return duetime ,used by enterabs"""
    nowtime = time.localtime()
    yr, mo, dy = nowtime.tm_year, nowtime.tm_mon, nowtime.tm_mday  #get now date
    duetime = time.mktime([yr, mo, dy, duetime_hour, duetime_min, 0, 0, 0, 0])
    return duetime


def AtTransactionTime():
    """ Transaction duration definition,and return which time segments """
    #print "Enter AtTransactionTime..."
    amStarttime, noonEndtime = datetime.time(9, 00), datetime.time(11, 30)
    pmStarttime, pmEndtime = datetime.time(13, 00), datetime.time(14, 59)
    amOpenPeriod, pmClosePeriod = datetime.time(10, 31), datetime.time(14, 01)
    nowtime = datetime.datetime.now().time()
    beforetime = nowtime < amStarttime
    AmDealtime = (nowtime > amStarttime) and (nowtime < noonEndtime )
    Noontime = (nowtime > noonEndtime) and (nowtime < pmStarttime )
    PmDealtime = (nowtime > pmStarttime) and (nowtime < pmEndtime )
    aftertime = (nowtime > pmEndtime )
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


def pause():
    """ just pause ,wait to input """
    print "=====Pause the execution ,press Enter"
    input = raw_input()
    print input


import unittest
from unittest import TestCase


class TestdaysDataOfStockClass(TestCase):
    def setUp(self):
        print "setUp", hex(id(self))

    def tearDown(self):
        print "tearDown"

    def test_findDataDir(self):
        filename = "sz000823.day"
        dataHome = "D:\\MyApps\\jcb_sina\\Vipdoc\\sz\\lday"
        print filename[:2]
        filepath = findDataDir(filename[:2])
        print filepath
        self.assertEqual(filepath, dataHome)

    def test_checkMarketIndex(self):
        dataMatrix = checkMarketIndex("sz", 20110830)
        print dataMatrix[-1]
        print "Done"

    def test_stackNpArray(self):
        npa1 = np.arange(7)
        npa2 = np.arange(10, 17)
        npa = stackNpArray(npa1, npa2)
        self.assertEqual(npa.shape, (2, 7))

    def test_getApex(self):
        filename = "sz300006.day"
        dataHome = "D:\\MyApps\\jcb_sina\\Vipdoc\\sz\\lday"
        filepath = findDataDir(filename[:2])
        fullname = filepath + "\\" + filename
        CLOSE = 4
        stocksObj = daysDataOfStock(fullname, 100)
        closelist = stocksObj.getColumnArray(CLOSE)
        closelist = closelist.tolist()
        maxlist, minlist = getApex(closelist)
        print ">>getApex>>", maxlist, "\n", minlist
        tp, low = getHulls(closelist)
        print  ">>>getHulls>>>", len(tp), "---", tp, "\n", len(low), "---", low
        self.assertEqual(filepath, dataHome)
        print filterNearVal(tp, 1)
        print  filterNearVal(low, 0)
        print filterOut(tp)
        print filterOut(low)

    def test_DateParse(self):
        tests = (
            "January 3, 2003",  # a string
            (5, "Oct", 55),  # a tuple
            "Thursday, November 18",  # longer string without year
            "7/24/04",  # a string with slashes
            "24-7-2004",  # European-format string
            {'date': "5-10-1955", "dayfirst": True},  # a dict including the kwarg
            "5101955",  # dayfirst, no kwarg
            19950317,  # not a string
            "11AM on the 11th day of 11th month, in the year of our Lord 1945",
        )
        for test in tests:  # testing date formats
            DateParse(test)

    def test_checkDateSpan(self):
        self.assertEqual(checkDateSpan(20100901, 20100905), 4)
        print checkDateSpan(20100801, 20100905)
        self.assertEqual(checkDateSpan(20100801, 20100905), 35)

    #def  test_checkMarketIndex(self):
    #print "test check Market Index Health!"
    #self.assertEqual(checkMarketIndex('sh',20110603),  "worse" )

    def test_orientation(self):
        print "test  orientation"
        p1, p2, p3 = (1, 5), (2, 5), (3, 5)
        self.assertEqual(orientation(p1, p2, p3), 0)
        p1, p2, p3 = (1, 5), (2, 10), (3, 1)
        print orientation(p1, p2, p3)
        p1, p2, p3 = (1, 20), (2, 1), (3, 15)
        print orientation(p1, p2, p3)

    def test_hulls(self):
        plist = [3, 5, 3, 9, 8, 2, 7, 11, 13, 11, 9, 5, 2, 1, 5, 9, 11, 15, 13, 9, 5, 4, 10, 20, 21, 24, 22, 13]
        tp, lw = getHulls(plist)
        print tp
        print lw

    def test_validDate(self):
        dateOK = validDate(20091231)
        dateX = validDate(20131231)
        self.assertFalse(dateX)
        self.assertTrue(dateOK)

    def test_initlog(self):
        logging = initlog()
        logging.info('?¢²á')
        localVar = [4, 32, 21, 4, 5, 55, 321, 12]
        logging.info('the local variable is --> %s' % localVar)
        logging.info('the local variable is -->%s ', str(localVar))
        logging.debug('the local variable is -->%s ' % localVar)
        logging.error('the local variable is --> %s', str(localVar))

    def test_uniquer(self):
        testList = [(0, '6.5'), (2, '7.17'), (2, '7.17'), (3, '7.4'), (5, '7.78'), (16, '6.57'), (17, '6.65'),
                    (22, '6.55'), (33, '6.7'), (34, '6.61'), (35, '6.44'), (41, '6.96'), (43, '7.61'), (54, '7.27'),
                    (62, '6.88'), (108, '9.05'), (113, '9.85'), (113, '9.85'), (116, '9.62'), (123, '9.02'),
                    (138, '10.84'), (144, '9.63'), (149, '10.82')]
        lowlist = [(0, '6.5'), (1, '6.83'), (8, '7.24'), (16, '6.57'), (19, '6.73'), (28, '6.25'), (35, '6.44'),
                   (43, '7.61'), (46, '7.36'), (57, '6.75'), (62, '6.88'), (64, '6.98'), (71, '7.7'), (73, '7.84'),
                   (91, '7.9'), (119, '8.69'), (135, '10.03'), (140, '9.79'), (141, '9.91'), (143, '9.53'),
                   (144, '9.63'), (149, '10.82')]
        print len(testList), len(lowlist)
        catlist = testList + lowlist
        print catlist
        rlst = uniquer(testList + lowlist)
        print len(rlst), len(testList)
        print rlst

    #def test_filterNearVal(self):
    #testList  = [(0, '6.5'), (2, '7.17'),  (3, '7.4'), (5, '7.78'), (16, '6.57'), (17, '6.65'), (22, '6.55'), (33, '6.7'), (34, '6.61'), (35, '6.44'),(44, '6.44')]
    #print len(testList)
    #result = filterNearVal(testList,max = 1)
    #self.assertEqual(result[0:3],[(5, '7.78'), (17, '6.65'),  (22, '6.55')])
    #t2list = [(62, '6.88'), (108, '9.05'), (113, '9.85'), (116, '9.62'), (123, '9.02'), (138, '10.84'), (144, '9.63'), (149, '10.82')]
    #print len(t2list)
    #result = filterNearVal(t2list,max = 1)
    #self.assertEqual(result[0:3],[(62, '6.88'), (108, '9.05'), (113, '9.85')])
    #mlist = [(0, 6.5), (1, 6.83), (8, 7.24), (16, 6.57), (19, 6.73), (28, 6.25), (35, 6.44), (43, 7.61), (46, 7.36)]
    #print len(mlist)
    #result = filterNearVal(mlist,max = 0)
    ##self.assertEqual(result[0:6],[(0, '6.5'), (8, '7.24'), (16, '6.57'), (28, '6.25'), (35, '6.44'), (43, '7.61')])
    #self.assertEqual(result[0:6],[(0, 6.5), (8, 7.24), (16, 6.57), (28, 6.25), (35, 6.44), (46, 7.36)])


if __name__ == "__main__":
    print "===About to test wait ====="
    pause()
    unittest.main()
#~ filepath = findDatadir()
#~ print filepath
