'''
Used as Pandas plotting backend.
'''

import quantlplot


def plot(df, x, y, kind, **kwargs):
    _x = df.index if y is None else df[x]
    try:
        _y = df[x].reset_index(drop=True) if y is None else df[y]
    except:
        _y = df.reset_index(drop=True)
    kwargs = dict(kwargs)
    if 'by' in kwargs:
        del kwargs['by']
    if kind in ('candle', 'candle_ochl', 'candlestick', 'candlestick_ochl', 'volume', 'volume_ocv', 'renko'):
        if 'candle' in kind:
            return quantlplot.candlestick_ochl(df, **kwargs)
        elif 'volume' in kind:
            return quantlplot.volume_ocv(df, **kwargs)
        elif 'renko' in kind:
            return quantlplot.renko(df, **kwargs)
    elif kind == 'scatter':
        if 'style' not in kwargs:
            kwargs['style'] = 'o'
        return quantlplot.plot(_x, _y, **kwargs)
    elif kind == 'bar':
        return quantlplot.bar(_x, _y, **kwargs)
    elif kind in ('barh', 'horiz_time_volume'):
        return quantlplot.horiz_time_volume(df, **kwargs)
    elif kind in ('heatmap'):
        return quantlplot.heatmap(df, **kwargs)
    elif kind in ('labels'):
        return quantlplot.labels(df, **kwargs)
    elif kind in ('hist', 'histogram'):
        return quantlplot.hist(df, **kwargs)
    else:
        if x is None:
            _x = df
            _y = None
        if 'style' not in kwargs:
            kwargs['style'] = None
        return quantlplot.plot(_x, _y, **kwargs)
