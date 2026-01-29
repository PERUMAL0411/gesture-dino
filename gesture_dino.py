import pygame
import cv2
import mediapipe as mp
import random
import sys

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 900, 300
GROUND_Y = 230
FPS = 60

JUMP_VEL = -18
GRAVITY = 1

# ---------------- ASCII DINO ----------------
DINO_ART = [
    "  ██ ",
    " ████",
    " █ ██",
    "█████",
    "  █ █"
]

# ---------------- GESTURE CONTROLLER ----------------
class GestureController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def get_command(self):
        ret, frame = self.cap.read()
        if not ret:
            return "run"

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        if not result.multi_hand_landmarks:
            return "run"

        lm = result.multi_hand_landmarks[0].landmark

        fingers = 0
        tips = [8, 12, 16, 20]
        for tip in tips:
            if lm[tip].y < lm[tip - 2].y:
                fingers += 1

        if fingers >= 4:
            return "jump"
        elif fingers <= 1:
            return "duck"
        return "run"

    def release(self):
        self.cap.release()

# ---------------- DINO ----------------
class Dino:
    def __init__(self):
        self.y = GROUND_Y
        self.vel = 0
        self.ducking = False

    def update(self, command):
        if command == "jump" and self.y == GROUND_Y:
            self.vel = JUMP_VEL

        self.ducking = (command == "duck")

        self.y += self.vel
        self.vel += GRAVITY

        if self.y > GROUND_Y:
            self.y = GROUND_Y
            self.vel = 0

    def rect(self):
        height = 30 if self.ducking else 50
        return pygame.Rect(80, self.y - height, 40, height)

# ---------------- OBSTACLE ----------------
class Obstacle:
    def __init__(self):
        self.x = WIDTH
        self.speed = 8
        self.rect = pygame.Rect(self.x, GROUND_Y - 40, 30, 40)

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x

    def offscreen(self):
        return self.x < -50

# ---------------- MAIN GAME ----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gesture Dino")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    dino = Dino()
    obstacles = []
    gesture = GestureController()

    score = 0
    spawn_timer = 0
    running = True

    try:
        while running:
            clock.tick(FPS)
            score += 1
            spawn_timer += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            command = gesture.get_command()
            dino.update(command)

            if spawn_timer > 90:
                obstacles.append(Obstacle())
                spawn_timer = 0

            for obs in obstacles:
                obs.update()
                if obs.rect.colliderect(dino.rect()):
                    running = False

            obstacles = [o for o in obstacles if not o.offscreen()]

            # -------- DRAW --------
            screen.fill((245, 245, 245))
            pygame.draw.line(screen, (0, 0, 0), (0, GROUND_Y + 5), (WIDTH, GROUND_Y + 5), 2)

            for i, row in enumerate(DINO_ART):
                surf = font.render(row, True, (0, 0, 0))
                screen.blit(surf, (80, dino.y - 50 + i * 10))

            for obs in obstacles:
                pygame.draw.rect(screen, (0, 150, 0), obs.rect)

            screen.blit(font.render(f"Score: {score}", True, (0, 0, 0)), (10, 10))
            pygame.display.flip()

    finally:
        gesture.release()
        pygame.quit()
        sys.exit()

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
