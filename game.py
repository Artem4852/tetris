import pygame
import random
import time

shapes = ["L", "S", "LR", "LL", "ZR", "ZL", "C"]
shapes_2d = {
    "L": [[0, 0], [0, 1], [0, 2], [0, 3]],
    "S": [[0, 0], [0, 1], [1, 0], [1, 1]],
    "LR": [[0, 0], [0, 1], [0, 2], [1, 2]],
    "LL": [[1, 0], [1, 1], [1, 2], [0, 2]],
    "ZR": [[1, 0], [1, 1], [0, 1], [0, 2]],
    "ZL": [[0, 0], [0, 1], [1, 1], [1, 2]],
    "C": [[0, 0], [1, 0], [1, 1], [2, 0]]
}

colors = {
    "red": (245, 45, 30),
    "white": (246, 237, 237),
    "black": (27, 27, 27),
    "grey": (180, 180, 180)
}

class Block:
    def __init__(self, shape):
        self.shape = shape
        self.shape_idx = shapes.index(shape)
        self.x = 5
        self.y = 0
        self.rotation = 0
        self.shape_2d = shapes_2d[shape]
        self.center_x = int(sum([p[0] for p in self.shape_2d]) / len(self.shape_2d))
        self.center_y = int(sum([p[1] for p in self.shape_2d]) / len(self.shape_2d))
        self.last_moved = time.time()
        self.interval = 1
    
    def rotate(self, board):
        moved_shape = [[p[0]-self.center_x, p[1]-self.center_y] for p in self.shape_2d]
        rotated_shape = [[p[1], -p[0]] for p in moved_shape]
        new_shape = [[p[0]+self.center_x, p[1]+self.center_y] for p in rotated_shape]
        if self.x + min([p[0] for p in new_shape]) >= 0 and self.x + max([p[0] for p in new_shape]) <= 9 and self.y + max([p[1] for p in new_shape]) <= 19 and not self.check_collision(board, new_shape):
            self.shape_2d = new_shape
            self.rotation += 90
            self.rotation %= 360
    
    def move(self, x, board):
        if self.x + x + min([p[0] for p in self.shape_2d]) >= 0 and self.x + x + max([p[0] for p in self.shape_2d]) <= 9:
            self.x += x
        if self.check_collision(board):
            self.x -= x

    def move_down(self):
        if time.time() - self.last_moved > self.interval:
            self.y += 1
            self.last_moved = time.time()
    
    def check_collision(self, board, shape=None):
        if not shape: shape = self.shape_2d
        for x, y in shape:
            try: 
                if self.y + y == 19 or board[self.y+y+1][self.x+x]: return True
            except: return True

class Game:
    def __init__(self, cell_size=30):
        pygame.init()
        self.cell_size = cell_size
        self.screen = pygame.display.set_mode((cell_size*10, cell_size*20))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.restart()
    
    def restart(self):
        self.score = 0
        self.board = [[0 for _ in range(10)] for _ in range(20)]
        self.current_block = self.new_block()
        self.is_new_block = False

        self.reward = 0

    def new_block(self):
        self.is_new_block = True
        return Block(random.choice(shapes))
    
    def merge_block(self):
        if not self.current_block.check_collision(self.board):
            return
        holes = self.check_holes()
        for x, y in self.current_block.shape_2d:
            try: self.board[self.current_block.y+y][self.current_block.x+x] = 1
            except: print(self.board, x, y)
        holes_after = self.check_holes()
        self.reward += (holes - holes_after) * 100
        if holes == holes_after: self.reward += 20
        self.current_block = self.new_block()

    def check_rows(self):
        unavailable = self.check_holes()
        for y, row in enumerate(self.board):
            if all(row):
                self.board.pop(y)
                self.board.insert(0, [0 for _ in range(10)])
                self.score += 1
                self.reward += 100
        unavailable_after = self.check_holes()
        self.reward += (unavailable - unavailable_after) * 100

    def check_holes(self):
        holes = 0
        for x in range(len(self.board)):
            for y in range(len(self.board[0])):
                if self.board[x][y] == 0 or x == 19: continue
                elif self.board[x+1][y] == 0: holes += 1
        return holes

    def lost(self):
        for cell in self.board[1]:
            if cell:
                return True
        return False
    
    def handle_input(self):
        self.current_block.interval = 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                pressed = event.key
                if pressed == pygame.K_r:
                    self.current_block.rotate(self.board)
                if pressed == pygame.K_c:
                    self.restart()
                if pressed in [pygame.K_LEFT, pygame.K_a]:
                    self.current_block.move(-1, self.board)
                if pressed in [pygame.K_RIGHT, pygame.K_d]:
                    self.current_block.move(1, self.board)
                if pressed == pygame.K_SPACE:
                    self.is_new_block = False
        
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            self.current_block.interval = 0.1
        elif pressed[pygame.K_SPACE] and self.is_new_block == False:
            self.current_block.interval = 0.01
    
    def draw_grid(self):
        for x in range(0, 10):
            pygame.draw.line(self.screen, colors["grey"], (x*self.cell_size, 0), (x*self.cell_size, 20*self.cell_size))
        for y in range(0, 20):
            pygame.draw.line(self.screen, colors["grey"], (0, y*self.cell_size), (10*self.cell_size, y*self.cell_size))

    def draw(self, moves=[0, 0], games=0, reward=0):
        self.screen.fill(colors["white"])
        self.draw_grid()
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, colors["red"], (x*self.cell_size, y*self.cell_size, self.cell_size, self.cell_size))
        for x, y in self.current_block.shape_2d:
            pygame.draw.rect(self.screen, colors["red"], ((x+self.current_block.x)*self.cell_size, (y+self.current_block.y)*self.cell_size, self.cell_size, self.cell_size))
        if moves[0]: pygame.display.set_caption(f"Tetris | Games: {games} | Reward: {reward} | Moves: {moves[0]}/{moves[1]}")
        else: pygame.display.set_caption(f"Tetris | Score: {self.score}")
        pygame.display.flip()

    def get_state(self):
        state = []
        state.append(self.current_block.shape_idx)
        state.append(self.current_block.x)
        state.append(self.current_block.y)
        state.append(self.current_block.rotation)
        for row in self.board:
            state.extend(row)
        for x in range(10):
            for y in range(20):
                if self.board[y][x]:
                    state.append(y)
                    break
            else:
                state.append(20)
        return state

    def step(self, action):
        self.reward = 0
        if action == 0:
            self.current_block.move(-1, self.board)
        if action == 1:
            self.current_block.move(1, self.board)
        if action == 2:
            self.current_block.rotate(self.board)
        self.current_block.interval = 0.01
        self.current_block.move_down()
        self.merge_block()
        self.check_rows()
        if self.lost():
            self.reward = -1000
        return self.get_state(), self.reward, self.lost()
    
    def run(self):
        while True:
            self.clock.tick(60)
            self.reward = 0
            self.handle_input()
            self.current_block.move_down()
            self.merge_block()
            self.check_rows()
            if self.lost():
                self.restart()
            self.draw()


if __name__ == '__main__':
    game = Game(30)
    game.run()