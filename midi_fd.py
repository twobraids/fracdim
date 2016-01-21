#!/usr/bin/env python
# MIT licensed

from configman import configuration, Namespace

import math
import random

from mido import MidiFile, Message
from PIL import Image, ImageDraw

def scale(a_number, max_number, max_scale):
    """take a_number from the range 0..max_number and scale it into
    the range 0..max_scale - integer arithmethic only"""
    return (a_number * max_scale / max_number)

def scale_point(
    a_point,
    min_point_range,
    max_point_range,
    image_dimensions
):
    x, y = a_point
    min_x, min_y = min_point_range
    max_x, max_y = max_point_range

    image_max_x, image_max_y = image_dimensions

    translated_x = x - min_x
    translated_y = y - min_y
    scaled_x = scale(translated_x, max_x - min_x, image_max_x)
    scaled_y = scale(translated_y, max_y - min_y, image_max_y)

    return (scaled_x, scaled_y)


def plot_midi_as_image(
    midi_file_name,
    image_max_x,
    image_max_y,
    plot_type,
    line_width,
    circle_radius
):
    with MidiFile(midi_file_name) as mf:
        notes = [
            a_note
            for a_note in mf
            if isinstance(a_note, Message) and a_note.type == 'note_on'
        ]

    number_of_notes = len(notes)

    min_note = min(notes, key=lambda a_note: a_note.note).note
    min_point_range = (0, min_note)
    max_note = max(notes, key=lambda a_note: a_note.note).note
    max_point_range = (number_of_notes, max_note)

    image_size = (image_max_x, image_max_y)

    image = Image.new("RGB", image_size)
    draw_image = ImageDraw.Draw(image)

    most_recent_note_as_a_point = scale_point(
        (0, notes[0].note),
        min_point_range,
        max_point_range,
        (image_max_x, image_max_y)
    )

    for count, a_note in enumerate(notes[1:]):
        note_index = count + 1
        new_note_as_point = scale_point(
            (note_index, a_note.note),
            min_point_range,
            max_point_range,
            (image_max_x, image_max_y)
        )
        if plot_type ==  'line':
            a_line = (
                most_recent_note_as_a_point[0],
                most_recent_note_as_a_point[1],
                new_note_as_point[0],
                new_note_as_point[1],
            )
        ##    print a_line
            draw_image.line(a_line, width=line_width)
        elif plot_type ==  'circle':
            bounding_box = (
                new_note_as_point[0] - circle_radius,
                new_note_as_point[1] - circle_radius,
                new_note_as_point[0] + circle_radius,
                new_note_as_point[1] + circle_radius,
            )
            draw_image.ellipse(bounding_box, fill=(255, 255, 255))
        else:
            draw_image.point(new_note_as_point)
        most_recent_note_as_a_point = new_note_as_point

    return image


if __name__ == "__main__":
    from box_count import required_config as box_count_required_config

    required_config = Namespace()
    required_config.add_option(
        'midi_file_name',
        default='temp.mid',
        is_argument=True,
        doc='name of the midi file',
    )
    required_config.add_option(
        'image_max_x',
        default=1024,
        doc='the width of image in pixels',
    )
    required_config.add_option(
        'image_max_y',
        default=600,
        doc='the height of image in pixels',
    )
    required_config.add_option(
        'line_width',
        default=1,
        doc='the stroke width of lines',
    )
    required_config.add_option(
        'plot_type',
        default='line',
        doc='line, dot, circle',
    )
    required_config.add_option(
        'circle_radius',
        default=10,
        doc='the radius of a circle in pixels',
    )
    required_config.update(box_count_required_config)
    required_config.add_option(
        'image_file',
        default='',
        is_argument=True,
        doc='name of an image file, any instance of "FD" is replaced with the fractal dimension',
    )

    config = configuration(required_config)

    image = plot_midi_as_image(
        config.midi_file_name,
        config.image_max_x,
        config.image_max_y,
        config.plot_type,
        config.line_width,
        config.circle_radius
    )

    from box_count import box_count

    fractal_dimension = box_count(
        image,
        config.box_sizes,
        config.interesting_pixel_function
    )

    print fractal_dimension

    if 'FD' in config.image_file:
        file_name = config.image_file.replace('FD', str(fractal_dimension))
    else:
        file_name = config.image_file
    image.save(file_name, format="PNG")
