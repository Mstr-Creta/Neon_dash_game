import pygame
import sys
import random
import math
from pygame import gfxdraw

# Initialize pygame
pygame.init()
pygame.mixer.init()  # For sound

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGBA for glow effects)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
LIME = (0, 255, 0)
NEON_COLORS = [CYAN, MAGENTA, YELLOW, LIME]

# Game variables
score = 0
high_score = 0
game_speed = 5
difficulty_timer = 0
difficulty_increase_rate = 5  # seconds
game_over = False
game_started = False

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Neon Dash")
clock = pygame.time.Clock()

# Load fonts
try:
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
except:
    print("Font loading error")
    font_large = pygame.font.SysFont('arial', 74)
    font_medium = pygame.font.SysFont('arial', 48)
    font_small = pygame.font.SysFont('arial', 36)

# Load sounds
try:
    pickup_sound = pygame.mixer.Sound("pickup.wav")
    crash_sound = pygame.mixer.Sound("crash.wav")
    dodge_sound = pygame.mixer.Sound("dodge.wav")
    # Background music
    pygame.mixer.music.load("synthwave.mp3")
    pygame.mixer.music.set_volume(0.5)
    sounds_loaded = True
except:
    print("Sound files not found. Continuing without sound.")
    sounds_loaded = False

# Player class
class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 100
        self.speed = 8
        self.color = CYAN
        self.trail = []
        self.max_trail_length = 10
        self.boost = False
        self.boost_meter = 0
        self.max_boost = 100
        self.boost_speed = 12
        self.boost_drain_rate = 1
        self.boost_fill_rate = 0.2
    
    def move(self, direction):
        if self.boost:
            speed = self.boost_speed
        else:
            speed = self.speed
            
        if direction == "left" and self.x > 0:
            self.x -= speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += speed
    
    def update(self):
        # Update trail
        self.trail.insert(0, (self.x + self.width // 2, self.y + self.height))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop()
        
        # Update boost meter
        if self.boost:
            self.boost_meter -= self.boost_drain_rate
            if self.boost_meter <= 0:
                self.boost = False
                self.boost_meter = 0
        else:
            self.boost_meter += self.boost_fill_rate
            if self.boost_meter > self.max_boost:
                self.boost_meter = self.max_boost
    
    def activate_boost(self):
        if self.boost_meter > 20:  # Minimum boost threshold
            self.boost = True
    
    def deactivate_boost(self):
        self.boost = False
    
    def draw(self, surface):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = 255 - int(255 * (i / self.max_trail_length))
            radius = int(self.width / 3 * (1 - i / self.max_trail_length))
            trail_color = (*self.color[:3], alpha)
            
            # Draw glowing trail circle
            pygame.draw.circle(surface, trail_color, (trail_x, trail_y), radius)
            
            # Add inner glow
            if radius > 2:
                inner_color = (*WHITE[:3], alpha // 2)
                pygame.draw.circle(surface, inner_color, (trail_x, trail_y), radius // 2)
        
        # Draw player vehicle (triangle)
        points = [
            (self.x + self.width // 2, self.y),  # Top
            (self.x, self.y + self.height),      # Bottom left
            (self.x + self.width, self.y + self.height)  # Bottom right
        ]
        
        # Draw glow effect
        for i in range(3, 0, -1):
            glow_color = (*self.color[:3], 100 - i * 30)
            glow_points = [
                (points[0][0], points[0][1] - i * 2),
                (points[1][0] - i * 2, points[1][1] + i),
                (points[2][0] + i * 2, points[2][1] + i)
            ]
            pygame.draw.polygon(surface, glow_color, glow_points)
        
        # Draw main vehicle
        pygame.draw.polygon(surface, self.color, points)
        
        # Draw inner highlight
        inner_points = [
            (self.x + self.width // 2, self.y + 10),
            (self.x + 10, self.y + self.height - 10),
            (self.x + self.width - 10, self.y + self.height - 10)
        ]
        pygame.draw.polygon(surface, WHITE, inner_points)
        
        # Draw boost meter
        meter_width = 50
        meter_height = 5
        meter_x = self.x + (self.width - meter_width) // 2
        meter_y = self.y + self.height + 10
        
        # Meter background
        pygame.draw.rect(surface, (50, 50, 50), (meter_x, meter_y, meter_width, meter_height))
        
        # Meter fill
        fill_width = int(meter_width * (self.boost_meter / self.max_boost))
        if fill_width > 0:
            if self.boost:
                boost_color = YELLOW
            else:
                boost_color = LIME
            pygame.draw.rect(surface, boost_color, (meter_x, meter_y, fill_width, meter_height))

# Obstacle class
class Obstacle:
    def __init__(self, speed):
        self.width = random.randint(50, 200)
        self.height = random.randint(20, 40)
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = speed
        self.color = random.choice(NEON_COLORS)
        self.pulse_effect = 0
        self.pulse_direction = 1
    
    def update(self):
        self.y += self.speed
        
        # Pulse effect for glow
        self.pulse_effect += 0.1 * self.pulse_direction
        if self.pulse_effect >= 1.0 or self.pulse_effect <= 0.0:
            self.pulse_direction *= -1
    
    def draw(self, surface):
        # Draw glow effect
        glow_size = int(5 + 3 * self.pulse_effect)
        glow_rect = (self.x - glow_size, self.y - glow_size, 
                    self.width + glow_size * 2, self.height + glow_size * 2)
        glow_color = (*self.color[:3], 100)
        
        pygame.draw.rect(surface, glow_color, glow_rect, border_radius=glow_size)
        
        # Draw main obstacle
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw inner highlight
        inner_rect = (self.x + 5, self.y + 5, self.width - 10, self.height - 10)
        inner_color = (*WHITE[:3], 150)
        pygame.draw.rect(surface, inner_color, inner_rect)
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

# Pickup class
class Pickup:
    def __init__(self, speed):
        self.radius = 15
        self.x = random.randint(self.radius, SCREEN_WIDTH - self.radius)
        self.y = -self.radius * 2
        self.speed = speed
        self.color = random.choice(NEON_COLORS)
        self.pulse = 0
        self.pulse_speed = random.uniform(0.05, 0.1)
        self.value = random.choice([1, 1, 1, 2, 3])  # Most pickups are worth 1, some worth more
    
    def update(self):
        self.y += self.speed
        self.pulse = (self.pulse + self.pulse_speed) % (2 * math.pi)
    
    def draw(self, surface):
        # Calculate pulse effect
        pulse_radius = self.radius + int(math.sin(self.pulse) * 3)
        
        # Draw outer glow
        for i in range(3, 0, -1):
            glow_radius = pulse_radius + i * 3
            glow_color = (*self.color[:3], 70 - i * 20)
            pygame.draw.circle(surface, glow_color, (self.x, self.y), glow_radius)
        
        # Draw main circle
        pygame.draw.circle(surface, self.color, (self.x, self.y), pulse_radius)
        
        # Draw inner highlight
        inner_radius = max(2, pulse_radius // 2)
        pygame.draw.circle(surface, WHITE, (self.x, self.y), inner_radius)
        
        # Draw value indicator (more lines for higher value)
        if self.value > 1:
            for i in range(self.value):
                angle = i * (2 * math.pi / self.value)
                end_x = self.x + int(math.cos(angle) * (pulse_radius + 5))
                end_y = self.y + int(math.sin(angle) * (pulse_radius + 5))
                pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), 2)
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + self.radius

# Particle effect class
class Particle:
    def __init__(self, x, y, color, is_crash=False):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 8)
        self.lifetime = random.randint(20, 40)
        
        if is_crash:
            # Explosion effect
            speed = random.uniform(2, 10)
            angle = random.uniform(0, 2 * math.pi)
            self.x_vel = math.cos(angle) * speed
            self.y_vel = math.sin(angle) * speed
        else:
            # Pickup effect (mostly upward)
            self.x_vel = random.uniform(-2, 2)
            self.y_vel = random.uniform(-5, -1)
    
    def update(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)
    
    def draw(self, surface):
        alpha = int(255 * (self.lifetime / 40))
        particle_color = (*self.color[:3], alpha)
        pygame.draw.circle(surface, particle_color, (int(self.x), int(self.y)), int(self.size))
    
    def is_dead(self):
        return self.lifetime <= 0

# Background grid class
class NeonGrid:
    def __init__(self):
        self.grid_size = 50
        self.line_color = (20, 20, 50, 150)
        self.highlight_color = (40, 40, 100, 200)
        self.offset_y = 0
        self.grid_speed = 2
        self.pulse = 0
        self.pulse_speed = 0.02
    
    def update(self, speed_factor=1.0):
        self.offset_y = (self.offset_y + self.grid_speed * speed_factor) % self.grid_size
        self.pulse = (self.pulse + self.pulse_speed) % (2 * math.pi)
    
    def draw(self, surface):
        # Draw horizontal lines
        for y in range(-self.grid_size, SCREEN_HEIGHT + self.grid_size, self.grid_size):
            actual_y = y + self.offset_y
            
            # Make lines closer to player brighter
            distance_factor = 1 - (abs(actual_y - SCREEN_HEIGHT) / SCREEN_HEIGHT)
            alpha = int(100 + distance_factor * 155)
            line_color = (*self.line_color[:3], alpha)
            
            pygame.draw.line(surface, line_color, (0, actual_y), (SCREEN_WIDTH, actual_y), 1)
        
        # Draw vertical lines
        for x in range(0, SCREEN_WIDTH + self.grid_size, self.grid_size):
            pygame.draw.line(surface, self.line_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        
        # Draw pulsing horizon line
        horizon_y = SCREEN_HEIGHT // 2
        pulse_width = 3 + int(math.sin(self.pulse) * 2)
        pygame.draw.line(surface, self.highlight_color, (0, horizon_y), (SCREEN_WIDTH, horizon_y), pulse_width)

# Game state functions
def reset_game():
    global player, obstacles, pickups, particles, score, game_speed, game_over, difficulty_timer
    player = Player()
    obstacles = []
    pickups = []
    particles = []
    score = 0
    game_speed = 5
    game_over = False
    difficulty_timer = 0
    
    # Start background music
    if sounds_loaded:
        try:
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except:
            pass

def spawn_obstacle():
    obstacles.append(Obstacle(game_speed))

def spawn_pickup():
    pickups.append(Pickup(game_speed * 0.8))  # Pickups move slightly slower

def check_collisions():
    global score, high_score, game_over
    
    # Check obstacle collisions
    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
        if player_rect.colliderect(obstacle_rect):
            game_over = True
            high_score = max(score, high_score)
            
            # Create explosion particles
            for _ in range(50):
                particles.append(Particle(player.x + player.width // 2, 
                                         player.y + player.height // 2, 
                                         player.color, True))
            
            # Play crash sound
            if sounds_loaded:
                try:
                    crash_sound.play()
                    pygame.mixer.music.stop()
                except:
                    pass
            
            return
    
    # Check pickup collisions
    for pickup in pickups[:]:
        distance = math.sqrt((player.x + player.width // 2 - pickup.x) ** 2 + 
                            (player.y + player.height // 2 - pickup.y) ** 2)
        
        if distance < player.width // 2 + pickup.radius:
            # Add score
            score += pickup.value
            
            # Create particles
            for _ in range(20):
                particles.append(Particle(pickup.x, pickup.y, pickup.color))
            
            # Remove pickup
            pickups.remove(pickup)
            
            # Increase boost meter
            player.boost_meter = min(player.max_boost, player.boost_meter + 10)
            
            # Play pickup sound
            if sounds_loaded:
                try:
                    pickup_sound.play()
                except:
                    pass

def update_difficulty():
    global game_speed, difficulty_timer
    
    difficulty_timer += 1 / FPS
    if difficulty_timer >= difficulty_increase_rate:
        difficulty_timer = 0
        game_speed += 0.5

def draw_text(text, font, color, x, y, glow=True):
    # Draw glow effect
    if glow:
        glow_surf = font.render(text, True, (*color[:3], 150))
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            screen.blit(glow_surf, (x + offset[0], y + offset[1]))
    
    # Draw main text
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_game_over():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    draw_text("GAME OVER", font_large, MAGENTA, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100)
    draw_text(f"Score: {score}", font_medium, CYAN, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2)
    draw_text("Press R to restart", font_small, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60)
    draw_text("Press Q to quit", font_small, WHITE, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 100)

def draw_start_screen():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    draw_text("NEON DASH", font_large, CYAN, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100)
    draw_text("Arrow keys to move", font_small, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    draw_text("Space for boost", font_small, YELLOW, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 40)
    draw_text("Press ENTER to start", font_medium, MAGENTA, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100)

def draw_hud():
    # Draw score
    draw_text(f"Score: {score}", font_medium, WHITE, 20, 20)
    
    # Draw high score
    if high_score > 0:
        draw_text(f"Best: {high_score}", font_small, YELLOW, 20, 70)
    
    # Draw speed indicator
    draw_text(f"Speed: {int(game_speed)}", font_small, LIME, SCREEN_WIDTH - 150, 20)

# Initialize game objects
neon_grid = NeonGrid()
player = None
obstacles = []
pickups = []
particles = []

# Main game loop
running = True
obstacle_timer = 0
pickup_timer = 0
screen_shake = 0

reset_game()  # Initialize game state

while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()
            
            if event.key == pygame.K_q and game_over:
                running = False
            
            if event.key == pygame.K_RETURN and not game_started:
                game_started = True
                reset_game()
            
            if event.key == pygame.K_SPACE:
                player.activate_boost()
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                player.deactivate_boost()
    
    # Skip updates if game not started or game over
    if not game_started:
        # Draw background
        screen.fill(BLACK)
        neon_grid.update(0.5)
        neon_grid.draw(screen)
        
        # Draw start screen
        draw_start_screen()
        
        pygame.display.flip()
        clock.tick(FPS)
        continue
    
    if not game_over:
        # Get keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move("left")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move("right")
        
        # Update player
        player.update()
        
        # Update obstacles
        for obstacle in obstacles[:]:
            obstacle.update()
            if obstacle.is_off_screen():
                obstacles.remove(obstacle)
        
        # Update pickups
        for pickup in pickups[:]:
            pickup.update()
            if pickup.is_off_screen():
                pickups.remove(pickup)
        
        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.is_dead():
                particles.remove(particle)
        
        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer >= FPS * (2.0 - min(1.5, game_speed / 15)):  # Spawn faster as speed increases
            obstacle_timer = 0
            spawn_obstacle()
        
        # Spawn pickups
        pickup_timer += 1
        if pickup_timer >= FPS * 3:  # Spawn pickup every 3 seconds
            pickup_timer = 0
            spawn_pickup()
        
        # Check collisions
        check_collisions()
        
        # Update difficulty
        update_difficulty()
        
        # Update background
        neon_grid.update(game_speed / 5)
        
        # Update screen shake
        if screen_shake > 0:
            screen_shake -= 1
    
    # Draw everything
    screen.fill(BLACK)
    
    # Draw background
    neon_grid.draw(screen)
    
    # Apply screen shake
    shake_offset = (0, 0)
    if screen_shake > 0:
        shake_offset = (random.randint(-3, 3), random.randint(-3, 3))
    
    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw(screen)
    
    # Draw pickups
    for pickup in pickups:
        pickup.draw(screen)
    
    # Draw player
    if not game_over:
        player.draw(screen)
    
    # Draw particles
    for particle in particles:
        particle.draw(screen)
    
    # Draw HUD
    draw_hud()
    
    # Draw game over screen
    if game_over:
        draw_game_over()
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(FPS)

# Quit the game
pygame.quit()
sys.exit()
