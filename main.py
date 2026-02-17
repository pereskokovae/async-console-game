import asyncio
import curses
import itertools
import random
import time
from curses_tools import draw_frame, get_frame_size, read_controls

TIC_TIMEOUT = 0.1
STAR_SYMBOLS = ('*', '+', '.', ':')
FRAMES_FILES = ('rocket_frame_1.txt', 'rocket_frame_2.txt')


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


async def sleep_ticks(ticks=1):
    for _ in range(ticks):
        await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'
    max_row, max_column = (s - 1 for s in canvas.getmaxyx())

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    await sleep_ticks(random.randint(0, 20))

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep_ticks(20)

        canvas.addstr(row, column, symbol)
        await sleep_ticks(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep_ticks(5)

        canvas.addstr(row, column, symbol)
        await sleep_ticks(3)


def load_frames():
    return [open(name, encoding="utf-8").read() for name in FRAMES_FILES]


async def animate_spaceship(canvas, start_row, start_column, frames):
    row, column = start_row, start_column
    frame_height, frame_width = get_frame_size(frames[0])

    prev_row, prev_col = row, column
    prev_frame = frames[0]

    for frame in itertools.cycle(frames):
        draw_frame(canvas, prev_row, prev_col, prev_frame, negative=True)

        rows_direction, columns_direction, _ = read_controls(canvas)
        row += rows_direction
        column += columns_direction

        max_row, max_column = canvas.getmaxyx()
        row = clamp(row, 1, max_row - frame_height - 1)
        column = clamp(column, 1, max_column - frame_width - 1)

        draw_frame(canvas, row, column, frame)

        prev_row, prev_col, prev_frame = row, column, frame

        await sleep_ticks(2)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    canvas.border()

    max_row, max_column = canvas.getmaxyx()
    coroutines = []

    for _ in range(100):
        row = random.randint(1, max_row - 2)
        col = random.randint(1, max_column - 2)
        coroutines.append(blink(canvas, row, col, random.choice(STAR_SYMBOLS)))

    frames = load_frames()
    h, w = get_frame_size(frames[0])
    center_row = max_row // 2 - h // 2
    center_col = max_column // 2 - w // 2
    coroutines.append(animate_spaceship(canvas, center_row, center_col, frames))

    coroutines.append(fire(canvas, max_row // 2, max_column // 2))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)