import pygame
import sys
import math

# --- Initialization ---
pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
PINK = (248, 200, 220)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FPS = 60
FRICTION = 0.98
MAX_POWER = 15

# --- Game State ---
strokes = 0
total_score = 0
mouse_down = False
drag_vector = pygame.Vector2(0, 0)
shooting = False

# --- Ball Setup ---
ball_radius = 10
ball_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
ball_vel = pygame.Vector2(0, 0)

# --- Hole Setup ---
hole_radius = 15
hole_pos = pygame.Vector2(700, 500)

# --- collision helpers ---
def reflect_velocity(ball_pos, ball_vel, point1, point2):
    line = pygame.Vector2(point2) - pygame.Vector2(point1)
    normal = pygame.Vector2(-line.y, line.x).normalize()
    if ball_vel.dot(normal) > 0:
        normal = -normal
    return ball_vel - 2 * ball_vel.dot(normal) * normal

def collide_polygon(ball_pos, ball_vel, points):
    for i in range(len(points)):
        p1 = pygame.Vector2(points[i])
        p2 = pygame.Vector2(points[(i + 1) % len(points)])
        line = p2 - p1
        t = max(0, min(1, (ball_pos - p1).dot(line) / line.length_squared()))
        closest = p1 + line * t
        if (ball_pos - closest).length() <= ball_radius:
            return reflect_velocity(ball_pos, ball_vel, p1, p2)
    return ball_vel

# --- Hole Layouts ---
hole_layouts = [
    {
        "start_pos": pygame.Vector2(100, 100),
        "hole_pos": pygame.Vector2(700, 500),
        "obstacles": []
    },
    {
        "start_pos": pygame.Vector2(150, 300),
        "hole_pos": pygame.Vector2(600, 100),
        "obstacles": [
            {"type": "rect", "shape": pygame.Rect(300, 250, 200, 20)},
            {"type": "rect", "shape": pygame.Rect(400, 150, 20, 100)}
        ]
    },
    {
        "start_pos": pygame.Vector2(100, 500),
        "hole_pos": pygame.Vector2(700, 100),
        "obstacles": [
            {"type": "rect", "shape": pygame.Rect(200, 400, 400, 20)},
            {"type": "rect", "shape": pygame.Rect(400, 200, 20, 200)},
            # Triangle obstacle test
           # {"type": "triangle", "shape": [(300, 300), (350, 250), (400, 300)]}
        ]
    },
    {
        "start_pos": pygame.Vector2(130, 150),
        "hole_pos": pygame.Vector2(700, 100),
        "obstacles": [
            {"type": "polygon", "shape": [(400, 70),(320,220), (660, 220)]},
            {"type": "polygon", "shape": [(570, 290), (470, 420), (670, 420)]},
            {"type": "rect", "shape": pygame.Rect(40, 40, 200, 20)},
        ]
    }
]
current_hole_index = 0

# --- Load Hole Function ---
def load_hole(index):
    global ball_pos, hole_pos, obstacles, ball_vel, shooting
    layout = hole_layouts[index]
    ball_pos = layout["start_pos"].copy()
    hole_pos = layout["hole_pos"]
    obstacles = layout["obstacles"]
    ball_vel = pygame.Vector2(0, 0)
    shooting = False

# --- Pygame Setup ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Golf")
clock = pygame.time.Clock()
load_hole(current_hole_index)

# --- Main Game Loop ---
running = True
while running:
    clock.tick(FPS)
    screen.fill(PINK)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not shooting:
            mouse_down = True

        if event.type == pygame.MOUSEBUTTONUP and mouse_down:
            mouse_down = False
            drag_vector = ball_pos - pygame.Vector2(pygame.mouse.get_pos())
            power = min(drag_vector.length() * 0.1, MAX_POWER)

            if drag_vector.length() != 0:
                direction = drag_vector.normalize()
                ball_vel = direction * power
                shooting = True
                strokes += 1

    # --- Ball Movement ---
    if shooting:
        ball_pos += ball_vel
        ball_vel *= FRICTION
        if ball_vel.length() < 0.1:
            ball_vel = pygame.Vector2(0, 0)
            shooting = False

    # --- Wall Collision ---
    if ball_pos.x <= ball_radius or ball_pos.x >= WIDTH - ball_radius:
        ball_vel.x *= -1
    if ball_pos.y <= ball_radius or ball_pos.y >= HEIGHT - ball_radius:
        ball_vel.y *= -1

    # --- Obstacle Collision ---
    for obs in obstacles:
        if obs["type"] == "rect":
            rect = obs["shape"]
            if rect.collidepoint(ball_pos.x + ball_vel.x, ball_pos.y):
                ball_vel.x *= -1
            if rect.collidepoint(ball_pos.x, ball_pos.y + ball_vel.y):
                ball_vel.y *= -1

        elif obs["type"] == "polygon":
            ball_vel = collide_polygon(ball_pos, ball_vel, obs["shape"])
            

    # --- Hole Collision ---
    if (ball_pos - hole_pos).length() < hole_radius:
        if ball_vel.length() < 1:
            ball_vel = pygame.Vector2(0, 0)
            shooting = False
            total_score += strokes
            strokes = 0
            current_hole_index += 1

            if current_hole_index < len(hole_layouts):
                load_hole(current_hole_index)
            else:
                # --- End Screen ---
                end_screen = True
                while end_screen:
                    screen.fill(PINK)
                    font_big = pygame.font.SysFont(None, 64)
                    font_small = pygame.font.SysFont(None, 32)

                    title = font_big.render("Good job!", True, BLACK)
                    score_text = font_small.render(f"Total Strokes: {total_score}", True, BLACK)
                    hint_text = font_small.render("Press R to restart or Q to quit", True, BLACK)

                    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
                    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 30))
                    screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT//2 + 40))

                    pygame.display.flip()

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            end_screen = False
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                end_screen = False
                                running = False
                            if event.key == pygame.K_r:
                                current_hole_index = 0
                                total_score = 0
                                strokes = 0
                                load_hole(current_hole_index)
                                end_screen = False

    # --- Draw Hole ---
    pygame.draw.circle(screen, BLACK, (int(hole_pos.x), int(hole_pos.y)), hole_radius)

    # --- Draw Obstacles ---
    for obs in obstacles:
        if obs["type"] == "rect":
            pygame.draw.rect(screen, WHITE, obs["shape"])
        elif obs["type"] == "polygon":
            pygame.draw.polygon(screen, WHITE, obs["shape"])

    # --- Draw Ball with Border ---
    pygame.draw.circle(screen, BLACK, (int(ball_pos.x), int(ball_pos.y)), ball_radius + 2)
    pygame.draw.circle(screen, WHITE, (int(ball_pos.x), int(ball_pos.y)), ball_radius)

    # --- Draw Aiming Arrow ---
    if mouse_down and not shooting:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        drag_vector = ball_pos - mouse_pos
        power = min(drag_vector.length() * 0.1, MAX_POWER)

        if drag_vector.length() != 0:
            direction = drag_vector.normalize()
            end_pos = ball_pos + direction * power * 20

            # Shaft
            pygame.draw.line(screen, BLACK, ball_pos, end_pos, 3)

            # Arrowhead
            perp = pygame.Vector2(-direction.y, direction.x)
            tip = end_pos
            left = end_pos - direction * 15 + perp * 7
            right = end_pos - direction * 15 - perp * 7
            pygame.draw.polygon(screen, BLACK, [tip, left, right])

    # --- UI: Stroke Counter ---
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"Hole {current_hole_index + 1} | Strokes: {strokes} | Total: {total_score}", True, BLACK)
    screen.blit(text, (10, 10))

    # --- Update Display ---
    pygame.display.flip()

# --- Quit ---
pygame.quit()
sys.exit()
