# -*- coding: utf-8 -*-
import os
import media_moover as mm
from os.path import join, exists, getmtime
import time
import subprocess

FFMPEG = 'ffmpeg  -i {0} -vcodec mpeg4 -acodec mp3 -b:v 3000k -b:a 96k -vf scale=-1:480 {1}'

def new_file_name(path):
    lt = time.localtime(getmtime(path))
    name = "%04i-%02i-%02i_%02i%02i%02i.avi" % (lt.tm_year, lt.tm_mon,
                                                lt.tm_mday, lt.tm_hour,
                                                lt.tm_min, lt.tm_sec)
    return str(lt.tm_year), name

def save_converted(source, name):
    mm.move_to(source, name, 'converted')


def main():
    try:
        source, destination, test = mm.parse()
    except ValueError as e:
        print(e)
        quit()

    for avi in mm.file_list(source, 'avi'):
        source_name = join(source, avi)
        year, new_name = new_file_name(source_name)
        dest_name = join(destination, year, new_name)
        print('{} -> {}'.format(source_name, dest_name))
        if test:
              continue
        mm.check_dest_path(destination, year)
        res = subprocess.run(FFMPEG.format(source_name, dest_name), shell=True)
        if res.returncode:
            print('Ошибка запуса конвертера')
        else:
            save_converted(source, avi)


if __name__ == '__main__':
    main()
