import urllib.request as get
from bs4 import BeautifulSoup as bs
import time
import smtplib
import os
import sys
import re

'''
A program that runs from a cronjob to extract the rates of required indian stocks mention in the list
'''

codeList = ['']


class IndianStock:

    page_link = 'https://in.finance.yahoo.com/quote/'
    page = None
    soup = None

    log_file = None
    log_filepath = None
    output_file = None
    output_filepath = None
    graph_file = None
    graph_filepath = None

    home_dir = None     # os.path.expandvars('$HOME')
    stock_dir = os.path.join(os.getcwd(), 'india_finance')

    title = ['h1', {'data-reactid': '7'}]
    # present_price = ['span', {'data-reactid': '36'}]
    # opening_price = ['td', {'data-test': 'OPEN-value'}]
    # previous_close_price = ['td', {'data-test': 'PREV_CLOSE-value'}]
    # day_range_price = ['td', {'data-test': 'DAYS_RANGE-value'}]
    # price_change = ['span', {'data-reactid': '37'}]

    present_price = 14
    previous_close_price = 0
    opening_price = 1
    day_range_price = 4
    price_change = 13   # to be done

    values = []

    def __init__(self, code):
        self.home_dir = os.path.expandvars('$HOME') + '/'
        self.stock_dir = os.path.join(self.stock_dir, code)

        if not(os.path.exists(self.stock_dir)):
            os.makedirs(self.stock_dir)

        self.stock_dir += '/' + self.getdate()

        if not(os.path.exists(self.stock_dir)):
            os.makedirs(self.stock_dir)

        self.log_filepath = self.stock_dir + '/' + 'logfile.txt'
        self.output_filepath = self.stock_dir + '/' + 'output.txt'
        self.graph_filepath = self.stock_dir + '/' + 'graph_output.txt'

        try:
            self.log_file = open(self.log_filepath, 'a')
            self.output_file = open(self.output_filepath, 'w')
            self.graph_file = open(self.graph_filepath, 'a')
        except IOError:
            print('Could not open log file or output file...')
            pass

        self.log('NEW OBJECT INITIALIZED')
        self.log('Output file path : ' + self.output_filepath)
        self.log('Graph output file path : ' + self.graph_filepath)

        self.page_link = 'https://in.finance.yahoo.com/quote/'
        self.page_link = self.page_link + code + '/'
        self.page = get.urlopen(self.page_link)
        self.log('Page Downloaded.')  # To issue a log into log_file
        self.log('Page link : ' + self.page_link)
        self.soup = bs(self.page, 'html.parser')
        self.log('Page parsed, soup created')
        self.log('Stock for ' + self.soup.find(self.title[0], attrs=self.title[1]).get_text())
        self.get_values()

    def get_values(self):
        datas = []
        datas = self.soup.findAll('td')
        for d in self.soup.findAll('span'):
            datas.append(d)
        for sp in datas:
            if re.match(r'^([\d]+[\.|\,][\d]+)+', sp.text) and sp.text not in self.values:
                self.values.append(sp.text)

    def refresh(self):
        self.page = get.urlopen(self.page_link)
        self.log('Page Downloaded.')  # To issue a log into log_file
        self.soup = bs(self.page, 'html.parser')
        self.log('Page parsed, soup created')
        self.log('Data refreshed...')
        self.log('Stock for ' + self.soup.find(self.title[0], attrs=self.title[1]).get_text())

    def get_current_price(self):
        # if self.soup.find(self.present_price[0], attrs=self.present_price[1]).get_text() is not None:
        if self.values[self.present_price] is not None:
            price = str(self.values[self.present_price]).replace(',', '')
            price = float(price)
            self.log('Current price extracted : ' + str(price))
            return price
        else:
            self.log('Current Price UNAVAILABLE')
            return None

    def get_opening_price(self):
        # if self.soup.find(self.opening_price[0], attrs=self.opening_price[1]).get_text() is not None:
        if self.values[self.opening_price] is not None:
            price = str(self.values[self.opening_price]).replace(',', '')
            price = float(price)
            self.log('Opening price extracted : ' + str(price))
            return price
        else:
            self.log('Opening Price UNAVAILABLE')
            return None

    def get_previous_closing_price(self):
        # if self.soup.find(self.previous_close_price[0], attrs=self.previous_close_price[1]).get_text() is not None:
        if self.values[self.previous_close_price] is not None:
            price = str(self.values[self.previous_close_price]).replace(',', '')
            price = float(price)
            self.log('Previous closing price extracted : ' + str(price))
            return price
        else:
            self.log('Previous Closing Price UNAVAILABLE')
            return None

    def get_day_range(self):
        # if self.soup.find(self.day_range_price[0], attrs=self.day_range_price[1]).get_text() is not None:
        if self.values[self.day_range_price] is not None:
            days_range = self.values[self.day_range_price]
            self.log('Day\'s range : ' + days_range)
            return days_range
        else:
            self.log('Day\'s Range UNAVAILABLE')
            return None

    def get_change(self):
        # if self.soup.find(self.price_change[0], attrs=self.price_change[1]).get_text() is not None:
        if self.values[self.price_change] is not None:
            price_change = self.values[self.price_change]
            self.log('Price Change : ' + price_change)
            return price_change
        else:
            self.log('Change in Price UNAVAILABLE')
            return None

    def gettime(self):
        return time.asctime(time.localtime(time.time()))

    def getdate(self):
        local_time = time.localtime(time.time())
        return str(local_time.tm_mday) + '_' + str(local_time.tm_mon) + '_' + str(local_time.tm_year)

    def log(self, report):
        self.log_file.write(self.gettime() + '\t' + report + '\n')
        self.log_file.flush()
        return

    def output_line(self, line):
        self.output_file.write(line + '\n')
        self.output_file.flush()
        # self.log('Output Written to : ' + self.output_filepath)
        return

    def record_graph_point(self, point):
        local_time = time.localtime(time.time())
        ordinate = str(local_time.tm_hour) + str(local_time.tm_min)
        self.graph_file.write(ordinate + ' ' + str(point) + '\n')
        self.graph_file.flush()
        self.log('Point plotted with abscissa : ' + str(point))
        return

    def __del__(self):
        self.log_file.close()
        self.output_file.close()


class SendNotification:
    '''
    To send a notification via email when the current stock price rises above the previous limit
    '''
    message = None
    username = 'ideapad.divyaksh@gmail.com'
    password = 'Divyaksh1997'
    to_address = ['divyaksh.shukla@gmail.com', 'sudhat.shukla@gmail.com', 'ideapad.divyaksh@gmail.com']

    def __init__(self, indian_stock):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.username, self.password)

        self.message = '''
        Current Price = {}
        Opening Price = {}
        Change in Price = {}
        Previous Closing = {}
        Today\'s Range = {}'''.format(str(indian_stock.get_current_price()),
                                      str(indian_stock.get_opening_price()),
                                      str(indian_stock.get_change()),
                                      str(indian_stock.get_previous_closing_price()),
                                      str(indian_stock.get_day_range()))

        for recipient in self.to_address:
            server.sendmail(self.username, recipient, self.message)

        indian_stock.log('Message sent')


def main():

    sys.argv = sys.argv[1:]
    for code in sys.argv:
        indian_stock = IndianStock(code)

        indian_stock.output_line(indian_stock.gettime())
        indian_stock.output_line('Current Price = ' + str(indian_stock.get_current_price()))
        indian_stock.output_line('Opening Price = ' + str(indian_stock.get_opening_price()))
        indian_stock.output_line('Change_in_price = ' + indian_stock.get_change())
        indian_stock.output_line('Previous Closing = ' + str(indian_stock.get_previous_closing_price()))
        indian_stock.output_line('Today\'s Range = ' + indian_stock.get_day_range())

        indian_stock.record_graph_point(indian_stock.get_current_price())

        indian_stock.__del__()
        indian_stock = None

    return None


if __name__ == '__main__':
    main()
