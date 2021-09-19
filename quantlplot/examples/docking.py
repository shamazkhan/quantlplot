import quantlplot as qplt
from functools import lru_cache
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QGraphicsView, QComboBox, QLabel
from pyqtgraph.dockarea import DockArea, Dock
from threading import Thread
from pymongo import MongoClient
from collections import defaultdict
import pandas as pd
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
win = QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(1600,800)
win.setWindowTitle("Docking charts example for quantlplot")

# Set width/height of QSplitter
win.setStyleSheet("QSplitter { width : 20px; height : 20px; }")

# Create docks
dock_0 = Dock("dock_0", size = (1000, 100), closable = True)
dock_1 = Dock("dock_1", size = (1000, 100), closable = True)
dock_2 = Dock("dock_2", size = (1000, 100), closable = True)
area.addDock(dock_0)
area.addDock(dock_1)
area.addDock(dock_2)

# Create example charts
combo = QComboBox()
combo.setEditable(True)
[combo.addItem(i) for i in 'AAPL SHOP ZI'.split()]
dock_0.addWidget(combo, 0, 0, 1, 1)
info = QLabel()
dock_0.addWidget(info, 0, 1, 1, 1)

# Chart for dock_0
ax0,ax1,ax2 = qplt.create_plot_widget(master=area, rows=3, init_zoom_periods=100)

area.axs = [ax0, ax1, ax2]
dock_0.addWidget(ax0.ax_widget, 1, 0, 1, 2)
dock_1.addWidget(ax1.ax_widget, 1, 0, 1, 2)
dock_2.addWidget(ax2.ax_widget, 1, 0, 1, 2)

# Link x-axis
ax1.setXLink(ax0)
ax2.setXLink(ax0)
win.axs = [ax0] # quantlplot requres this property
ax2 = ax0.overlay()

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
    #info.setText("Loading symbol name...")
    price = df ["Open Close High Low".split()]
    ma20 = df.Close.rolling(20).mean()
    ma50 = df.Close.rolling(50).mean()
    volume = df ["Open Close Volume".split()]
    ax0.reset() # remove previous plots
    ax1.reset() # remove previous plots
    ax2.reset() # remove previous plots
    qplt.candlestick_ochl(price, ax = ax0)
    qplt.plot(ma20, legend = "MA-20", ax = ax1)
    qplt.plot(ma50, legend = "MA-50", ax = ax1)
    qplt.volume_ocv(volume, ax = ax2)
    qplt.refresh() # refresh autoscaling when all plots complete
    Thread(target=lambda: info.setText(get_name(txt))).start() # slow, so use thread

combo.currentTextChanged.connect(update)
update(combo.currentText())

qplt.show(qt_exec = False) # prepares plots when they're all setup
win.show()
app.exec_()
