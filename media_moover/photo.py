# -*- coding: utf-8 -*-
import os
import media_moover as mm
from os.path import join,exists
import exifread
import argparse

def store_bad_jpeg(source, name):
    store_dir = join(source, 'bad_exif')
    if not os.path.exists(store_dir):
        os.mkdir(store_dir)
    old_name = join(source, name)
    new_name = join(store_dir, name)
    os.rename(old_name, new_name)
    print('Файл "{}" перемещен'.format(name))


def new_file_name(tag):
    date, time = tag.values.split(' ')
    date = date.replace(":", "-")
    time = time.replace(":", "")
    year = date[0:4]
    filename = '{}_{}.jpg'.format(date, time)
    return  year, filename


def check_dest_path(dest, year):
    store_dir = join(dest, year)
    if not os.path.exists(store_dir):
        print('Создан каталог: {}'.format(store_dir))
        os.mkdir(store_dir)


def main():
    parser = argparse.ArgumentParser(description='Переименование фотографий, согласно даты, взятой из exif')
    parser.add_argument('-t',action='store_true',
                        help='Тестирование. Показывает, что будет делать, но реально файлы не трогает')
    parser.add_argument('-s',dest='source',
                        help='Источник. Каталог, откуда берутся фотографии',
                        required=False,
                        default=mm.DEFAULT_SOURCE)
    parser.add_argument('-d',dest='destination',
                        help='Назначение. Каталог, куда переносятся фотографии',
                        required=False,
                        default=mm.DEFAULT_DESTANATION)

    args=parser.parse_args()

    source = args.source
    destination = args.destination
    testOnly=args.t

    try:
        mm.validate_paths(source, destination)
    except ValueError as e:
        print(e)
        quit()

    if testOnly:
        print("Режим тестирования!")

    for jpeg in mm.file_list(source, 'jpg'):
        path = join(source, jpeg)
        with open(path, 'rb') as f:
            tags = exifread.process_file(f)
            date_times = tags.get('Image DateTime')
            if not date_times:
                print("Тег времени отсутствует")
                store_bad_jpeg(source, jpeg)
                continue
        try:
            year, new_name = new_file_name(date_times)
        except ValueError as e:
            print(e)
            print('Неправильное значение тега: {}'.format(date_times))
            continue
        old_path = join(source, jpeg)
        new_path = join(destination, year, new_name)
        check_dest_path(destination, year)
        print('{} -> {}'.format(old_path, new_path))
        if not testOnly:
            os.rename(old_path, new_path)


if __name__ == '__main__':
    main()
