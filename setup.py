from distutils.core import setup

setup(name='media_moover',
      version='1.0',
      description='Move and rename photo and video',
      author='Konstantin Ilyashenko',
      author_email='kx13@ya.ru',
      packages=['media_moover'],
      install_requires=['exifread'],
      entry_points={
          'console_scripts': [
              'video-rotate=media_moover.video_rotate:main',
              'video-setrotate=media_moover.video_setrotatemeta:main',
              'video-merge=media_moover.video_merge:main',
              'video-move=media_moover.video_move:main',
              'photo-move=media_moover.photo_move:main']})
