#!/usr/bin/env python3

import quantlplot as qplt
from functools import lru_cache
from PyQt5.QtWidgets import QApplication, QGridLayout, QGraphicsView, QComboBox, QLabel
from threading import Thread
import yfinance as yf


app = QApplication([])
win = QGraphicsView()
win.setWindowTitle('TradingView wannabe')
layout = QGridLayout()
win.setLayout(layout)
win.resize(600, 500)

combo = QComboBox()
combo.setEditable(True)
[combo.addItem(i) for i in 'AMRK FB GFN REVG TSLA TWTR WMT CT=F GC=F ^FTSE ^N225 EURUSD=X ETH-USD'.split()]
layout.addWidget(combo, 0, 0, 1, 1)
info = QLabel()
layout.addWidget(info, 0, 1, 1, 1)

ax = qplt.create_plot(init_zoom_periods=100)
win.axs = [ax] # quantlplot requres this property
axo = ax.overlay()
layout.addWidget(ax.vb.win, 1, 0, 1, 2)


@lru_cache(maxsize=15)
def download(symbol):
    return yf.download(symbol, '2019-01-01')

@lru_cache(maxsize=100)
def get_name(symbol):
    return yf.Ticker(symbol).info['shortName']

plots = []
def update(txt):
    df = download(txt)
    if len(df) < 20: # symbol does not exist
        return
    info.setText('Loading symbol name...')
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


qplt.show(qt_exec=False) # prepares plots when they're all setup
win.show()
app.exec_()
