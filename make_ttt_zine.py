"""
Tic Tac Toe Zine Maker by Al Sweigart 2025

This program creates a `boards` list of TTT board dictionaries. The dictionaries have keys of
space strings (e.g. 'TL' for top-left). The value is either 'X', 'O', or a number. The number
is an index in `boards` to the board if the human player moves on that space (along with the
zine's response). The `boards` list contains a sort of "multiverse" of all possible TTT games.

For example, run `python -i make_ttt_zine.py` to open an interactive shell after the program
finishes. The pb() function prints human-readable form of a TTT board dictionary. Call `pb(0)` to
look at the first board. Each space has an index to examine if you make that move. E.g. if `pb(0)`
shows a board with 204 in the top-left space, `pb(204)` shows the board after you move on that
space and the zine's response move.

Git repo of this code is at: https://github.com/asweigart/tictactoe_zine
Neat website on TTT strategy: https://tictactoefree.com/tips/how-to-win-in-tic-tac-toe
"""

import random, copy, io, os
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfWriter, PdfReader
random.seed(44)  # Change this to generate other games. 

OUTPUT_PDF_FILENAME = 'tictactoe_zine.pdf'
ZINE_BLUNDER_RATE = 0.25  # 0.0 makes best moves. 1.0 always makes random moves.

ALL_SPACES = 'TL TM TR ML MM MR BL BM BR'.split()
HUMAN_MARK = 'X'
ZINE_MARK = 'O'
EMPTY = ' '

def get_blank_board():
    """Return a new dictionary with all spaces set to None."""
    board = {}
    for move in ALL_SPACES:
        board[move] = None
    return board

def is_winner(player, board):
    """Returns True if `player` has three in a row on `board`."""
    b = board
    return (b['TL'] == b['TM'] == b['TR'] == player) or \
           (b['ML'] == b['MM'] == b['MR'] == player) or \
           (b['BL'] == b['BM'] == b['BR'] == player) or \
           (b['TL'] == b['ML'] == b['BL'] == player) or \
           (b['TM'] == b['MM'] == b['BM'] == player) or \
           (b['TR'] == b['MR'] == b['BR'] == player) or \
           (b['TL'] == b['MM'] == b['BR'] == player) or \
           (b['TR'] == b['MM'] == b['BL'] == player)

def is_full(board):
    """Returns True if the board is full with no winners."""
    for space in ALL_SPACES:
        if board[space] not in (HUMAN_MARK, ZINE_MARK):
            return False
    return True

def get_zine_move(board):
    if random.random() < ZINE_BLUNDER_RATE:
        # Just make a random move on a free space:
        free_spaces = []
        for space in ALL_SPACES:
            if board[space] is None:
                free_spaces.append(space)
        return random.choice(free_spaces)

    # Stop potential forking manuever by playing the opposite corner:
    forkable_board = get_blank_board()
    forkable_board['TL'] = HUMAN_MARK
    if board == forkable_board:
        return 'BR'
    forkable_board = get_blank_board()
    forkable_board['TR'] = HUMAN_MARK
    if board == forkable_board:
        return 'BL'
    forkable_board = get_blank_board()
    forkable_board['BL'] = HUMAN_MARK
    if board == forkable_board:
        return 'TR'
    forkable_board = get_blank_board()
    forkable_board['BR'] = HUMAN_MARK
    if board == forkable_board:
        return 'TL'
    forkable_board = get_blank_board()
    forkable_board['MM'] = HUMAN_MARK
    if board == forkable_board:
        return 'TL'  # Any corner will do to respond to the center-first move.
    
    # Make a winning move if possible:
    for space in ALL_SPACES:
        if board[space] is None:
            test_board = copy_marks(board)
            test_board[space] = ZINE_MARK
            if is_winner(ZINE_MARK, test_board):
                return space

    # Make a blocking move if necessary:
    for space in ALL_SPACES:
        if board[space] is None:
            test_board = copy_marks(board)
            test_board[space] = HUMAN_MARK
            if is_winner(HUMAN_MARK, test_board):
                return space

    # Make a center move if available:
    if board['MM'] is None:
        return 'MM'

    # Make a corner move if available:
    free_corners = []
    for space in ('TL', 'TR', 'BL', 'BR'):
        if board[space] is None:
            free_corners.append(space)
    if len(free_corners) > 0:
        return random.choice(free_corners)

    # Make a side move if available:
    free_sides = []
    for space in ('TM', 'BM', 'ML', 'MR'):
        if board[space] is None:
            free_sides.append(space)
    if len(free_sides) > 0:
        return random.choice(free_sides)

    assert False  # Something is wrong and `board` is full.

def copy_marks(board):
    """Return a new board that only has the X and O marks copied."""
    new_board = get_blank_board()
    for space in ALL_SPACES:
        if board[space] == HUMAN_MARK or board[space] == ZINE_MARK:
            new_board[space] = board[space]
    return new_board

def get_board_text(idx):
    b = copy.copy(boards[idx])
    for space in ALL_SPACES:
        b[space] = str(b[space]).center(3)
    VERTICAL = '   |   |   '
    HORIZONTAL = '---+---+---'
    t = []
    #t.append([VERTICAL])
    t.append('%s|%s|%s' % (b['TL'], b['TM'], b['TR']))
    t.append(HORIZONTAL) #t.extend((VERTICAL, HORIZONTAL, VERTICAL))
    t.append('%s|%s|%s' % (b['ML'], b['MM'], b['MR']))
    if is_winner(HUMAN_MARK, boards[idx]):
        t.append('-YOU WIN!--') #t.extend((VERTICAL, '-YOU WIN!--', VERTICAL))
    elif is_winner(ZINE_MARK, boards[idx]):
        t.append('-ZINE WON!-') #t.extend((VERTICAL, '-ZINE WON!-', VERTICAL))
    elif is_full(boards[idx]):
        t.append('---+TIE+---') #t.extend((VERTICAL, '---+TIE+---', VERTICAL))
    else:
        t.append(HORIZONTAL) #t.extend((VERTICAL, HORIZONTAL, VERTICAL))
    t.append('%s|%s|%s' % (b['BL'], b['BM'], b['BR']))
    #t.append(VERTICAL)
    t.append('    #' + str(idx).ljust(3) + '   ')
    
    # Replace the characters with box-drawing characters:
    for i in range(len(t)):
        t[i] = t[i].replace('-', chr(9472)).replace('|', chr(9474)).replace('+', chr(9532))
    return t

def pb(idx):
    print('\n'.join(get_board_text(idx)))


if not os.path.exists('zine_frontcover.png'):
    sys.exit('Missing zine_frontcover.png. Get from https://github.com/asweigart/tictactoe_zine')
if not os.path.exists('zine_backcover.png'):
    sys.exit('Missing zine_backcover.png. Get from https://github.com/asweigart/tictactoe_zine')
if not os.path.exists('zine_centerfold.png'):
    sys.exit('Missing zine_centerfold.png. Get from https://github.com/asweigart/tictactoe_zine')
if not os.path.exists('zine_smartphone.png'):
    sys.exit('Missing zine_smartphone.png. Get from https://github.com/asweigart/tictactoe_zine')
if not os.path.exists('zine_magnifyingglass.png'):
    sys.exit('Missing zine_magnifyingglass.png. Get from https://github.com/asweigart/tictactoe_zine')


boards = [get_blank_board()]
now_working_on_idx = 0
wins = 0
losses = 0
ties = 0

while now_working_on_idx < len(boards):
    current_board = boards[now_working_on_idx]

    # Check if the current board is a winner:
    if is_winner(HUMAN_MARK, current_board) or is_winner(ZINE_MARK, current_board):
        if is_winner(HUMAN_MARK, current_board):
            wins += 1
        if is_winner(ZINE_MARK, current_board):
            losses += 1
        # To finish the current board, change all None spaces to EMPTY:
        for space in ALL_SPACES:
            if current_board[space] is None:
                current_board[space] = EMPTY
        now_working_on_idx += 1  # Start work on next tic tac toe board.
        continue

    # Check if the current board is full:
    if is_full(current_board):
        ties += 1
        now_working_on_idx += 1  # Start work on next tic tac toe board.
        continue

    # Add new boards with every possible move for the current board:
    for space in ALL_SPACES:
        if current_board[space] is None:
            new_board = copy_marks(current_board)
            new_board[space] = HUMAN_MARK

            if not (is_winner(HUMAN_MARK, new_board) or is_full(new_board)):
                # The zine makes a move:
                new_board[get_zine_move(new_board)] = ZINE_MARK
            
            boards.append(new_board)  # Add the new board to the list.
            current_board[space] = len(boards) - 1  # Set the space to point to the new board.
    now_working_on_idx += 1

print('Number of boards:', len(boards), 'Wins:', wins, 'Losses:', losses, 'Ties:', ties)

# Shuffle the boards into a random order:
for this_idx, this_board in enumerate(boards):
    if this_idx == 0: continue  # Skip the starting board.

    # Randomly pick another board:
    other_idx = this_idx
    while other_idx == this_idx:
        other_idx = random.randint(1, len(boards) - 1)

    # Swap the two boards:
    boards[this_idx], boards[other_idx] = boards[other_idx], boards[this_idx]

    # Update the indexes in all of the boards:
    for j in range(len(boards)):
        for space in ALL_SPACES:
            if boards[j][space] == this_idx:
                boards[j][space] = other_idx
            elif boards[j][space] == other_idx:
                boards[j][space] = this_idx


# Check for duplicates:
dupes = set()
for i in range(len(boards)):
    for j in range(i + 1, len(boards)):
        if boards[i] == boards[j] and i not in dupes:
            dupes.add(i)

dupes_removed = 0
i = 0
while i < len(boards):
    j = i + 1
    while j < len(boards):
        # NOTE: j will always be larger than i
        if boards[i] == boards[j]:
            # Duplicate found. Delete the jth board:
            del boards[j]
            dupes_removed += 1

            # Re-number all indexes that pointed to the jth board to now point to the ith board:
            for k in range(len(boards)):
                for space in ALL_SPACES:
                    if boards[k][space] == j:
                        boards[k][space] = i

            # Shift all indexes greater than j down one on all boards:
            for k in range(len(boards)):
                for space in ALL_SPACES:
                    if str(boards[k][space]).isdigit() and boards[k][space] > j:
                        boards[k][space] -= 1
        j += 1
    i += 1

print('Duplicates removed:', dupes_removed)
print('Number of boards after removing duplicates:', len(boards))

assert len(boards) <= 600, 'ERROR: The number of boards must be under 600 to fit them in 25 zine pages.'

print('Writing `boards` data to ttt_data.txt...')
with open('ttt_data.txt', 'w') as fo:
    fo.write(str(boards))
print('Done.')

# Create the multi-line strings of 4x6 boards for each page:
pages = []
pages_im = []
pages.append('\n'.join(get_board_text(0)))  # The first page is just the starting board.
SEP = ' '
BOARDS_PER_ROW = 4
ROWS_PER_PAGE = 6
ROWS_IN_PRINTED_BOARD = len(get_board_text(0))
FONT_SIZE = 24
IM_WIDTH = 825 + 0  # Increasing the width adds to the left-right trim in the final PDF.
IM_HEIGHT = 1275 + 0  
SEPARATOR_LINE_COLOR = (200, 200, 200)  # Light gray

# Create the page for the first board:

# Adjust the page text to include instructiosn and a pointer to the board number:
pages[0] = """e.g. to move on top-
right, go to board #147
               %s
""" % (chr(9660)) + \
'\n'.join(['      ' + line for line in pages[0].splitlines()]) + \
"""
           %s
           Board number\n\n""" % (chr(9650))

with open('ttt_page_0.txt', 'w') as fo:
    fo.write(pages[0])
print('ttt_page_0.txt created.')

im = Image.new('RGB', (IM_WIDTH, IM_HEIGHT), (255, 255, 255))
draw = ImageDraw.Draw(im)
font = ImageFont.truetype('Courier New Bold.ttf', FONT_SIZE * 2)
bbox = draw.textbbox((0, 0), pages[0], font=font)
draw.multiline_text(((IM_WIDTH - bbox[2]) // 2, (IM_HEIGHT - bbox[3]) // 2), pages[0], fill=(0, 0, 0), font=font)

# Add instructions to the page:
instructions = 'You are X. The zine is O.\nStart on this page at\nboard #0. Pick a space &\ngo to its numbered board.'
bbox = draw.textbbox((0, 0), instructions, font=font)
draw.multiline_text(((IM_WIDTH - bbox[2]) // 2, 40), instructions, fill=(0, 0, 0), font=font)

# Add help to the page:
help = 'Text too small?\nUse your phone camera\nas a magnifying glass.'
bbox = draw.textbbox((0, 0), help, font=font)
draw.multiline_text(((IM_WIDTH - bbox[2]) // 2, (IM_HEIGHT - bbox[3] - 40)), help, fill=(0, 0, 0), font=font)

# Add the smartphone and magnifying glass images:
im.paste(Image.open('zine_smartphone.png'), (150, IM_HEIGHT - 400))
im.paste(Image.open('zine_magnifyingglass.png'), (350, IM_HEIGHT - 400))

im.save('ttt_page_0.png')
pages_im.append(im)
print('ttt_page_0.png created.')


# Create the pages of boards:
for i in range(1, len(boards), BOARDS_PER_ROW * ROWS_PER_PAGE):
    page = ''
    for y in range(ROWS_PER_PAGE):
        for row in range(ROWS_IN_PRINTED_BOARD):
            page_row_text = []
            for x in range(BOARDS_PER_ROW):
                if i + x + (y * BOARDS_PER_ROW) < len(boards):
                    page_row_text.append(get_board_text(i + x + (y * BOARDS_PER_ROW))[row])
            page += SEP.join(page_row_text) + '\n'
        page += '\n'
    page += ('#' + str(i) + ' to #' + str(i + BOARDS_PER_ROW * ROWS_PER_PAGE - 1)).center(BOARDS_PER_ROW * 12 - 1) + '\n'
    pages.append(page)

    with open('ttt_page_%s.txt' % (len(pages) - 1), 'w') as fo:
        fo.write(page)
    print('ttt_page_%s.txt created.' % (len(pages) - 1))

    # Create PNG image of the page:
    im = Image.new('RGB', (IM_WIDTH, IM_HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype('Courier New Bold.ttf', FONT_SIZE)
    bbox = draw.textbbox((0, 0), page, font=font)
    draw.multiline_text(((IM_WIDTH - bbox[2]) // 2, (IM_HEIGHT - bbox[3]) // 2), page, fill=(0, 0, 0), font=font)    
    im.save('ttt_page_%s.png' % (len(pages) - 1))
    pages_im.append(im)

    print('ttt_page_%s.png created.' % (len(pages) - 1))
print('Done writing page files..')

with open('ttt_page_ALL.txt', 'w') as fo:
    fo.write('\n\n\n\n'.join(pages))

def add_separator_lines(im):
    draw = ImageDraw.Draw(im)
    draw.line([(0, IM_HEIGHT), (IM_WIDTH * 4, IM_HEIGHT)], fill=SEPARATOR_LINE_COLOR)
    draw.line([(IM_WIDTH, 0), (IM_WIDTH, IM_HEIGHT * 2)], fill=SEPARATOR_LINE_COLOR)
    #draw.line([(IM_WIDTH * 2, 0), (IM_WIDTH * 2, IM_HEIGHT * 2)], fill=SEPARATOR_LINE_COLOR)
    draw.line([(IM_WIDTH * 3, 0), (IM_WIDTH * 3, IM_HEIGHT * 2)], fill=SEPARATOR_LINE_COLOR)

# Create the zine sheet images, which are composed of 4x2 pages. Sheets are US letter landscape.

# Sheet 1 front:
im = Image.new('RGB', (IM_WIDTH * 4, IM_HEIGHT * 2), (255, 255, 255))
im.paste(pages_im[0], (0, 0))
im.paste(pages_im[25], (IM_WIDTH, 0))
im.paste(pages_im[2], (IM_WIDTH * 2, 0))
im.paste(pages_im[23], (IM_WIDTH * 3, 0))
im.paste(pages_im[4], (0, IM_HEIGHT))
im.paste(pages_im[21], (IM_WIDTH, IM_HEIGHT))
im.paste(pages_im[6], (IM_WIDTH * 2, IM_HEIGHT))
im.paste(pages_im[19], (IM_WIDTH * 3, IM_HEIGHT))
add_separator_lines(im)
im = im.transpose(Image.ROTATE_270)

im.save('sheet_1_front.png')
print('Sheet 1 front created.')

# Sheet 1 back:
im = Image.new('RGB', (IM_WIDTH * 4, IM_HEIGHT * 2), (255, 255, 255))
im.paste(pages_im[24], (0, 0))
im.paste(pages_im[1], (IM_WIDTH, 0))
im.paste(Image.open('zine_backcover.png'), (IM_WIDTH * 2, 0))
im.paste(Image.open('zine_frontcover.png'), (IM_WIDTH * 3, 0))
im.paste(pages_im[20], (0, IM_HEIGHT))
im.paste(pages_im[5], (IM_WIDTH, IM_HEIGHT))
im.paste(pages_im[22], (IM_WIDTH * 2, IM_HEIGHT))
im.paste(pages_im[3], (IM_WIDTH * 3, IM_HEIGHT))
add_separator_lines(im)
im = im.transpose(Image.ROTATE_90)
im.save('sheet_1_back.png')
print('Sheet 1 back created.')

# Sheet 2 front:
im = Image.new('RGB', (IM_WIDTH * 4, IM_HEIGHT * 2), (255, 255, 255))
im.paste(pages_im[18], (0, 0))
im.paste(pages_im[7], (IM_WIDTH, 0))
im.paste(pages_im[13].transpose(Image.ROTATE_180), (IM_WIDTH * 2, 0))
im.paste(pages_im[12].transpose(Image.ROTATE_180), (IM_WIDTH * 3, 0))
im.paste(pages_im[16], (0, IM_HEIGHT))
im.paste(pages_im[9], (IM_WIDTH, IM_HEIGHT))
im.paste(pages_im[14], (IM_WIDTH * 2, IM_HEIGHT))
im.paste(pages_im[11], (IM_WIDTH * 3, IM_HEIGHT))
add_separator_lines(im)
im = im.transpose(Image.ROTATE_270)
im.save('sheet_2_front.png')
print('Sheet 2 front created.')

# Sheet 2 back:
im = Image.new('RGB', (IM_WIDTH * 4, IM_HEIGHT * 2), (255, 255, 255))
im.paste(Image.open('zine_centerfold.png'), (0, 0))
im.paste(pages_im[8], (IM_WIDTH * 2, 0))
im.paste(pages_im[17], (IM_WIDTH * 3, 0))
im.paste(pages_im[10], (IM_WIDTH * 2, IM_HEIGHT))
im.paste(pages_im[15], (IM_WIDTH * 3, IM_HEIGHT))
add_separator_lines(im)
im = im.transpose(Image.ROTATE_90)
im.save('sheet_2_back.png')
print('Sheet 2 back created.')

# Create the PDF from the sheet images:
def image_to_pdf_bytes(image_path):
    with Image.open(image_path) as im:
        im = im.convert("RGB")  # PDF requires RGB
        buffer = io.BytesIO()
        im.save(buffer, format="PDF", resolution=300.0)  # 300 DPI for high quality
        buffer.seek(0)
        return buffer

def create_pdf_with_images(image_paths, output_pdf):
    writer = PdfWriter()

    for path in image_paths:
        pdf_buffer = image_to_pdf_bytes(path)
        reader = PdfReader(pdf_buffer)
        writer.add_page(reader.pages[0])

    with open(output_pdf, "wb") as f:
        writer.write(f)

create_pdf_with_images(['sheet_1_front.png', 'sheet_1_back.png', 'sheet_2_front.png', 'sheet_2_back.png'], OUTPUT_PDF_FILENAME)
print('Print PDF %s created.' % (OUTPUT_PDF_FILENAME))


# Create the PDF that can be read linearly on a computer:
writer = PdfWriter()
for page_im in [Image.open('zine_frontcover.png'), Image.open('zine_centerfold.png')] + pages_im + [Image.open('zine_backcover.png')]:
    page_im = page_im.convert('RGB')
    buffer = io.BytesIO()
    page_im.save(buffer, format="PDF", resolution=300.0) 
    buffer.seek(0)
    reader = PdfReader(buffer)
    writer.add_page(reader.pages[0])
with open('tictactoe_zine_linear.pdf', "wb") as f:
    writer.write(f)

print('Linear PDF tictactoe_zine_linear created.')
print('Done.')
