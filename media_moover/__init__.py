# -*- coding: utf-8 -*-
import argparse
import os
import shutil
from os.path import join, getmtime, basename
import subprocess
import time
import re
from datetime import datetime
from collections import namedtuple

DEFAULT_SOURCE = '/home/kostya/Изображения/Входящие'
DEFAULT_DESTANATION = '/home/media/Фото/Детки'

MediaInfo = namedtuple('Mediainfo', 'codec resolution rotation duration time')


def parse():
    parser = argparse.ArgumentParser(
        description='Переименование фотографий, согласно даты, взятой из exif')
    parser.add_argument('-t', action='store_true',
                        help='Тестирование. Показывает, что будет делать,'
                        ' но реально файлы не трогает')
    parser.add_argument('-s', dest='source',
                        help='Источник. Каталог, откуда берутся фотографии',
                        required=False,
                        default=DEFAULT_SOURCE)
    parser.add_argument('-d', dest='destination',
                        help='Назначение. Каталог, куда переносятся фотографии',
                        required=False,
                        default=DEFAULT_DESTANATION)
    args = parser.parse_args()
    source = args.source
    destination = args.destination
    test = args.t
    validate_paths(source, destination)
    if test:
        print("Режим тестирования!")
    return source, destination, test


def file_list(path, ext):
    return [f for f in os.listdir(path) if f.lower().endswith(ext)]


def validate_paths(source, destanation):
    if not os.path.exists(source):
        raise ValueError("Нужен правильный исходный каталог")
    if not os.path.exists(destanation):
        raise ValueError("Нужен правильный каталог назанчения")
    if source == destanation:
        raise ValueError("Пути должны быть различные")


def check_dest_path(dest, year):
    store_dir = join(dest, year)
    if not os.path.exists(store_dir):
        print('Создан каталог: {}'.format(store_dir))
        os.mkdir(store_dir)


def move_to(source, filename, dirname):
    store_dir = join(source, dirname)
    if not os.path.exists(store_dir):
        os.mkdir(store_dir)
    old_name = join(source, filename)
    new_name = join(store_dir, filename)
    shutil.move(old_name, new_name)
    # print('Файл "{}" перемещен'.format(filename))


def meta_from_mtime(path):
    lt = time.localtime(getmtime(path))
    return datetime(lt.tm_year, lt.tm_mon,
                    lt.tm_mday, lt.tm_hour,
                    lt.tm_min, lt.tm_sec)


def meta_from_creation_time(time_string):
    ts = time_string
    return datetime(*(int(i) for i in (ts[0:4], ts[5:7], ts[8:10],
                                       ts[11:13], ts[14:16], ts[17:19])))


def meta_from_filename(filename):
    base = basename(filename)
    match1 = re.match('VID_(\d{8})_(\d{6}).*', base)
    if match1:
        date = match1.group(1)
        time = match1.group(2)
        return datetime(*(int(i) for i in (date[0:4], date[4:6], date[6:8],
                                           time[0:2], time[2:4], time[4:6])))


def name_from_meta(info, filename):
    meta = None
    if info.time:
        meta = meta_from_creation_time(info.time)
    else:
        meta = meta_from_filename(filename)
        if not meta:
            meta = meta_from_creation_time(filename)
    if not meta:
        raise RuntimeError('Невозможно определить дату создания')
    name = "{:04}-{:02}-{:02}_{:02}{:02}{:02}".format(
        meta.year, meta.month, meta.day,
        meta.hour, meta.minute, meta.second)
    year = str(meta.year)
    return year, name + '.mp4'


def media_info(file):
    codec = None
    resolution = None
    rotation = 0
    duration = None
    time = ''

    res = subprocess.run('ffprobe "{}"'.format(file),
                         stderr=subprocess.PIPE, shell=True)
    if res.returncode:
        print("Ошибка детектора")
        print(res.stderr.decode())
        quit(1)

    for line in res.stderr.decode().split('\n'):
        match = re.search('Video: (.+?) \(.+', line)
        if match:
            codec = match.group(1)
        match = re.search(', (\d{2,4}x\d{2,4})', line)
        if match:
            resolution = [int(i) for i in match.group(1).split('x')]
        match = re.search('Duration: (.+?),', line)
        if match:
            duration = match.group(1)
        match = re.search('rotate          : (\d{2,3})', line)
        if match:
            rotation = int(match.group(1))
        if 'creation_time' in line:
            match = re.match('.+creation_time.+: (.+)', line)
            if match:
                time = match.group(1)
        elif 'date' in line:
            match = re.match('.+date.+: (.+)', line)
        if match:
            time = match.group(1)

    mi = MediaInfo(codec, resolution, rotation, duration, time)
    # print(mi)
    return mi
