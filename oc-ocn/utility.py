import time
import sqlite3 as sql
from bs4 import BeautifulSoup
import unicodedata as ucd
import scipy.stats as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def get_text_alt(elem, tag, alt=None):
    try:
        return elem.find(tag).text
    except AttributeError:
        return alt


def converte_data(data_string):
    """ Converte as data_strings em milisegundos a partir da epoch"""

    return time.mktime(time.strptime(data_string, '%Y-%m-%d'))


def mark_ecdf(ax, x, y, **kwargs):
    xx, yy = ax.transAxes.inverted().transform(ax.transData.transform((x, y)))
    # print(x, y, xx, yy)
    ax.axvline(x, 0, yy, **kwargs)
    kwargs['label'] = None  # quick fix to avoid duplicates in plot legend
    ax.axhline(y, 0, xx, **kwargs)


def ecdf_plot(data, xlabel, title=None, subplot=False, rasterized=True):
    data = np.array(sorted(data))
    plt.plot(data, np.linspace(0, 100, len(data)), '.', rasterized=rasterized)

    if title:
        title = 'ECDF plot - ' + title
    elif title is None:
        title = 'ECDF plot - ' + xlabel
    else:
        title = 'ECDF plot'

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Cumulative Relative Frequency (%)')

    mark_ecdf(plt.gca(), 0, 0)  # dirtiest fix to a nasty bug

    mean = data.mean()
    mean_percentile = st.percentileofscore(data, mean)
    mark_mean_settings = {
        'c': 'r', 'ls': ':', 'marker': 'o',
        'label': 'Mean: ({:.2f}, {:.2f})'.format(mean, mean_percentile)}
    mark_ecdf(plt.gca(), mean, mean_percentile, **mark_mean_settings)

    median = np.median(data)
    median_percentile = 50
    mark_median_settings = {
        'c': 'g', 'ls': '--', 'marker': 's',
        'label': 'Median: ({:.2f}, {:.2f})'.format(median, median_percentile)}
    mark_ecdf(plt.gca(), median, median_percentile, **mark_median_settings)

    plt.legend()
    plt.grid()
    if not subplot:
        plt.show()


def bar_plot(data, labels, title=False, subplot=False, show_mean_median=True):
    data_serie = pd.Series(data)
    mean, median = data_serie.mean(), data_serie.median()

    if show_mean_median:
        data_serie['[[ Mean ]]'], data_serie['[[ Median ]]'] = mean, median

    data_serie = data_serie.sort_values(ascending=False)
    data_serie_chart = sns.barplot(x=data_serie.index, y=data_serie.values)
    plt.grid(axis='y')

    data_serie_chart.set_xticklabels(data_serie_chart.get_xticklabels(), rotation=90)

    if title:
        title = 'Bar plot - ' + title
    else:
        title = 'Bar plot'

    plt.title(title)
    plt.xlabel(labels['xlabel'])
    plt.ylabel(labels['ylabel'])
    if not subplot:
        plt.show()


def top_bottom_n(df, n=10):
    head, tail = df.head(n), df.tail(n)
    head.reset_index(drop=True, inplace=True)
    tail.reset_index(drop=True, inplace=True)
    return pd.concat([head, tail], axis=1)