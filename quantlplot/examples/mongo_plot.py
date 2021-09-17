'' This code connects to Polygon's server via REST API to fetch & store historical data for a
given equity. at the moment only single equity is supported. Data is stored to MongoDB Cluster '''

import json
import bson
import pymongo
from pymongo import MongoClient
from collections import defaultdict
from polygon_rest import RESTClient
import datetime
import pandas as pd
from pandas.io.json import json_normalize
import quantlplot as qplt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def _connect_mongo(host, port, username, password, db):
    '''function to establish a connection with MongoDB'''

    if username and password:
        mongo_uri = "mongodb+srv://skhan:A330airbus@cluster0.f4uut.mongodb.net/POLYGON_STOCKS_EOD?retryWrites=true&w=majority"
        conn = MongoClient(mongo_uri)
    else:
        ''' Change this part of code when MongoDB is deployed as a Service. Host/Port configuration is defined in 
        <config> file. Until than keep it as it is. However this isnt the most efficient way to do this. 
        '''

        #conn = MongoClient(host, port)
        mongo_uri = "mongodb+srv://skhan:A330airbus@cluster0.f4uut.mongodb.net/POLYGON_STOCKS_EOD?retryWrites=true&w=majority"
        conn = MongoClient(mongo_uri)

    return conn[db]

def read_mongo(db, collection, query={}, host='localhost', port=27017, username='skhan', password='A330airbus', no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    imported_data = list(cursor)
    df = pd.DataFrame(imported_data)

    # Delete the _id
    if no_id:
        del df['_id']

    '''MongoDB Cursor had whitespaces in Colums, hence we must rename them TO BE FIXED LATER'''
    df = df.rename(columns={'  Date': 'time', '  Open': 'Open', '  High': 'High', '  Low': 'Low', '  Close': 'Close',
                            '  Volume': 'Volume'})
    df = df.astype({'time': 'datetime64[ns]'})
    print(df)
    return df



def calc_volume_profile():
    '''Calculate a poor man's volume distribution/profile by "pinpointing" each kline volume to a certain
       price and placing them, into N buckets. (IRL volume would be something like "trade-bins" per candle.)
       The output format is a matrix, where each [period] time is a row index, and even columns contain
       start (low) price and odd columns contain volume (for that price and time interval). See
       finplot.horiz_time_volume() for more info.'''
    data = []
    period = 'W'
    bins = 100
    bins = 100
    qtl_data['hlc3'] = ( qtl_data.High +  qtl_data.Low +  qtl_data.Close) / 3 # assume this is volume center per each 1m candle
    _,all_bins = pd.cut( qtl_data.hlc3, bins, right=False, retbins=True)
    for _,g in  qtl_data.groupby(pd.Grouper(key='time', freq=period)):
        t = g.time.iloc[0]
        volbins = pd.cut(g.hlc3, all_bins, right=False)
        price2vol = defaultdict(float)
        for iv,vol in zip(volbins, g.Volume):
            price2vol[iv.left] += vol
        data.append([t, sorted(price2vol.items())])


    vwap = pd.Series([], dtype='float64')
    qtl_data['hlc3v'] =  qtl_data['hlc3'] *  qtl_data.Volume

    for _, g in  qtl_data.groupby(pd.Grouper(key='time', freq=period)):
        i0, i1 = g.index[0], g.index[-1]
        vwap = vwap.append(g.hlc3v.loc[i0:i1].cumsum() /  qtl_data.Volume.loc[i0:i1].cumsum())

    qplt.plot(qtl_data.time, qtl_data.Close, legend='Price')
    qplt.plot(qtl_data.time, vwap, style='--', legend='VWAP')
    qplt.horiz_time_volume(data, draw_va=0.7, draw_poc=1.0)
    qplt.show()





def plot_data():
    # create two axes
    ax, ax2 = qplt.create_plot(stock_id, rows=2)
    candles = qtl_data[['time', 'Open', 'Close', 'High', 'Low']]
    qplt.candlestick_ochl(candles)
    # overlay volume on the top plot
    volumes = qtl_data[['time', 'Open', 'Close', 'Volume']]
    qplt.volume_ocv(volumes, ax=ax.overlay())

    # put an MA on the close price
    qtl_data['SMA50'] = qtl_data['Close'].rolling(50).mean()
    qtl_data['SMA21'] = qtl_data['Close'].rolling(21).mean()
    qtl_data['VOL_AVERAGE'] = qtl_data['Volume'].rolling(21).mean()

    qplt.plot(qtl_data['time'], qtl_data['SMA50'], ax=ax, legend='ma-50')
    qplt.plot(qtl_data['time'], qtl_data['SMA21'], ax=ax, legend='ma-21')

    # restore view (X-position and zoom) if we ever run this example again
    qplt.autoviewrestore()

    qplt.show()



if __name__ == '__main__':

  stock_id = 'SHOP'
  qtl_data = read_mongo('POLYGON_STOCKS_EOD',stock_id)
  plot_data()
  calc_volume_profile()


