# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 ---- Program:
 ---- Description:
 ---- Author: Ed
 ---- Date: 2018-07-21 15:46:34
 ---- Last modified: 2018-07-21 18:56:41
"""

import requests
import pymysql
from time import strptime
import os

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
SESSION = requests.Session()

class Mysql(object):

    config = dict(
            host = '10.43.37.104',
            user = 'wang',
            db = 'tigernews',
            charset = 'utf8',
            autocommit = True,
            )
    try:
        connection = pymysql.connect(**config)
    except Exception as e :
        print(e)
    else:
        print('Login in Mysql Successfully')
        cur = connection.cursor()


def get_data():
    resource_list_url = 'http://pc-shop.xiaoe-tech.com/appNpA3AQHk1411/open/column.resourcelist.get/2.0'
    data = {
        'data[page_index]' : '0',
        'data[page_size]' : '365',
        'data[order_by]' : 'start_at:desc',
        'data[resource_id]':'p_5a17b65cd894e_UrfTEcOq',
        'data[state]':'0',
        'data[resource_types][]':'2',
        }

    headers = {
        'Host': 'pc-shop.xiaoe-tech.com',
        'Origin': 'https://pc-shop.xiaoe-tech.com',
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 7.0; en-us; STF-AL10 Build/HUAWEISTF-AL10) AppleWebKit/537.36 (KHTML, like Gecko) MQQBrowser/7.3 Chrome/37.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://pc-shop.xiaoe-tech.com/appNpA3AQHk1411/columnist_detail?id=p_5a17b65cd894e_UrfTEcOq',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    cookies = {'laravel_session':'eyJpdiI6IjZyeDdxVVJuNFlOcFwvTWZoTG9UbGR3PT0iLCJ2YWx1ZSI6Ilk3R1o2eUk4Ukh3S1lQU2pncHpoVHFkN3dXb2NIOWswMXVKRUdwVlc4d3pxMTVTbGpHTlE2cFRSenJNcnBRSzlPTXVyNGhreUZtVmZXT3JCcjZhb1pBPT0iLCJtYWMiOiI2MmQ5ODFkNjA1NmQ1ZmZmYTZmNjkyMzY1MmNkMzZkNTNlNjEwMjViYjI5ZDZhZTczN2I2ZmJiN2VkMjc0YTE3In0%3D'}

    response = SESSION.post(resource_list_url, headers = headers, data = data, verify = False, cookies = cookies)
    return response

def parse(items):
    for each_item in items:
        if  '原文朗读' not in each_item['title'] :
            print('Downloading... {} {}'.format(each_item['created_at'], each_item['title']))
            each_item['title'] = each_item['title'].split('|')[-1].strip()
            each_item['audio_url'] = get_audio_url(each_item)
            save_txt(each_item)
            save_audio(each_item)
            insert_mysql(each_item)

def get_audio_url(item):
    audio_url = 'https://pc-shop.xiaoe-tech.com/appNpA3AQHk1411/open/audio.detail.get/1.0'
    data = {'data[resource_id]':item['id']}
    response = SESSION.post(audio_url, data = data, verify = False)
    audio_url = response.json()['data']['audio_url']
    return audio_url

def save_txt(item):
    txtname = os.path.join(THIS_DIR, 'Articles', '{}.html'.format(item['title']))
    with open(txtname, 'w', encoding = 'utf8') as f:
        f.write(item['desc'])
    print('{} {} was downloaded successfully!'.format(item['title'], item['created_at']))

def save_audio(item):
    audio_resource = SESSION.get(item['audio_url']).content
    audioname = os.path.join(THIS_DIR, 'Audios', '{}.mp3'.format(item['title']))
    with open(audioname, 'wb') as f:
        f.write(audio_resource)
    print('{} {} was downloaded successfully!'.format(item['title'], item['created_at']))

def insert_mysql(item):
    sql = 'insert into danhansong(id, title, start_at, created_at, summary, audio_url) values(%s,%s,%s,%s,%s,%s)'
    try:
        Mysql.cur.execute(sql, list(map(lambda x: item.get(x), ('id', 'title', 'start_at', 'created_at', 'summary', 'audio_url'))))
    except Exception as e:
        print(e)
    else:
        print('Insert {} {} successfully!'.format(item['title'], item['created_at']))

def main():
    response = get_data()
    if response.status_code == 200:
        articles = response.json()['data']
        parse(articles)
    else:
        print('Error!Can not connect to the server!')


if __name__ == '__main__':
    main()

"""
drop table if exists danhansong;
create table if not exists danhansong(
    id char(24) primary key,
    title varchar(100),
    start_at date,
    created_at date,
    summary varchar(250)
);
"""
