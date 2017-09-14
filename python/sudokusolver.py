import random
import argparse
import os

def get_section_coords(ind):
    
    if ind % 3 == 2:
        return ind-2, ind
    elif ind % 3 == 1:
        return ind-1,ind+1
    elif ind % 3 == 0:
        return ind, ind+2

class Square(object):
    def __init__(self,x,y,grid):
        self.row = x
        self.col = y
        self._val = 0
        self._grid = grid
        self.opts = []
        self.cmin, self.cmax = get_section_coords(self.col)
        self.rmin, self.rmax = get_section_coords(self.row)
    
    # By declaring the value a property, we can assure the value of a square doesn't get reassigned
    # after initial assignment without having lots of extra checks in the main body of the code

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self,val):
        """This setter makes sure a pre-existing value never gets overwritten, and whenever a new
        value is written all the options in the grid get refreshed"""
        if self._val == 0 or val == 0:
            self._val = val
            self._grid.get_square_opts() 

class Grid(object):
    sections = 3 
    rows = range(9)
    cols = range(9)
    nums = range(1,10)
    
    def __init__(self,puzzle_lines):
        self.solved = False
        # The 2nd element is the number of times a guess has ocurred, so we can avoid making an
        # incorrect guess multiple times
        self.guessed = False
        self.squares = []
        for row in range(len(puzzle_lines)):
            raw_squares = puzzle_lines[row].strip().split(",")
            for col in range(len(raw_squares)):
                sq = Square(row, col,self)
                val = int(raw_squares[col])    
                if val:
                    sq.val = val
                self.squares.append(sq)

    def _num_in_row(self,num,row):
        """Returns True if the number is in the provided row, False otherwise"""
        squares = filter(lambda sq: sq.row == row, self.squares)
        return any(sq.val == num for sq in squares)
    
    def _num_in_col(self,num,col):
        """Returns True is the number is in the provided column, False otherwise"""
        squares = filter(lambda sq: sq.col == col, self.squares)
        return any(sq.val == num for sq in squares)
    
    def _num_in_section(self,num,row,col):
        """Returns True if num is in the section containing the provided coordinates, False
        otherwise"""        
        rmin,rmax = get_section_coords(row)
        cmin,cmax = get_section_coords(col)
        squares = filter(lambda sq: (rmin <= sq.row <= rmax) and (cmin <= sq.col <= cmax),self.squares)
        return any(sq.val == num for sq in squares)

    def num_allowed(self,num,sq):
        """Determine is number is technically allowed in square"""        
        if self._num_in_row(num,sq.row) or self._num_in_col(num,sq.col) or self._num_in_section(num,sq.row,sq.col):
            return False
        else:
            return True

    def is_only_place_in_section(self,num,square):
        """Returns True if the provided square is the only place the provided number can be placed
        in the section of the provided square, False otherwise"""
        squares = filter(lambda sq: (square.rmin <= sq.row <= square.rmax and square.cmin <= sq.col
            <= square.cmax) and (sq != square),self.squares)
        if not any(num in sq.opts for sq in squares) and (num in square.opts):
            return True
        else:
            return False 
    
    def is_only_place_in_row(self,num,square):
        """Returns True if the provided square is the only place the provided number can be placed
        in the row of the provided square, False otherwise"""
        squares = filter(lambda sq: sq.row == square.row and sq != square,self.squares)
        if not any(num in sq.opts for sq in squares) and (num in square.opts):
            return True
        else:
            return False
    
    def is_only_place_in_col(self,num,square):
        """Returns True if the provided square is the only place the provided number can be placed
        in the column of the provided square, False otherwise"""
        squares = filter(lambda sq: sq.col == square.col and sq != square,self.squares)
        if not any(num in sq.opts for sq in squares) and (num in square.opts):
            return True
        else:
            return False
    
    def set_vals(self):
        """Sets any values that are guaranteed to be correct"""
        for sq in self.squares:
            # If there is only one option, thats the value
            if len(sq.opts) == 1:
                sq.val = sq.opts.pop()
            # If this square is the only place for num in row, column, or section then num must go
            # in this square
            for num in self.nums:
                if self.is_only_place_in_section(num,sq) or self.is_only_place_in_row(num,sq) or self.is_only_place_in_col(num,sq):
                    sq.val = num
    
    def eliminate_opts(self):
        """Do what we can to eliminate some options"""
        for sect in self.get_squares_by_section():
            for num in self.nums:
                poss_sqs = filter(lambda sq: num in sq.opts,sect)
                if poss_sqs:
                    if all(sq.row == poss_sqs[0].row for sq in poss_sqs):
                        for sq in filter(lambda sq: sq not in sect,self.get_row(poss_sqs[0].row)):
                            try:
                                sq.opts.remove(num)
                            except ValueError:
                                pass
                    elif all(sq.col == poss_sqs[0].col for sq in poss_sqs):
                        for sq in filter(lambda sq: sq not in sect,self.get_col(poss_sqs[0].col)):
                            try: 
                                sq.opts.remove(num)
                            except ValueError:
                                pass
    def guess(self):
        """Pick an unsolved square with the least number of options and set a random option to the
        value"""
        unsolved_sqs = filter(lambda sq: sq.val == 0,self.squares)
        sq = sorted(unsolved_sqs,cmp=lambda x,y: x-y,key=lambda sq: len(sq.opts))[0]
        opt = random.choice(sq.opts)
        sq.val = opt
        self.guessed = True

    def get_square_opts(self):
        """Get all possible options for every square on the board, without doing any intelligent
        elimination other than what is strictly not allowed"""
        for sq in self.squares:
            sq.opts = []
            for num in self.nums:
                if not sq.val and self.num_allowed(num,sq):
                    sq.opts.append(num)
    
    def get_square(self,row,col):
        """Get square by row and column. Remember to zero index!"""
        return self.squares[9*row+col]

    def get_row(self,row):
        """Get the specified row of squares"""
        return filter(lambda sq: sq.row == row,self.squares)

    def get_col(self,col):
        """Get the specified column of squares"""
        return filter(lambda sq: sq.col == col, self.squares)

    def get_squares_by_section(self):
        """Returns a list of squares grouped by section, sorted left-to-right, top-down"""
        sects = []
        for row in range(0,9,3):
            for col in range(0,9,3):
                sect = filter(lambda sq: row <= sq.row < row+3 and col <= sq.col < col+3,self.squares)
                sects.append(sect)
        return sects

    def has_conflict(self):
        for sq in self.squares:
            if len(sq.opts) == 0 and sq.val == 0:
                print "WE HAVE A CONFLICT"
                print "SQUARE (%d, %d)"%(sq.row,sq.col)
                self.show()
                return True
        return False
                
                    
    def is_solved(self):
        if all(sq.val != 0 for sq in self.squares):
            self.solved = True
        else:
            self.solved = False
    
    def show(self):
        """Print the current grid state to stdout"""
        print "-"*25
        row_counter = 0
        for i in range(0,73,9):
            row = "| %d %d %d | %d %d %d | %d %d %d |"%tuple(self.squares[i+j].val for j in self.cols)
            #row = "| "+" | ".join([str(self.squares[i+j].val) for j in self.cols])+" |"
            print row
            if row_counter == 2 or row_counter == 5 or row_counter == 8:
                print "-"*25
            row_counter += 1

def main():
    parser = argparse.ArgumentParser(description="""A simple program to solve sudoku puzzles""")
    parser.add_argument('puzzle_file',type=str,help="""The file containing the initial, unsolved
    puzzle""")
    args = parser.parse_args()

    if not os.path.isfile(args.puzzle_file):
        print "The file you specified does not exist"
        quit()
    
    # Load the puzzle
    with open(args.puzzle_file,'r') as pfile:
        grid = Grid(pfile.readlines())

    print "Initial Puzzle: "
    grid.show()
    c = 1
    # Start by getting all possible options for each square
    grid.get_square_opts()
    no_changes = 0
    while not grid.solved: 
        # Make a list of the old values before any changes
        old_vals = [sq.val for sq in grid.squares]
        print "Iteration ",c
        # Set any values that are certain
        grid.set_vals() 
        # Do what we can to eliminate some options 
        grid.eliminate_opts()
        # Get the new list of values 
        new_vals = [sq.val for sq in grid.squares]
        # Increment the amount of times nothing has changed
        if old_vals == new_vals:
            no_changes +=1
       
        if no_changes > 1 and grid.guessed and grid.has_conflict():
            print "WE HAVE ENCOUNTERED A CONFLICT FROM A GUESS AND ARE UNWINDING THE CONSEQUENCES"
            # We've already guessed and it created a conflict, so we need to unwind the all the
            # consequences of that guess
            for sq in first_unsolved_sqs:
                sq.val = 0
            grid.guessed = False
        elif no_changes > 1 and grid.guessed and not grid.has_conflict():
            print "WE ARE GUESSING AN ADDITIONAL TIME"
            # We've guessed at least once but there isn't a conflict yet, so we just need to guess again
            # without touching the list of unsolved squares from the first guess
            grid.guess()
            no_changes = 0
        elif no_changes > 1 and not grid.guessed:
            print "WE ARE GUESSING FOR THE FIRST TIME"
            # At this point we have exhausted our logic and we need to guess. Store all the unsolved
            # squares at the time of the guess
            first_unsolved_sqs = filter(lambda sq: sq.val == 0,grid.squares)
            # Now we guess
            grid.guess()
            no_changes = 0
        grid.show()
        grid.is_solved()
        c += 1
    print "Congratulations! Puzzle solved in %d iterations! Here is the solution: "%c
    grid.show() 

        
if __name__ == '__main__':
    main()
