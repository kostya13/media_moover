# -*- coding: utf-8 -*-
import argparse
from os.path import exists
import subprocess
import os
from media_moover import video_meta

FFMPEG = 'ffmpeg -i {} -metadata {}  -b:v 9000k -acodec copy -vf "{}" {}'

ROTATE_DIRECTIONS = {'cw': 'transpose=1',
                     'ccw': 'transpose=2',
                     '180': 'transpose=2,transpose=2'}


def main():
    parser = argparse.ArgumentParser(description='Вращение видео файла')
    parser.add_argument('--output',
                        help='Файл для сохранения')
    parser.add_argument('--backup', help='Сохранить копию файла',
                        action='store_true')
    parser.add_argument('direction',
                        help='Направление вращение,'
                        ' по часовой стрелке или против или на 180 градусов',
                        choices=['cw', 'ccw', '180'])
    parser.add_argument('file',
                        help='Исходный файл')
    args = parser.parse_args()
    if not exists(args.file):
        print('Исходный файл не найден')
        quit(1)
    ffmpeg_direction = ROTATE_DIRECTIONS[args.direction]
    meta = video_meta(args.file)
    if args.file.lower().endswith('mp4'):
        metadata = 'creation_time="{}"'.format(meta)
    else:
        metadata = 'ICRD="{}"'.format(meta)
    if not args.output:
        new_filename = 'tmp_{}'.format(args.file)
        os.rename(args.file, new_filename)
        res = subprocess.run(FFMPEG.format(new_filename, metadata,
                                           ffmpeg_direction,
                                           args.file), shell=True)
        if res.returncode:
            os.rename(new_filename, args.file)
        else:
            if not args.backup:
                os.remove(new_filename)
    else:
        res = subprocess.run(FFMPEG.format(args.file, metadata,
                                           ffmpeg_direction,
                                           args.output), shell=True)
    if res.returncode:
        print('Ошибка запуса конвертера')


if __name__ == '__main__':
    main()
