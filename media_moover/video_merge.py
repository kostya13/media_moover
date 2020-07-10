# -*- coding: utf-8 -*-
import argparse
import tempfile
from os.path import exists
import os
import subprocess
from media_moover import video_meta
import re

FFMPEG_COPY = 'ffmpeg -hide_banner -y -f concat -safe 0 -i "{}" -metadata {} -codec copy {}'
FFMPEG_ENCODE = """ffmpeg -hide_banner -y {inputs} \
-filter_complex "{streams}concat=n={number}:v=1:a=1[outv][outa]" \
-map "[outv]" -map "[outa]" -b:v 9000k {outfile}"""


def media_info(files):
    codecs = []
    resolutions = []
    rotations = []
    durations = []
    for f in files:
        res = subprocess.run('ffprobe "{}"'.format(f),
                             stderr=subprocess.PIPE, shell=True)
        if res.returncode:
            print("Ошибка детектора")
            quit(1)
        rot = '0'
        for line in res.stderr.decode().split('\n'):
            match = re.search('Video: (.+?) \(.+', line)
            if match:
                codecs.append(match.group(1))
            match = re.search(', (\d{2,4}x\d{2,4})', line)
            if match:
                resolutions.append(match.group(1))
            match = re.search('Duration: (.+?),', line)
            if match:
                durations.append(match.group(1))
            match = re.search('rotate          : (\d{2,3})', line)
            if match:
                rot = match.group(1)
        rotations.append(rot)

    return codecs, resolutions, rotations, durations


def same_codec(metadata, out_filename, files):
    with tempfile.NamedTemporaryFile(dir='.', mode='w', delete=False) as tf:
        temp_filename = tf.name
        for f in files:
            tf.write("file '{}'\n".format(f))
    res = subprocess.run(FFMPEG_COPY.format(temp_filename, metadata,
                                            out_filename), shell=True)
    if res.returncode:
        print('Ошибка запуса конвертера')
    os.unlink(temp_filename)


def different_codecs(metadata, out_filename, files):
    inputs = ' '.join(['-i {}'.format(f) for f in files])
    streams = ''.join(['[{0}:v:0][{0}:a:0]'.format(i)
                       for i in range(len(files))])
    number = len(files)

    res = subprocess.run(FFMPEG_ENCODE.format(inputs=inputs, streams=streams,
                                              number=number,
                                              outfile=out_filename), shell=True)
    if res.returncode:
        print('Ошибка запуса конвертера')


def overlay(blank_filename, resolutions, rotation, filename, max_size):
    x, y = [int(i) for i in resolutions.split('x')]
    out_name = '{}-overlay.mp4'.format(filename)
    transponse = ',transpose=1' if rotation == '90' else ''
    dx = (max_size // 2) - (x // 2)
    dy = (max_size // 2) - (y // 2)
    if rotation == '90':
        dx, dy = dy, dx
    res = subprocess.run('ffmpeg -hide_banner -y -i {} -vf "movie={}{} [a]; [in][a] overlay={}:{}" {}'.
                         format(blank_filename, filename, transponse, dx, dy,
                                out_name), shell=True)
    if res.returncode:
        print('Ошибка запуса конвертера')
        quit(1)
    return out_name


def blank_video(duration, filename, size):
    resolution = '{0}x{0}'.format(size)
    new_name = '{}-blank.mp4'.format(filename)
    res = subprocess.run(
        "ffmpeg -hide_banner -y -t {} -f lavfi -i color=c=black:s={} -c:v libx264 -tune stillimage -pix_fmt yuvj420p {}".
        format(duration, resolution, new_name), shell=True)
    if res.returncode:
        print('Ошибка запуса конвертера')
        quit(1)
    return new_name


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
    files = args.files[:]
    codecs, resolutions, rotations, durations = media_info(files)
    sizes = []
    for r in resolutions:
        sizes.extend([int(i) for i in r.split('x')])
    max_size = max(sizes)
    need_overlay = len(set(rotations)) > 1
    for fi in range(len(files)):
        if need_overlay:
            new_name = blank_video(durations[fi], files[fi], max_size)
            overlay_name = overlay(new_name, resolutions[fi],
                                   rotations[fi], files[fi], max_size)
            files[fi] = overlay_name
    if not need_overlay and len(set(resolutions)) > 1:
        print('Размеры исходных файлов не совпадают')
        quit(1)
    first_file = args.files[0]
    meta = video_meta(first_file)
    if first_file.lower().endswith('mp4'):
        metadata = 'creation_time="{}"'.format(meta)
    else:
        metadata = 'ICRD="{}"'.format(meta)
    ext = files[0].split('.')[-1]
    name = files[0].split('.')[0]
    out_filename = args.output if args.output else '"{}_merged.{}"'.format(name,
                                                                         ext)
    if len(set(codecs)) > 1:
        print('Кодеки различны файлы будут пережаты')
        different_codecs(metadata, out_filename, files)
    else:
        same_codec(metadata, out_filename, files)
    for f in args.files:
        os.rename(f, f + '.backup')
    subprocess.run('rm -f *-blank.mp4 *-overlay.mp4', shell=True)


if __name__ == '__main__':
    main()
