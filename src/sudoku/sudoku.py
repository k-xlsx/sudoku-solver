"""
Methods used to solve a sudoku board

    Main methods:
        sudoku_solve -- returns a solved board
        step_by_step_sudoku_solve -- yields a board every time it adds something to it or backtracks, until it's solved

        print_board -- prints the board to the console
        print_solving_step_by_step -- prints every consecutive step of solving the board
"""

from copy import deepcopy
from requestsJson import get_data_from_json_site
from sudokuexceptions import BoardError, ArgumentError

# char meaning the spot is empty
emptySpotChar = '0'

# the constMarker is for constant values that CANNOT be changed by the algorithm
_constMarker = '$'


def sudoku_solve(board, copyBoard=True, correctWrongChars=False):
    """
    Solves the given board.

    Keyword Arguments:
        copyBoard {bool} -- should the method work on a copied board and just return it (True)
        or just work with the original (False) (default: {True})
        correctWrongChars {bool} -- if True the method will mark every unknown char as emptySpotChar

    Raises:
        BoardError: Board's size must be a positive multiple of 3.
        BoardError: Board's row count and row length must be uniform.

    Returns:
        {a tuple of lists} -- the solved board
        or
        {None} -- if the board is unsolvable
    """


    if copyBoard:
        brd = deepcopy(board)
    else:
        brd = board

    # general checks if the board is valid for sudoku
    if len(brd) % 3 != 0 or len(brd) == 0:
        raise BoardError("Board's size must be a positive multiple of 3.")
    elif not(_is_board_square(brd)):
        raise BoardError("Board's row count and row length must be uniform.")


    maxBoardIndex = len(brd) - 1
    maxBoardRange = len(brd) + 1

    possibleNums = tuple([str(i)
                          for i in range(1, maxBoardRange)])

    brd = ensure_board_types(brd, correctWrongChars)
    brd = _mark_constants(brd)


    rowI = elementI = 0
    while True:

        # if it isn't taken by a constant num
        if brd[rowI][elementI] == emptySpotChar or brd[rowI][elementI] in possibleNums:

            # if it had already reached 9 before and it cannot increment further
            if brd[rowI][elementI] == possibleNums[-1]:

                # reset the spot
                brd[rowI][elementI] = emptySpotChar

                # backtrack to the last available spot
                newCoords = _get_bactrack_coordinates(rowI, elementI, brd)
                if not(newCoords):

                    # the board cannot be solved
                    return

                rowI = newCoords[0]
                elementI = newCoords[1]

            else:

                currentHorizontalNums = _get_horizontal_nums(brd)[rowI]
                currentVerticalNums = _get_vertical_nums(brd)[elementI]
                currentSquareNums = _get_nums_in_squares(brd)[_get_square_num(rowI, elementI, len(brd))]

                bannedNums = currentHorizontalNums | currentVerticalNums | currentSquareNums

                validNums = [num
                             for num in range(_get_current_num_incremented(rowI, elementI, brd), maxBoardRange)
                             if num not in bannedNums]

                # go through all nums valid nums
                for num in validNums:

                    # if the num isn't already on the horizontal or vertical line or in a square
                    if str(num) not in bannedNums:

                        # set the first available num on the spot
                        brd[rowI][elementI] = str(num)

                        # go forward a spot
                        newCoords = _get_forward_coordinates(rowI, elementI, maxBoardIndex)
                        if not(newCoords):

                            # final return (with the markers deleted for good measure)
                            return _remove_constant_marks(brd)

                        rowI = newCoords[0]
                        elementI = newCoords[1]

                        break

                    # if none of the spots are available
                    elif (num == maxBoardRange - 1):

                        # reset the spot
                        brd[rowI][elementI] = emptySpotChar

                        # backtrack to the last available spot
                        newCoords = _get_bactrack_coordinates(rowI, elementI, brd)
                        if not(newCoords):

                            # the board cannot be solved
                            return

                        rowI = newCoords[0]
                        elementI = newCoords[1]

        # if it's a constant num
        else:

            # go forward a spot
            newCoords = _get_forward_coordinates(rowI, elementI, maxBoardIndex)
            if not(newCoords):

                # final return (with the markers deleted for good measure)
                return _remove_constant_marks(brd)

            rowI = newCoords[0]
            elementI = newCoords[1]


def gen_sudoku_solving_step_by_step(board, copyBoard=True, correctWrongChars=False):
    """
    sudoku_solve but it yields the board every time it places or removes a num.

    Keyword Arguments:
        copyBoard {bool} -- should the method work on a copied board and just return it (True)
        or just work with the original (False) (default: {False})
        correctWrongChars {bool} -- if True the method will mark every unknown char as emptySpotChar

    Raises:
        BoardError: Board's size must be a positive multiple of 3.
        BoardError: Board's row count and row length must be uniform.
        ArgumentError: constMarker cannot be empty.

    Yields:
        {a tuple containing a tuple of lists and a bool} -- board in the current step with the information
        if it went forward(True) or backtracked(False)
        or
        {None} -- if the board is unsolvable
    """

    if copyBoard:
        brd = deepcopy(board)
    else:
        brd = board

    # general checks if the board is valid for sudoku
    if len(brd) % 3 != 0 or len(brd) == 0:
        raise Exception("Board's size must be a positive multiple of 3")
    elif not(_is_board_square(brd)):
        raise Exception("Board's row count and row length must be uniform")

    # the constMarker cannot be empty
    if _constMarker == '':
        raise ArgumentError('constMarker cannot be empty.')


    maxBoardIndex = len(brd) - 1
    maxBoardRange = len(brd) + 1

    possibleNums = tuple([str(i)
                          for i in range(1, maxBoardRange)])

    brd = ensure_board_types(brd, correctWrongChars)
    brd = _mark_constants(brd)

    rowI = elementI = 0
    while True:

        # if it isn't taken by a constant num
        if brd[rowI][elementI] == emptySpotChar or brd[rowI][elementI] in possibleNums:

            # if it had already reached 9 before and it cannot increment further
            if brd[rowI][elementI] == possibleNums[-1]:

                # reset the spot
                brd[rowI][elementI] = emptySpotChar
                yield (_remove_constant_marks(brd), False)

                # backtrack to the last available spot
                newCoords = _get_bactrack_coordinates(rowI, elementI, brd)
                if not(newCoords):

                    # the board cannot be solved
                    yield None
                    return

                rowI = newCoords[0]
                elementI = newCoords[1]

            else:

                currentHorizontalNums = _get_horizontal_nums(brd)[rowI]
                currentVerticalNums = _get_vertical_nums(brd)[elementI]
                currentSquareNums = _get_nums_in_squares(brd)[_get_square_num(rowI, elementI, len(brd))]

                bannedNums = currentHorizontalNums | currentVerticalNums | currentSquareNums

                validNums = [num
                             for num in range(_get_current_num_incremented(rowI, elementI, brd), maxBoardRange)
                             if num not in bannedNums]

                # go through all valid nums
                for num in validNums:

                    # if the num isn't already on the horizontal or vertical line or in a square
                    if str(num) not in bannedNums:


                        # set the first available num on the spot
                        brd[rowI][elementI] = str(num)
                        yield (_remove_constant_marks(brd), True)

                        # go forward a spot
                        newCoords = _get_forward_coordinates(rowI, elementI, maxBoardIndex)
                        if not(newCoords):

                            # board solved
                            return

                        rowI = newCoords[0]
                        elementI = newCoords[1]

                        break

                    # if none of the spots are available
                    elif (num == maxBoardRange - 1):

                        # reset the spot
                        brd[rowI][elementI] = emptySpotChar
                        yield (_remove_constant_marks(brd), False)

                        # backtrack to the last available spot
                        newCoords = _get_bactrack_coordinates(rowI, elementI, brd)
                        if not(newCoords):

                            # the board cannot be solved
                            return

                        rowI = newCoords[0]
                        elementI = newCoords[1]

        # if it's a constant num
        else:

            # go forward a spot
            newCoords = _get_forward_coordinates(rowI, elementI, maxBoardIndex)
            if not(newCoords):

                # board solved
                yield (_remove_constant_marks(brd), True)
                return

            rowI = newCoords[0]
            elementI = newCoords[1]


def print_board(board):
    """
    Prints the given board.

    Arguments:
        board {tuple of lists} -- the tuple contains lists(rows), and the lists contain the actual elements

    If board is None it prints No solution
    """

    if not(board):
        print('No Solution')

    for row in board:
        i = 0
        for element in row:

            pelement = element

            if len(board) > 9:
                if i == 0 and len(element) == 1:
                    pelement = ' ' + pelement

            try:
                if((len(element) == 1 and len(row[i + 1]) == 1) or
                   (len(element) == 2 and len(row[i + 1]) == 1)):
                    gap = 2 * ' '
                elif((len(element) == 2 and len(row[i + 1]) == 2) or
                     (len(element) == 1 and len(row[i + 1]) == 2)):
                    gap = ' '
            except IndexError:
                gap = ''

                print(pelement.replace(_constMarker, '') + gap, end='')

                i += 1
            print()


def print_solving_step_by_step(board):
    """
    Prints every step (board) of the algorithm solving the board.

    Keyword Arguments:
        copyBoard {bool} -- should the method work on a copied board and just return it (True)
        or just work with the original (False) (default: {True})
    """

    print_board(board)
    print('Going forward...')

    solveStepByStep = gen_sudoku_solving_step_by_step(board)

    while True:
        try:
            step = next(solveStepByStep)
        except StopIteration:
            print('Done!')
            break
        else:
            try:
                print_board(step[0])
            except TypeError:
                print('No solution!')
                break
            else:
                if step[1]:
                    print('Went forward.')
                else:
                    print('Went back.')

                print()


def generate_board_from_api(difficulty='medium'):
    """
    Generates a board (9x9) from berto's API (https://sugoku.herokuapp.com/board)
        His emptySpotChars are '0'!

    Keyword Arguments:
        difficulty {str} -- easy, medium or hard (default: {'medium'})

    Raises:
        ArgumentError: Incorrect difficulty ('easy', 'medium' or 'hard').

    Returns:
        {tuple of lists} -- board converted to my format (9 lists in a tuple, each containing 9 elements)
    """

    difficulty = difficulty.lower()

    if difficulty not in ('easy', 'medium', 'hard'):
        raise ArgumentError("Incorrect difficulty ('easy', 'medium' or 'hard').")

    # https://github.com/berto/sugoku - thanks berto!
    boardGeneratorApiURL = 'https://sugoku.herokuapp.com/board'

    generatedBoard = get_data_from_json_site(boardGeneratorApiURL, params={'difficulty': difficulty})['board']

    return tuple(generatedBoard)


def ensure_board_types(board, correctWrongChars=False):
    """
    Ensures the board and its contents contain correct types of elements.

    Arguments:
        board {a tuple of lists} -- the tuple contains lists(rows), and the lists contain the actual elements

    Keyword Arguments:
        correctWrongChars {bool} -- if True the method will mark every unknown char as emptySpotChar

    Returns:
        {a tuple of lists} -- corrected board

    Raises:
        BoardError: Unknown char in board. (if it encountered it while correctWrongChars is False)
        ArgumentError: correctWrongChars must be boolean.
    """

    if not(isinstance(correctWrongChars, bool)):
        raise ArgumentError('correctWrongChars must be boolean.')

    possibleNums = tuple([str(i)
                          for i in range(1, len(board) + 1)])

    ensuredBoard = []
    rowI = 0
    elementI = 0
    for row in board:

        ensuredBoard.append(list(row))
        for _ in row:

            char = str(ensuredBoard[rowI][elementI])

            if char not in possibleNums and char != emptySpotChar:
                if correctWrongChars:
                    char = emptySpotChar
                else:
                    raise BoardError('Unknown char in board.')

            ensuredBoard[rowI][elementI] = char

            elementI += 1

        rowI += 1
        elementI = 0


    return tuple(ensuredBoard)



def _get_forward_coordinates(rowI, elementI, maxBoardIndex):
    """
    Returns the next coordinates (as a tuple) or None

    Arguments:
        rowI {int} -- index of the current row
        elementI {int} -- index of the current element
        maxBoardIndex {int} -- max index of the current board

    Returns:
        {tuple} -- next coordinates on the board (row index, element index)
        or
        {None} -- the board is solved (the algorithm tried to go past the last element of the board)
    """

    # go to the next spot (if it's the last one, go down a row)
    elementI += 1
    if elementI > maxBoardIndex:
        elementI = 0
        rowI += 1

        # if it tries to go past the last item on the board
        if rowI > maxBoardIndex:
            return

    return (rowI, elementI)


def _get_bactrack_coordinates(rowI, elementI, board):
    """
    Returns the last available coordinates or None.

    Arguments:
        rowI {int} -- current row index
        elementI {int} -- current element index
        board {tuple of lists} -- current board

    Returns:
        {tuple} -- last available coordinates (row index, element index)
        or
        {None} -- the board is unsolvable (the algorithm tried to backtrack past the first element)
    """

    maxBoardIndex = len(board) - 1

    # go back a spot (if it's the first one, go up a row)
    elementI -= 1
    if elementI < 0:
        rowI -= 1

        # if it tried to backtrack from the first spot
        if rowI < 0:
            return

        # it goes to the last spot of the previous row (it moves through the board like a snake)
        else:
            elementI = maxBoardIndex

    # while the current element it's checking is a constant
    # DOESN'T WORK PROPERLY i.e. doesn't work at all
    # UPDATE: i think it does now
    while '$' in board[rowI][elementI]:

        elementI -= 1
        if elementI < 0:
            rowI -= 1

            # if it tried to backtrack from the first spot
            if rowI < 0:
                return

            # it goes to the last spot of the previous row (it moves through the board like a snake)
            else:
                elementI = maxBoardIndex

    return (rowI, elementI)


def _get_current_num_incremented(rowI, elementI, board):
    """
    It's used to set the lower bound to check for nums

    Arguments:
        rowI {int} -- current row index
        elementI {int} -- current element index
        board {tuple of lists} -- current board

    Returns:
        {int} -- num placed in the current element + 1 or 1 (if the element is empty) or max num of the board (if the num is equal to the max num)
    """

    if board[rowI][elementI] == emptySpotChar:

        return 1

    elif board[rowI][elementI] == str(len(board)):

        return int(board[rowI][elementI])

    else:

        return int(board[rowI][elementI]) + 1


def _get_square_num(rowI, elementI, boardLen):
    """
    Returns the square's index, in which are the given coordinates.
    Squares are marked horizontally starting at the leftmost corner, heading rightwards

    Arguments:
        rowI {int} -- index of the current row
        elementI {int} -- index of the current element
        boardLen {int} -- length of the board

    Returns:
        {int} -- index used to mark the squares in get_nums_in_squares
    """

    squareSize = int(boardLen / 3)
    squareMaxYs = tuple(filter(lambda x: x % 3 == 0, range(3, boardLen + 1)))
    squareMaxXs = tuple(filter(lambda x: x % squareSize == 0, range(squareSize, boardLen + 1)))

    index = 0
    for maxY in squareMaxYs:
        if rowI < maxY:
            for maxX in squareMaxXs:
                if elementI < maxX:
                    return index
                else:
                    index += 1
        else:
            index += 3


def _get_horizontal_nums(board):
    """
    Returns a list of nums in corresponding horizontal lines.

    Arguments:
        board {tuple of lists} -- current board

    Returns:
        {tuple of sets} -- tuple contains sets of nums in corresponding rows
    """

    # pretty much copies the board without blank spaces and const markers
    horizontals = [{element.replace(_constMarker, '')
                    for element in row
                    if element != emptySpotChar}
                   for row in board]

    return tuple(horizontals)


def _get_vertical_nums(board):
    """
    Returns a list of nums in corresponding vertical lines.

    Arguments:
        board {tuple of lists} -- current board

    Returns:
        {tuple of sets} -- tuple contains sets of nums in corresponding columns
    """

    # empty list the same size as the board but filled with empty lists|
    verticals = [set()
                 for row in board]

    for elNum in range(len(board)):
        for rowNum in range(len(board)):
            # adds only nums to save time
            if board[rowNum][elNum] != emptySpotChar:
                verticals[elNum].add(board[rowNum][elNum].replace(_constMarker, ''))

    return tuple(verticals)


def _get_nums_in_squares(board):
    """
    Returns a list of nums in corresponding squares
    (they're marked horizontally starting at the leftmost corner, heading rightwards).

    Arguments:
        board {tuple of lists} -- current board

    Returns:
        {tuple of sets} -- tuple contains sets of nums in corresponding squares
    """

    squareSize = int(len(board) / 3)
    squareY = 3
    squareX = squareSize

    # empty list the same size as the board but filled with empty sets
    squares = [set()
               for row in board]

    for squareNum in range(len(board)):
        for y in range(squareY - 3, squareY):
            for x in range(squareX - squareSize, squareX):
                # adds only nums to save time
                if board[y][x] != emptySpotChar:
                    squares[squareNum].add(board[y][x].replace(_constMarker, ''))

        squareX += squareSize
        if squareX > len(board):
            squareX = int(len(board) / 3)
            squareY += 3

    return tuple(squares)



def _is_board_square(board):
    """
    Checks whether the board's length is the same as each row's length.

    Arguments:
        board {a tuple of lists} -- the tuple contains lists(rows), and the lists contain the actual elements

    Returns:
        {bool}
    """

    for row in board:
        if len(board) != len(row):
            return False

    return True


def _mark_constants(board):
    """
    Returns a board with the nums coming pre-set marked with constMarker.

    Arguments:
        board {a tuple of lists} -- the tuple contains lists(rows), and the lists contain the actual elements

    Raises:
        ArgumentError: constMarker cannot be empty.

    Returns:
        {tuple of lists} -- board but the nums in it were marked
    """

    if _constMarker == '':
        raise ArgumentError('constMarker cannot be empty.')

    for row in board:
        for element in row:
            if element != emptySpotChar:
                board[board.index(row)][row.index(element)] += _constMarker

    return board


def _remove_constant_marks(board):
    """
    Returns a board with the constMarkers removed if i'll ever need it.

    Arguments:
        board {a tuple of lists} -- the tuple contains lists(rows), and the lists contain the actual elements

    Returns:
        {tuple of lists} -- board but the marked nums are unmarked
    """

    for row in board:
        for element in row:
            if element != emptySpotChar:
                board[board.index(row)][row.index(element)] = board[board.index(row)][row.index(element)].replace(_constMarker, '')

    return board