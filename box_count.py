#!/usr/bin/env python
# based on http://code.activestate.com/recipes/578048-ifs-fractal-dimension-calculation/

# MIT licensed

# IFS fractal dimension calculation using box-counting method
# http://en.wikipedia.org/wiki/Iterated_function_system
# http://en.wikipedia.org/wiki/Fractal_dimension
# http://en.wikipedia.org/wiki/Box-counting_dimension
# http://en.wikipedia.org/wiki/Simple_linear_regression
# FB - 20120211
import math


from configman import configuration, Namespace
from configman.converters import str_to_python_object, list_converter

from functools import partial

from PIL import Image

required_config = Namespace()
required_config.add_option(
    'image_file',
    default='',
    is_argument=True,
    doc='name of an image file',
)
required_config.add_option(
    'interesting_pixel_function',
    default='box_count.is_not_black',
    doc='name of an image file',
    from_string_converter=str_to_python_object
)
required_config.add_option(
    'box_sizes',
    default='100, 50, 25, 10',
    doc='name of an image file',
    from_string_converter=partial(list_converter, item_converter=int)
)

def is_not_black(pixel_tuple):
    return pixel_tuple > (1, 0, 0)

def is_white(pixel_tuple):
    return pixel_tuple == (255, 255, 255)

from  scipy.stats import linregress


def box_count(pixels, box_sizes, interesting_pixel_function):

    image_max_x, image_max_y = pixels.size

    gx = [] # x coordinates of graph points
    gy = [] # y coordinates of graph points
    for a_box_size in box_sizes:
        number_of_boxes_in_x = int(image_max_x / a_box_size)
        number_of_boxes_in_y = int(image_max_y / a_box_size)
        print 'boxes', a_box_size, number_of_boxes_in_x, number_of_boxes_in_y
        box_count = 0
        for box_y in range(number_of_boxes_in_y):
            for box_x in range(number_of_boxes_in_x):
                # if there are any pixels in the box then increase box count
                found_pixel = False
                for box_relative_y in range(a_box_size):
                    for box_relative_x in range(a_box_size):
                        if interesting_pixel_function(
                            pixels.getpixel(
                                (
                                    a_box_size * box_x + box_relative_x,
                                    a_box_size * box_y + box_relative_y
                                )
                            )
                        ):
                            found_pixel = True
                            box_count += 1
                            break
                    if found_pixel:
                        break
        gx.append(math.log(1.0 / a_box_size))
        print box_count
        gy.append(math.log(box_count))

    print gx, gy

    slope, intercept, r_value, p_value, std_err = linregress(gx, gy)
    return slope


if __name__ == "__main__":

    config = configuration(required_config)

    pixels = Image.open(config.image_file)
    print box_count(pixels, config.box_sizes, config.interesting_pixel_function)

