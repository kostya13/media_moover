# -*- coding: utf-8 -*-
import argparse
import tempfile
from os.path import exists
import os
import subprocess
from media_moover import video_meta
import re

FFMPEG_COPY = 'ffmpeg -f concat -i "{}" -metadata {} -codec copy {}'
FFMPEG_ENCODE = """ffmpeg {inputs} \
-filter_complex "{streams}concat=n={number}:v=1:a=1[outv][outa]" \
-map "[outv]" -map "[outa]" -b:v 9000k {outfile}"""


def media_info(files):
    codecs = []
    resolutions = []
    for f in files:
        res = subprocess.run('ffprobe "{}"'.format(f),
                             stderr=subprocess.PIPE, shell=True)
        if res.returncode:
            print("Ошибка детектора")
            quit(1)
        for line in res.stderr.decode().split('\n'):
            match = re.search('Video: (.+?) \(.+', line)
            if match:
                codecs.append(match.group(1))
            match = re.search(', (\d{2,4}x\d{2,4})', line)
            if match:
                resolutions.append(match.group(1))
    return codecs, resolutions


def same_codec(metadata, out_filename, args):
    with tempfile.NamedTemporaryFile(dir='.', mode='w', delete=False) as tf:
        temp_filename = tf.name
        for f in args.files:
            tf.write("file '{}'\n".format(f))
    res = subprocess.run(FFMPEG_COPY.format(temp_filename, metadata,
                                            out_filename), shell=True)
    if res.returncode:
        print('Ошибка запуса конвертера')
    os.unlink(temp_filename)


def different_codecs(metadata, out_filename, args):
    inputs = ' '.join(['-i {}'.format(f) for f in args.files])
    streams = ''.join(['[{0}:v:0][{0}:a:0]'.format(i)
                       for i in range(len(args.files))])
    number = len(args.files)

    res = subprocess.run(FFMPEG_ENCODE.format(inputs=inputs, streams=streams,
                                              number=number,
                                              outfile=out_filename), shell=True)
    if res.returncode:
        print('Ошибка запуса конвертера')


def main():
    parser = argparse.ArgumentParser(description='Склеивание нескольких файлов')
    parser.add_argument('--output',
                        help='Файл для сохранения')
    parser.add_argument('files', nargs='+',
                        help='Исходные файлы')
    args = parser.parse_args()
    for f in args.files:
        if not exists(f):
            print('Исходный файл не найден: {}'.format(f))
            quit(1)
    codecs, resolutions = media_info(args.files)
    if len(set(resolutions)) > 1:
            print('Размеры исходных файлов не совпадают')
            quit(1)
    first_file = args.files[0]
    meta = video_meta(first_file)
    if first_file.lower().endswith('mp4'):
        metadata = 'creation_time="{}"'.format(meta)
    else:
        metadata = 'ICRD="{}"'.format(meta)
    ext = args.files[0].split('.')[1]
    name = args.files[0].split('.')[0]
    out_filename = args.output if args.output else '{}_merged.{}'.format(name,
                                                                         ext)
    if len(set(codecs)) > 1:
        print('Кодеки различны файлы будут пережаты')
        different_codecs(metadata, out_filename, args)
    else:
        same_codec(metadata, out_filename, args)
    for f in args.files:
        os.rename(f, f + '.backup')


if __name__ == '__main__':
    main()
