# pip3 install bottle-fdsend pillow
from bottle import run, template, get, post, request
from PIL import Image
from io import BytesIO
from fdsend import send_file
import os

BASE_PATH = '.'

TEMPLATE = """
<!DOCTYPE HTML>
<html>
 <head>
  <meta charset="utf-8">
  <title>Фильтр</title>
 </head>
 <body>
 <p>
    <form style="display: inline" action="" method="post">
        <input type="hidden" name="image" value="{{prev_image}}">
        <input type="submit" value="<<">
    </form>
    <form style="display: inline" action="" method="post">
        <input type="hidden" name="image" value="{{next_image}}">
        <input type="submit" value=">>">
    </form>
 </p>
<img src="images/{{image}}">
 <form action="" method="post">
    <input type="hidden" name="delete" value="true">
    <input type="hidden" name="image" value="{{image}}">
  <p><input type="submit" value="[X]"></p>
 </form>
 </body>
</html>
"""

EMPTY = """
<!DOCTYPE HTML>
<html>
 <head>
  <meta charset="utf-8">
  <title>Фильтр</title>
 </head>
 <body>
 Изображений не найдно
 </body>
</html>
"""


@get('/images/<filename>')
def image(filename):
    buf = BytesIO()
    im = Image.open(os.path.join(BASE_PATH, 'images', filename))
    im.thumbnail((700, 700))
    im.save(buf, "JPEG")
    buf.seek(0)
    return send_file(buf, ctype='image/jpeg')


@get('/')
def get_main():
    def index_by_length(array):
        length = len(array)
        if length == 1:
            return 0, 0, 0
        elif length == 2:
            return 0, 1, 0
        else:
            return 0, 1, -1

    all_images = file_list()
    if not all_images:
        return template(EMPTY)
    cur_i, next_i, prev_i = index_by_length(all_images)
    return template(TEMPLATE, image=all_images[cur_i],
                    next_image=all_images[next_i],
                    prev_image=all_images[prev_i])


@post('/')
def post_main():
    image = request.forms.get('image')
    delete = request.forms.get('delete')
    if delete:
        image = delete_image(image)
        if not image:
            return template(EMPTY)
    next_image, prev_image = get_images(image)
    return template(TEMPLATE, image=image,
                    next_image=next_image,
                    prev_image=prev_image)


def get_images(image):
    all_images = file_list()
    index = all_images.index(image)
    if len(all_images) == 1:
        return image, image
    elif len(all_images) == 2:
        if index == 0:
            return all_images[1], all_images[0]
        else:
            return all_images[0], all_images[1]
    else:
        if index == 0:
            return all_images[1], all_images[-1]
        elif index == len(all_images) - 1:
            return all_images[0], all_images[-2]
        else:
            return all_images[index + 1], all_images[index - 1]


def delete_image(image):
    if not os.path.exists(os.path.join(BASE_PATH, 'deleted')):
        os.mkdir('deleted')
    all_images = file_list()
    index = all_images.index(image)
    if index == len(all_images) - 1:
        new_image = all_images[0]
    else:
        new_image = all_images[index + 1]
    os.rename(os.path.join('images', image), os.path.join('deleted', image))
    if len(all_images) == 1:
        return None
    else:
        return new_image


def file_list():
    return sorted(os.listdir(os.path.join(BASE_PATH, 'images')))


def main():
    run(host='localhost', port=8080, reloader=True)
    # run(host='localhost', port=8080, reloader=True)


if __name__ == '__main__':
    main()
