#
# portfolio.py

import datetime
import numpy as np
import pandas as pd
import Queue

from abc import ABCMeta, abstractmethod
from math import floor

from event import FillEvent, OrderEvent


class Portfolio(object):
    """
    The Portfolio class handles the positions and market
    value of all instruments at a resolution of a "bar",
    i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders based on the portfolio logic.
        """
        raise NotImplementedError("Should implement update_signal()")

    @abstractmethod
    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings from a FillEvent.
        """
        raise NotImplementedError("Should implement update_fill()")


class NaivePortfolio(Portfolio):
    """
    The NaivePortfolio object is designed to send orders to
    a brokerage object with a constant quantity size blindly,
    i.e. without any risk management or position sizing. It is
    used to test simpler strategies such as BuyAndHoldStrategy.
    """

    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        """
        Initialises the portfolio with bars and an event queue. Also includes
        a starting datetime index and initial capital (USD unless otherwise stated).
        Parameters:
        bars - The DataHandler object with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital
        self.all_positions = self.construct_all_positions()
        self.current_positions = dict((k, v)
                                      for k, v in [(s, 0)
                                                   for s in self.symbol_list])

        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

    def construct_all_positions(self):
        """
        Constructs the positions list using the start_date
        to determine when the time index will begin.
        """
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 5.0
        d['total'] = self.initial_capital
        return [d]

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all symbols.
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 5.0
        d['total'] = self.initial_capital
        return d

    def update_timeindex(self, event):
        """
        Adds a new record to the positions matrix for the current market data bar.
        This reflects the PREVIOUS bar, i.e. all current market data at this stage
        is known (OLHCVI). Makes use of a MarketEvent from the events queue.
        """
        bars = {}
        for sym in self.symbol_list:
            bars[sym] = self.bars.get_latest_bars(sym, N=1)

        # Update positions
        dp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dp['datetime'] = bars[self.symbol_list[0]][0][1]

        for s in self.symbol_list:
            dp[s] = self.current_positions[s]
            # TODO: Given T+1 rule, position must have a quantity of today's available

            # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        dh = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dh['datetime'] = bars[self.symbol_list[0]][0][1]
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_list:
            # Approximation to the real value
            market_value = self.current_positions[s] * bars[s][0][5]
            dh[s] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill):
        """
        Takes a FilltEvent object and updates the position matrix
        to reflect the new position.

        Parameters:
        fill - The FillEvent object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update positions list with new quantities
        self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def update_holdings_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the holdings matrix
        to reflect the holdings value.

        Parameters:
        fill - The FillEvent object to update the holdings with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bars(fill.symbol)[0][5]  # Close price
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        """
        Simply transacts an OrderEvent object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The SignalEvent signal information.
        """
        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength

        mkt_quantity = floor(strength) * 100
        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')

        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.equity_curve = curve


class TrendPortfolio(Portfolio):
    """
    The TrendPortfolio object is designed to send orders to
    a brokerage object with a caculated quantity ,
    i.e. with risk management and position sizing. It is
    used to test strategies such as BollingStrategy.
    """

    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        """
        Initialises the portfolio with bars and an event queue. Also includes
        a starting datetime index and initial capital (USD unless otherwise stated).
        Parameters:
        bars - The DataHandler object with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital
        self.current_positions = self.get_inintal_positions()
        self.all_filled_orders = []  #store all filled orders
        self.all_positions = self.construct_all_positions()
        self.available_positions = self.current_positions.copy(
        )  # for T+1 rules
        self.current_holdings = self.construct_current_holdings()
        self.all_holdings = self.construct_all_holdings()
        self.port_state = self.initial_port_state()

    def initial_port_state(self):
        """
        Not include cash which is in holdings as a total attribute !!
        :return: np.array(["datetime","code","hold@start","available","cost per share" \
                 "cost total" ,"mktvalue", "profit", "freeze number" ])
        """
        port_state = []
        for s in self.symbol_list:
            _bar = self.bars.get_latest_bars(s)  # Close price
            _stockcode = s
            _datetime = _bar[0][1]
            _preclose = _bar[0][5]  # as percost @beginning
            _tothold = self.current_positions[s]
            _available = _tothold
            _mktvalue = _tothold * _preclose
            _totcost = _mktvalue * (1.0003)
            _profit = 0
            _incoming = 0  # buying number of shares ,freezed, locked in t+1
            _cash = self.current_holdings['cash']
            # [_datetime, code, totalholding, available,percost, cost, mktvalue,
            # profit, incoming]
            _state = [_datetime, _stockcode, _tothold, _available, _preclose,
                      _totcost, _mktvalue, _profit, _incoming, _preclose,
                      _cash]
            port_state.append(_state)
        return port_state
        # TODO : think twice if really need this numpy array

    def get_inintal_positions(self):
        """  Imitating
        Getting the starting positions list using Windows transaction Proxy
        """
        # Suppose initial volume a thousand
        pos_dic = self.current_positions = \
            dict((k, v) for k, v in [(s, 1000) for s in self.symbol_list])
        return pos_dic

    def construct_all_positions(self):
        """
        Constructs the positions list using the start_date
        to determine when the time index will begin.
        """
        d = self.get_inintal_positions()
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        # d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d = self.current_holdings
        d['datetime'] = self.start_date
        return [d]

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all symbols.
        """
        # Approximation to the real value,  each holding market value
        bars = {}
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 5.0  # at least 5 yuan
        d['total'] = self.initial_capital
        for s in self.symbol_list:
            bars[s] = self.bars.get_latest_bars(s, N=1)
            market_value = self.current_positions[s] * bars[s][0][5]
            d[s] = market_value
            d['total'] += market_value
        return d

    def update_timeindex(self, event):
        """
        Adds a new record to the positions matrix for the current market data bar.
        This reflects the PREVIOUS bar, i.e. all current market data at this stage
        is known (OLHCVI). Makes use of a MarketEvent from the events queue.
        """
        bars = {}
        samePosition = True
        for sym in self.symbol_list:
            bars[sym] = self.bars.get_latest_bars(sym, N=1)
            # new day holdings and position changed
            newdaytime = bars[sym][0][1].strftime("%Y%m%d%H%M")
            #if bars[sym][0][1].strftime("%H%M") == "0931":
            if newdaytime[-4:] == "0931":
                print "======== New Trading day ===>>%s========" % newdaytime
                print "Current Pos", self.current_positions
                print "All Pos ,last", self.all_positions[-1]
                # self.all_positions[-1][sym] = self.current_positions[sym]
                self.available_positions[sym] = self.current_positions[sym]
                print "Available Pos :", self.available_positions

            # if position is the same then ignore and break
        self.update_append_holdings(bars)  # update and append holdings
        self.update_append_positions(bars)

    # def cut_profit_lost(self):
    #     """ Cut profit and lost
    #     :return: if symbol values/profit/lost decrease
    #     """
    #     for sym in self.symbol_list:
    #         bars[sym] = self.bars.get_latest_bars(sym, N=1)
    #         # new day holdings and position changed
    #         if bars[sym][0][1].strftime("%H%M") == "0931":
    #             print "=========== New Trading day ==========="
    #             print "Current Pos", self.current_positions
    #             print "All Pos ,last", self.all_positions[-1]
    #             # self.all_positions[-1][sym] = self.current_positions[sym]
    #             self.available_positions[sym] = self.current_positions[sym]

    def update_append_positions(self, bars):
        # Update positions
        dp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dp['datetime'] = bars[self.symbol_list[0]][0][1]

        for s in self.symbol_list:
            dp[s] = self.current_positions[s]

        # Append the current positions
        max_length = 120  # keep max 120 positions history
        self.all_positions.append(dp)
        length = len(self.all_positions)
        if length > max_length:
            self.all_positions.pop(0)

    def update_append_holdings(self, bars):
        # Update holdings
        dh = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dh['datetime'] = bars[self.symbol_list[0]][0][1]
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_list:
            # Approximation to the real value,  each holding market value
            market_value = self.current_positions[s] * bars[s][0][5]
            dh[s] = market_value
            dh['total'] += market_value

        self.current_holdings = dh
        # Append the current holdings
        self.all_holdings.append(dh)
        max_length = 60  # keep max 60 items
        length = len(self.all_holdings)
        if length > max_length:
            self.all_holdings.pop(0)
            # TODO : if big jump found, %3 up/down then trigger what signals

    def get_port_state(self, symbol):
        """
        :param symbol:  stock symbol
        :return: return port_state by symbol
        """
        return [ps for ps in self.port_state if ps[1] == symbol]

    # TODO : where to put ,On which events,  and when Order filled updated
    # Nov, 4th 1621 Memo , to be continued
    def update_port_state(self, fill):
        # Update portfolio state
        # [_datetime, code, totalholding, available,percost, cost, mktvalue,
        # profit, incoming]
        #  Check whether the fill is a buy or sell
        _state = []
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
            _incomming = fill.quantity
        if fill.direction == 'SELL':
            fill_dir = -1
            _incomming = -1 * fill.quantity
        _datetime = fill.timeindex
        #_cash = self.current_holdings['cash']

        _preclose = self.bars.get_latest_bars(fill.symbol)[0][5]  # Close price
        #previous cost
        _precost = self.get_port_state(fill.symbol)[-1][5]
        _total_pos = self.current_positions[fill.symbol]
        _market_value = _total_pos * _preclose
        _available = self.available_positions[fill.symbol]
        # spend or gain money amount
        _amount = fill_dir * fill.fill_cost * fill.quantity
        # _percost algorithms  = sum(pi*ni)/sum(ni)
        # when order filled so as to cause percost change
        _cost = _precost + _amount + fill.commission
        # when all sold
        _percost = _cost / _total_pos if _total_pos > 0 else 0
        _profit = _market_value - _cost
        _cash = self.current_holdings['cash']
        _state = [_datetime, fill.symbol, _total_pos, _available, _percost,
                  _cost, _market_value, _profit, _incomming, _preclose, _cash]

        # Append the current holdings
        #self.port_state = _state
        self.port_state.append(_state)
        max_length = 2048  # keep max 2048 items
        length = len(self.port_state)
        if length > max_length:
            self.all_holdings.pop(0)
            # TODO : if big jump found, %3 up/down then trigger what signals

    def update_positions_from_fill(self, fill):
        """
        Takes a FilltEvent object and updates the position matrix
        to reflect the new position.

        Parameters:
        fill - The FillEvent object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
            # T+1 rule : Can't sell the quantity of today buy
            self.available_positions[fill.symbol] += fill_dir * fill.quantity

        # Update positions list with new quantities
        self.current_positions['datetime'] = fill.timeindex
        self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def update_filled_orders(self, fill):
        """  save all the filled order in a list ===> ready convert to numpy array
        :param fill:  filled order
        :return:  self.all_filled_orders list
        """
        amount = fill.fill_cost * fill.quantity + fill.commission
        _filled_order = [fill.timeindex, fill.symbol, fill.direction,
                         fill.fill_cost, fill.quantity, fill.commission,
                         amount]
        self.all_filled_orders.append(_filled_order)

    def update_holdings_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the holdings matrix
        to reflect the holdings value.

        Parameters:
        fill - The FillEvent object to update the holdings with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bars(fill.symbol)[0][5]  # Close price
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings['datetime'] = fill.timeindex
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            print "Current Positions=====>", self.current_positions
            print "Available Pos==>", self.available_positions
            self.update_holdings_from_fill(event)
            print "Current cash=====>", self.current_holdings["cash"]
            self.create_equity_curve_dataframe()
            print "=" * 10 + 'EquityCurve' + "=" * 10, self.equity_curve[
                "equity_curve"][-1]
            self.update_filled_orders(event)
            self.update_port_state(event)
    # Nov. 4th 1619 === how and when to update the portofolio state
    #TODO Done: when Order filled, then update portofolio state

    # def ifTrade(self, signal):
    #
    #     if direction == 'LONG' and cur_quantity == 0:
    #         order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
    #     if direction == 'SHORT' and cur_quantity == 0:
    #         order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')
    #
    #     if direction == 'EXIT' and cur_quantity > 0:
    #         order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
    #     if direction == 'EXIT' and cur_quantity < 0:
    #         order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
    #     return order

    def generate_trend_order(self, signal):
        """
        Simply transacts an OrderEvent object as a trading quantity
        sizing of the signal object, with risk management or
        position sizing considerations.

        Parameters:
        signal - The SignalEvent signal information.
        """
        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength
        price = signal.price
        datetime = signal.datetime
        # TODO : above try to set datetime in signal or event

        # mkt_quantity = floor(strength)*100
        trade_quantity = floor(strength) * 100
        # cur_quantity = self.current_positions[symbol]
        cur_quantity = self.available_positions[symbol]
        order_type = 'MKT'
        # order_type = 'LMT'

        if direction == 'LONG':
            cash_paid = trade_quantity * price * 1.0003  # add fee
            if self.current_holdings["cash"] - cash_paid >= 0.0:
                order = OrderEvent(symbol, price, order_type, trade_quantity,
                                   'BUY', datetime)
            else:
                print "!!No Cash!! ==> current cash:", self.current_holdings[
                    "cash"]

        if direction == 'SHORT':
            if self.available_positions[symbol] - trade_quantity >= 0:
                order = OrderEvent(symbol, price, order_type, trade_quantity,
                                   'SELL', datetime)
            else:
                print "!!No Available !! ==> current pos:", self.available_positions[
                    symbol]
        # TODO: EXIT to sell out all of the holdings of symbol stock
        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, price, order_type, abs(cur_quantity),
                               'SELL', datetime)
        #
        # if direction == 'LONG' and cur_quantity == 0:
        #     order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        # if direction == 'SHORT' and cur_quantity == 0:
        #     order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')
        #
        # if direction == 'EXIT' and cur_quantity > 0:
        #     order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        # if direction == 'EXIT' and cur_quantity < 0:
        #     order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_trend_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.equity_curve = curve
