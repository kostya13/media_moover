# -*- coding: utf-8 -*-
import shutil
import media_moover as mm
from os.path import join
import exifread
import re


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
    match = re.match('IMG_(\d{8})_(\d{6}).*.jpg', filename)
    if match:
        date = match.group(1)
        time = match.group(2)
        year = date[:4]
        name = '{}-{}-{}_{}.jpg'.format(date[0:4], date[4:6], date[6:8], time)
        return year, name
    else:
        return None, None


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
                print("Тег времени отсутствует")
                year, new_name = rename_by_filename(jpeg)
                if not year:
                    store_bad_jpeg(source, jpeg)
                    continue
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
            shutil.move(old_path, new_path)


if __name__ == '__main__':
    main()
