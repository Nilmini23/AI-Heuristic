from tkinter import Frame, Label, CENTER
import random
import logic
import constants as c
import helpers as h
import sys
import AI_heuristics_edited as AI
import pandas as pd
import time

sys.setrecursionlimit(10**6)

def gen():
    return random.randint(0, c.GRID_LEN - 1)

class GameGrid(Frame):
    """Method to close the game window"""
    def close_game(self):
        self.destroy()
        self.master.destroy()

    def __init__(self, draw=True, max_depth=2):
        self.max_depth = max_depth
        self.draw = draw
        Frame.__init__(self)
        self.game_over = False
        self.start = True
        self.points = 0

        self.grid()
        self.master.title('2048')

        self.done = False
        self.commands = {
            c.KEY_UP: logic.up,
            c.KEY_DOWN: logic.down,
            c.KEY_LEFT: logic.left,
            c.KEY_RIGHT: logic.right
        }

        self.grid_cells = []
        self.init_grid()
        self.matrix = logic.new_game(c.GRID_LEN)
        self.history_matrixs = []
        self.update_grid_cells()
        self.update_view()

    def init_grid(self):
        background = Frame(self, bg=c.BACKGROUND_COLOR_GAME, width=c.SIZE, height=c.SIZE)
        background.grid()
        for i in range(c.GRID_LEN):
            grid_row = []
            for j in range(c.GRID_LEN):
                cell = Frame(background, bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                             width=c.SIZE / c.GRID_LEN, height=c.SIZE / c.GRID_LEN)
                cell.grid(row=i, column=j, padx=c.GRID_PADDING, pady=c.GRID_PADDING)
                t = Label(master=cell, text="", bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                          justify=CENTER, font=c.FONT, width=5, height=2)
                t.grid()
                grid_row.append(t)
            self.grid_cells.append(grid_row)

    def update_grid_cells(self):
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(
                        text=str(new_number),
                        bg=c.BACKGROUND_COLOR_DICT[new_number],
                        fg=c.CELL_COLOR_DICT[new_number]
                    )

    def update_view(self):
        if not self.game_over and self.start:
            self.start = False
            self.update_grid_cells()
            if self.draw:
                self.update()

        elif not self.game_over:
            key = AI.AI_play(self.matrix, self.max_depth)
            self.matrix, done, points = self.commands[key](self.matrix)
            self.points += points
            if done:
                self.done = True
                self.matrix = logic.add_two(self.matrix)
                self.history_matrixs.append(self.matrix)
                self.update_grid_cells()

                state = logic.game_state(self.matrix)
                if state == 'win':
                    h.print_results_board(self.grid_cells, self.points, win=True)
                    self.game_over = True
                    if self.draw:
                        self.update()
                        time.sleep(1)  # display result for 1 second
                        self.destroy()
                elif state == 'lose':
                    h.print_results_board(self.grid_cells, self.points, win=False)
                    self.game_over = True
                    if self.draw:
                        self.update()
                        time.sleep(1)
                        self.destroy()

                if self.draw and not self.game_over:
                    self.update()

        if not self.game_over:
            self.update_view()


# ====================== MAIN FUNCTION ======================
def main():
    draw = True
    sims = 20
    max_depth = -1

    heuristics = ["empty_tile", "max_tile", "monotonicity", "smoothness", "combined"]
    results_dict = {}

    print("Max Depth =", max_depth)

    for heuristic in heuristics:
        AI.CURRENT_HEURISTIC = heuristic
        print(f"\nTesting heuristic: {heuristic}")
        scores = []

        for i in range(sims):
            print(f"Trial {i+1}")
            game_grid = GameGrid(draw, max_depth=max_depth)

            while not game_grid.game_over:
                game_grid.update()
           # game_grid.master.mainloop()  # Wait until game finishes
            scores.append(game_grid.points)

        results_dict[heuristic] = scores

    # Create a DataFrame for results
    sim_results = pd.DataFrame(results_dict)
    sim_results.index = [f"Trial {i+1}" for i in range(sims)]

    print("\n---Results Table---")
    print(sim_results)
    sim_results.to_csv("heuristic_results_table.csv")

    print("\n---Mean Scores---")
    print(sim_results.mean())


if __name__ == "__main__":
    main()
