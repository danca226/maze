# python 3.6
from tkinter import *
from enum import Enum
from random import choice
from threading import Thread
from time import sleep
import sys
from collections import deque

# maze configuration
ROWS = 40
COLS = 60
SIZE = 10
MARGIN = SIZE / 2
CANVAS_WIDTH = COLS*SIZE + SIZE
CANVAS_HEIGHT = ROWS*SIZE + SIZE
BORDER = 1

# search states
NOTVISITED = 0
VISITING = 1
BACKTRACKED = 2

# up, down, right, left
DIRS = ((-1, 0), (1, 0), (0, 1), (0, -1))


class Solution:
    def __init__(self, m, gr, gc):
        self.m = m
        self.goal_r = gr
        self.goal_c = gc
        self.states = [[NOTVISITED for r in range(COLS)] for c in range(ROWS)]
        self.processed = []

    def is_solved(self):
        return self.states[self.goal_r][self.goal_c] == VISITING

    def visit(self, r, c):
        self.states[r][c] = VISITING
        self.processed.append((r, c))

    def next_cells(self, r, c):
        adj = self.m[r][c]['adj']
        return list(filter(lambda rc: self.states[rc[0]][rc[1]] == NOTVISITED, adj))

    def backtrack(self, r, c):
        self.states[r][c] = BACKTRACKED
        self.processed.append((r, c))


class MazeUI:
    def __init__(self):
        self.init_ui()

    def init_ui(self):
        self.window = Tk()
        self.window.title('maze')
        self.window.resizable(False, False)

        fm = Frame(self.window)
        Button(fm, text="generate", command=self.btn_generate).pack(side=LEFT)
        Button(fm, text="dfs", command=self.btn_dfs).pack(side=LEFT)
        Button(fm, text="bfs", command=self.btn_bfs).pack(side=LEFT)
        fm.pack(fill=BOTH, expand=YES)

        self.canvas = Canvas(self.window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background="white", bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack()

        self.btn_generate()

        self.window.mainloop()

    def btn_generate(self):
        self.maze = [[{'visited': False, 'adj': []} for r in range(COLS)] for c in range(ROWS)]
        self.create_maze(0, 0)
        self.draw_maze()

    def btn_dfs(self):
        sys.setrecursionlimit(ROWS*COLS)

        def async():
            solution = Solution(self.maze, ROWS-1, COLS-1)
            self.solve_dfs(0, 0, solution)
        t = Thread(target=async).start()

    def btn_bfs(self):
        def async():
            solution = Solution(self.maze, ROWS-1, COLS-1)
            self.solve_bfs(0, 0, solution)
        t = Thread(target=async).start()

    def create_maze(self, r, c):
        self.maze[r][c]['visited'] = True
        stack = []

        while True:
            adj = []
            for d in DIRS:
                nr, nc = r+d[0], c+d[1]
                if 0 <= nr < len(self.maze) and 0 <= nc < len(self.maze[0]) and not self.maze[nr][nc]['visited']:
                    adj.append((nr, nc))

            if adj:
                nr, nc = choice(adj)
                self.maze[r][c]['adj'].append((nr, nc))
                stack.append((r, c))
                r, c = nr, nc
                self.maze[r][c]['visited'] = True
            elif not stack:
                break
            else:
                r, c = stack.pop()

    def draw_maze(self):
        # clear canvas
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill='white')

        # punch out path
        for r in range(ROWS):
            for c in range(COLS):
                for ar, ac in self.maze[r][c]['adj']:
                    y0 = min(r, ar)*SIZE+BORDER+MARGIN
                    x0 = min(c, ac)*SIZE+BORDER+MARGIN
                    y1 = max(r, ar)*SIZE+(SIZE-BORDER)+MARGIN
                    x1 = max(c, ac)*SIZE+(SIZE-BORDER)+MARGIN
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="black", outline='')

    def draw_solution(self, solution):
        colors = {VISITING: 'yellow', NOTVISITED: 'black', BACKTRACKED: 'red'}

        # only draw whats changed since last iteration
        for r, c in solution.processed:
            x0 = c*SIZE+MARGIN+BORDER+1
            y0 = r*SIZE+MARGIN+BORDER+1
            x1 = c*SIZE+MARGIN+SIZE-BORDER-1
            y1 = r*SIZE+MARGIN+SIZE-BORDER-1
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=colors[solution.states[r][c]], outline='')

        # clear processed nodes for next iteration
        solution.processed.clear()
        sleep(0.001)

    def solve_dfs(self, r, c, solution):
        solution.visit(r, c)
        self.draw_solution(solution)

        if solution.is_solved():
            return

        for nr, nc in solution.next_cells(r, c):
            self.solve_dfs(nr, nc, solution)
            if(solution.is_solved()):
                return

        solution.backtrack(r, c)
        self.draw_solution(solution)

    def solve_bfs(self, r, c, solution):
        parents = [[None for r in range(COLS)] for c in range(ROWS)]

        q = deque()
        q.append((r, c))

        while q:
            r, c = q.popleft()
            solution.visit(r, c)
            self.draw_solution(solution)

            if solution.is_solved():
                # trace path backwards and draw final solution
                solution.processed = [(r, c)]
                while parents[r][c]:
                    solution.states[r][c] = BACKTRACKED
                    solution.processed.append(parents[r][c])
                    r, c = parents[r][c]

                solution.states[0][0] = BACKTRACKED
                solution.processed.append((0, 0))

                self.draw_solution(solution)
                return

            for nr, nc in solution.next_cells(r, c):
                q.append((nr, nc))
                parents[nr][nc] = (r, c)


if __name__ == '__main__':
    MazeUI()

