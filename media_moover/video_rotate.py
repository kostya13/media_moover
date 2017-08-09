# -*- coding: utf-8 -*-
import argparse
from os.path import exists
import subprocess

FFMPEG = 'ffmpeg -i {} -b:a 96k -b:v 3000k -vf "transpose={}" {}'
CLOCKWISE = 1
COUNTERCLOCKWISE = 2

ROTATE_DIRECTIONS = {'cw': CLOCKWISE,
                     'ccw': COUNTERCLOCKWISE}

def main():
    parser = argparse.ArgumentParser(description='Вращение видео файла')
    parser.add_argument('--output',
                        help='Файл для сохранения')
    parser.add_argument('direction',
                        help='Направление вращение,'
                        ' по часовой стрелке или против',
                        choices=['cw', 'ccw'])
    parser.add_argument('file',
                        help='Исходный файл')
    args = parser.parse_args()
    if not exists(args.file):
        print('Исходный файл не найден')
        quit(1)
    out_filename = args.output if args.output else 'rotated_{}'.format(args.file)
    ffmpeg_direction = ROTATE_DIRECTIONS[args.direction]
    res = subprocess.run(FFMPEG.format(args.file, ffmpeg_direction,
                                       out_filename), shell=True)
    if res.returncode:
        print('Ошибка запуса конвертера')


if __name__ == '__main__':
    main()
