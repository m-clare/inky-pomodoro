import os
import numpy
import json
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
from datetime import datetime

PATH = os.path.dirname(os.path.abspath(__file__))

def format_line(font, msg):
    lines = []
    w, h = font.getsize(msg)
    if w <= inky_display.WIDTH:
        lines.append(msg)
    else:
        toks = msg.split()
        cur_line = ''
        for tok in toks:
            cur_w, _ = font.getsize(cur_line + tok + ' ')
            if cur_w <= inky_display.WIDTH:
                cur_line = cur_line + tok + ' '
            else:
                lines.append(cur_line)
                cur_line = tok + ' '
        lines.append(cur_line)
    return lines

def get_pomodoro_time(start_time):
    # set pomodoro cycle length
    pomodoro = 25 * 60 # typical length in seconds
    small_break = 5 * 60
    long_break = 25 * 60
    cycle_length = (pomodoro + small_break) * 3 +  pomodoro + long_break
    curr_time = int(datetime.utcnow().timestamp()) % 86400
    time_since_start = curr_time - start_time
    completed_cycles = int(time_since_start // cycle_length)
    pt_in_cycle = time_since_start - completed_cycles * cycle_length
    num_tomato = int(pt_in_cycle // (pomodoro + small_break))
    if int(pt_in_cycle % (pomodoro + small_break)  >= pomodoro) and (num_tomato < 3):
        return (num_tomato, "break time!")
    elif (pt_in_cycle > (4 * pomodoro + 3 * small_break)):
        return (num_tomato, "looooong break time!")
    else:
        return (num_tomato, "still working")

def get_tomato_image(inky_display, image_num):
    """
    Use PIL library to open tomato image and transpose for inky display
    """
    rel_path = os.path.join(PATH, "assets/tomato_" + str(image_num) + ".png")
    img = Image.open(rel_path).resize(inky_display.resolution)
    canvas = Image.new("P", (inky_display.rows, inky_display.cols))
    canvas.paste(img, (0,0)) # no offset of image
    canvas = canvas.transpose(Image.ROTATE_90)
    return canvas

def get_text_image(inky_display, break_text):
    font = ImageFont.truetype(FredokaOne, 32)
    lines = format_line(font, break_text)
    _, line_height = font.getsize(lines[0])
    centered_y = (inky_display.HEIGHT / 2) - ((line_height * len(lines)) / 2)
    height_counter = centered_y
    img = Image.new("P", (inky_display.rows, inky_display.cols))
    draw = ImageDraw.Draw(img)
    for i in range(0, len(lines)):
        msg = lines[i]
        w, h = font.getsize(msg)
        x = (inky_display.WIDTH / 2) - (w / 2)
        y = height_counter
        draw.text((x, y), msg, inky_display.BLACK, font)
        height_counter += h
    canvas = img.transpose(Image.ROTATE_90)
    return canvas

def check_display(inky_display, tomato, cycle, start_time):
    num_tomato, text = get_pomodoro_time(start_time)
    # check if status has changed
    if text == cycle:
        return
    else:
        if text == "still working":
            img = get_tomato_image(inky_display, num_tomato)
        else:
            img = get_text_image(inky_display, text)
        # update status
        out_dict = {'num_tomato': num_tomato,
                    'status_cycle': text,
                    'start_time': start_time}
        with open(PATH + '/status.json', 'w') as fh:
            json.dump(out_dict, fh)
        inky_display.set_image(img)
        inky_display.show()

# Global Inky Properties
inky_display = InkyPHAT("red")
inky_display.rotation = 0 # avoid unnecessary swap

# default start values
tomato = 0
cycle = "still working"
start_time = int(datetime.utcnow().timestamp()) % 86400

if os.path.exists(PATH + '/status.json'):
    with open(PATH + '/status.json', 'r') as fh:
        status = json.load(fh)
        tomato = status["num_tomato"]
        cycle = status["status_cycle"]
        start_time = status['start_time']
else:
    status = {'num_tomato': tomato,
              'status_cycle': cycle,
              'start_time': start_time}
    # reset display
    img = get_tomato_image(inky_display, 0)
    inky_display.set_image(img)
    inky_display.show()
    with open(PATH + '/status.json', 'w') as fh:
        json.dump(status, fh)

check_display(inky_display, tomato, cycle, start_time)
