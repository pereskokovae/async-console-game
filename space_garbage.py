from curses_tools import draw_frame, get_frame_size
from obstacles import Obstacle
import asyncio

obstacles = []

async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Column position will stay same."""

    global obstacles

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    frame_rows, frame_columns = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, frame_rows, frame_columns)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            draw_frame(canvas, row, column, garbage_frame)

            await asyncio.sleep(0)

            draw_frame(canvas, row, column, garbage_frame, negative=True)

            row += speed
            obstacle.row = row
            obstacle.column = column

    finally:
        if obstacle in obstacles:
            obstacles.remove(obstacle)