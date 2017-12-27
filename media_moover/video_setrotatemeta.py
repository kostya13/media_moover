# -*- coding: utf-8 -*-
import argparse
from os.path import exists
import subprocess
import os
from media_moover import video_meta

FFMPEG = 'ffmpeg -i {} -metadata:s:v rotate={} -metadata creation_time="{}" -codec copy  {}'


def main():
    parser = argparse.ArgumentParser(
        description='Вращение видео файла. Только для mp4')
    parser.add_argument('--output',
                        help='Файл для сохранения')
    parser.add_argument('--backup', help='Сохранить копию файла',
                        action='store_true')
    parser.add_argument('value',
                        help='угол поворота',
                        choices=['0', '90', '180', '270'])
    parser.add_argument('file',
                        help='Исходный файл')
    args = parser.parse_args()
    if not exists(args.file):
        print('Исходный файл не найден')
        quit(1)
    if not args.file.lower().endswith('mp4'):
        print('Команда работает только с mp4 контейнером')
        quit(1)
    if args.output == args.file:
        print('Ошибка имя входного и выходного файлов совпадают')
        quit(1)
    metadata = video_meta(args.file)
    if not args.output:
        new_filename = 'tmp_{}'.format(args.file)
        os.rename(args.file, new_filename)
        res = subprocess.run(FFMPEG.format(new_filename, args.value, metadata,
                                           args.file),
                             stderr=subprocess.PIPE,
                             shell=True)
        if res.returncode:
            os.rename(new_filename, args.file)
        else:
            if not args.backup:
                os.remove(new_filename)
    else:
        res = subprocess.run(FFMPEG.format(args.file, args.value, metadata,
                                           args.output),
                             stderr=subprocess.PIPE,
                             shell=True)

    if res.returncode:
        print('Ошибка запуса конвертера')


if __name__ == '__main__':
    main()
