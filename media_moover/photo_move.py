# -*- coding: utf-8 -*-
import shutil
import media_moover as mm
from os.path import join
import exifread


def store_bad_jpeg(source, name):
    mm.move_to(source, name, 'bad_exif')


def new_file_name(tag):
    date, time = tag.values.split(' ')
    date = date.replace(":", "-")
    time = time.replace(":", "")
    year = date[0:4]
    filename = '{}_{}.jpg'.format(date, time)
    return year, filename


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
        mm.check_dest_path(destination, year)
        print('{} -> {}'.format(old_path, new_path))
        if not test:
            # os.rename(old_path, new_path)
            shutil.move(old_path, new_path)


if __name__ == '__main__':
    main()
