# -*- coding: UTF-8 -*-

import requests
import re
import json
import os, sys
import argparse
import time
from datetime import timedelta
import execjs
import threading
import multiprocessing
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import fnmatch
from fundfilter import *
from threadpool import *

pyfund_version = '1.0'

list_url = 'http://fund.eastmoney.com/js/fundcode_search.js'
headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56',
    }
plt.rcParams['font.sans-serif']=['SimHei']

totay = time.strftime("%Y%m%d", time.localtime())
dbpath = os.path.join(os.getcwd(), 'db', totay)
max_day_count = 90

def get_funds_list():
    global list_url
    resp = requests.get(list_url)

    if resp.status_code != 200:
        return None

    try:
        jsctx = execjs.compile(resp.text)
        funds_list = jsctx.eval('r')

        return list(filter(lambda fund: fund[3] in funds_type_filter_list, funds_list))
    except:
        return None

def funds_list_to_string(funds_list):
    header = (
        'Code', 'Pinyin Abbreviation', 'Chinese Name', 'Type', 'Pinyin'
    )

    line = ''
    for item in header:
        line += '%s, ' % item

    line = line[:-2]

    yield line

    for item in funds_list:
        line = ''
        for var in item:
            line += '%s, ' % var
        line = line[:-2]

        yield line

def dump_fund_info(fund_info, fund_content):

    if os.access(os.path.join(os.getcwd(), 'db'), os.F_OK) is False:
        os.mkdir(os.path.join(os.getcwd(), 'db'))
    if os.access(dbpath, os.F_OK) is False:
        os.mkdir(dbpath)

    with open(os.path.join(dbpath, '%s_%s_%s.js' % fund_info), 'w+') as f:
        f.write(fund_content)
        
def seek_fund_info(code):
    global headers
    resp = requests.get('http://fund.eastmoney.com/pingzhongdata/%s.js?v=%s' % (code, time.strftime("%Y%m%d%H%M%S", time.localtime())),
         headers=headers)

    return resp.text if resp.status_code == 200 else None

def get_fund_info(code, fund, count=None):

    try:
        jsctx = execjs.compile(fund)
        networth = jsctx.eval('Data_netWorthTrend')
        fundname = jsctx.eval('fS_name')
        fundcode = code

        if type(count) is int and len(networth) > count:
            networth = networth[-count:]

        return (fundname, fundcode, networth)
    except:
        return None


def show_fund_info(fund):

    fundname, fundcode, networth = fund

    x = []
    y = []
    for item in networth:
        x.append(item['x']//1000)
        y.append(item['y'])

    fig, ax = plt.subplots()
    xtick = [i for i in range(0, len(x), len(x) // 10)]
    xlabels = [time.strftime("%Y-%m-%d", time.localtime(x[i])) for i in xtick]
    xtick.append(len(x))
    xlabels.append(time.strftime("%Y-%m-%d", time.localtime(x[-1])))
    ax.set_xticks(xtick)
    ax.set_xticklabels(xlabels, rotation=-30)

    labeltext = plt.text(len(x) -1 , y[-1], '', fontsize = 10)

    def show_day_info(event):
        try:
            if event.xdata < 0:
                return
            xpos = int(np.round(event.xdata))
            yval = y[xpos]
            labeltext.set_position((xpos, yval))
            color = 'black'
            if xpos > 0:
                increment = (yval - y[xpos - 1]) * 100 / y[xpos - 1]
                color = 'red' if increment > 0 else 'green' if increment < 0 else color
                disptext = 'Value: %f\nIncrement: %0.2f%%\nDate: %s' % (yval, increment, time.strftime("%Y-%m-%d", time.localtime(x[xpos])))
            else:
                disptext = 'Value: %f\nDate: %s' % (yval, time.strftime("%Y-%m-%d", time.localtime(x[xpos])))
            labeltext.set_text(disptext)
            labeltext.set_color(color)
            fig.canvas.draw_idle()
        except:
            pass

    
    for index, yval in enumerate(y):
        increment = 1 if index == 0 else (yval - y[index - 1]) / y[index - 1]
        _x = [index]
        _y = [yval]
        plt.fill_between(_x, _y, 1, color='red' if increment > 0 else 'green', alpha=0.5, linewidth=1.5)

    fig.canvas.mpl_connect('motion_notify_event', show_day_info)
    fig.canvas.set_window_title('%s(%s)' % (fundname, fundcode))
    plt.grid(True)
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('%s(%s)' % (fundname, fundcode))
    plt.plot(y)
    plt.show()


def do_seek_funds():

    funds_list = get_funds_list()

    if funds_list is None:
        print('failed to get funds list')
        exit(-1)

    middleware = [
        is_my_favorite
    ]

    def middleware_filter_routine(fund_info):
        for mw in middleware:
            if mw(fund_info) is False:
                return False

        return True

    t = time.time()
    mu = threading.Lock()
    pool = threadpool(multiprocessing.cpu_count())
    print('my favorite funds:')
    funds_info_list = []
    for fund in funds_list:

        def thread_run(fund):
            try:
                fund_raw = seek_fund_info(fund[0])
                fund_info = get_fund_info(fund[0], fund_raw, max_day_count)
                if fund_info is None:
                    raise 'failed to analyze this fund, fund_info is None'
                if middleware_filter_routine(fund_info) is False:
                    raise 'this fund is not suit for me'

                dump_fund_info((fund[0], fund[2], fund[3]), fund_raw)
                mu.acquire()
                print(fund[0], fund[2], fund[3])
                funds_info_list.append(fund_info)
                mu.release()
            except:
                pass
            
        pool.submit(thread_run, (fund,))
    
    pool.join_all()
    print('elapse:', str(timedelta(seconds=int(time.time() - t))))

def do_analyze():
    if os.access(dbpath, os.F_OK) is False or len(os.listdir(dbpath)) == None:
        print('no datafile found')
        return

    funds_file_list = os.listdir(dbpath)

    print('saved funds are listed as below:')
    for files in funds_file_list:
        print(os.path.splitext(files)[0])

    while True:
        code = input('please select your favorite fund or input \"quit\" to exit: ')

        if code == 'quit':
            break

        filename = None
        for fn in funds_file_list:
            if fnmatch.fnmatch(fn, '%s_*.js' % code):
                filename = fn
                break

        if filename is None or filename == '':
            print('no matched fund found')
            continue

        fd = None
        fund_info = None
        fund_ctx = ''
        try:
            fd = open(os.path.join(dbpath, filename))
            fund_ctx = fd.read()
            fund_info = get_fund_info(code, fund_ctx, max_day_count)
            if fund_info is None:
                continue

            show_fund_info(fund_info)
            
        except Exception as e:
            print(e, 'invalid fund code')
        finally:
            if fd is not None:
                fd.close()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--seek', '-s', help='to seek funds data', action="store_true")
    parser.add_argument('--analyze', '-a', help='to analyze saved funds data', action="store_true")

    args = parser.parse_args()

    print(pyfund_version)

    if args.seek:
        do_seek_funds()

    if args.analyze:
        do_analyze()

    