import pygame
import random
import os
import time
from PIL import Image  # Import Pillow for GIF handling

# Initialize pygame
pygame.init()

# Set up display
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Game")

# Initialize pygame mixer for audio
pygame.mixer.init()

# Load and set volume for both music tracks
start_music_path = "intro_start.mp3"
game_music_path = "arcadebgm.mp3"
score_sound_path = "flapscore.wav"
game_over_sound_path = "gameover.wav"
restart_sound_path = "restart.wav"
pygame.mixer.music.set_volume(0.5)

# Load sound effects
score_sound = pygame.mixer.Sound(score_sound_path)
game_over_sound = pygame.mixer.Sound(game_over_sound_path)

# Set up clock
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (0, 128, 128)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
DARK_VIOLET = (48, 25, 52)
PURPLE = (128, 0, 128)
CLOUD_BURST = (34, 34, 52)

# Set up arcade font
arcade_font_path = "gamefont.ttf"
FONT = pygame.font.Font(arcade_font_path, 30)
FONT1 = pygame.font.Font(arcade_font_path, 15)

# Function to render text that fits within the screen width
def render_fitting_text(text, color, background_color, max_width, initial_font_size=30):
    font_size = initial_font_size
    font = pygame.font.Font(arcade_font_path, font_size)
    rendered_text = font.render(text, True, color, background_color)
    
    # Reduce font size until the text width fits within max_width
    while rendered_text.get_width() > max_width and font_size > 10:
        font_size -= 1
        font = pygame.font.Font(arcade_font_path, font_size)
        rendered_text = font.render(text, True, color, background_color)
    
    return rendered_text

# Loading screen function
def loading_screen():
    loading_text = FONT.render("Loading...", True, WHITE)
    loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    
    # Define the progress bar dimensions
    progress_bar_width = 300
    progress_bar_height = 30
    progress_bar_x = (SCREEN_WIDTH - progress_bar_width) // 2
    progress_bar_y = SCREEN_HEIGHT // 2
    
    # Simulate loading progress
    for i in range(101):
        SCREEN.fill(BLACK)
        SCREEN.blit(loading_text, loading_rect)
        
        # Draw the progress bar background
        pygame.draw.rect(SCREEN, GRAY, (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
        
        # Draw the progress bar fill based on current loading progress
        pygame.draw.rect(SCREEN, GREEN, (progress_bar_x, progress_bar_y, progress_bar_width * (i / 100), progress_bar_height))
        
        # Update the display and simulate loading time
        pygame.display.update()
        time.sleep(0.01)

# Display loading screen
loading_screen()

# Load the background image and scale it to fit the screen size
background = pygame.image.load('arcadebackground5.jpg')
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

def draw_button(text, center_x, y, inactive_color, active_color):
    # Render the text surface and get its dimensions
    text_surface = FONT.render(text, True, BLACK)
    text_width, text_height = text_surface.get_size()
    
    # Define button dimensions based on text size + padding
    padding = 20
    button_width = text_width + padding
    button_height = text_height + padding
    
    # Center the button horizontally around the provided center_x
    button_x = center_x - button_width // 2
    button_rect = pygame.Rect(button_x, y, button_width, button_height)
    
    # Change color on hover
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if button_rect.collidepoint(mouse):
        pygame.draw.rect(SCREEN, active_color, button_rect)
        if click[0] == 1:
            return True  # Button is clicked
    else:
        pygame.draw.rect(SCREEN, inactive_color, button_rect)
    
    # Draw text in the center of the button
    text_rect = text_surface.get_rect(center=button_rect.center)
    SCREEN.blit(text_surface, text_rect)
    
    return False

# Set up bird properties
BIRD_WIDTH = 55
BIRD_HEIGHT = 48

# Load the bird animated GIF using Pillow
bird_gif = Image.open('fly.gif')
bird_frames = []
for frame in range(bird_gif.n_frames):
    bird_gif.seek(frame)
    bird_frame = bird_gif.convert("RGBA")
    bird_surface = pygame.image.fromstring(bird_frame.tobytes(), bird_frame.size, bird_frame.mode)
    bird_surface = pygame.transform.scale(bird_surface, (BIRD_WIDTH, BIRD_HEIGHT))
    bird_frames.append(bird_surface)

# Bird animation variables
current_frame = 0
frame_delay = 5
frame_counter = 0

# Bird physics constants
GRAVITY = 0.5
FLAP_STRENGTH = -10

# Pipe constants
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_VELOCITY = -3
# Define the outline width
PIPE_OUTLINE_WIDTH = 4

# Pipe constants
PIPE_WIDTH = 80
PIPE_GAP = 170
PIPE_VELOCITY = -4  # Slightly faster initial speed by making this more negative

# Function to increase difficulty
def increase_difficulty(score):
    global PIPE_VELOCITY, PIPE_GAP
    if score % 10 == 0 and score != 0:
        PIPE_VELOCITY -= 0.02  # Slightly increase speed every 10 points
        PIPE_GAP = max(170, PIPE_GAP - 10)  # Maintain a reasonable minimum gap size


# Load high score from file
high_score_file = "high_score.txt"
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as file:
        high_score = int(file.read())
else:
    high_score = 0

# Function to save high score to file
def save_high_score(score):
    with open(high_score_file, "w") as file:
        file.write(str(score))

# Define initial constants for reset values
INITIAL_PIPE_VELOCITY = -4
INITIAL_PIPE_GAP = 170

# Reset game function
def reset_game():
    global bird, bird_y_velocity, pipe1, pipe2, score, running, current_frame, PIPE_VELOCITY, PIPE_GAP
    
    bird = pygame.Rect(100, 240, BIRD_WIDTH, BIRD_HEIGHT)
    bird_y_velocity = 0
    current_frame = 0
    score = 0
    
    # Reset pipes
    pipe_height = random.randint(130, 280)
    pipe1 = pygame.Rect(SCREEN_WIDTH, 0, PIPE_WIDTH, pipe_height)
    pipe2 = pygame.Rect(SCREEN_WIDTH, pipe_height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - pipe_height - PIPE_GAP)

    # Reset difficulty
    PIPE_VELOCITY = INITIAL_PIPE_VELOCITY
    PIPE_GAP = INITIAL_PIPE_GAP

# Function to display the start screen
def start_game():
    pygame.mixer.music.load(start_music_path)
    pygame.mixer.music.play(-1)

    SCREEN.blit(background, (0, 0))  # Draw background
    title_text = FONT.render("Flappy Game", True, BLACK)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70))
       
    waiting_to_start = True
    while waiting_to_start:
        SCREEN.blit(background, (0, 0))
        SCREEN.blit(title_text, title_rect)

        # Draw the start button and check for click
        if draw_button("Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, TEAL, CLOUD_BURST):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(game_music_path)
            pygame.mixer.music.play(-1)
            waiting_to_start = False
        
        if draw_button("Quit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, TEAL, CLOUD_BURST):
            # Display "Thank you for playing" message
            thank_you_text = FONT1.render("Thank you for playing!", True, WHITE)
            thank_you_rect = thank_you_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            SCREEN.fill(BLACK)  # Clear the screen
            SCREEN.blit(thank_you_text, thank_you_rect)
            pygame.display.update()
            time.sleep(2) 
            pygame.quit()
            exit()
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

# Function to display the Game Over screen
def game_over_screen():
    game_over_sound.play()

    SCREEN.fill(BLACK)
    game_over_text = FONT.render("Game Over", True, WHITE)
    score_text = FONT1.render(f"Your Score: {score}", True, WHITE)
    high_score_text = FONT1.render(f"High Score: {high_score}", True, WHITE)
    SCREEN.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
    pygame.display.update()

    # Center the text
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    SCREEN.blit(game_over_text, game_over_rect)

    # Center the text with score and high score under the Game Over title
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    SCREEN.blit(score_text, score_rect)
    SCREEN.blit(high_score_text, high_score_rect)
    
    # Save high score if the new score is higher
    if score > high_score:
        save_high_score(score)
    
    # Check for quit or restart
    pygame.display.update()
    time.sleep(0)
    waiting_for_restart = True
    while waiting_for_restart:
        # Check for quit or restart button clicks
        if draw_button("Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, TEAL, CLOUD_BURST):
            reset_game()
            return
        if draw_button("Quit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180, TEAL, CLOUD_BURST):
            # Display "Thank you for playing" message
            thank_you_text = FONT1.render("Thank you for playing!", True, WHITE)
            thank_you_rect = thank_you_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            SCREEN.fill(BLACK)  # Clear the screen
            SCREEN.blit(thank_you_text, thank_you_rect)
            pygame.display.update()
            time.sleep(2)  # Wait a moment before quitting
            pygame.quit()
            exit()
        
        pygame.display.update()

        # Check for quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

# Game loop initialization
start_game()
reset_game()

# Main game loop
running = True

while running:
    score = 0
    bird_y_velocity = 0

    # Initialize pipes
    pipe_height = random.randint(130, 280)
    pipe1 = pygame.Rect(SCREEN_WIDTH, 0, PIPE_WIDTH, pipe_height)
    pipe2 = pygame.Rect(SCREEN_WIDTH, pipe_height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - pipe_height - PIPE_GAP)

    game_active = True  # Flag to track if the game is active
    while game_active:  # Continue the game loop while the game is active
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_active = False  # Exit the inner loop
            # Check for spacebar or left mouse click
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_y_velocity = FLAP_STRENGTH
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                bird_y_velocity = FLAP_STRENGTH
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()

        # Increase difficulty if score is a multiple of 10
        increase_difficulty(score)

        # Move bird
        bird_y_velocity += GRAVITY
        bird.y += int(bird_y_velocity)

        # Move pipes
        pipe1.x += PIPE_VELOCITY
        pipe2.x += PIPE_VELOCITY

        # If pipes go off screen, reset them
        if pipe1.x + PIPE_WIDTH < 0:
            pipe1.x = SCREEN_WIDTH
            pipe2.x = SCREEN_WIDTH
            pipe_height = random.randint(130, 280)
            pipe1.height = pipe_height
            pipe2.y = pipe_height + PIPE_GAP
            pipe2.height = SCREEN_HEIGHT - pipe_height - PIPE_GAP
            score += 1

            # Play score sound effect
            score_sound.play()

        # Check for collision
        if bird.colliderect(pipe1) or bird.colliderect(pipe2) or bird.y < 0 or bird.y > SCREEN_HEIGHT:
            game_active = False  # Set to false to exit the game loop

        # Update high score if current score is higher
        if score > high_score:
            high_score = score
            save_high_score(high_score)

        # Draw everything
        SCREEN.blit(background, (0, 0)) 
        
        # Draw bird image (animated)
        frame_counter += 1
        if frame_counter >= frame_delay:
            current_frame = (current_frame + 1) % len(bird_frames)
            frame_counter = 0
        SCREEN.blit(bird_frames[current_frame], (bird.x, bird.y))

        # Draw pipes
        pygame.draw.rect(SCREEN, CLOUD_BURST, pipe1)
        pygame.draw.rect(SCREEN, CLOUD_BURST, pipe2)

        # Draw score and high score box
        score_box_width = 300
        score_box_height = 75
        score_box_rect = pygame.Rect(50, 10, score_box_width, score_box_height)
        
        # Draw the outer rectangle (outline)
        pygame.draw.rect(SCREEN, DARK_VIOLET, score_box_rect)  # Dark purple for outline
        pygame.draw.rect(SCREEN, TEAL, (score_box_rect.x + 2, score_box_rect.y + 2, score_box_width - 4, score_box_height - 4))  # Purple for the inside

        # Draw score and high score text
        score_text = FONT1.render(f"Score: {score}", True, BLACK)
        high_score_text = FONT1.render(f"High Score: {high_score}", True, BLACK)
        SCREEN.blit(score_text, (score_box_rect.x + 10, score_box_rect.y + 15))
        SCREEN.blit(high_score_text, (score_box_rect.x + 10, score_box_rect.y + 40))

        # Update display
        pygame.display.update()
        clock.tick(60)

    # Call the game over screen
    game_over_screen()  # This will also handle resetting the game if necessary

pygame.quit()
