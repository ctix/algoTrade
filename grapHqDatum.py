# -*- coding:utf-8 -*-

import time
import datetime
import sched
import numpy as np
import threading
import pandas as pd
import chorelib
import os


# initiating the sched module scheduler
sch = sched.scheduler(time.time, time.sleep)
# logger = utilities.initlog()
columns =  ['stockcode','open', 'close','price','high', 'low',
            'buy1','buy2','vol', 'amount', 'B1V','B1', 'B2V',
            'B2','B3V','B3','B4V','B4', 'B5V','B5','S1V', 'S1',
            'S2V','S2', 'S3V','S3','S4V','S4','S5V','S5','DateTime' ]

cols_use =  ['stockcode','open', 'close','price','high', 'low','vol', 'DateTime']

class TasksPool:
    """ mutil-rows Array to store todo tasks"""
    def __init__(self, tasks):
        self.tasks = tasks
        if self.validate_(tasks):
            self.tasks = tasks

    def validate_(self, tasks):
        """ if task is valid ,ie task ["sell","002594", 59.35, 300]"""
        error_msg = ""
        for task in tasks:
            cmd, stockcode, atprice, volume = task
            if cmd not in ["sell", "buy"]:
                error_msg = "\n===>invalid command, not sell or buy"
            elif type(atprice) is not float:
                error_msg = "\n===>invalid atprice, must be float"
            elif volume % 100:
                error_msg = "\n===>invalid volume, must be 100 times"
        if not error_msg:
            return True
        else:
            print error_msg
            return False

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        self.tasks.remove(task)

    def filter_name(self, name):
        return [t for t in self.tasks if t[1] == name[2:]]


class MinuteGrabRealtimeData:
    def __init__(self,stock_list):
        self.Segment_Data = []
        self.MarketCloseTime = chorelib.DueTime(15, 00)
        self.stockCodeList = stock_list
        self.MarketDataFrame  = pd.DataFrame(columns=columns)
        self.MDF_counter = 0

    def emptySegmentData(self):
        self.Segment_Data = []

    def getStockDataFrame(self, stockcode):
        """get stock DataFrame by stock code """
        # TODO : filter dataframe by 1 column
        DF = self.MarketDataFrame
        df = DF[DF.stockcode == stockcode]
        return df[['open', 'high', 'low', 'close', 'vol']]

    def add2DataFrame(self, tick_data):
        """tickdata is list [stockcode, open, ...]"""
        # connect and read data
        # dtime = pd.Timestamp(tick_data[-1])
        npary = np.array(tick_data[:31])
        self.MarketDataFrame.loc[self.MDF_counter] = npary
        self.MDF_counter += 1
        print "Running MDF_counter--%s==>>"%self.MDF_counter
        # MarketData.index = MarketData["DateTime"]
        # MarketData


    def perform(self, inc, name):
        """perform cycle scheduled task of xxx seconds """
        if chorelib.AtTransactionTime() in ["noon", "after"]:
            for task in sch.queue:
                if task.time - time.time() < 300:  # remove the am event from stack
                    sch.cancel(task)
                    print "scheduled latest removed by Close!!,clean up ready,save2db !!"
            chorelib.SaveRec2db(self.Segment_Data)
            self.emptySegmentData()
            return 1
        sch.enter(inc, 0, self.perform, (inc, name))
        oneline = chorelib.getStockData(name)
        if not oneline:
            print "Previous getting url sinaHq Errors! ,return 0 ,do nothing!!"
            return 0
        # replace the last 2 pos gotten with the epoch time elapsed
        # bid_t = oneline[-2] + " " + oneline[-1]  #last 2 is date and time
        print "online from getStockData by name\n ", oneline
        stockcode = name[2:] # for consistence use stockcode
        tick_line = [stockcode] + oneline
        self.Segment_Data.append(tick_line)
        self.add2DataFrame(tick_line)
        timepoint = time.localtime()
        if timepoint.tm_min % 5 == 0:
            print "Time to Write to sqlite ,and empty this Segment_Data Array!!!"
            chorelib.SaveRec2db(self.Segment_Data)
            self.emptySegmentData()
            print "the last in DataFrame==>\n",self.MarketDataFrame.tail(2)

    def realtimeDataTracking(self, inc=60):
        """ tracking all the stocks in List ,and retrieve data and store and analysis """
        start = time.time()
        print('grabbing START:', time.ctime(start))
        # 锟斤拷锟矫碉拷锟斤拷
        # Below code should be observed if duetime past ,should executed immediately
        workAmTime = chorelib.DueTime(9, 30)
        workPmTime = chorelib.DueTime(13, 00)
        print workAmTime

        j = 0  # delay counter
        for stockcode in self.stockCodeList:  # improving below
            stockname = "sh" + stockcode if stockcode[:2] == "60" else "sz" + stockcode
            sch.enterabs(workAmTime + 40 * j, 1, self.perform, (inc, stockname))
            sch.enterabs(workPmTime + 40 * j, 1, self.perform, (inc, stockname))
            j += 1

        print sch.queue
        # 锟斤拷锟斤拷锟竭筹拷
        t = threading.Thread(target=sch.run)  # 通锟斤拷锟斤拷锟届函锟斤拷锟斤拷锟斤拷锟竭筹拷
        t.start()  # 锟竭筹拷锟斤拷锟斤拷
        t.join()  # 锟斤拷锟斤拷锟竭筹拷




# 锟斤拷锟皆达拷锟斤拷
if __name__ == "__main__":
    stockCodeList = ["002594", "002415", "601336", "002001"]
    now = datetime.datetime.now()
    print os.getcwd()
    print str(now) + "\n"
    mgrd = MinuteGrabRealtimeData(stockCodeList)
    mgrd.realtimeDataTracking(59)


    # TODO : 1, get realtime data to [stockcode]+ tickdata
    # into the DataFrame
    # 2, Consider save it to sqlite every 5min
    # 3, Use the DataFrame to calculate the cci/trends/
     # 3.1 volumn brust compare to the pervious statistics
