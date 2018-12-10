# coding=gbk
import time
import datetime
import sched
import threading
from chorelib import *
import os


# initiating the sched module scheduler
sch = sched.scheduler(time.time, time.sleep)
# logger = utilities.initlog()


class MinuteGrabRealtimeData:
    def __init__(self, stocklist):
        self.SegmentData = []
        self.MarketCloseTime = DueTime(15, 00)
        self.stockCodeList = stocklist

    def emptySegmentData(self):
        self.SegmentData = []

    def perform(self, inc, name):
        """perform cycle scheduled task of xxx seconds """
        if AtTransactionTime() in ["noon", "after"]:
            for task in s.queue:
                if task.time - time.time() < 300:  # remove the am event from stack
                    sch.cancel(task)
                    print "scheduled latest removed by Close!!,clean up ready,save2db !!"
            SaveRec2db(self.SegmentData)
            self.emptySegmentData()
            # return 1
        sch.enter(inc, 0, self.perform, (inc, name))
        oneline = getStockData(name)
        if not oneline:
            print "Previous getting url sinaHq Errors! ,return 0 ,do nothing!!"
            return 0
        # replace the last 2 pos gotten with the epoch time elapsed
        # bid_t = oneline[-2] + " " + oneline[-1]  #last 2 is date and time
        self.SegmentData.append([name] + oneline)
        timepoint = time.localtime()
        if timepoint.tm_min % 5 == 0:
            print "Time to Write to sqlite ,and empty this SegmentData Array!!!"
            SaveRec2db(self.SegmentData)
            self.emptySegmentData()

    def realtimeDataTracking(self, inc=60):
        """ tracking all the stocks in List ,and retrieve data and store and analysis """
        start = time.time()
        print('grabbing START:', time.ctime(start))
        # ���õ���
        # Below code should be observed if duetime past ,should executed immediately
        workAmTime = DueTime(9, 30)
        workPmTime = DueTime(13, 00)
        print workAmTime

        j = 0  # delay counter
        for stockcode in self.stockCodeList:  # improving below
            stockname = "sh" + stockcode if stockcode[:2] == "60" else "sz" + stockcode
            sch.enterabs(workAmTime + 40 * j, 1, self.perform, (inc, stockname))
            sch.enterabs(workPmTime + 40 * j, 1, self.perform, (inc, stockname))
            j += 1

        print sch.queue
        # �����߳�
        t = threading.Thread(target=sch.run)  # ͨ�����캯�������߳�
        t.start()  # �߳�����
        t.join()  # �����߳�


# ���Դ���
if __name__ == "__main__":
    # os.chdir('D:/Runnings/')
    stockCodeList = ["300070", "002594", "002415", "601336", "601727"]
    now = datetime.datetime.now()
    print os.getcwd()
    print str(now) + "\n"
    mgrd = MinuteGrabRealtimeData(stockCodeList)
    mgrd.realtimeDataTracking(59)
