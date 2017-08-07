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
              'move_photo=media_moover.photo:main',
              'move_video=media_moover.video:main']})
