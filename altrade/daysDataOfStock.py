import numpy as np
import datetime
import utilities


class daysDataOfStock:
    def __init__(self, fullname, latestNDays=60):
        self.fullname = fullname
        # stockday = np.dtype({
        # 'names':['date', 'open', 'high', 'low', 'close', 'amount',
        # 'vol','lastClose'],
        # 'formats':['i','i', 'i','i', 'i','i', 'i','i']})
        # self.datum1d=np.fromfile(self.fullname,dtype = stockday)
        self.datum1d = np.fromfile(self.fullname, dtype=int)
        self.latestNDays = latestNDays
        nrows = int(self.datum1d.size / 8)
        self.datum2d = self.datum1d.reshape(nrows, 8)
        if (nrows < latestNDays):
            # if the stock recent IPO and less than latestNdays on market
            self.datumLast = self.datum2d[-1 * nrows:]
        else:
            self.datumLast = self.datum2d[-1 * latestNDays:]

    def getAllData(self):
        """get all data from the file ,from start to end!! """
        # self.datum1d=np.fromfile(self.fullname,dtype = int)
        # return self.datumLast
        return self.datum2d

    def checkDivideRight(self):
        """if Divide Right found ,then minus the delta from the day ahead """
        npOpens = self.datumLast.T[1][1:]  # open np array
        npCloses = self.datumLast.T[4][:-1]  # Close np array
        dateList = self.datumLast.T[0][1:]
        jumpRates = (npCloses - npOpens) / np.float32(npCloses)
        loc = jumpRates.argmax()
        if jumpRates[loc] > 0.11:  #if next day Open jump down 10.1percent
            delta = npCloses[loc] - npOpens[loc]
            print "DR delta is %d" % delta
            self.datumLast[:, 1:5][:loc + 1] = self.datumLast[:, 1:
                                                              5][:loc +
                                                                 1] - delta
            print "function checkDivideRight() done, DR@ %d!!!" % dateList[loc]
        else:
            print "No DR found!!!"
        #return self.datumLast

    def getFromDateDatum(self, adate):
        """ get dataset from the designated date to the end """
        indx = np.abs(self.datum2d[:, 0] - adate).argmin()
        return self.datum2d[indx:]

    def getPrevDateDatum(self, mydate, numOfDays):
        """ get dataset previous the date designated! """
        indx = np.abs(self.datum2d[:, 0] - mydate).argmin()
        print "<---=>indx", indx, self.datum2d[:, 0][indx]
        # self.datum2d[:,0][indx] > mydate
        if self.datum2d[:, 0][indx] > mydate:  #include the designated date
            indx -= 1
        #todo : 1 or 2 days after appears!!! :-(
        #~ print "<---=>indx",indx
        startpoint = indx + 1 - numOfDays if indx > numOfDays else 0
        assert startpoint >= 0
        self.datumLast = self.datum2d[ startpoint:indx ]
        # indx+1 include the day,should be indx only
        #print "the length of the daily datum %d"%len(self.datumLast),mydate
        return self.datumLast

    def getLatestNdaysMatrix(self, days=60):
        if self.latestNDays > days:
            return self.datum2d[-1 * days:]
        else:
            return 0
        #~ return self.datumLast

    def getDateBetween(self, frdate, endate):
        """ get stock data between eg. 20101123 to 20110401  """
        fd = self.find_nearest_dateindex(frdate) if frdate <> 0 else 0
        ed = self.find_nearest_dateindex(endate)
        datum1d = self.datum1d[fd:ed + 8]
        nrows = int(datum1d.size / 8)
        datum2d = datum1d.reshape(nrows, 8)
        return datum2d
        # return self.datum2d[fd:ed+8]

    def find_nearest_date(self, dateintvalue):
        """  find nearest data date ! if it 's not exist !  or return the date index """
        idx = (np.abs(self.datum1d - dateintvalue)).argmin()
        datefnd = self.datum1d[idx]
        if utilities.validDate(datefnd):
            return datefnd if (idx % 8) == 0 else 0
        else:
            return 0

    def find_nearest_dateindex(self, dateintvalue):
        """  find nearest data date ! if it 's not exist !  or return the date index """
        idx = (np.abs(self.datum1d - dateintvalue)).argmin()
        datefnd = self.datum1d[idx]
        if utilities.validDate(datefnd):
            return idx if (idx % 8) == 0 else 0
        else:
            return 0


    def scanDateContinuous(self, dayspan):
        """ see if each date is continuous, span less than 20 days is valid"""
        DateList = self.getColumnArray(0)
        previousdate = DateList[0]
        for adate in DateList[1:]:
            if utilities.checkDateSpan(previousdate, adate) < dayspan:
                previousdate = adate
            else:
                print "date span greater than %d days" % dayspan, previousdate, adate
                return 0
        return 1

    def getColumnArray(self, col):
        """ get transpose of a matrix column :
        formats: date open high low close  amount vol  lastClose """
        #~ transArray = self.datum2d.T
        transArray = self.datumLast.T
        return transArray[col]

    def getLastDate(self):
        """ return Latest Date as yyyymmdd"""
        print "About to print getLastDate"
        return self.datumLast.T[0][-1]

    def getDateSpan(self):
        """ return  Date Span as [yyyymmdd,yyyymmdd]"""
        print "About to print getDateSpan"
        endate = self.datum2d.T[0][-1]
        firstdate = self.datum2d[0][0]
        return [firstdate, endate]

    def getWeekDatum(self):
        """ deprecated ! Use Pandas module to get/sum up Weekly datum
        return weekly sum datum from daybyday data
        """
        weekDatum = []
        dateList = self.getColumnArray(0)
        weekindexlist = utilities.weekIndexList(dateList)
        for i in range(len(weekindexlist) - 1):
            start, end = weekindexlist[i], weekindexlist[i + 1]
            weeklastdate = self.getColumnArray(0)[end - 1]
            weekOpen = self.getColumnArray(1)[start]
            weekHigh = max(self.getColumnArray(2)[start:end])
            weekLow = min(self.getColumnArray(3)[start:end])
            weekClose = self.getColumnArray(4)[end - 1]
            #~ print start,end,self.getColumnArray(6)[start:end]
            weekVol = sum(self.getColumnArray(6)[start:end])
            weekDatum.append([weeklastdate, weekOpen, weekHigh, weekLow,
                              weekClose, weekVol])

        last = weekindexlist[-1]
        weeklastdate = self.getColumnArray(0)[-1]
        weekOpen = self.getColumnArray(1)[last]
        weekHigh = max(self.getColumnArray(2)[last:])
        weekLow = min(self.getColumnArray(3)[last:])
        weekClose = self.getColumnArray(4)[-1]
        weekVol = sum(self.getColumnArray(6)[last:])
        weekDatum.append([weeklastdate, weekOpen, weekHigh, weekLow, weekClose,
                          weekVol])

        return weekDatum

    def BBiBoll(self):
        pass


if __name__ == "__main__":
    unittest.main()
