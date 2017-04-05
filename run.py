import matplotlib
matplotlib.use("TkAgg")
import datetime
import urllib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy

from scipy.interpolate import *
from functools import partial
import matplotlib.animation as animation


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk

LARGE_FONT = ("Verdana", 12)

dict = {
    'Google':'goog',
    'Apple':'aapl',
    'Yahoo': 'yhoo',
    'HP':'hpq',
    'Facebook' :'fb',
    'Amazon' : 'amzn',
    'Twitter' : 'twtr'}

f = Figure(figsize=(10, 10), dpi=100)
a = f.add_subplot(111)
sixMonthAgo = datetime.date.today() - datetime.timedelta(6 * 365 / 12)


# Default values
comp = dict.items()[0][0]
code = dict.items()[0][1]


class Quote(object):
    DATE_FMT = '%Y-%m-%d'
    TIME_FMT = '%H:%M:%S'

    def __init__(self):
        self.symbol = ''
        self.date, self.time, self.open_, self.high, self.low, self.close, self.volume = ([] for _ in range(7))

    def append(self, dt, open_, high, low, close, volume):
        self.date.append(dt.date())
        self.time.append(dt.time())
        self.open_.append(float(open_))
        self.high.append(float(high))
        self.low.append(float(low))
        self.close.append(float(close))
        self.volume.append(int(volume))

    def to_csv(self):
        return ''.join(["{0},{1},{2},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7}\n".format(self.symbol,
                                                                                   self.date[bar].strftime('%Y-%m-%d'),
                                                                                   self.time[bar].strftime('%H:%M:%S'),
                                                                                   self.open_[bar], self.high[bar],
                                                                                   self.low[bar], self.close[bar],
                                                                                   self.volume[bar])
                        for bar in xrange(len(self.close))])

    def write_csv(self, filename):
        with open(filename, 'w') as f:
            f.write(self.to_csv())

    def read_csv(self, filename):
        self.symbol = ''
        self.date, self.time, self.open_, self.high, self.low, self.close, self.volume = ([] for _ in range(7))
        for line in open(filename, 'r'):
            symbol, ds, ts, open_, high, low, close, volume = line.rstrip().split(',')
            self.symbol = symbol
            dt = datetime.datetime.strptime(ds + ' ' + ts, self.DATE_FMT + ' ' + self.TIME_FMT)
            self.append(dt, open_, high, low, close, volume)
        return True

    def __repr__(self):
        return self.to_csv()

class Yahoo(Quote):
  ''' Daily quotes from Yahoo. Date format='yyyy-mm-dd' '''
  def __init__(self,symbol,start_date,end_date=datetime.date.today().isoformat()):
    super(Yahoo, self).__init__()
    self.symbol = symbol.upper()
    start_year,start_month,start_day = start_date.split('-')
    start_month = str(int(start_month)-1)
    end_year,end_month,end_day = end_date.split('-')
    end_month = str(int(end_month)-1)
    url_string = "http://ichart.finance.yahoo.com/table.csv?s={0}".format(symbol)
    url_string += "&a={0}&b={1}&c={2}".format(start_month,start_day,start_year)
    url_string += "&d={0}&e={1}&f={2}".format(end_month,end_day,end_year)
    csv = urllib.urlopen(url_string).readlines()
    csv.reverse()
    for bar in xrange(0,len(csv)-1):
      ds,open_,high,low,close,volume,adjc = csv[bar].rstrip().split(',')
      open_,high,low,close,adjc = [float(x) for x in [open_,high,low,close,adjc]]
      if close != adjc:
        factor = adjc/close
        open_,high,low,close = [x*factor for x in [open_,high,low,close]]
      dt = datetime.datetime.strptime(ds,'%Y-%m-%d')
      self.append(dt,open_,high,low,close,volume)



# http://ichart.yahoo.com/table.csv?s=S58.SI&c=2009&a=9&b=23&f=2014&d=9&e=22&g=d&ignore=.csv
#
# The blue part is the stock symbol (only one symbol can be run at a time), the pink and green portion represent the start and end date respectively.
# The brown portion is the interval in d,m, y.
# By changing the interval g = v, the dividend information as in the dividend payout at the particular date is given. The url str is as below.

# http://ichart.yahoo.com/table.csv?s=S58.SI&c=2009&a=9&b=23&f=2014&d=9&e=22&g=v&ignore=.csv
#
# For the script, the interval is easily set by using the following part of the code.
# The formation of url will straight away append the hist price url and dividend url in a single function.


class Gui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack()
        # container.pack(side = "top", fill = "both", expend = True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}
        frame= StartPage(container, self)

        self.frames[StartPage] = frame

        frame.grid()
        # frame.grid(row = 0, column = 0, sticky = "Main Windows")

        self.show_frame(StartPage)

    def show_frame(self, count):
        frame = self.frames[count]
        frame.tkraise()


def calculation_plots():
    q = Yahoo(str(code), str(sixMonthAgo))  # download six month ago data
    q.write_csv('db.csv')  # save it to disk
    # print q  # print it out
    # q = YahooQuote('orcl','2017-03-01','2017-04-3')   # download Oracle data
    # q.write_csv('orcl.csv')                           # save it to disk
    # q = Quote()                                       # create a generic quote object
    # q.read_csv('orcl.csv')                            # populate it with our previously saved data
    # print q                                           # print it out

    pullData = open("db.csv", "r").read()
    dataList = pullData.split('\n')
    xList = []
    yList = []
    xReg=[]
    yReg=[]

    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.title("Graph")

    for line in dataList:
        if len(line) > 1:
            obj = line.split(',')
            print (obj)
            # [0:Name, 1: Date, 2: Time, 3: Open, 4: High, 5: Low, 6: Close, 7: Volume]
            y = float(obj[6])
            x = datetime.datetime.strptime(obj[1], "%Y-%m-%d")
            xList.append(x)
            yList.append(y)

            x = float(obj[3])
            y = float(obj[6])
            xReg.append(x)
            yReg.append(y)


    # a.clear()

    print (xReg)
    print (yReg)
    coefficients = numpy.polyfit(xReg, yReg, 1)
    polynomial = numpy.poly1d(coefficients)
    final = polynomial(xReg)

    print (polynomial)
    print (coefficients)
    # plt.plot(xReg, numpy.polyval(var, xReg), 'r-')


    plt.plot(xReg, final, 'r-')
    # plt.plot(xList, yList, 'o')

    plt.legend()
    plt.show()


# a.plot([1,2,3,4,5,6,7,8],[5,6,2,7,9,3,3,5])

def googleHandler():
    global comp, code
    comp = "Google"
    code = dict[comp]
    calculation_plots()


def appleHandler():
    global comp, code
    comp = "Apple"
    code = dict[comp]
    calculation_plots()


def yahooHandler():
    global comp, code
    comp = "Yahoo"
    code = dict[comp]
    calculation_plots()


def hpHandler():
    global comp, code
    comp = "HP"
    code = dict[comp]
    calculation_plots()


def facebookHandler():
    global comp, code
    comp = "Facebook"
    code = dict[comp]
    calculation_plots()


def amazonHandler():
    global comp, code
    comp = "Amazon"
    code = dict[comp]
    calculation_plots()


def twitterHandler():
    global comp, code
    comp = "Twitter"
    code = dict[comp]
    calculation_plots()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text = "Regression On Stocks")
        label.pack()

        label2 = tk.Label(self, text = "Choose a company")
        label2.pack()


        button1 = tk.Button(self, text = "Google",
                            command = lambda: googleHandler())
        button1.pack()

        button2 = tk.Button(self, text = "Apple",
                            command = lambda: appleHandler())
        button2.pack()

        button3 = tk.Button(self, text = "Yahoo",
                            command = lambda: yahooHandler())
        button3.pack()

        button4 = tk.Button(self, text = "HP",
                            command = lambda: hpHandler())
        button4.pack()
        
        button5 = tk.Button(self, text = "Facebook",
                            command = lambda: facebookHandler())
        button5.pack()

        button6 = tk.Button(self, text="Amazon",
                            command=lambda: amazonHandler())
        button6.pack()

        button7 = tk.Button(self, text="Twitter",
                            command=lambda: twitterHandler())
        button7.pack()

        # canvas = FigureCanvasTkAgg(f, self)
        # canvas.show()
        # canvas.get_tk_widget().pack()





if __name__ == '__main__':
    # # Gui installation


    run = Gui()
    run.mainloop()



