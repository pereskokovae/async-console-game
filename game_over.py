from curses_tools import draw_frame, get_frame_size


GAME_OVER_FRAME = """                                                                                   
    ▄▄▄▄                                             ▄▄▄▄                                 
  ██▀▀▀▀█                                           ██▀▀██                                
 ██         ▄█████▄  ████▄██▄   ▄████▄             ██    ██  ██▄  ▄██   ▄████▄    ██▄████ 
 ██  ▄▄▄▄   ▀ ▄▄▄██  ██ ██ ██  ██▄▄▄▄██            ██    ██   ██  ██   ██▄▄▄▄██   ██▀     
 ██  ▀▀██  ▄██▀▀▀██  ██ ██ ██  ██▀▀▀▀▀▀            ██    ██   ▀█▄▄█▀   ██▀▀▀▀▀▀   ██ 
  ██▄▄▄██  ██▄▄▄███  ██ ██ ██  ▀██▄▄▄▄█             ██▄▄██     ████    ▀██▄▄▄▄█   ██      
    ▀▀▀▀    ▀▀▀▀ ▀▀  ▀▀ ▀▀ ▀▀    ▀▀▀▀▀               ▀▀▀▀       ▀▀       ▀▀▀▀▀    ▀▀     
"""


async def show_gameover(canvas, sleep):
    rows_number, columns_number = canvas.getmaxyx()
    frame_height, frame_width = get_frame_size(GAME_OVER_FRAME)

    start_row = rows_number // 2 - frame_height // 2
    start_column = columns_number // 2 - frame_width // 2

    while True:
        draw_frame(canvas, start_row, start_column, GAME_OVER_FRAME)
        await sleep(1)