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
              'rotate-video=media_moover.video_rotate:main',
              'move-photo=media_moover.photo:main',
              'move-video=media_moover.video:main']})
