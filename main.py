import asyncio
import curses
import itertools
import random
import time

from curses_tools import draw_frame, get_frame_size, read_controls
from space_garbage import fly_garbage


TIC_TIMEOUT = 0.1

STAR_SYMBOLS = ('*', '+', '.', ':')
SHIP_FRAMES_FILES = ('rocket_frame_1.txt', 'rocket_frame_2.txt')
GARBAGE_FRAMES_FILES = (
    'duck.txt',
    'lamp.txt',
    'hubble.txt',
    'trash_large.txt',
    'trash_small.txt',
    'trash_xl.txt',
)

coroutines = []


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


async def sleep_ticks(ticks=1):
    for _ in range(ticks):
        await asyncio.sleep(0)


def load_frames(filenames):
    frames = []
    for filename in filenames:
        with open(filename, encoding='utf-8') as file:
            frames.append(file.read())
    return frames


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), ' ')
    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'
    max_row, max_column = (size - 1 for size in canvas.getmaxyx())

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)

        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, offset_tics=0, symbol='*'):
    await sleep_ticks(offset_tics)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep_ticks(20)

        canvas.addstr(row, column, symbol)
        await sleep_ticks(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep_ticks(5)

        canvas.addstr(row, column, symbol)
        await sleep_ticks(3)


async def animate_spaceship(canvas, start_row, start_column, frames):
    row, column = start_row, start_column
    frame_height, frame_width = get_frame_size(frames[0])

    prev_row, prev_column = row, column
    prev_frame = frames[0]

    animation_frames = []
    for frame in frames:
        animation_frames.extend([frame, frame])

    for frame in itertools.cycle(animation_frames):

        draw_frame(canvas, prev_row, prev_column, prev_frame, negative=True)

        rows_direction, columns_direction, _ = read_controls(canvas)
        row += rows_direction
        column += columns_direction
        
        max_row, max_column = canvas.getmaxyx()
        row = clamp(row, 1, max_row - frame_height - 1)
        column = clamp(column, 1, max_column - frame_width - 1)

        draw_frame(canvas, row, column, frame)

        prev_row, prev_column, prev_frame = row, column, frame

        await sleep_ticks(1)


async def fill_orbit_with_garbage(canvas, garbage_frames):
    global coroutines

    while True:
        _, max_column = canvas.getmaxyx()

        garbage_frame = random.choice(garbage_frames)
        column = random.randint(1, max_column - 2)

        coroutines.append(
            fly_garbage(canvas, column=column, garbage_frame=garbage_frame)
        )
        await sleep_ticks(10)


def draw(canvas):
    global coroutines
    coroutines = []

    curses.curs_set(False)
    canvas.nodelay(True)
    canvas.border()

    max_row, max_column = canvas.getmaxyx()

    for _ in range(100):
        row = random.randint(1, max_row - 2)
        column = random.randint(1, max_column - 2)
        symbol = random.choice(STAR_SYMBOLS)
        offset_tics = random.randint(0, 20)

        coroutines.append(
            blink(canvas, row, column, offset_tics, symbol)
        )

    ship_frames = load_frames(SHIP_FRAMES_FILES)
    frame_height, frame_width = get_frame_size(ship_frames[0])

    center_row = max_row // 2 - frame_height // 2
    center_column = max_column // 2 - frame_width // 2

    coroutines.append(
        animate_spaceship(canvas, center_row, center_column, ship_frames)
    )

    coroutines.append(
        fire(canvas, max_row // 2, max_column // 2)
    )

    garbage_frames = load_frames(GARBAGE_FRAMES_FILES)
    coroutines.append(
        fill_orbit_with_garbage(canvas, garbage_frames)
    )
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)