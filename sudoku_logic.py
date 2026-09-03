import copy
import random

SIZE = 9
EMPTY = 0

# Difficulty levels with clue counts
DIFFICULTY_EASY = 'easy'
DIFFICULTY_MEDIUM = 'medium'
DIFFICULTY_HARD = 'hard'

DIFFICULTY_CLUES = {
    DIFFICULTY_EASY: 50,
    DIFFICULTY_MEDIUM: 40,
    DIFFICULTY_HARD: 25,
}

DEFAULT_DIFFICULTY = DIFFICULTY_MEDIUM

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    # Remove cells while ensuring the resulting puzzle has exactly one solution.
    cells_to_remove = SIZE * SIZE - clues

    # We'll attempt deterministic passes over shuffled cell positions and reshuffle
    # when a full pass makes no progress. This reduces flakiness versus a fixed
    # random-attempt budget.
    positions = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    attempts = cells_to_remove

    # Number of times we will reshuffle and retry before giving up.
    # Keep modest to avoid long runs; generate_puzzle will regenerate the board
    # if this pass cannot reach the target clue count.
    reshuffle_limit = 60
    reshuffles = 0

    while attempts > 0 and reshuffles < reshuffle_limit:
        random.shuffle(positions)
        made_progress = False
        for row, col in positions:
            if attempts <= 0:
                break
            if board[row][col] == EMPTY:
                continue
            saved = board[row][col]
            board[row][col] = EMPTY
            # If removal causes multiple solutions, revert it
            if count_solutions(board, limit=2) != 1:
                board[row][col] = saved
            else:
                attempts -= 1
                made_progress = True
        if not made_progress:
            reshuffles += 1
            continue
    # If we exit loop without achieving attempts==0, try one final exhaustive pass
    # over all positions just in case.
    if attempts > 0:
        for row, col in positions:
            if attempts <= 0:
                break
            if board[row][col] == EMPTY:
                continue
            saved = board[row][col]
            board[row][col] = EMPTY
            if count_solutions(board, limit=2) != 1:
                board[row][col] = saved
            else:
                attempts -= 1

def generate_puzzle(clues=None, difficulty=None):
    """Generate a Sudoku puzzle with exactly one solution.
    
    Args:
        clues: Number of clues to leave on the board. If None, use difficulty.
        difficulty: One of 'easy', 'medium', 'hard'. Overridden by clues if provided.
                   Defaults to 'medium' if neither is specified.
    
    Returns:
        (puzzle, solution) tuple where puzzle has empty cells (0) and solution is complete.
    """
    if clues is None:
        if difficulty is None:
            difficulty = DEFAULT_DIFFICULTY
        if difficulty not in DIFFICULTY_CLUES:
            raise ValueError(f"Invalid difficulty: {difficulty}")
        clues = DIFFICULTY_CLUES[difficulty]
    
    # Some clue targets (especially low-clue hard puzzles) can fail to reach
    # the exact count with a single removal pass due to uniqueness constraints.
    # Retry full generation a bounded number of times to keep behavior reliable.
    max_generations = 20
    for attempt in range(max_generations):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        remove_cells(board, clues)
        puzzle = deep_copy(board)
        clue_count = sum(1 for row in puzzle for cell in row if cell != EMPTY)
        if clue_count == clues:
            return puzzle, solution
    # If we reached here, generation failed to meet the exact clue count;
    # raise an error rather than silently returning an incorrect puzzle.
    raise RuntimeError(f"Failed to generate puzzle with exactly {clues} clues after {max_generations} attempts")


def count_solutions(board, limit=2):
    """Count number of solutions for a given board up to `limit`.

    Uses backtracking with a simple minimum-remaining-values heuristic to keep
    the search reasonably efficient. Stops early once the count reaches
    `limit` and returns that (or higher) value.
    """
    board_copy = deep_copy(board)

    def solve():
        # Find empty cell with fewest candidates (MRV heuristic)
        min_pos = None
        min_cands = None
        for r in range(SIZE):
            for c in range(SIZE):
                if board_copy[r][c] == EMPTY:
                    cands = []
                    for n in range(1, SIZE + 1):
                        if is_safe(board_copy, r, c, n):
                            cands.append(n)
                    if not cands:
                        return 0
                    if min_cands is None or len(cands) < len(min_cands):
                        min_cands = cands
                        min_pos = (r, c)
        # No empty cells, found a valid solution
        if min_pos is None:
            return 1

        r, c = min_pos
        total = 0
        for n in min_cands:
            board_copy[r][c] = n
            total += solve()
            board_copy[r][c] = EMPTY
            if total >= limit:
                return total
        return total

    return solve()
