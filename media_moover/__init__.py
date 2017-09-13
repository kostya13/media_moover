# -*- coding: utf-8 -*-
import argparse
import os
import shutil
from os.path import exists, join

DEFAULT_SOURCE = '/home/kostya/Изображения/Входящие'
DEFAULT_DESTANATION = '/home/media/Фото/Детки'


def parse():
    parser = argparse.ArgumentParser(
        description='Переименование фотографий, согласно даты, взятой из exif')
    parser.add_argument('-t',action='store_true',
                        help='Тестирование. Показывает, что будет делать,'
                        ' но реально файлы не трогает')
    parser.add_argument('-s',dest='source',
                        help='Источник. Каталог, откуда берутся фотографии',
                        required=False,
                        default=DEFAULT_SOURCE)
    parser.add_argument('-d',dest='destination',
                        help='Назначение. Каталог, куда переносятся фотографии',
                        required=False,
                        default=DEFAULT_DESTANATION)
    args=parser.parse_args()
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
    if source==destanation:
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
    # os.rename(old_name, new_name)
    shutil.move(old_name, new_name)
    print('Файл "{}" перемещен'.format(filename))
