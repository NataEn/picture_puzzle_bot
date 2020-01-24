from random import shuffle
import io, logging
from PIL import Image
import requests

logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

img_url = 'https://image.shutterstock.com/image-photo/bright-spring-view-cameo-island-260nw-1048185397.jpg'
dog_url = 'http://images.unsplash.com/photo-1568564321589-3e581d074f9b?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=1080&fit=max'


def import_img(url: str):
    binary_image = requests.get(url).content
    img_b = Image.open(io.BytesIO(binary_image))
    # logger.info(img_b.size, img_b.mode, img_b.format, f'{img_b.filename}=name')
    img_b.save('img.png')
    return img_b


def resize_img(img: Image, x: int, y: int):
    return img.resize((x, y))


def cut_img(img: Image, part_size: int):
    '''returns a list containing parts cut out of the img'''
    parts = [img.crop((x, y, x + part_size, y + part_size)) for x in range(0, img.size[0], part_size) for y in
             range(0, img.size[0], part_size)]
    return parts


def assemble_img(parts: list, width: int, height: int, part_size: int):
    '''assembles a new image from given list of parts according to given width and height'''
    new_img = Image.new('RGBA', (width, height))
    coordinates = [(x, y) for x in range(0, width, part_size) for y in range(0, height, part_size)]
    shuffle(coordinates)
    for part, coordinate in zip(parts, coordinates):
        new_img.paste(part, coordinate)
    return new_img


# dog_img = import_img(dog_url)
# dog_img.show()
# dog_resized = resize_img(dog_img, 600, 600)
# logger.info(img_resized.size, img_resized.mode, img_resized.format)
# dog_parts = cut_img(dog_resized, 100)
# new_dog_img = assemble_img(dog_parts, 600, 600, 100)
# new_dog_img.save('new_dog_img.png')


