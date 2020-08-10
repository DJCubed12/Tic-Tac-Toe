import tkinter as tk
from random import randrange
import re

# WARNINGS FOR PROGRAMMING:
'''
If a Board object is ever assigned to another variable, ex:
a = Board(next(Test()))
b = a
they are dynamic. Therefore any changes to b will also change a.
'''

def play(gui=True, *, devmode=False):
    ''' Main function that runs the game. START HERE. '''
    global ConsoleInterface, GUIInterface, findNewWins, spaceUsed, randMove, findSecondMove, SecondMovePlan, Board, randrange, re, play, tk

    if gui:
        inter = GUIInterface()
    else:
        inter = ConsoleInterface(devmode)

    row = randrange(3)
    start = Board([[0,0,0], [0,0,0], [0,0,0]]) # Separates randrange to insure randomness
    column = randrange(3)
    current = start + (row, column, 1)

    current = inter.interface(current)
    # First Moves Complete

    Plan = findSecondMove(current)  # Second Move is decided. Third moves are ready
    current = inter.interface(Plan.SecondMove)
    # Second Moves Complete

    try:
        # By here a win is possible so everything is in a try except expression because wins and cats are shown with exceptions.
        if len(current.compwins) > 0:   # Win
            row, column = current.compwins[0]
            third = current + (row, column, 1)
        elif len(current.playerwins) > 0:   # Block Player Win
            row, column = current.playerwins[0]
            third = current + (row, column, 1)
        else:   # Continue Plan
            for option in Plan.thirdmoves:  # Check options
                # option is a tuple: (Board object, row, column)
                if not spaceUsed(current, option[1], option[2]):
                    third = current + (option[1], option[2], 1)
                    break
            else:
                third = randMove(current)
        current = inter.interface(third)
        # Third Move Complete

        # Fourth and higher Moves:
        # Continue making moves until win or cat:
        while True:
            if len(current.compwins) > 0:
                # inter.interface(current with winning position move)
                current = inter.interface(current + (current.compwins[0][0], current.compwins[0][1], 1))
            elif len(current.playerwins) > 0:
                # inter.interface(current with blocking win position)
                current = inter.interface(current + (current.playerwins[0][0], current.playerwins[0][1], 1))
            else:
                current = inter.interface(randMove(current))
    except Exception as error:
        if error.args[0] == 1:
            # Comp Win
            inter.compWin()
        elif error.args[0] == 0:
            # Cat Game
            inter.cat()
        elif error.args[0] == -1:
            # Player Win
            inter.playerWin()
        else:
            # Something went wrong
            inter.error()

        # Play Again?
        if inter.playAgain():
            play(devmode=devmode)

class ConsoleInterface:
    ''' Object that is used to print the outputs and use the inputs of the game. '''

    def __init__(self, devmode):
        ''' Sets self.devmode to true or false. '''
        self.devmode = devmode

    def interface(self, board):
        ''' Dictates the interaction between player input and the program. Should return row, column for the position of the user's player. '''
        while True:
            def show(board, row, column):
                if board.board[row][column] == 1:
                    return 'X'
                elif board.board[row][column] == -1:
                    return 'O'
                else:
                    return ' '

            # Be sure to show board before raising any exception
            print("")
            print("  0 1 2")
            print("0 {0}|{1}|{2}".format(show(board, 0, 0), show(board, 0, 1), show(board, 0, 2)))
            print("  -+-+-")
            print("1 {0}|{1}|{2}".format(show(board, 1, 0), show(board, 1, 1), show(board, 1, 2)))
            print("  -+-+-")
            print("2 {0}|{1}|{2}".format(show(board, 2, 0), show(board, 2, 1), show(board, 2, 2)))
            print("")

            if self.devmode:
                print(board.board)
                print("")

            # Win Check:
            if board.win != 0:
                raise Exception(board.win)
            else:
                randMove(board)

            print("Your Move:")
            print("(Input: row, column)")
            move = input("")

            try:
                move = re.search(r'\D*(\d)\D*(\d)\D*', move).groups()

                row, column = int(move[0]), int(move[1])

                if spaceUsed(board, row, column):
                    print("I'm sorry, but that spot is taken.")
                else:
                    return board + (row, column, -1)
            except (IndexError, AttributeError):
                print("That is not a valid response. Please respond in the form: row, column. Row and column can each be either 0, 1, or 2.")

    def compWin(self):
        ''' Prints a message stating that the player lost. '''
        print("You Lose")
    def cat(self):
        ''' Prints a message stating it was a cat game. '''
        print("Cat Game")
    def playerWin(self):
        ''' Prints an unhappy message stating the player won. '''
        print("You Win\n")
        print("Fuck...")
        print("\n\n\n\n\n")
        print("That wasn't supposed to happen.")
    def error(self):
        ''' Prints a message stating something went wrong. '''
        print("I'm sorry, but there seems to have been an internal error.")
        print("Please contact for Friendly Neighborhood Tech Guy so he can attempt to resolve this issue.")
    def playAgain(self):
        ''' Asks the player if they would like to play again. Returns true if so. '''
        print('\n')
        response = input("Play Again? ")
        if response.count('y') > 0:
            return True

class GUIInterface:
    ''' Object for TicTacToe used to give output and get input. Uses tkinter to achieve this with a gui window. An alternative to Console Interface. '''

    def __init__(self):
        ''' Starts the window and sets up all buttons. '''
        # CONSTANTS
        font = 'Ariel 18'
        btnsize = 125
        pad = 5
        self.waittime = 2

        # VARS
        self.buttons = []
        self.selected = (0, 0)
        self.games = 0

        self.root = tk.Tk()
        self.root.columnconfigure([x for x in range(3)], weight=1, minsize=btnsize)
        self.root.rowconfigure([1,2,3], weight=1, minsize=btnsize)

        self.top = tk.Label(self.root, text="Your Turn", font=font)
        self.top.grid(row=0, column=0, columnspan=3, padx=pad, pady=pad)

        self.bot = tk.Label(self.root, text="", font=font)
        self.bot.grid(row=4, column=0, columnspan=3, padx=pad, pady=pad)

        for row in range(3):
            inner = []
            for column in range(3):
                frm = tk.Frame(self.root)
                frm.grid(row=row+1, column=column, padx=pad, pady=pad, sticky="nesw")
                btn = tk.Button(frm, text="", font=font, command=self.boardButtons(row, column))
                btn.pack(expand=True, fill=tk.BOTH)
                inner.append(btn)
            self.buttons.append(inner)

        self.root.update()
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
        #self.root.maxsize(self.root.winfo_width(), self.root.winfo_height())


    def boardButtons(self, row, column):
        ''' Method that returns a function based on the buttons row and column. The function returned will set self.selected to the coordinate of the board they chose and it will exit the event loop. '''
        def f(r=row, c=column):
            self.selected = (r, c)
            self.root.quit()
        return f

    def interface(self, board):
        ''' Method called by the play() function. Updates the buttons' text and starts mainloop() to wait for which option they choose. '''
        global spaceUsed, randMove

        for row in range(3):
            for column in range(3):
                x = board.board[row][column]
                if x == 1:
                    txt = "X"
                elif x == -1:
                    txt = "O"
                else:
                    txt = ""
                self.buttons[row][column]["text"] = txt

        # Win Check:
        if board.win != 0:
            raise Exception(board.win)
        else:
            randMove(board)

        while True:
            self.root.mainloop()
            if spaceUsed(board, self.selected[0], self.selected[1]):
                self.top["text"] = "That space is already used."
                continue
            self.buttons[self.selected[0]][self.selected[1]]["text"] = "O"
            return board + (self.selected[0], self.selected[1], -1)

    def buttonMessage(self, words):
        ''' A method that changes the text on each button to the corresponding string in 'words'. '''
        for x in range(3):
            for y in range(3):
                try:
                    self.buttons[x][y]["text"] = words[x + (y*3)]
                except:
                    pass

    def compWin(self):
        ''' Prints a message stating that the player lost. '''
        self.top["text"] = "You Lose"
    def cat(self):
        ''' Prints a message stating it was a cat game. '''
        self.top["text"] = "Cat Game"
    def playerWin(self):
        ''' Prints an unhappy message stating the player won. '''
        self.top["text"] = "You Win"
        self.buttonMessage(["Shit", "that", "wasn't", "supposed", "to", "happen", "", "!", ""])
    def error(self):
        ''' Prints a message stating something went wrong. '''
        self.top["text"] = "An error has occured"
        for inner in self.buttons:
            for btn in inner:
                btn["bg"] = "red"
        self.buttons[1][1]["text"] = "!"
    def playAgain(self):
        ''' Asks the player if they would like to play again. Returns true if so. '''
        self.bot["text"] = "Click any button to play again."
        self.root.mainloop()
        self.root.destroy()
        return True

def findNewWins(origional, new):
    ''' Returns the number of new win lines that appeared from the move in te new version. origional and new should both be Board objects. '''
    return len(new.compwins + new.playerwins) - len(origional.compwins + origional.playerwins)
def spaceUsed(boardobj, row, column):
    ''' Returns true if the specified position already has something there. boardobj should be a Board object. '''
    if boardobj.board[row][column] != 0:
        return True
def randMove(board):
    ''' Returns a Board object with a pointless move made once the plan has failed. '''

    for row in range(3):
        for column in range(3):
            if not spaceUsed(board, row, column):
                return board + (row, column, 1)
    else:
        # Cat games are symbolized with a '0' Exception
        raise Exception(0)


def findSecondMove(startboard):
    ''' Uses a Board object describing the first computer move and player move to decide on the computer's second move. plans is a list of all possible second moves (in the form of SecondMovePlan objects). That list is then sorted by each object's thirdmoves length (number of third moves that create win win scenarios). The first of that list is then returned as a SecondMovePlan object.
    startboard is a Board object
    Returns SecondMovePlan object
    '''

    plans = []

    # Goes through all positions
    for row in range(3):
        for column in range(3):
            # Skip this position if it's already filled
            if spaceUsed(startboard, row, column):
                continue

            SecondMove = startboard + (row, column, 1)
            Plan = SecondMovePlan(SecondMove)

            # If there the move creates a win line and has a third move that creates a win win scenario, use it instead of any other because it can't be stoped.
            if findNewWins(startboard, SecondMove) == 1:
                try:
                    if findNewWins(Plan.SecondMove, Plan.thirdmoves[0][0]) == 2:
                        return Plan
                except:
                    pass
            else:
                # Add the SecondMovePlan object with this position as 2nd move.
                plans.append(Plan)

    # Sorts plans by each SecondMovePlan's thirdmoves list length. Plans with length 2 have 2 different third moves that guarantee a win, so they are the best.
    sortedplans = sorted(plans, key=lambda secmoveplan: len(secmoveplan.thirdmoves), reverse=True)

    return sortedplans[0]


class SecondMovePlan:
    ''' An object that enumerates third move options based on a specified second move. Use SecondMovePlan.SecondMove.board for the Board object describing the second move. Use SecondMovePlan.thirdmoves for a list of tuples containing a Board object describing a third move that create win win senarios and the moves row and column.
    secondmoveBoard is a Board object
    '''

    def __init__(self, secondmoveBoard):
        ''' secondmoveBoard should be a Board object. '''
        self.SecondMove = secondmoveBoard   # Board object
        self.thirdmoves = []
        self.findThirdMoves()

    def findThirdMoves(self):
        ''' Finds third move positions based on the secondMove and adds them to thirdmoves list. '''

        # The for loops continue after finding a third move so it can find out if this second move has multiple third moves for winning, which would make it the best option.

        for row in range(3):
            for column in range(3):
                # Checks and skips if the position already has something there.
                if spaceUsed(self.SecondMove, row, column):
                    continue

                # Creates a new Board with a 1 at row, column
                Third = self.SecondMove + (row, column, 1)
                # if there are 2 or more new possible win lines, this is considered a valid third move and is added to the list.
                if findNewWins(self.SecondMove, Third) == 2:
                    self.thirdmoves.append((Third, row, column))

class Board:
    ''' Object that contains a 3x3 matrix representing a situation in tic-tac-toe. 1's represent the computer (X's), -1's represents the player (O's), and 0 shows an empty space. Also contains a list of all possible win spaces for each team, the player and the computer. '''

    def __init__(self, board):
        ''' Sets the board variable. Immediatly uses winSpaces() to determine any possible win spaces for each team and sets them to a list for eahc team. '''

        self.board = board
        # (row, column) winning positions
        self.compwins = []
        self.playerwins = []
        self.win = 0

        self.winSpaces()

    def __add__(self, right):
        ''' Defines adding to a Board. Adding a tuple of a tuple showing the co-ordinates and the value [Board + (row, column, value)] returns a new Board with that position changed to that value. '''

        # if right[2] is -1, 0, or 1
        if [-1, 0, 1].count(right[2]) == 1:
            from copy import deepcopy
            newboard = deepcopy(self.board)
            newboard[right[0]][right[1]] = right[2]
            return Board(newboard)

    def transpose(self, matrix):
        ''' Returns a transposed 3x3 matrix. Effectively converts all columns into rows, and all rows into columns. Made for use in the winSpaces() for column loop. '''

        transposed = []

        for column in range(3):
            newrow = []
            for row in range(3):
                newrow.append(matrix[row][column])
            transposed.append(newrow)

        return transposed

    def winSpaces(self):
        ''' Finds spaces that could complete win lines. Returns (row, column) in a list for all spaces that could win. team == -1 or +1 depending on which team is being checked. 1 being an X (Computer space), -1 being an O (Player space). '''

        # If you sum a line, it will be +/-2 if it is a possible win line (two of the same team in line). If there are 2 of one team and one of the other (thereby preventing a win), then +/-1 will be the sum.
        # The following loops sum all possible lines and finds any finds any win lines:

        def winLine(team, row, column):
            ''' Adds the co-ordinate to one of the item's list, depending on which team it is. '''
            if team > 0:
                self.compwins.append((row, column))
            else:
                self.playerwins.append((row, column))

        # Rows:
        for row in range(3):

            total = sum(self.board[row])

            if abs(total) >= 2:
                if abs(total) == 3:
                    self.win = total//3
                else:
                    winLine(total, row, self.board[row].index(0))

        # Columns
        for column in range(3):

            transposed = self.transpose(self.board)

            total = sum(transposed[column])

            if abs(total) >= 2:
                if abs(total) == 3:
                    self.win = total//3
                else:
                    winLine(total, transposed[column].index(0), column)

        # Top Right to Bot Left Diagonal
        topright = [self.board[x][x] for x in range(3)]

        total = sum(topright)
        if abs(total) >= 2:
            if abs(total) == 3:
                self.win = total//3
            else:
                winLine(total, topright.index(0), topright.index(0))

        # Bot Right to Top Left Diagonal
        botrightindexes = [(2, 0), (1, 1), (0, 2)]
        botright = [self.board[row][column] for row, column in botrightindexes]

        total = sum(botright)
        if abs(total) >= 2:
            if abs(total) == 3:
                self.win = total//3
            else:
                # Finds the index of 0 in botright, and then finds the actual position of it with botrightindexes, and then does winLines with the row and column specified from botrightindexes.
                winLine(total, botrightindexes[botright.index(0)][0], botrightindexes[botright.index(0)][1])

if (__name__ == "__main__") | (__name__ == "runclass"):
    play()
