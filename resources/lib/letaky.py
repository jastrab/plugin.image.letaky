# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import unicodedata
import requests

import re
import json
import os
import datetime


import zipfile

#Python 2
try: 
    import urllib2 as request
    import urllib as parse
    def encode(string):
        string = str(unicodedata.normalize('NFKD', string).encode('ascii', 'ignore'))#, "utf-8")
        return string
#Python 3
except:
    from urllib import parse, request
    def encode(string):
        string = str(unicodedata.normalize('NFKD', string).encode('ascii', 'ignore'), "utf-8")
        return string

_url = sys.argv[0]
try:
    _handle = int(sys.argv[1])
except:
    pass

addon = xbmcaddon.Addon()


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, parse.urlencode(kwargs, 'utf-8'))

def load_url(url, req=None, headers={}):
    if req:
        req = parse.urlencode(req).encode('utf-8')
        req = request.Request(url, req, headers=headers)
    else:
        req = request.Request(url, headers=headers)
    r =  request.urlopen(req)
    response = r.read()
    return response.decode()

temp = 'data.zip'

def post_search(search_key):
    data = {'token': 'XXahoj@@post&&moje!!kodi@@', 'search': search_key}
    data = requests.post(URL_API, data=data)
    data = json.loads(data.text)
    data = sortDataSpecific(data)
    return data

def load_url_zip(url, req=None, headers={}):
    try:
        response = requests.get(url, stream=True)
        with open(temp, "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return True
    except:
        return False
   

def json_load_data0000():
    down_zip = False    
    data_web = load_url_zip(URL_JSON_ZIP)
    if data_web:
        try:
            archive = zipfile.ZipFile(temp, 'r')
            data = archive.read('data_test.json')
            data = json.loads(data)
            down_zip = True    

        except:
            down_zip = False    

    if not down_zip:
        data_web = load_url(URL_JSON)
        data = json.loads(data_web)
 
    return data

def json_load_data():
    data_web = load_url(URL_JSON)
    data = json.loads(data_web)
    return data

_max_old_items = 3

LANG = addon.getSetting("lang")

OBCHODY = addon.getSetting("obchody")
OBCHODY_CZ = addon.getSetting("obchody_cz")

if LANG =='cz':
    OBCHODY = OBCHODY_CZ
    URL_API = 'https://letaciky.cz/api.php'
    # URL = 'https://letaciky.cz/images/%s'%( LANG)
    # URL = 'https://iovca.eu/images2/%s'%( LANG)
    URL_JSON = 'https://letaciky.cz/json/data_cz.json'
else:
    URL_API = 'https://letaciky.sk/api.php'
    # URL = 'https://letaciky.sk/images/%s'%( LANG)
    URL_JSON = 'https://letaciky.sk/json/data_sk.json'


URL = 'https://iovca.eu/images2/%s'%( LANG)
# URL = 'https://iovca.eu/images/%s'%( LANG)
#URL_JSON = 'https://iovca.eu/images/data_test.json'
#URL_JSON_ZIP = 'https://iovca.eu/images/data_test.zip'


_icons = 'https://iovca.eu/images/icons/'

# DATA_SEARCH = {}
DATA = json_load_data()[LANG]
data_filter = {}

if len(OBCHODY) > 1:
    OBCHODY = sorted(list(OBCHODY.split('|')))
else:
    OBCHODY = sorted(list(DATA.keys()))

for f in OBCHODY:
    if f in DATA.keys():
        data_filter[f] =  DATA [f] 

# DATA = data_filter
DATA_FILTER = data_filter
FORMAT_IMG = 'webp'

MM = [00, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]

def currentDate():
    today = datetime.date.today()
    return today.strftime("%Y-%m-%d")



def getDataCell(data, cell, key):
    data_select = []
    for d in data:    
        if type(cell) == list:
            b = getCell(d, cell)
        else:
            b = d.get(cell)

        if b == None:
            b = 'None'
        if b and b == key:
                data_select.append(d)
    return data_select


def getCell(data, cells):
    idata = None
    for c in cells:
        if c in data:
            idata = data.get(c)
    return idata


def sortData(data, cell, reverse=False):
    ckeys = []
    for d in data:
        if type(cell) == list:
            dcell = getCell(d, cell) #d[cell]
        else:
            dcell = d.get(cell)

        if dcell not in ckeys:
            ckeys.append(dcell)

    if None in ckeys:
        ckeys[ ckeys.index(None) ] = 'None'
 
    ckeys.sort(reverse=reverse) 
    data_new = []
    for c in ckeys:
        sub_data = getDataCell(data, cell, c)
        data_new += sub_data

    return data_new



def sortDataSpecific(datas):
    #for data in datas:
    for i in range(len(datas)):
        data = datas[i]
        sub_title = ''
        if 'sub_title' in data:
            sub_title = data['sub_title']
        idx = 1
        if  'days' in data and data['days'] > 62 and  data['endDate']:
            idx = 2

        if 'endDate' in data and data['endDate'] and currentDate() > data['endDate']:
            idx = 3

        datas[i]['idx'] = idx
    data_new = []
    for i in range(1, 4):
        data = getDataCell(datas, 'idx', i)
        data = sortData(data, 'startDate', True)
        data_new += data

    return data_new


"""
Posun datumu vpred, alebo vzad na dni

update 21/2/2022 - fix na dni -> 365+ - pridane while
"""
def shiftDate(date, shift = -1):
    months = MM
    y, m, d = date.split('-')
    d = int(d)
    m = int(m)
    y = int(y)
    #fix priestupny rok
    if y % 4 == 0:
        months[2] += 1

    d += shift

    if d < 1:
        while d < 1:
            m -= 1
            if m < 1:
                y -= 1
                m += 12
            d = months[m] + d

    else:
        while d > months[m]:
            d = d - months[m]
            m += 1
            if m > 12:
                y += 1
                m -= 12
        
    return '{}-{:02d}-{:02d}'.format(y,m,d)

"""
Vrati priblizni pocet dni od datumov
startDate = "2021-10-13"
endDate   = "2023-01-01"
"""
def days_from_dates(startDate, endDate):
    _mm = MM
    _yy = 365   #ignorujem priestupny rok

    if startDate == None:
        startDate = currentDate()

    #Neviem koniec datumu tak mu dam 10 rokov -> osetrim kodom do neznama
    if endDate == None:
        endDate = shiftDate (currentDate(), 365*10)

    sy, sm, sd = startDate.split('-')
    sd = int(sd)
    sm = int(sm)
    sy = int(sy)
    ey, em, ed = endDate.split('-')
    ed = int(ed)
    em = int(em)
    ey = int(ey)

    y = ey - sy
    m = em - sm
    d = ed - sd

    if d < 0:
        d += _mm[sm]
        m -= 1

    if m < 0:
        m += 12
        y -= 1

    month = 0
    for i in range(m):
        month += _mm[i+1]
    
    days = d + month + (y * _yy)
    return days

"""
Prida / Odobere nuly v cislach
"""
def zero(num, typ):
    if not num:
        return None
    if not typ:
        return num
    elif typ == '00':
        return '{:02d}'.format(int(num))
    elif typ == '0':
        return '{:01d}'.format(int(num))


# "2022-01-30"
# "2022-01-24"
# od 24.1. do 30.1.2022
def fixDateNew(startDate, endDate, typ = None):
    sy, sm, sd = startDate.split('-')
    ey, em, ed = endDate.split('-')
    sd = zero(sd, typ)
    sm = zero(sm, typ)
    ed = zero(ed, typ)
    em = zero(em, typ)
    if int(ey) == 2100:#Konecny datum neexistuje
        return 'od {}.{}.{}'.format(sd, sm, sy)
    else:
        return 'od {}.{}. do {}.{}.{}'.format(sd, sm, ed, em, ey)

def fixDateNewColor(startDate, endDate, color='blue', typ = None):
    sy, sm, sd = startDate.split('-')
    ey, em, ed = endDate.split('-')
    sd = zero(sd, typ)
    sm = zero(sm, typ)
    ed = zero(ed, typ)
    em = zero(em, typ)
    
    if int(ey) == 2100: #Konecny datum neexistuje
        return 'od [COLOR={}]{}.{}.{}[/COLOR]'.format(color, sd, sm, sy)
    else:
        return 'od [COLOR={}]{}.{}.[/COLOR] do [COLOR={}]{}.{}.{}[/COLOR]'.format(color, sd, sm,  color, ed, em, ey)


_CHR = ['%20', '%21', '%22', '%23', '%24', '%25', '%26', '%27', '%28', '%29', '%2a', '%2b', '%2c', '%2d', '%2e', '%2f', '%3a', '%3b', '%3c', '%3d', '%3e', '%3f', '%40']
_UTF = [' ', '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@']
def parse_par(text):
    data = {}
    if not text or text == '':
        return data
    if text and text != '':
        for t in text.split('&'):
            k, v = t.split('=')
            if 'http' in v[:4]:
                for i in range(len(_CHR)):
                    if _CHR [i] in v:
                        v = v.replace( _CHR [i], _UTF[i] )
            data[k] = v
    return data


def fixTitle(title):
    title = title.replace('_', ' ')
    title = title[0].upper() + title[1:]
    title = title.replace('.%s'%FORMAT_IMG, '') 
    return title


def menu_new(data_type='all'):

    if data_type:
        if data_type == 'filter':
            datas = DATA_FILTER
        elif data_type == 'all':
            # Zoradenie podla title v DATAch
            data_infos = []
            for k, v in DATA.items():
                v['info']['id'] = k
                data_infos.append(v['info'])

            data_infos = sortData(data_infos, 'title')
            datas = {}
            for d in data_infos:
                datas[d['id']] = {'info': d}


    list_item = xbmcgui.ListItem(label=addon.getLocalizedString(32100))
    list_item.setInfo('image', {'title': addon.getLocalizedString(32100),
                                'genre': addon.getLocalizedString(32100)})
    list_item.setArt({'icon': 'DefaultAddonsSearch.png'})
    link = get_url(search='1')
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, link, list_item, is_folder)

    if data_type != 'all':
        list_item = xbmcgui.ListItem(label=addon.getLocalizedString(32004))
        list_item.setInfo('image', {'title': addon.getLocalizedString(32004),
                                    'genre': addon.getLocalizedString(32004)})
        # list_item.setArt({'icon': 'DefaultAddonsSearch.png'})
        link = get_url(action = 'menu_all')
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, link, list_item, is_folder)

    # menu_new_items(data_type='filter')

    for k, v in datas.items():
        #title = v['info']['title']['title']
        title = v['info']['title']
        name = fixTitle ( title )
        list_item = xbmcgui.ListItem(label=name)
        list_item.setIsFolder(True)
        url = URL + '/' + k
        # icon = '%s/__cover__.%s'%(url, FORMAT_IMG)
        icon = '%s/%s.webp'%(_icons, k)

        list_item.setArt({'thumb': icon, 'icon': icon})
        link = get_url(action = 'folders_new', path = encode(url), id = k, data_type=data_type)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, link, list_item, is_folder)
    # xbmcplugin.endOfDirectory(_handle)
    xbmcplugin.endOfDirectory(_handle)


def color_text(data, is_search=False):
    actual = currentDate()
    DD = {'letak': {'name': 'Leták',   'date_color_cur': 'lightgreen', 'date_color_old': 'gray', 'date_color_new': 'orange'},
        'katalog': {'name': 'Katalóg', 'date_color_cur': 'lightblue',  'date_color_old': 'gray', 'date_color_new': 'violet'}}

    typ = 'letak'
    days = data['days']
    if days > 60:
        typ = 'katalog'

    startDate =  data['startDate']
    endDate =  data['endDate']
    if 'startDate' not in data or data['startDate'] is None:
        startDate = '2000-01-01'

    if 'endDate' not in data or endDate is None:# is  or data['endDate'] is None:
        endDate = '2100-01-01'

    """
    wait: - ostavajuce dni
     2 - buduci
     1 - aktualny
     0 - stary
    -1 - katalog... - bez ostavajucich dni 
    """
    dd = DD[typ]
    old = False
    color = dd['date_color_cur']
    if startDate > actual:
        color = dd['date_color_new']
        idays = days_from_dates(actual, startDate)
        check_text = ' dostupný o [COLOR=red]%s[/COLOR] %s'%(idays, 'dni' if idays!=1 else 'deň')
    elif endDate < actual:
        color = dd['date_color_old']
        old = True
        idays = days_from_dates(endDate, actual) - 1
        check_text = ' skončilo pred %s %s'%(idays, 'dňami' if idays!=1 else 'dňom')
    else:
        idays = days_from_dates(actual, endDate) + 1
        check_text = ' ostáva [COLOR=red]%s[/COLOR] %s'%(idays, 'dni' if idays!=1 else 'deň')
    if  typ == 'katalog':
        check_text = ''

    #pages = data['pages2']
    pages = data['pages']

    sub_title = ''
    if 'sub_title' in data and data['sub_title'] != None:
        sub_title = data['sub_title']
    
    if is_search:
            date_od_do = fixDateNewColor(startDate, endDate, color)
            # page = data['strana_kodi']
            page = data['strana']
            name = '[COLOR=yellow]%s[/COLOR] strana [COLOR=yellow]%s[/COLOR] %s %s ([COLOR=red]%s[/COLOR])'%(data['obchod'], page, date_od_do, sub_title, pages )
    else:
        if not old:
            date_od_do = fixDateNewColor(startDate, endDate, color)
            name = '%s %s %s ([COLOR=red]%s[/COLOR]) %s'%(dd['name'], date_od_do, sub_title, pages, check_text )
        else:
            date_od_do = fixDateNew(startDate, endDate)
            name = '[COLOR=%s]%s %s %s (%s) %s[/COLOR]'%(color, dd['name'], date_od_do, sub_title, pages, check_text )
        # return name
    return {'old': old, 'name': name }


def folder_new(id, data_type='all'):
    idx_old = 0
    actual = currentDate()
    is_search = False
    if data_type:
        if data_type == 'filter':
            datas = sortDataSpecific(DATA_FILTER[id]['data'])
        elif data_type == 'search':
            datas = DATA_SEARCH
            is_search = True
        elif data_type == 'all':
            datas = sortDataSpecific(DATA[id]['data'])


    for data in datas:
        title = data['title']
        name = fixTitle ( title )
        if 'days' in data:
            # name = color_text(data)
            no = color_text(data, is_search)
            if no['old']:
                idx_old += 1
            name = no['name'] if idx_old <= _max_old_items else None
            if not name:
                continue

        listitem = xbmcgui.ListItem(label=name)
        listitem.setIsFolder(True)        
        if is_search:
            # page = data['strana_kodi']
            page = data['strana']
            id = data['obchod']
            url = '%s/%s/%s'%(URL, id, title)
            icon = '{}/strana_{:02d}.{}'.format(url, page, FORMAT_IMG)
        else:
            url = '%s/%s/%s'%(URL, id, title)
            icon = '%s/__cover__.%s'%(url, FORMAT_IMG)

        listitem.setArt({'thumb': icon, 'icon': icon})
        url = get_url(action = 'pictures_new', path = encode(url), id = id, letak = data['title'], pages = data['pages'])
        xbmcplugin.addDirectoryItem(_handle, url, listitem, True)
    xbmcplugin.endOfDirectory(_handle)

def pictures_new(id, letak, pages):
    for i in range(int(pages)):
        title = 'strana_{:02d}.{}'.format(i+1, FORMAT_IMG)
        name = fixTitle ( title)
        url = '%s/%s/%s/%s'%(URL, id, letak, title) 
        listitem = xbmcgui.ListItem(label=name)
        listitem.setInfo('pictures', {'title': name})
        if addon.getSetting("thumb_enabled") == "false":
            listitem.setArt({'thumb': 'DefaultPicture.png', 'icon': 'DefaultPicture.png'})
        xbmcplugin.addDirectoryItem(_handle, url, listitem, False)
    xbmcplugin.endOfDirectory(_handle)

def list_search(query=None):
    global DATA_SEARCH
    xbmcplugin.setPluginCategory(_handle, (addon.getLocalizedString(32100)))

    if query is None:
        kb = xbmc.Keyboard('', addon.getLocalizedString(32100))
        kb.doModal()
        if kb.isConfirmed():
            query = kb.getText()
        else:
            query = ''

    if query:
        DATA_SEARCH = post_search(query)
        folder_new(None, 'search')
      
    xbmcplugin.endOfDirectory(_handle)


def router(paramstring):
    params = parse_par(paramstring)
    if params:
        if 'action' in params:
            if params['action'] == 'menu_new':
                menu_new(data_type='filter')

            elif params['action'] == 'menu_all':
                menu_new(data_type='all')

            elif params['action'] == 'folders_new':
                folder_new(params["id"], params["data_type"])

            elif params['action'] == 'pictures_new':
                pictures_new(params["id"], params["letak"], params["pages"])

            else:
                menu_new(data_type='filter')

        elif 'query' in params:
            list_search(params['query'])

        elif 'search' in params:
            list_search()

        else:
            menu_new(data_type='filter')
    else:
        menu_new(data_type='filter')

