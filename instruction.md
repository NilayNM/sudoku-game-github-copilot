# Project-level instructions for GitHub Copilot

- Project type: Flask-based Sudoku game with HTML, CSS, and vanilla JavaScript.
- Preserve existing functionality and backward compatibility for all changes.
- Sudoku generation must remain mathematically valid: every generated puzzle must have exactly one solution.
- Difficulty levels and clue counts (do not change): Easy = 50 clues, Medium = 40 clues, Hard = 25 clues.
- Prefilled/clue cells must remain locked on the client (non-editable) and not be alterable by UI.
- Keep backend logic in Flask/Python and frontend behavior in HTML/CSS/JavaScript — avoid moving core logic across the boundary.
- Prefer small, modular, reusable changes over broad refactors unless explicitly requested.
- Maintain clear error handling and add concise, readable comments where they aid understanding.
- Add or update automated tests for any functional changes; run the full `pytest` suite and ensure it passes before committing.
- Do not add optional or extraneous features unless the request explicitly asks for them.

DO NOT MODIFY any existing application code for this task. This file (`instruction.md`) is the only file you should create when asked to add project-level guidance.
