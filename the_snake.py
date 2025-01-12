from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

GRID_CENTER_X = GRID_WIDTH // 2
GRID_CENTER_Y = GRID_HEIGHT // 2

ALL_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(0, GRID_WIDTH)
    for y in range(0, GRID_HEIGHT)
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

NEXT_DIRECTION = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
    (pygame.K_LEFT, DOWN): LEFT
}

# Цвета
BOARD_BACKGROUND_COLOR = (0, 64, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
BAD_APPLE_COLOR = (200, 172, 64)
STONE_COLOR = (172, 172, 172)
SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (0, 128, 0)
DEFAULT_COLOR = (255, 255, 255)
DEFAULT_POSITION = (0, 0)

SPEED = 10
SPEED_DECREMENT = 2

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)

# Заголовок окна
pygame.display.set_caption('змейка!')

# Настройка времени
clock = pygame.time.Clock()

# Классы игры
class GameObject:
    """Описывает стандартный объект игры."""

    def __init__(self, position=DEFAULT_POSITION, body_color=DEFAULT_COLOR):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод для отрисовки игрового объекта."""
        pass

    def draw_cell(self, position, color):
        """Метод для покраски одной клетки."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw_clear_cell(self, position, color):
        """Метод для покраски одной клетки в цвет фона."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


class Apple(GameObject):
    """Описывает объект яблока."""

    def __init__(self, occupied: set[tuple[int, int]], body_color=APPLE_COLOR):
        self.position = None
        super().__init__(position=self.randomize_position(occupied=occupied), body_color=body_color)

    def randomize_position(self, occupied: set[tuple[int, int]]):
        """Задает яблоку случайную позицию на игровом поле, не пересекающуюся с объектами."""
        new_position = choice(tuple(ALL_CELLS - occupied))
        self.position = new_position
        return self.position

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position, self.body_color)


class BadApple(Apple):
    """Описывает объект "плохого" яблока."""

    def __init__(self, occupied_cells: set[tuple[int, int]], body_color=BAD_APPLE_COLOR):
        super().__init__(occupied=occupied_cells, body_color=body_color)


class Stone(GameObject):
    """Описывает объект камня."""

    def __init__(self, occupied: set[tuple[int, int]], body_color=STONE_COLOR):
        self.position = self.randomize_position(occupied=occupied)
        self.body_color = body_color

    def randomize_position(self, occupied: set[tuple[int, int]]):
        """Задает случайную позицию на игровом поле."""
        new_position = choice(tuple(ALL_CELLS - occupied))
        self.position = new_position
        return self.position

    def draw(self):
        """Отрисовывает камень на игровом поле."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Описывает объект змейки."""

    def __init__(self, length=1, positions=[(GRID_CENTER_X * GRID_SIZE, GRID_CENTER_Y * GRID_SIZE)], direction=RIGHT, next_direction=None, body_color=SNAKE_COLOR, speed=SPEED):
        self.length = length
        self.positions = positions
        self.direction = direction
        self.next_direction = next_direction
        self.last = None
        self.speed = speed
        super().__init__(position=positions[0], body_color=body_color)

    def update_direction(self):
        """Обновление направление после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def update_speed(self):
        """Обновление скорости после увеличения длины."""
        if self.length >= 50:
            self.speed = 5
        elif self.length >= 40:
            self.speed = 7
        elif self.length >= 30:
            self.speed = 10
        elif self.length >= 20:
            self.speed = 12
        elif self.length >= 10:
            self.speed = 15
        else:
            self.speed = 20

    def move(self):
        """Движение змейки вперед в направлении direction."""
        old_head = self.get_head_position()
        new_head_x = (old_head[0] + self.direction[0] * GRID_SIZE) % (GRID_WIDTH * GRID_SIZE)
        new_head_y = (old_head[1] + self.direction[1] * GRID_SIZE) % (GRID_HEIGHT * GRID_SIZE)
        self.position = (new_head_x, new_head_y)
        self.positions.insert(0, self.position)
        self.last = self.positions.pop()

    def draw(self):
        """Отрисовка змейки на игровом поле."""
        if self.length > 1:
            self.draw_cell(self.positions[1], self.body_color)

        # Отрисовка головы змейки
        self.draw_cell(self.position, SNAKE_HEAD_COLOR)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.position

    def reset(self):
        """Возвращает змейку в начальную позицию после поражения."""
        self.length = 1
        self.positions = [(GRID_CENTER_X * GRID_SIZE, GRID_CENTER_Y * GRID_SIZE)]
        self.direction = choice([RIGHT, DOWN, LEFT, UP])
        self.next_direction = None
        self.position = self.positions[0]
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)


# Обработка действий пользователя
def handle_keys(game_object):
    """Обработка действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            elif event.key == pygame.K_q:
                game_object.speed += SPEED_DECREMENT
            elif event.key == pygame.K_w and game_object.speed > SPEED_DECREMENT:
                game_object.speed -= SPEED_DECREMENT
            elif (event.key, game_object.direction) in NEXT_DIRECTION.keys():
                game_object.next_direction = NEXT_DIRECTION[(event.key, game_object.direction)]


# Главная функция
def main():
    """Основная функция игрового процесса."""
    pygame.init()
    snake = Snake()
    occupied_cells = set(snake.positions)
    apple = Apple(occupied_cells)
    occupied_cells.add(apple.position)
    bad_apple = BadApple(occupied_cells)
    occupied_cells.add(bad_apple.position)
    stone = Stone(occupied_cells)

    while True:
        clock.tick(snake.speed)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        snake.update_speed()

        # Рисование объектов
        screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        bad_apple.draw()
        stone.draw()
        snake.draw()

        pygame.display.update()


if __name__ == "__main__":
    main()
