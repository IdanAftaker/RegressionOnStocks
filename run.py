import datetime
import urllib
import Tkinter as tk

LARGE_FONT = ("Verdana", 12)

dict = {
    'google':'goog',
    'apple':'aapl',
    'yahoo': 'yhoo',
    'hp':'hpq'}


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

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = "Regression On Stocks")
        label.pack()
        # label.pack(pady = 10, padx = 10)

if __name__ == '__main__':

    q = Yahoo('goog', '2017-03-01')                     # download year to date Apple data
    q.write_csv('quote.csv')                            # save it to disk
    # print q                                           # print it out
    # q = YahooQuote('orcl','2017-03-01','2017-04-3')   # download Oracle data
    # q.write_csv('orcl.csv')                           # save it to disk
    # q = Quote()                                       # create a generic quote object
    # q.read_csv('orcl.csv')                            # populate it with our previously saved data
    # print q                                           # print it out

    run = Gui()
    # # Gui installation


    run.mainloop()



