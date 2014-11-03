#! /usr/bin/env python

"""
:Description:

A Python 3 script to download price-volume, dividend, split data for
stocks. By default it downloads data in the following three files:

./hist_data/prc_vol_{ticker}_{start_date}_{end_date}.csv
./hist_data/div_{ticker}_{start_date}_{end_date}.csv
./hist_data/splt_{ticker}_{start_date}_{end_date}.csv


If optional filepath(s) are provided by -p, -d and -s, as shown below,
only those kind(s) of data are downloaded.



:Example:

1. Download all data (since 1900101) till today for ticker:

./hist_data.py C


2. Download all data for ticker, start_date & end_date:

./hist_data.py C 20000101 20110101


3. Download __only price-volume__ data for ticker, start_date &
end_date in the specified filenames:

./hist_data.py C 20000101 20110101 \
   -p "/tmp/price_volume_{ticker}.csv"


4. Download all data for ticker, start_date & end_date in the
specified filenames:

./hist_data.py C 20000101 20110101 \
   -p "/tmp/price_volume_{ticker}.csv" \
   -d "/tmp/dividend_{ticker}.csv" \
   -s "/tmp/split_{ticker}.csv"



:See also:

http://search.cpan.org/dist/Finance-QuoteHist/lib/Finance/QuoteHist/Yahoo.pm
http://code.activestate.com/recipes/511444-stock-prices-historical-data-bulk-download-from-in/
http://www.goldb.org/ystockquote.html
"""



__author__  = 'Gopi Goswami   <grgoswami@gmail.com>'
__version__ = '1.0'
__all__     = ['StkDataDownload']



#import urllib.request - modified by Ravi for python 2.7
import urllib2
#from html.parser import HTMLParser
from htmllib import HTMLParser
import re
import datetime
import csv
import os
import sys
import optparse
import logging



logging.basicConfig(level = logging.INFO,
                    format = ('%(levelname)s   %(asctime)s   '
                              '%(filename)s:%(lineno)s   %(message)s'))



# ----------------------------------------------------------------------------
def _to_date(yyyymmdd):
    format = '%Y%m%d'
    try:
        date = datetime.datetime.strptime(yyyymmdd, format)
    except:
        raise Exception('Invalid date: ' + yyyymmdd)
    return date


def _makedirs(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def _abspath(path):
    if path is None:
        return None
    return os.path.abspath(path)


# ----------------------------------------------------------------------------
_splt_field_names = [ 'Ticker', 'Date', 'Splits' ]
_splt_header      = dict(zip(_splt_field_names, _splt_field_names))
_splt_row         = dict.fromkeys(_splt_field_names)
_splt_writer      = None



# ----------------------------------------------------------------------------
_compiled_reg_exps = \
    [('date', \
          re.compile(r'(?P<mon>[a-zA-Z]+)\s+(?P<dd>[0-9]+),\s+(?P<yyyy>[0-9]{4,4}).*', re.MULTILINE)), \
         ('dvd', \
              re.compile(r'\s+\$\s+(?P<div>.*)\s+Dividend$', re.MULTILINE)), \
         ('splt', \
              re.compile(r'(?P<denom>.*):\s+(?P<numer>.*)\s+Stock\s+Split$', re.MULTILINE)), \
         ]

class _Splt(HTMLParser):
    def handle_data(self, data):
        # Set the reg_exps
        tag = self.get_starttag_text( )
        if tag is None:
            return None
        logging.debug('tag={0}, line="{1}"'.format(tag, data))
        if not tag.startswith('<td'):
            return None
        global _splt_row
        global _splt_writer
        for desc, rec in _compiled_reg_exps:
            ss = rec.search(data)
            if ss is None:
                continue
            if desc == 'date':
                date = datetime.datetime.strptime(' '.join(ss.groups( )),
                                                  '%b %d %Y')
                date = datetime.datetime.strftime(date, '%Y-%m-%d')
                _splt_row['Date'] = date
            elif desc == 'splt':
                denom = float(ss.group('denom'))
                if denom <= 0.0:
                    logging.error('Found bad split: line={0}'.format(data))
                splt = (float(ss.group('numer')) /
                        float(ss.group('denom')))
                _splt_row['Splits'] = splt
                _splt_writer.writerow(_splt_row)



# ----------------------------------------------------------------------------
class StkDataDownload(object):
    def __init__(self,
                 prc_filepath  = './hist_data/prc_vol_{ticker}_{start_date}_{end_date}.csv',
                 dvd_filepath  = './hist_data/dvd_{ticker}_{start_date}_{end_date}.csv',
                 splt_filepath = './hist_data/splt_{ticker}_{start_date}_{end_date}.csv',
                 gzip          = False):
        # Set the filepaths
        self.prc_filepath  = _abspath(prc_filepath)
        self.dvd_filepath  = _abspath(dvd_filepath)
        self.splt_filepath = _abspath(splt_filepath)
        self.gzip          = gzip
        # Set the urls, e.g.,
        #
        # http://finance.yahoo.com/d/quotes.csv?s=IBM&f=l1c1va2xj1b4j4dyekjm3m4rr5p5p6s7
        # http://finance.yahoo.com/q/hp?s=C&a=00&b=2&c=1962&d=10&e=17&f=2010&g=v&z=66&y=0
        # http://finance.yahoo.com/q/hp?s=C&a=00&b=2&c=1962&d=10&e=17&f=2010&g=v&z=66&y=66
        # http://finance.yahoo.com/q/hp?s=C&a=00&b=2&c=1962&d=10&e=17&f=2010&g=v&z=66&y=132
        self.yahoo_ichart_url = ('http://ichart.yahoo.com/table.csv?' +
                                 's={ticker}&' +
                                 'a={start_mm}&' +
                                 'b={start_dd}&' +
                                 'c={start_yyyy}&' +
                                 'd={end_mm}&' +
                                 'e={end_dd}&' +
                                 'f={end_yyyy}&' +
                                 'g={data_type}&' +
                                 'x=.csv')
        self.yahoo_finance_url = ('http://finance.yahoo.com/q/hp?' +
                                  's={ticker}&' +
                                  'a={start_mm}&' +
                                  'b={start_dd}&' +
                                  'c={start_yyyy}&' +
                                  'd={end_mm}&' +
                                  'e={end_dd}&' +
                                  'f={end_yyyy}&' +
                                  'g=v&' +
                                  'z=66&' +
                                  'y={count}')
        self.out_filepath = None
        self.html         = None
        self.no_data_ids  = ['There are no All Markets results for',
                             'Get Quotes Results for',
                             'Historical quote data is unavailable for the specified date range',
                             'Dividend data is unavailable for the specified date range',
                             'Sorry, Internal Server Error'
                             ]

        logging.debug(('prc_filepath={0}, '
                       'dvd_filepath={1}, '
                       'splt_filepath={2}').format(self.prc_filepath,
                                                   self.dvd_filepath,
                                                   self.splt_filepath))

    def _set_out_filepath(self, filepath):
        self.out_filepath = filepath.format(ticker     = self.ticker,
                                            start_date = self.start_yyyymmdd,
                                            end_date   = self.end_yyyymmdd)
        _makedirs(os.path.dirname(self.out_filepath))

    def _no_data(self):
        logging.info(('No data available for: '
                      'ticker={0}, '
                      'start_date={1}, '
                      'end_date={2}').format(self.ticker,
                                             self.start_yyyymmdd,
                                             self.end_yyyymmdd))
        return False

    def _set_url(self,
                  url,
                  data_type,
                  count = 0):
        url = url.format(ticker     = self.ticker,
                         #start_mm   = self.start_date.month,
                         start_mm   = self.start_date.month - 1,
                         start_dd   = self.start_date.day,
                         start_yyyy = self.start_date.year,
                         #end_mm     = self.end_date.month,
                         end_mm     = self.end_date.month -1,
                         end_dd     = self.end_date.day,
                         end_yyyy   = self.end_date.year,
                         data_type  = data_type,
                         count      = count)
        logging.info('The download url="{0}"'.format(url))
        try:
            # sock = urllib.request.urlopen(url) # modified by Ravi
            sock = urllib2.urlopen(url)
        #except urllib.error.HTTPError:
        except urllib2.HTTPError:
            return self._no_data( )
        #except urllib.error.URLError:
        except urllib2.URLError:
            return self._no_data( )
        else:
            self.html = sock.read( ).decode('utf-8')
        for check in self.no_data_ids:
            if self.html.find(check) >= 0:
                return self._no_data( )
        return True

    def _gzip(self, path):
        cmd = 'gzip -f {0}'.format(path)
        logging.info('Running: cmd="{0}"'.format(cmd))
        os.system(cmd)

    def _run_xxx(self, filepath, data_type):
        self._set_out_filepath(filepath)
        if not self._set_url(self.yahoo_ichart_url, data_type):
            return False
        with open(self.out_filepath, 'w') as outfile:
            for count, line in enumerate(self.html.split('\n')):
                if not line.strip( ):
                    continue
                if count == 0:
                    tt = 'Ticker'
                else:
                    tt = self.ticker
                outfile.writelines(tt + ',' + line + '\n')
        logging.info('Download path={0}'.format(self.out_filepath))
        if self.gzip:
            self._gzip(self.out_filepath)
        return True

    def _run_splt(self):
        self._set_out_filepath(self.splt_filepath)
        global _splt_writer
        with open(self.out_filepath, 'w') as outfile:
            _splt_writer = csv.DictWriter(outfile, _splt_field_names)
            _splt_writer.writerow(_splt_header)
            _splt_row['Ticker'] = self.ticker
            _splt   = _Splt( )
            count   = 0
            while True:
                if not self._set_url(self.yahoo_finance_url, 'v', count):
                    break
                _splt.feed(self.html)
                count += 66
                if count >= 1000:
                    # count too big, probably getting errors anyway
                    break
            logging.info('Download path={0}'.format(self.out_filepath))
        if self.gzip:
            self._gzip(self.out_filepath)
        return True

    def run(self,
            ticker,
            start_date,
            end_date):
        self.ticker         = ticker
        self.start_yyyymmdd = start_date
        self.start_date     = _to_date(start_date)
        self.end_date       = _to_date(end_date)
        self.end_yyyymmdd   = end_date
        logging.info(('ticker={0}, '
                       'start_date={1}, '
                       'end_date={2}').format(self.ticker,
                                              self.start_yyyymmdd,
                                              self.end_yyyymmdd))
        if self.prc_filepath is not None:
            if not self._run_xxx(self.prc_filepath, 's'):
                return False
        if self.dvd_filepath is not None:
            if not self._run_xxx(self.dvd_filepath, 'v'):
                return False
        if self.splt_filepath is not None:
            if not self._run_splt( ):
                return False



# ----------------------------------------------------------------------------
def _main( ):
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-p',
                      '--prc_filepath',
                      dest    = 'prc_filepath',
                      help    = 'Download filepath for price volume data',
                      default = None)
    parser.add_option('-d',
                      '--dvd_filepath',
                      dest    = 'dvd_filepath',
                      help    = 'Download filepath for dividend data',
                      default = None)
    parser.add_option('-s',
                      '--splt_filepath',
                      dest    = 'splt_filepath',
                      help    = 'Download filepath for split data',
                      default = None)
    parser.add_option('-q',
                      '--quiet',
                      dest    = 'quiet',
                      help    = 'Not verbose',
                      action  = 'store_true',
                      default = False)
    options, args = parser.parse_args( )
    num_args = len(args)
    if num_args == 1:
        ticker     = args[0]
        #start_date = '19000101'
        start_date = '20000101'
        end_date   = datetime.datetime.strftime(datetime.datetime.now( ),
                                                '%Y%m%d')
    elif num_args == 3:
        ticker, start_date, end_date = tuple(args)
    else:
        parser.error('Failed to parse args; see usage: '
                     'num_args={0}'.format(num_args))
    if options.quiet:
        logging.getLogger('').setLevel(logging.CRITICAL)
    if options.prc_filepath is None and \
            options.dvd_filepath is None and \
            options.splt_filepath is None:
            # Default: all of the following are None, so download all
            # data
        stk = StkDataDownload( )
    else:
        stk = StkDataDownload(options.prc_filepath,
                              options.dvd_filepath,
                              options.splt_filepath)
    stk.run(ticker, start_date, end_date)



# ----------------------------------------------------------------------------
if __name__ == '__main__':
    _main( )
