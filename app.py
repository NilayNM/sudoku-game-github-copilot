from flask import Flask, render_template, jsonify, request
import random
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    # Support both 'clues' (backward compatibility) and 'difficulty' parameters
    clues = request.args.get('clues', type=int)
    difficulty = request.args.get('difficulty', default=None)
    
    # If clues is provided explicitly, use it; otherwise use difficulty
    if clues is not None:
        puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
        # Infer difficulty from clue count for response (best guess)
        inferred_difficulty = None
        for diff, clue_count in sudoku_logic.DIFFICULTY_CLUES.items():
            if clues == clue_count:
                inferred_difficulty = diff
                break
    else:
        # Use difficulty (default to 'medium' if not specified)
        if difficulty is None:
            difficulty = sudoku_logic.DEFAULT_DIFFICULTY
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
        inferred_difficulty = difficulty
    
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle, 'difficulty': inferred_difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint')
def hint():
    """Return a single correct cell (row, col, value) for the current puzzle.

    The full solution is NOT returned. This endpoint picks one currently-empty
    cell from the stored puzzle and returns the correct value from the server-side
    solution so the client can fill a single hint cell without learning the whole board.
    """
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400

    empty_positions = [(r, c) for r in range(sudoku_logic.SIZE)
                       for c in range(sudoku_logic.SIZE)
                       if puzzle[r][c] == sudoku_logic.EMPTY]
    if not empty_positions:
        return jsonify({'error': 'No empty cells available'}), 400

    r, c = random.choice(empty_positions)
    return jsonify({'row': r, 'col': c, 'value': solution[r][c]})

if __name__ == '__main__':
    app.run(debug=True)