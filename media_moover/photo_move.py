# -*- coding: utf-8 -*-
import shutil
import media_moover as mm
from os.path import join, getmtime
import exifread
import re
import time


def store_bad_jpeg(source, name):
    mm.move_to(source, name, 'bad_exif')


def rename_by_tag(tag):
    date, time = tag.values.split(' ')
    date = date.replace(":", "-")
    time = time.replace(":", "")
    year = date[0:4]
    filename = '{}_{}.jpg'.format(date, time)
    return year, filename


def rename_by_filename(filename):
    match1 = re.match('IMG_(\d{8})_(\d{6}).*.jpg', filename)
    match2 = re.match('(\d{4})-(\d{2})-(\d{2}) (\d{2})-(\d{2})-(\d{2}).*.JPG', filename)
    match3 = re.match('viber image (\d{4})-(\d{2})-(\d{2}) , (\d{2}).(\d{2}).(\d{2}).jpg', filename)
    if match1:
        date = match1.group(1)
        time = match1.group(2)
        year = date[:4]
        name = '{}-{}-{}_{}.jpg'.format(date[0:4], date[4:6], date[6:8], time)
        return year, name
    elif match2 or match3:
        match = match2 if match2 else match3
        year = match.group(1)
        m2g = match.group
        time = '{}{}{}'.format(m2g(4), m2g(5), m2g(6))
        name = '{}-{}-{}_{}.jpg'.format(m2g(1), m2g(2), m2g(3), time)
        return year, name
    else:
        return None, None


def rename_by_mtime(path):
    lt = time.localtime(getmtime(path))
    name = "%04i-%02i-%02i %02i:%02i:%02i" % (lt.tm_year, lt.tm_mon,
                                              lt.tm_mday, lt.tm_hour,
                                              lt.tm_min, lt.tm_sec)
    return str(lt.tm_year), name

def main():
    try:
        source, destination, test = mm.parse()
    except ValueError as e:
        print(e)
        quit()

    for jpeg in mm.file_list(source, 'jpg'):
        path = join(source, jpeg)
        with open(path, 'rb') as f:
            tags = exifread.process_file(f)
        date_times = tags.get('Image DateTime')
        try:
            if date_times:
                year, new_name = rename_by_tag(date_times)
            else:
                year, new_name = rename_by_filename(jpeg)
                if not year:
                    year, new_name = rename_by_mtime(path)
        except ValueError as e:
            print(e)
            print('Неправильное значение тега: {}'.format(date_times))
            store_bad_jpeg(source, jpeg)
            continue
        old_path = join(source, jpeg)
        new_path = join(destination, year, new_name)
        mm.check_dest_path(destination, year)
        print('{} -> {}'.format(old_path, new_path))
        if not test:
            # os.rename(old_path, new_path)
            if os.path.exists(new_path):
                print('Файл уже существует ', new_path)
            else:
                shutil.move(old_path, new_path)


if __name__ == '__main__':
    main()
