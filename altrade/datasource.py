#
# datasource.py
#
import datetime
import os
import os.path
import pandas as pd
import numpy as np
from abc import ABCMeta, abstractmethod
from event import MarketEvent
from stockdata import minuteOfStock
import Queue


class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OLHCVI) for each symbol requested.

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or fewer if less bars are available.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bar to the latest symbol structure
        for all symbols in the symbol list.
        """
        raise NotImplementedError("Should implement update_bars()")


class HistoricDataHandler(DataHandler):
    """
    HistoricDataHandler is designed to read files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """

    def __init__(self, events, symbol_list):
        """
        Initialises the historic data handler by requesting
        the location of the data files and a list of symbols.
        Parameters:
        events - The Event Queue.
        symbol_list - A list of symbol strings.
        """
        self.events = events
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of
        (sybmbol, datetime, open, low, high, close, volume).
        """
        for b in self.symbol_data[symbol]:
            # print "b  ===>" , b
            yield tuple([symbol, datetime.datetime.strptime(b[
                0], '%Y-%m-%d %H:%M:%S'), b[1][0], b[1][1], b[1][2], b[1][3],
                         b[1][4]])

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print "That symbol is not available in the historical data set."
        else:
            return bars_list[-N:]

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = self._get_new_bar(s).next()
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())


class HistoricCSVDataHandler(HistoricDataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """

    def __init__(self, events, csv_dir, symbol_list):
        HistoricDataHandler.__init__(self, events, symbol_list)
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.
        It will be assumed that all files are of the form
        'symbol.csv', where symbol is a string in the list.

        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        self.csv_dir = csv_dir
        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting
        them into pandas DataFrames within a symbol dictionary.

        For this handler it will be assumed that the data is
        taken from DTN IQFeed. Thus its format will be respected.
        """
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on date
            self.symbol_data[s] = pd.io.parsers.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s),
                header=0,
                index_col=0,
                names=['datetime', 'open', 'high', 'low', 'close', 'volume'])

            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []

        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(
                index=comb_index,
                method='pad').iterrows()


class HistoricTDXDataHandler(HistoricDataHandler):
    """
    Now only read the minutes bars, for the sake of the simulation
    """

    def __init__(self, events, file_dir, symbol_list):
        """ Parameters :
            file_dir : TDX datafiles location :
            'D:\\tools\\new_tdx\\vipdoc\\sz\\minline'
        """
        HistoricDataHandler.__init__(self, events, symbol_list)
        self.file_dir = file_dir
        # for the concern of test running,
        # load this not in production mode
        # self._open_convert_tdx_files()

    def _makefullname_(self, symbol):
        """ make full filename,
        Parameters symbol : like 002594 path and name
        return : ".//path/fullfilename" Absolute path name
        """
        fullname = ""
        first2 = symbol[:2]
        validprefix = ["99","60","30","00"]
        assert first2 in  validprefix
        pre = "sh" if first2 in ["99","60"] else  "sz"
        suffix = "lc1"
        fullname = self.file_dir + "//" + pre + symbol + "." + suffix
        return fullname

    def _open_convert_tdx_files(self):
        """
        Opens the TDX files from the data directory, converting
        them into pandas DataFrames within a symbol dictionary.
        """
        comb_index = None
        for s in self.symbol_list:
            # Load the TDX file with no header information, indexed on date
            fullname = self._makefullname_(s)
            _temp = minuteOfStock(fullname)
            self.symbol_data[s] = _temp.DF
            # print self.symbol_data[s][:5]
            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []

        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(
                index=comb_index,
                method='pad').iterrows()

    def load_bars(self, n=100):
        """
        :param n:  previous n bars
        :return:
        """
        for i in range(0, n):
            for s in self.symbol_list:
                try:
                    bar = self._get_new_bar(s).next()
                except StopIteration:
                    self.continue_backtest = False
                else:
                    if bar is not None:
                        self.latest_symbol_data[s].append(bar)


if __name__ == '__main__':
    datadir = ".\\data\\"
    events = Queue.Queue()
    symbol_list = ["300024"]
    testRobot = HistoricCSVDataHandler(events, datadir, symbol_list)
    print events
    print testRobot.symbol_data
    testRobot.update_bars()
    print events.get()
    print testRobot.get_latest_bars("300024")
    testRobot.update_bars()
    print events.get()
    print testRobot.get_latest_bars("300024")
    print "==============================="
    datadir = "D:\\tools\\new_tdx\\vipdoc\\sz\\minline"
    testRobot = HistoricTDXDataHandler(events, datadir, symbol_list)
    testRobot.update_bars()
    print events.get()
    print testRobot.get_latest_bars("300024")
    testRobot.update_bars()
    print testRobot.get_latest_bars("300024")
    print "----below get latest 10 bars------"
    print testRobot.get_latest_bars("300024", 4)
    # pdDF = pd.DataFrame(testRobot.symbol_data["300024"])
    # print pdDF[-5:]
    # print testRobot.symbol_data["300024"]
    for i in range(0, 9):
        testRobot.update_bars()
    cols = ['code', 'datetime', 'open', 'high', 'low', 'close', 'volume']
    bars = testRobot.get_latest_bars("300024", 10)
    print np.array(bars).T[2]
    tmpdf = pd.DataFrame(testRobot.get_latest_bars("300024", 10), columns=cols)
    print tmpdf
    # print testRobot.symbol_data["300024"]
