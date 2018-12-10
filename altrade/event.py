#
# event.py
#


class Event(object):
    """
    Event is base class providing an interface for all subsequent (inherited) events, that will trigger further events in the trading infrastructure.
    """
    pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with corresponding bars.
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = 'MARKET'


class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object. 
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, symbol, datetime, signal_type, strength, price):
        """
        Initialises the SignalEvent.

        Parameters:
        symbol - The ticker symbol, e.g. 'GOOG'.
        datetime - The timestamp at which the signal was generated.
        signal_type - 'LONG' or 'SHORT'.
        """
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength
        self.price = price


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit), price
    quantity and a direction.
    """

    def __init__(self, symbol, price, order_type, quantity, direction,
                 datetime):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has a quantity (integral) and its direction ('BUY' or
        'SELL').
        Parameters:
        symbol - The instrument to trade.
        price - The price to execute the order
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        datetime - The timestamp at which the order was generated.
        """
        self.type = 'ORDER'
        self.symbol = symbol
        self.price = price
        self.datetime = datetime
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

        self.print_order()

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print self.datetime
        print "Order: Symbol=%s, Price=%s Type=%s, Quantity=%s, Direction=%s" % \
            (self.symbol, self.price, self.order_type, self.quantity, self.direction)


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self,
                 timeindex,
                 symbol,
                 exchange,
                 quantity,
                 direction,
                 fill_cost,
                 commission=None):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        timeindex - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        ##exchange - The exchange where the order was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        fill_cost - The holdings value in dollars.
        commission - An optional commission sent from IB.
        """
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        #self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        # Calculate commission
        if commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission

    def calculate_ib_commission(self):
        """
        Calculates the fees of trading based on an Interactive
        Brokers fee structure for API RMB
        tax fee : 0.001 when SELL
        exchange fee:  0.00002
        transaction fee :boker fee ===>>0.00028  when less than 17848 5yuan
        """
        full_cost = 5
        taxrate, exchrate, brokrate = 0.001, 0.00002, 0.00028
        amount = self.quantity * self.fill_cost
        taxfee = taxrate * amount
        exchfee = exchrate * amount
        bokerfee = amount * brokrate if amount >= 17848.0 else 5.0
        # Above enlighten that high frequency trading spend more money
        if self.direction == "BUY":
            full_cost = exchfee + bokerfee
        elif self.direction == "SELL":
            full_cost = exchfee + bokerfee + taxfee
        return full_cost
