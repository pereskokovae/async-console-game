import asyncio
from curses_tools import draw_frame, get_frame_size
from expose import explode
from obstacles import Obstacle

obstacles = []
obstacles_in_last_collisions = []


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    rows_number, columns_number = canvas.getmaxyx()
    row = 0

    frame_rows, frame_columns = get_frame_size(garbage_frame)
    column = max(0, min(column, columns_number - frame_columns - 1))

    obstacle = Obstacle(row, column, frame_rows, frame_columns)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            if obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(obstacle)

                center_row = row + frame_rows / 2
                center_column = column + frame_columns / 2
                await explode(canvas, center_row, center_column)
                return

            obstacle.row = row
            obstacle.column = column

            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)

            row += speed

    finally:
        if obstacle in obstacles:
            obstacles.remove(obstacle)