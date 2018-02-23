#! /usr/bin/env python3
import time
import sys
import getopt
import datetime
import signal
import os

from api_poloniex import *
from settings import *
# Statics
#period = 1              #seconds

# Helper Functions
clear = lambda: os.system('cls' if os.name=='nt' else 'clear') # Windows Safe
#clear()

def signal_handler(signal, frame):
    #clear()
    print ('\n=============================================================')
    print('>>> Good Bye!! [Ctrl+C Pressed] !!')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def json_dump(dump):
    print(json.dumps(dump, indent=4, sort_keys=True))

def main(argv):
    period = 10
    pair = "BTC_ZEC"
    prices = []
    currentMovingAverage = 0;
    lengthOfMA = 0
    startTime = False           # UNIX Timestamp
    endTime = False             # UNIX Timestamp
    historicalData = False
    tradePlaced = False
    typeOfTrade = False
    dataDate = ""
    orderNumber = ""

    try:
        opts, args = getopt.getopt(argv,"hp:c:n:s:e:",["period=","currency=","points="])
    except getopt.GetoptError:
        print ('trading-bot.py -p <period length> -c <currency pair> -n <period of moving average> -s <startTime> -e <endTime>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
        	print ('trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>')
        	sys.exit()
        elif opt in ("-p", "--period"):
        	if (int(arg) in [300,900,1800,7200,14400,86400]):
        		period = arg
        	else:
        		print ('Poloniex requires periods in 300,900,1800,7200,14400, or 86400 second increments')
        		sys.exit(2)
        elif opt in ("-c", "--currency"):
        	pair = arg
        elif opt in ("-n", "--points"):
        	lengthOfMA = int(arg)
        elif opt in ("-s"):
        	startTime = arg
        elif opt in ("-e"):
        	endTime = arg

    conn = poloniex(api_key,api_secret)

    if (startTime):
        historicalData = conn.api_query("returnChartData",{"currencyPair":pair,"start":startTime,"end":endTime,"period":period})

    while True:
        currentValues = conn.api_query("returnTicker")
        lastPairPrice = currentValues[pair]["last"]

        #json_dump(currentValues)
        #json_dump(lastPairPrice)

        if (startTime and historicalData):
            nextDataPoint = historicalData.pop(0)
            lastPairPrice = nextDataPoint['weightedAverage']
            dataDate = datetime.datetime.fromtimestamp(int(nextDataPoint['date'])).strftime('%Y-%m-%d %H:%M:%S')
        elif(startTime and not historicalData):
            exit()
        else:
            currentValues = conn.api_query("returnTicker")
            lastPairPrice = float(currentValues[pair]["last"])
            dataDate = datetime.datetime.now()

        if (len(prices) > 0):
            currentMovingAverage = sum(prices) / float(len(prices))
            previousPrice = prices[-1]

            # print(type(lastPairPrice))
            # print(lastPairPrice)
            # print(type(currentMovingAverage))
            # print(currentMovingAverage)

            print("tradePlaced:", tradePlaced)
            print("typeOfTrade:", typeOfTrade)
            print("lastPairPrice:", lastPairPrice)
            print("currentMovingAverage:", currentMovingAverage)
            print("previousPrice:", previousPrice)
            if (not tradePlaced):
                print("here")
                if ( (lastPairPrice > currentMovingAverage) and (lastPairPrice < previousPrice) ):
                    print ("SELL ORDER")
                    #orderNumber = conn.sell(pair,lastPairPrice,.01)
                    tradePlaced = True
                    typeOfTrade = "short"
                elif ( (lastPairPrice < currentMovingAverage) and (lastPairPrice > previousPrice) ):
                    print ("BUY ORDER")
                    #orderNumber = conn.buy(pair,lastPairPrice,.01)
                    tradePlaced = True
                    typeOfTrade = "long"
            elif (typeOfTrade == "short"):
                if ( lastPairPrice < currentMovingAverage ):
                    print ("EXIT TRADE")
                    #conn.cancel(pair,orderNumber)
                    tradePlaced = False
                    typeOfTrade = False
            elif (typeOfTrade == "long"):
                if ( lastPairPrice > currentMovingAverage ):
                    print ("EXIT TRADE")
                    #conn.cancel(pair,orderNumber)
                    tradePlaced = False
                    typeOfTrade = False
        else:
            previousPrice = 0

        print ("%s Period: %ss %s: %s Moving Average: %s" % (dataDate,period,pair,lastPairPrice,currentMovingAverage))

        prices.append(float(lastPairPrice))
        prices = prices[-lengthOfMA:]
        if (not startTime):
            time.sleep(int(period))

if __name__=="__main__":
    main(sys.argv[1:])
