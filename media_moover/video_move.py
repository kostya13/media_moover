# -*- coding: utf-8 -*-
import media_moover as mm
from os.path import join
import subprocess


FFMPEG = 'ffmpeg  -hide_banner -y -i "{0}" -vcodec mpeg4 -acodec mp3 -b:v 3000k -b:a 96k -vf scale={1} {2}'


def rotation(filename):
    rot = ''
    res = subprocess.run('ffprobe "{}"'.format(filename),
                         stderr=subprocess.PIPE, shell=True)
    if res.returncode:
        print("Ошибка детектора")
        quit(1)
    for line in res.stderr.decode().split('\n'):
        if 'rotate' in line:
            rot = line.split(':')[1].strip()
            break
    return rot


def save_converted(source, name):
    mm.move_to(source, name, 'converted')


def main():
    try:
        source, destination, test = mm.parse()
    except ValueError as e:
        print(e)
        quit()

    for avi in mm.file_list(source, 'avi') + mm.file_list(source, 'mp4'):
        source_name = join(source, avi)
        metadata = mm.video_meta(source_name)
        year, new_name = mm.name_from_meta(metadata)
        dest_name = join(destination, year, new_name)
        print('{} -> {}'.format(source_name, dest_name))
        if test:
            continue
        mm.check_dest_path(destination, year)
        if rotation(source_name) in ['90', '-90', '270']:
            scale = '640:-1'
        else:
            scale = '-1:480'
        res = subprocess.run(FFMPEG.format(source_name, scale, dest_name),
                             stderr=subprocess.PIPE, shell=True)
        if res.returncode:
            print('Ошибка запуска конвертера')
        else:
            save_converted(source, avi)


if __name__ == '__main__':
    main()
