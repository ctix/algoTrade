#coding=gbk
import time
import datetime
import sched
import numpy as np
import threading
import utilities
from daysDataOfStock import *
from config import AccState,MarketState,DealDatum
import Math

global rDatum
rDatum = []
######################################
### TODO : 1  use previous stocks data to estimate the daily strategy to deal , then find the win lose rate
###  2 : Check|ToDeal just use 1 to trading , then count into task made deals ,
###  3 :  use the daily moment data to simulae trading , then find next delta price to bid over and over!
###
######################################
#initiating the sched module scheduler
s = sched.scheduler(time.time, time.sleep)
logger = utilities.initlog()

def  showCodeList(Datum):
	"""show current stockCodeList unique set"""
	stockCodeList = [lst[0] for lst in Datum]
	return set(stockCodeList)

def loadfromFile(datefile = "datum20130329.npy"):
	""" Load save numpy Array for daily simulation"""
	global rDatum
	datefile = "datum20130329.npy"
	rDatum = np.load(datefile)
	#MarketState['SegmentData']=rDatum

def simulatedHq(stockcode):
	"""Generate moment data from npy files """
	#rDatum = MarketState['SegmentData']
	global rDatum
	if  len(MarketState['SegmentData'] ) == 0:
		loadfromFile()
	stock_dayDatum = [dArray[1:31] for dArray in rDatum if dArray[0] == stockcode]
	for line in stock_dayDatum:
		array_f = map(float,line)
		rDatumlst = rDatum.tolist()
		linelst = [stockcode]+line.tolist()
		lineindex = rDatumlst.index(linelst)
		rDatum = np.delete(rDatum,lineindex,0)
		yield array_f

def getStockData(stockCode):
	"""use urllib to open and get real time stock pricing but delays exist """
	import time
	logger.info( "\n simulation working time , ==> %s so return generated data"%stockCode )
	time.sleep(1) 	 # simulating the time consuming for getting data online
	simulArray =  simulatedHq(stockCode)
	#logger.debug("stockCode ==>%s ,simulArray ===> %s"% (stockCode,simulArray))
	nextItem =  simulArray.next()
	logger.debug("simulate return Item  ===> \ n %s"% nextItem)
	return nextItem

def	fillOrderData(dealtype,stockcode,atprice,vol) :
	logger.info( "dealtype=>%s, code=%s, @price=%s, vol= %s"%(dealtype,stockcode,atprice,vol))

def callAutoTransaction(dealtype,ParameterList):
	""" Call AutoIt invoke the proxy client and buy/sell stock
	dealtype is "buy","sell" """
	time.sleep(1)
	[stockcode,atprice,vol] = ParameterList
	fillOrderData(dealtype,stockcode,atprice,vol)
	logger.info("\n +++==stock deal %s @ ++=="%dealtype)
	logger.info("+++==stock deal  Parameters===> \n %s "%ParameterList)


def FeaturesOfHoldings(stockcodeList):
	"""daily traits of the Holdings
	TODO 1:  to see 1 min trading vol statistics"""
	preDate  = 20130329
	print stockcodeList
	for stockcode in stockcodeList:
		stockname = "sh"+stockcode if stockcode[:2] == "60" else "sz"+stockcode
		filename = stockname[2:]+".day"
		instance = utilities.prepareStock(filename,100)
		sdatum  = instance.getPrevDateDatum(preDate,100)
		close_np, vol_np  = sdatum.T[4]/100.0,sdatum.T[6]
		logger.info("****************\n previous Date Datum list ===> \n %s "% sdatum.T[0][-5:] )
		mas_lst = utilities.getMAs(close_np,3)
		macd_np = Math.MACD(close_np,6)
		#print "MACD ap array of last 6==>", macd_np
		xs_lst = Math.XSchannel(sdatum,5)

#<<<<<<< local
#		volma_np = np.array(Math.getMovingAverages(vol_np,10))  #VOL 6 10 days MA
#		minuteVol = np.round(volma_np/240.0 ,3)   #compare to the volumn from hq sina to check how wide is the diff!!
#		print "1minutes Vol 10 day list",minuteVol[-20:]  #got to be divided by 10K, should compare to vol diff 1 min
#=======
		volma_np = np.array(Math.getMovingAverages(vol_np,10))  #VOL 6 10 days MA
		minuteVol = np.round(vol_np/240.0 ,0)[-10:]   #compare to the volumn from hq sina to check how wide is the diff!!
		#print "1minutes Vol 10 day list",minuteVol[-10:]  #got to be divided by 10K
#>>>>>>> other
		wav_np =  Math.getWavingRange(sdatum)
		highlow20 = utilities.getTurtlePos(close_np)

		#print "waving diff==>" ,wav_np
		#vcohlst = Math.getVCOHL(sdatum)
		#print "VolX CloseOpenHighLow ==> ",vcohlst
		fluxpare_np = Math.getFluxPare(sdatum,10)
		#logger.debug("flux pare uprate , vol  ==>\n %s "%fluxpare_np )
		stock_tech_stat = { 'mas': mas_lst, 'macd':macd_np, 'volmin':minuteVol, 'xs': xs_lst,
		                    'wave': wav_np,'flux':fluxpare_np, 'turtle':highlow20
				           }
		stockcode = stockcode[2:]
		DealDatum[stockcode] = stock_tech_stat
		logger.debug("stock Tech statistics  ==>\n %s "%DealDatum[stockcode])
		#print stockcode
		#assert DealDatum['002236'] == DealDatum[stockcode]
		signalTrigger(stockcode)
		print DealDatum.keys()
		utilities.pause()

def checkLatestTrend(stockcode,price):
	""" check Latest Trend parameters ,such as 1 minute Vol ,
		current price vesus previous price and up down ratio
		to be continued !! refining """
	print DealDatum[stockcode]

def signalTrigger(stockcode):
	"""base on technical indicator ,trigger order signals ,captalized word means dealing Long terms """
	maLine_lst =  DealDatum[stockcode]['mas']
	macd_lst =  DealDatum[stockcode]['macd']
	xsLine_lst =  DealDatum[stockcode]['xs']
	flux_lst =  DealDatum[stockcode]['flux']
	wav_lst =  DealDatum[stockcode]['wave']
	highlow_lst =  DealDatum[stockcode]['turtle']
	volmin_lst =  DealDatum[stockcode]['volmin']
	print "stock code ====> ",stockcode
	print "Ma ==>", maLine_lst
	print "XS ==>",xsLine_lst
	print "Vol in 1 min,mean, std===>",volmin_lst, np.mean(volmin_lst),np.std(volmin_lst)
	print "Wave range list,mean ,std ==>",wav_lst,np.mean(wav_lst),np.std(wav_lst)
	print "20days high low pos ===>" ,highlow_lst
	print "MACD ===>" ,macd_lst
	#maLine_lst[0][-2:] # MA4 line last 2 points
	#maLine_lst[1][-2:] # MA10 line last 2 points
	#utilities.ifLineCross(line2p,Line2p)
	MA4_10 = ifLineCross(maLine_lst[0],maLine_lst[1])
	MA10_40 = ifLineCross(maLine_lst[1],maLine_lst[2])
	MACD_DIF_DEA = ifLineCross(macd_lst[0],macd_lst[1])

	print "MA4_10",MA4_10
	print "MA10_40",MA10_40
	print "MACD DIF vs Dea",MACD_DIF_DEA
	utilities.pause()

def ifLineCross(upline,downline): # line np array
	"""captalized word means dealing Long terms """
	ifup_np = np.greater(upline,downline)
	#ifup = np.any(ifup_np)
	lst_ifup = list(ifup_np)
	ifdowncross = [True,False] == lst_ifup[-2:]
	ifupcross  = [False,True] == lst_ifup[-2:]
	ifup = np.all(ifup_np)
	print "Check bool array ifup_np, ifup", ifup_np , ifup
	if ifup:
		return "TOP"
	elif ifdowncross :
		return "downcross"
	elif  ifupcross :
		return  "upcross"
	elif [True,True] == lst_ifup[-2:] :
		return "TOP"
	elif [False,False] == lst_ifup[-2:] :
		return "LOW"

def checkToDeal(name, momentPrice):
	""" check the previous 1 day done transaction , decide when to bid again
	just for the thought of  higher frequency of transaction"""
	#global todayTask_lst
	name = name[2:]
	logger.info ( "\n ===Check Deal ====>> Name== %s"%name)
	dealtype = ''
	BidExecuted = False
	taskLst = DealDatum['todayTask_lst']
	check_lst = [row for row in taskLst if row[0] == name]
	check_lst.sort(lambda x, y: cmp(x[1], y[1])) # the min at first min==>->big sequence
	logger.info("check previous order list ===>%s<==="%check_lst)
	#signalTrigger(name)
	checkLatestTrend(name,momentPrice)

	print "pause inside checkToDeal function"
	utilities.pause()
	#logger.debug(" \n ==Show the loop List ==> \n %s "%check_lst)
	for order in check_lst:  #[['300070', -1, 46.83, 100.0, 4683.0], ['300...
		# stockCode , sellbuyFlag , dealATprice,Volumn = oder[0],order[1] , order[2], order[3]
		#only sell last bought, leave buying done manually!!r
		if order[3] < 0 :  # Cancelled Bidding
			continue  # next one, if vol < 0 means a canceled order
		elif order[1] == 1  :  # First check previous 1 days Sold Shares Volumn , buy again
			#if utilities.percentValue(0.997*momentPrice,order[2]) > 4.0 :   # !!!  need more consideration!!!!
			if (0.998*momentPrice-order[2])*order[3] < -159.0 :
				dealtype = "buy"
				if momentPrice * int(order[3]) > 5000.0 :    # should improve if split vol may cause a tax or fee rise!!!
					buy_vol = int(5000.0/momentPrice/100)*100+100  #ignore the available money
					deal_info = [order[0],momentPrice+0.1 ,buy_vol] #first to check
				else:
					deal_info = [order[0], momentPrice+0.1,int(order[3])]  #first to check
		elif order[1] == -1 :
			if (0.997*momentPrice-order[2])*order[3] > 99.0 :
				dealtype = "sell"
				#!!!order[2] far less thean momentPrice, Deal should be committed right now
				deal_info = [order[0],order[2] ,int(order[3])]
		if dealtype == '' :
			break   # out the loop ,cause same staock in min 2 max order
		else :
			callAutoTransaction(dealtype,deal_info)
			logger.info(">>====Sell stock done by Bidding \n %s====>>>"%deal_info)
			DealDatum['todayTask_lst'].remove(order)
			#todayTask_lst.remove(order)  # remove from the global task list
			BidExecuted =  True
			break            # just wait for nex moment another round deal check
	return BidExecuted

def perform(inc,name):
	"""perform cycle scheduled task of xxx seconds """
	#global SegmentData
	s.enter(inc,0,perform,(inc,name))
	oneline = getStockData(name)
	#logger.debug("oneline simulation from sina ===> \n %s "%oneline)
	MarketState['SegmentData'].append([name]+oneline) #may have errors in epoch_t
	#logger.debug("SegmentData content is ==> \n %s "% MarketState['SegmentData'])
	npArrayDatumAnalysis(name)


def getMadeDeals():
	""" click proxy terminal deal button and get made deal back"""
	#Py_autoit.clickBtn("deal")
	Task_lst = Py_autoit.getDealMade()
	return  Task_lst

def MergeDealsTasks(oldLst):
	"""  add Made Deals to todays_task_list , first should decide if new deals generated"""
	newLst = getMadeDeals()
	logger.info("GettingMade Deals==> %s <<=="%newLst)
	#print "GettingMade Deals==> %s <<=="%newLst
	#newDeals = [i for i,j in zip(newLst,oldLst) if i != j]
	newDeals = [i for i in newLst if i not in oldLst]
	if newDeals != [] :
		logger.info("new Made Deals ===> %s "%newDeals)
		DealDatum['todayTask_lst'] += newDeals
		logger.debug("todayTask list  updated!! ===> \n %s "%DealDatum['todayTask_lst'])
		AccState['dealsMade'] = newLst

def goGetMadeDeals(inc=1100):
	"""periodically getting Made deals, cycle scheduled task of 600 seconds """
	s.enter(inc,0,goGetMadeDeals,(1100,))
	oldLst = AccState['dealsMade']
	#logger.debug("===last Deal madelist ====>\n %s"oldLst)
	MergeDealsTasks(oldLst)

def perStockDatum(name):
	""" return Datum per stock code"""
	HqLst = MarketState['SegmentData']
	stockcode = name[2:]
	stock_temp_datum = [dAry[1:31] for dAry in HqLst if dAry[0]==name]
	np_stock_tmp_datum  = np.array(stock_temp_datum)
	return np_stock_tmp_datum

def minuteVol(name):
	""" 1 minute transaction Volumn  """
	np_stock_tmp_datum = perStockDatum(name)
	MomentHands_np= []
	if len(np_stock_tmp_datum) > 1:
		MomentHands_np = np.diff(np_stock_tmp_datum.T[7])
	return MomentHands_np

def getPrices(np_stock_tmp_datum):
	nowprice = np_stock_tmp_datum.T[2][-1]  #the momentPrice
	today_open = np_stock_tmp_datum.T[0][-1]  #the open
	pre_close = np_stock_tmp_datum.T[1][-1]  #the previous close
	high = np_stock_tmp_datum.T[3][-1]  #the moment  high Price
	low = np_stock_tmp_datum.T[4][-1]  #the moment low Price
	return nowprice,today_open,pre_close,high,low

def npArrayDatumAnalysis(name):
	""" Coming input data and check if actions be triggered"""
	#sort out per name stock datum
	Exed = False
	#meantime = stock_temp_datum[-1][-1]  # last should be the epoch_t
	#np_stock_tmp_datum  = np.array(stock_temp_datum)
	np_stock_tmp_datum = perStockDatum(name)
	npArrayLen = len(np_stock_tmp_datum)   # how many line in Array
	logger.info( "++++>>> %s <<<======>> %d items in storage!!"%(name, npArrayLen))
	nowPrice_np = np_stock_tmp_datum.T[2]
	nowprice = np_stock_tmp_datum.T[2][-1]  #the momentPrice

	if npArrayLen < 40:  #for the sake computing MovingAverage
		checkToDeal(name,nowprice) # check if to sell right now!!
	else:      # the first 1 hour ,we deal per last date trading info
		#print "Vol diff Array==>\n",np.diff(np_stock_tmp_datum.T[7])
		#MomentHands_np = np.diff(np_stock_tmp_datum.T[7])
		MomentHands_np = minuteVol(name)
		priceDelta_np =  np.diff(np_stock_tmp_datum.T[2]) #array of current price@now
		# priceMean = amount of money / totall Volumn
		priceMean_np = np.round(np_stock_tmp_datum.T[8]/np_stock_tmp_datum.T[7],2)
		max_price_np = nowPrice_np[np.argsort(nowPrice_np)[-13:]]
		min_price_np = nowPrice_np[np.argsort(nowPrice_np)[:8]]
		logger.debug("===Min price list===\n %s"%min_price_np)
		upRate,b,e = utilities.linearRegression(nowPrice_np[-30:])
		logger.debug("Go up Rate of the price === %s"%upRate)
		minClose_np = np_stock_tmp_datum.T[2]  #now price ,also latest Minute Close price
		boll_np = Math.BollLine(minClose_np,20) #
		[bollUp ,bMid , bollDwn] = boll_np[0],boll_np[1], boll_np[2]
		# give the basic reminding Sound Note , when nowprice cross the Boll Upper or lower lines
		cashFlow_np =  np.cumsum(priceDelta_np* MomentHands_np)
		logger.info("===!!!==approx cashFlow ====\n %s"%cashFlow_np[-8:])
		#VOL_end40_np = MomentHands_np[:-40]  #use the latest 40 values
		VOLtail_np = MomentHands_np   # use the whole set
		VOL_latest = MomentHands_np[-1]
		#below like array([7,8,9]) if narrow this array ,get max value
		#maxVols_np = VOL_end40_np[np.argsort(VOL_end40_np)[-4:]]
		maxVols_np = VOLtail_np[np.argsort(VOLtail_np)[-16:]]  # among the max 8 values
		#logger.info("Vol max 8 Array===> %s "%maxVols_np )
		HugVol = VOL_latest in maxVols_np
		#~ if HugVol:
			#~ print "++ Huge Volumn ===Latest Vol in max Array===> %s "%maxVols_np
			#~ maxVols_np
		TopPrice = nowprice in max_price_np
		LowPrice = nowprice in min_price_np
		FlowTop_moment_np = np.diff(cashFlow_np)
		FlowTop_np = FlowTop_moment_np[np.argsort(FlowTop_moment_np)[-10:]]
		#print "Flow Cash max === %s "%FlowTop_np
		logger.info("===Flow Cash max ===> \n %s "%FlowTop_np)
		HugFlow = FlowTop_moment_np[-1] in FlowTop_np
		nowprice,bolupper , bolower = nowPrice_np[-1],boll_np[0][-1],boll_np[2][-1]
		if (nowprice-bolupper) > 0.001:   # in the 2 cent range, near the upper
			logger.info( "!!!!Stock %s Up Cross Boll Upperline "%name)
			logger.debug("nowprice==>%s bolupper ==>%s"%(nowprice,bolupper))
			sellFlag = "-1"+name
			#peaksArray.append(sellFlag)
			DealDatum['peaksArray'].append(sellFlag)	# -1  mean sell      sellCont += 1
			logger.debug("+++ ===>the peaksArray ===> \n %S"%DealDatum['peaksArray'])
			Exed = checkToDeal(name,nowprice)
			if HugVol and TopPrice and upRate > 4.0:
				#BeepNote(200,100,9)
				logger.info( "!!!!Stock %s Should SELL OUT!!!! "%name)
				#though a little bit higher than current value, wait another up wave
				#then sell out, leave to the proxy designated value point for bidding
				#checkToDeal(name,nowprice)
				if DealDatum['peaksArray'].count(sellFlag) > 3 : # if sellCont > 4 :  #   if name+"3" in  operation Array
					volumn = int(5000.0/nowprice/100)*100+100  #ignore the available money
					sell_info = [stockcode,nowprice+0.12,volumn]
					callAutoTransaction("sell",sell_info) #!!waving Market Only ??
					logger.info(">>===Sell stock done by Bidding \n %s====>>>"%sell_info)
					#if Exed :  # if Deal executed then remove sell flag
					DealDatum['peaksArray'].remove(sellFlag)
					DealDatum['peaksArray'].remove(sellFlag)
					DealDatum['peaksArray'].remove(sellFlag)
					DealDatum['peaksArray'].remove(sellFlag)

					time.sleep(2)
					#sellCont = 0
		elif (nowprice-bolower) < 0.01:
			#BeepNote(400,800,10)
			#print "!!!!Stock %s Down Cross Boll Low"%name
			logger.info("!!!!Stock %s Down Cross Boll Low \n"%name)
			logger.debug("nowprice==>%s bolower ==>%s"%(nowprice,bolower))
			#print "+++ ===>the peaks Array ===>",peaksArray
			if HugVol  and LowPrice:
				buyFlag = "1"+name
				#DealDatum['peaksArray'].append([buyFlag])	  #	buyCont += 1
				DealDatum['peaksArray'] += [buyFlag]
				if DealDatum['peaksArray'].count(buyFlag) > 3:  #if buyCont > 2 :
					#print "!!!!Stock %s BUY IN!!!!!"%name
					logger.info( "!!!!Stock %s BUY IN  !!!!!  \n"%name)
					volumn = int(5000.0/nowprice/100)*100+100
					#no available cash caculate just wait to see how it react!!!
					bid_info = [stockcode,nowprice-0.1,volumn]
					callAutoTransaction("buy",bid_info) #!!waving Market Only ??
					#buyCont = 0
					logger.info(">>===Sell stock done by Bidding \n %s====>>>"%bid_info)
					DealDatum['peaksArray'].remove(buyFlag)
					DealDatum['peaksArray'].remove(buyFlag)
					DealDatum['peaksArray'].remove(buyFlag)
					DealDatum['peaksArray'].remove(buyFlag)
					time.sleep(2)


def getStockAcctTask():
	"""call transaction proxy to get today task list and
	return inhands stock code list  """
	global rDatum
	#"""余额:7869.99  可用:7869.99  可取:7869.99  参考市值:94205.00
	#资产:102074.99  盈亏:16446.59   """
	AccState['accAsset'] = [30000.0,30000.0,3000.0, 50000.0, 60000.0, 10000.0] # money in hand
	print DealDatum.keys()
	for key in DealDatum:
		print key , DealDatum[key]
	logger.debug(" ===account Asset===> \n  %s"%AccState['accAsset'])
	stockCodeList =  showCodeList(rDatum)
	DealDatum['todayTask_lst'] = [ ]
	#print "Today deal task list===>",todayTask_lst
	logger.info("====Today deal task list===>\n %s"%DealDatum['todayTask_lst'])
	#logger.info("====Account General info ===>\n %s"%accInfo_lst)
	return stockCodeList

def realtimeDataTracking(inc=60):
	""" tracking all the stocks in List ,and retrieve data and store and analysis """
	start = time.time()
	print('START:',time.ctime(start))
	MarketState['MarketCloseTime'] = DueTime(14,57)
	logger.debug("==MarketCloseTime==>%s"%MarketState['MarketCloseTime'])
	#utilities.pause()
	stockCodeList = getStockAcctTask()
	logger.info("==StockCodeList====> \n %s "%stockCodeList)
	#utilities.pause()
	j = 0   # delay counter
	for stockname in stockCodeList: #improving below
		#stockname = "sh"+stockcode if stockcode[:2] == "60" else "sz"+stockcode
		print "Enter debug mode .... "
		inc =1
		s.enter(2+3*j,1,perform,(inc,stockname))
	j +=1

	# get the Deals Done !!
#	s.enterabs(workAmTime+600,1,goGetMadeDeals,(1100,))
#	s.enterabs(workPmTime+60,1,goGetMadeDeals,(1100,))

	print s.queue
	logger.info("==Scheduled perform queue====> \n"%s.queue)
	t=threading.Thread(target=s.run)
	t.start()
	t.join()
#[['002008', 1700.0, 0.609, 10.27, 16424.06],
#['300122', 2100.0, 36.238, 35.81, -899.16],
#['300177', 100.0, 6.233, 15.45, 921.69]]
def callAutoGetHands():
	"""Simulating Call AutoIt get stocks in hands [[],[],[], ...] """
	global rDatum
	stocksInfoList  = []
	#Datum  = MarketState['SegmentData']
	stockCodeList =set([lst[0] for lst in rDatum])
	for stockname in stockCodeList :
		code = stockname[2:]
		stocksInfoList.append([code,1000.0,99.9,49.9, -999.0])
	return stocksInfoList

def DueTime(duetime_hour,duetime_min):
	""" input duetime hour ,min Output Should return duetime ,used by enterabs"""
	nowtime = time.localtime()
	yr,mo,dy = nowtime.tm_year,nowtime.tm_mon,nowtime.tm_mday #get now date
	duetime = time.mktime([yr,mo,dy,duetime_hour,duetime_min,0,0,0,0])
	return duetime

import unittest
from unittest import TestCase, TestSuite
class TestSepcifyTimeclass(TestCase):
	def setUp(self):
		print "setUp", hex(id(self))
	def tearDown(self):
		print "tearDown"
	def test_simulatedHq(self):
		testData = simulatedHq("sz300024","test")
		#for i in range(21):
		#	print testData.next()
		for line in simulatedHq("sz002008","test"):
			print line
	def test_getStockData(self):
		print getStockData("sz300024")
		print getStockData("sz300024")

	#def test_realtimeDataTracking(self):
	#	realtimeDataTracking(60)

#测试代码
if __name__ == "__main__":
	loadfromFile()
	#print rDatum
	stockList = showCodeList(rDatum)
	print stockList
	print  callAutoGetHands()
	FeaturesOfHoldings(stockList)
	realtimeDataTracking(60)
	#unittest.main()
	#########################################################
