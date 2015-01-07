''' Script for solving http://gameaboutsquares.com/ puzzles. '''
import time, random
# use symbols for directions and numbers for colors to avoid conflicts (0 - empty field)
# 'symbol': (dx, dy)
direction = { '.': (0, +1), '^': (0, -1), '>': (+1, 0), '<': (-1, 0) }
colors = {1: 'Red', 2: 'Blue', 3: 'Navy'}
class Square:
    def __init__(self, color, x, y, dir):
        self.color = color
        self.x = x
        self.y = y
        self.dir = dir
    def __repr__(self):
        return str('Square(' + str(self.color) + ',' + str(self.x) + ',' +
            str(self.y) + ',"' + self.dir + '")')
    def __hash__(self):
        return hash((self.color, self.x, self.y, self.dir))
        # (self.color << 24) + ((self.x & 0xff) << 16) + ((self.y & 0xff) << 8) + ord(self.dir)
    def __eq__(self, other):
        return (self.color == other.color and self.x == other.x and 
            self.y == other.y and self.dir == other.dir)
    def __ne__(self, other):
        return not self==other


class puzzle_31:
    # first row should be full length, it's used to determine the width of a core field
    field = [
        [0, 0,'.',0, 0],
        [0,'>',0, 0, 0],
        [2, 0, 1,'<',3],
        [], # nothing interesting in this row
        [0, 0,'^',0, 0]
    ]
    # it should be hashable, so use tuple
    squares = ( Square(1, 3, 2, '<'),
        Square(2, 2, 0, '.'),
        Square(3, 1, 1, '>') )

class puzzle_32:
    field = [
        [0,'.',1, 0, 0],
        [2, 0, 0, 0, 0],
        ['>',0,0, 0 ,0],
        [0, 0, 0, 0,'<'],
        [0,'^',0, 0, 0]
    ]
    squares = ( Square(1, 0, 2, '>'),
        Square(2, 1, 0, '.'),
        Square(3, 4, 1, '.') )

class puzzle_33:
    field = (
        (2, 1, 3, 0, 0),
        (0,'.',0, 0,'<'),
        (),
        (0,'>',0,'^',0),
    )
    squares = ( Square(1, 3, 3, '^'),
        Square(2, 1, 1, '.'),
        Square(3, 1, 3, '>') )

def is_inside(field, sq):
    ''' Is a square inside an original field? Positive answer means
        that the square could reach its final position, or change direction. '''
    return sq.y >= 0 and sq.y < len(field) and sq.x >= 0 and sq.x < len(field[sq.y])

def is_solved(field, squares):
    for sq in squares:
        # check if square is in a final position only if the position is present in the field
        if ((not is_inside(field, sq) or
            field[sq.y][sq.x] != sq.color) and
            any(f == sq.color for row in field for f in row)):
            return False
    return True

def is_square(field, squares, pos):
    ''' Is there a square at a given position? Also, return its color. '''
    for sq in squares:
        if pos.x == sq.x and pos.y == sq.y:
            return (True, sq.color)
    return (False, 0)

def update_dirs(field, squares):
    ''' Update directions of squares after move: 
        change square direction if it's on a special field.
        Tuples are immutable, so create a new one. '''
    return tuple( Square(sq.color, sq.x, sq.y, field[sq.y][sq.x])
        if (is_inside(field, sq) and field[sq.y][sq.x] in direction)
        else Square(sq.color, sq.x, sq.y, sq.dir) for sq in squares )

def move(field, squares, sq):
    ''' Move a square and squares behind it, return a new state '''
    to_move = []
    # create a copy of square, otherwise when we change it original object will change
    pos = Square(sq.color, sq.x, sq.y, sq.dir)
    incr = direction[sq.dir]
    # check if there are more squares behind the one to be moved
    more = True
    color = sq.color
    while more:
        to_move += [color]
        pos.x += incr[0]
        pos.y += incr[1]
        (more, color) = is_square(field, squares, pos)
    # actually move the squares (squares that don't move are copied verbatim)
    temp = tuple( Square(sq.color, sq.x + incr[0], sq.y + incr[1], sq.dir)
        if sq.color in to_move else Square(sq.color, sq.x, sq.y, sq.dir)
        for sq in squares )
    # update squares directions
    return update_dirs(field, temp)

def is_valid(field, squares):
    ''' State is valid if squares are not too far from the core field.
    '''
    # Squares can't go beyond the core field farther than number of squares (if they push each other).
    border = len(squares)
    # Strict conditions are removed because they can sometimes miss a correct solution,
    # but a puzzle is solved slower.
    for sq in squares:
        if (# sq.x < 0 and sq.dir == '<' or
            # sq.y < 0 and sq.dir == '^' or
            # sq.x >= len(field[0]) and sq.dir == '>' or
            # sq.y >= len(field) and sq.dir == '.' or
            sq.x <= -border or sq.y <= -border or
            sq.x > len(field[0]) + border or sq.y > len(field) + border):
            return False
    return True

def solve(puzzle, depth = 50):
    ''' Solve a puzzle '''
    start_time = time.time()
    # puzzle.squares is an initial state (so empty path),
    # each state should be immutable to be hashable, so a tuple is used instead of a list
    sol_tree = { puzzle.squares : [] }
    # level = [ (puzzle.squares, []) ]
    print sol_tree
    for i in range(0, depth):
        print i, ':', len(sol_tree), time.time()-start_time
        # next_level = []
        for (squares, path) in sol_tree.items(): # items() creates a copy, so iteration is not influenced by added items
        # for j in level: 
            # (squares, path) = j[:]
            if len(path) < i: # already processed
                continue
            if is_solved(puzzle.field, squares):
                return path
            for sq in squares:
                # generate new move for given square
                next = move(puzzle.field, squares, sq)
                # if state is good and new, add to solution dict
                if is_valid(puzzle.field, next):
                    if not sol_tree.has_key(next):
                        sol_tree[next] = path + [sq.color]
                        # next_level.append((next, path + [sq.color]))
        # level = next_level
    return 'Could not solve with depth ' + str(depth)

def test_hashes():
    for x in range(-10, 15):
        for y in range(-10, 15):
            for color in range(1, 4):
                for dir in ('.', '^', '<', '>'):
                    if Square(color, x, y, dir) != Square.fromhash(Square(color, x, y, dir).__hash__()):
                        print Square(color, x, y, dir), '!=', Square.fromhash(Square(color, x, y, dir).__hash__())

def rand_square():
    rand_square.counter += 1
    return Square(1 + rand_square.counter % 3, 
        2 + rand_square.counter % 7193, 
        3 + rand_square.counter % 4793, 
        '.<>^'[rand_square.counter % 4])
    # return Square(random.randint(1,3), random.randint(0, 10), random.randint(0, 10), random.choice('.<>^'))
rand_square.counter = 0

def test_hash_speed():
    d = {}
    start_time = time.time()
    for i in range(0, 1000000):
        s = []
        for j in range(0, 3):
            s.append(rand_square())
        d[tuple(s)] = ['path']
    print 'Filled dictionary in', time.time()-start_time, 'sec'
    print 'Size', len(d)
    start_time = time.time()
    found = 0
    for i in range(0, 1000000):
        s = []
        for j in range(0, 3):
            s.append(rand_square())
        if d.has_key(tuple(s)):
            found += 1
    print 'Searched dictionary in', time.time()-start_time, 'sec'
    print 'Found', found, 'keys'
    
def test_move():
    print move(puzzle_31.field, (Square(1, 2, 0, '.'), Square(2, 2, 1, '>'), Square(3, 3, 2, '<')), Square(1, 2, 0, '.'))
                        
# test_hashes()
# test_move()
# test_hash_speed()

res = solve(puzzle_32)
# print res
print 'Solution:', [colors[m] for m in res]
