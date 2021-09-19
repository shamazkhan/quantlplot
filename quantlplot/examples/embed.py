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
from functools import lru_cache
from PyQt5.QtWidgets import QApplication, QGridLayout, QGraphicsView, QComboBox, QLabel
from threading import Thread
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
    df = df.rename(columns={'  Date': 'Date', '  Open': 'Open', '  High': 'High', '  Low': 'Low', '  Close': 'Close',
                            '  Volume': 'Volume'})
    df = df.astype({'Date': 'datetime64[ns]'})
    df['time'] =df['Date']
    df.set_index('Date', inplace=True)

    print(df)
    return df


app = QApplication([])
win = QGraphicsView()
win.setWindowTitle('Quantl AI Technical Analysis')
layout = QGridLayout()
win.setLayout(layout)
win.resize(600, 500)

combo = QComboBox()
combo.setEditable(True)
[combo.addItem(i) for i in 'AAPL SHOP ZI'.split()]
layout.addWidget(combo, 0, 0, 1, 1)
info = QLabel()
layout.addWidget(info, 0, 1, 1, 1)

ax = qplt.create_plot(init_zoom_periods=100)
win.axs = [ax] # quantlplot requres this property
axo = ax.overlay()
layout.addWidget(ax.vb.win, 1, 0, 1, 2)


@lru_cache(maxsize=15)
def download(symbol):
    return read_mongo('POLYGON_STOCKS_EOD',symbol)

#@lru_cache(maxsize=100)
def get_name(symbol):
    return read_mongo('POLYGON_STOCKS_EOD',symbol)

plots = []
def update(txt):
    df = download(txt)
    if len(df) < 20: # symbol does not exist
        return
    #info.setText('Loading symbol name...')
    price = df['Open Close High Low'.split()]
    ma20 = df.Close.rolling(20).mean()
    ma50 = df.Close.rolling(50).mean()
    volume = df['Open Close Volume'.split()]
    ax.reset() # remove previous plots
    axo.reset() # remove previous plots
    qplt.candlestick_ochl(price)
    qplt.plot(ma20, legend='MA-20')
    qplt.plot(ma50, legend='MA-50')
    qplt.volume_ocv(volume, ax=axo)
    qplt.refresh() # refresh autoscaling when all plots complete
    Thread(target=lambda: info.setText(get_name(txt))).start() # slow, so use thread

combo.currentTextChanged.connect(update)
update(combo.currentText())



if __name__ == '__main__':
    qplt.show(qt_exec=False)  # prepares plots when they're all setup
    win.show()
    app.exec_()
