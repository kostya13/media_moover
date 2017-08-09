# -*- coding: utf-8 -*-
import argparse
import tempfile
from os.path import exists, join
import os
import subprocess

FFMPEG = 'ffmpeg -f concat -i {} -codec copy {}'

def main():
    parser = argparse.ArgumentParser(description='Склеивание нескольких файлов')
    parser.add_argument('--output',
                        help='Файл для сохранения')
    parser.add_argument('files', nargs= '+',
                        help='Исходные файлы')
    args = parser.parse_args()
    for f in args.files:
        if not exists(f):
            print('Исходный файл не найден: {}'.format(f))
            quit(1)
    ext = args.files[0].split('.')[1]
    with tempfile.NamedTemporaryFile(dir='.', mode='w', delete=False) as tf:
        temp_filename = tf.name
        for f in args.files:
            tf.write("file '{}'\n".format(f))
    out_filename = args.output if args.output else 'merged.{}'.format(ext)
    res = subprocess.run(FFMPEG.format(temp_filename, out_filename), shell=True)
    if res.returncode:
        print('Ошибка запуса конвертера')
    os.unlink(temp_filename)


if __name__ == '__main__':
    main()
