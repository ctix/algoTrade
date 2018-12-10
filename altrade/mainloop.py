# Declare the components with respective parameters
import event
import Queue
from datasource import HistoricTDXDataHandler
from execution import SimulatedExecutionHandler
from Tradingstrategy import BollLineMinutesStrategy
import portfolio

events = Queue.Queue()
# first with a signal stock to go through testing
symbol_list = ["300024", "002594", "002415"]
datadir = "D:\\tools\\new_tdx\\vipdoc\\sz\\minline"
bars = HistoricTDXDataHandler(events, datadir, symbol_list)
bars.load_bars(480)  # load trading datum of two days minutes
strategy = BollLineMinutesStrategy(bars, events)
port = portfolio.TrendPortfolio(bars, events, "2015-02-06")
broker = SimulatedExecutionHandler(events
                                   )  # reinforce the Order execution,polish
# when deal with the real time transactions

while True:
    # Update the bars (specific backtest code, as opposed to live trading)
    if bars.continue_backtest == True:
        bars.update_bars()
    else:
        break

    # Handle the events
    while True:
        try:
            event = events.get(False)
        except Queue.Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    port.update_fill(event)

    # 10-Minute heartbeat
    # import time
    # time.sleep(10*60)
    #time.sleep(3)
