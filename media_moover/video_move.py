# -*- coding: utf-8 -*-
import media_moover as mm
from os.path import join
import subprocess


FFMPEG = 'ffmpeg -hide_banner -y -i "{0}" -vcodec h264 -acodec copy -b:v 3000k  -vf scale={1} {2}'


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


def set_scale(rotation, resolution):
    def fmt():
        return ':'.join((str(i) for i in res))

    MAX_SIZE = 800
    res = resolution[:]
    if rotation in [90, -90, 270]:
        res.reverse()
    max_size = max(res)
    min_size = min(res)
    if max_size <= MAX_SIZE:
        return fmt()
    else:
        factor = max_size / MAX_SIZE
        # делаем размер кратный двум
        min_scaled = ((min_size / factor) * 2) // 2
        if max_size == res[0]:
            res = [MAX_SIZE, min_scaled]
        else:
            res = [min_scaled, MAX_SIZE]
    return fmt()


def main():
    try:
        source, destination, test = mm.parse()
    except ValueError as e:
        print(e)
        quit()

    for avi in mm.file_list(source, 'avi') + mm.file_list(source, 'mp4'):
        source_name = join(source, avi)
        info = mm.media_info(source_name)
        year, new_name = mm.name_from_meta(info, source_name)
        dest_name = join(destination, year, new_name)
        print('{} -> {}'.format(source_name, dest_name))
        if test:
            continue
        mm.check_dest_path(destination, year)
        scale = set_scale(info.rotation, info.resolution)
        cmd = FFMPEG.format(source_name, scale, dest_name)
        print(cmd)
        res = subprocess.run(cmd, shell=True)
        if res.returncode:
            print('Ошибка запуска конвертера')
        else:
            save_converted(source, avi)


if __name__ == '__main__':
    main()
