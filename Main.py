import pygame
import cv2
import numpy as np
import random
import time
from src.ColorSequence import ColorSequence
from src.ScoreTable import ScoreTable
from src.CloseHand import CameraManager

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Balloon Sequence Game")

# Define fonts
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 36)

# Load colors
colors = ['red', 'green', 'blue', 'yellow', 'pink', 'gray']
color_images = []
for color in colors:
    img = pygame.image.load(f'images/Colors/{color}.png')
    color_images.append(img)

# Import logos
encuentro_logo = pygame.image.load('images/Logos/Logo_Encuentro_2025.png')
LUMACAD_logo = pygame.image.load('images/Logos/LumAcad_Logo.png')

# Game states
STATE_MENU = 0
STATE_PLAY = 1
STATE_SCORE = 2
STATE_NAME_INPUT = 3
STATE_GAME_OVER = 4
state = STATE_MENU

# Game variables
level = 1
lives = 3
score = 0
player_name = ""
color_sequence = None
user_sequence = []
current_color_index = 0
game_over_reason = ""
score_table = ScoreTable()

# Camera manager for hand detection
camera_manager = None

def menu_buttons():
    """Draw menu buttons and logos"""
    # Draw play button
    play_button = pygame.image.load('images/Buttons/play.png')
    play_button = pygame.transform.scale(play_button, (play_button.get_width() * 2, play_button.get_height() * 2))
    play_rect = play_button.get_rect(center=(screen_width // 4, screen_height - play_button.get_height() // 2 - 50))
    screen.blit(play_button, play_rect)

    # Draw score button
    score_button = pygame.image.load('images/Buttons/score.png')
    score_button = pygame.transform.scale(score_button, (score_button.get_width() * 2, score_button.get_height() * 2))
    score_rect = score_button.get_rect(center=(3 * screen_width // 4, screen_height - score_button.get_height() // 2 - 50))
    screen.blit(score_button, score_rect)

    # Scale and draw logos
    #encuentro_logo_scaled = pygame.transform.scale(encuentro_logo, (encuentro_logo.get_width() // 2, encuentro_logo.get_height() // 2))
    #LUMACAD_logo_scaled = pygame.transform.scale(LUMACAD_logo, (LUMACAD_logo.get_width() // 2, LUMACAD_logo.get_height() // 2))
    screen.blit(encuentro_logo, (20, 20))  # Top left corner
    screen.blit(LUMACAD_logo, (screen_width - LUMACAD_logo.get_width() - 20, 20))  # Top right corner

    return play_rect, score_rect

def draw_score_table(screen, score_table):
    """Draw score table screen"""
    # Define fonts and colors
    title_font = pygame.font.SysFont('Arial', 36)
    score_font = pygame.font.SysFont('Arial', 24)
    title_color = (0, 0, 0)
    score_color = (0, 0, 0)
    
    # Draw title
    title_text = title_font.render('Score Table', True, title_color)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))
    
    # Draw scores for top 5 levels
    ordered_scores = score_table.order_scores()
    top_scores = score_table.get_top_scores(5)
    for i, (name, score) in enumerate(top_scores.items()):
        level_text = score_font.render(f'TOP {i + 1}: {name} - {score}', True, score_color)
        screen.blit(level_text, (screen_width // 2 - level_text.get_width() // 2, 150 + i * 50))
    
    # Draw back button
    back_text = score_font.render('Back to Menu', True, score_color)
    back_rect = back_text.get_rect(center=(screen_width // 2, screen_height - 50))
    screen.blit(back_text, back_rect)
    
    return back_rect

def show_sequence(screen, color_sequence):
    """Show the color sequence to remember"""
    # Display sequence
    sequence = color_sequence.get_sequence()
    for color_name in sequence:
        # First, display camera feed as background
        if camera_manager and camera_manager.get_current_frame() is not None:
            camera_frame = camera_manager.get_current_frame()
            camera_surface = camera_frame_to_pygame(camera_frame)
            if camera_surface:
                screen.blit(camera_surface, (0, 0))
        else:
            screen.fill((255, 255, 255))

        # Add semi-transparent overlay for better visibility
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))  # White with alpha
        screen.blit(overlay, (0, 0))

        # Show color
        color_idx = colors.index(color_name)
        color_img = color_images[color_idx]
        screen.blit(color_img, (screen_width // 2 - color_img.get_width() // 2,
                                screen_height // 2 - color_img.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(1000)  # Show for 1 second

        # Show blank for a moment (with camera as background)
        if camera_manager and camera_manager.get_current_frame() is not None:
            camera_frame = camera_manager.get_current_frame()
            camera_surface = camera_frame_to_pygame(camera_frame)
            if camera_surface:
                screen.blit(camera_surface, (0, 0))
                screen.blit(overlay, (0, 0))
        else:
            screen.fill((255, 255, 255))

        pygame.display.flip()
        pygame.time.delay(500)  # Half a second between colors

def show_balloons_to_guess(screen, color_sequence, current_index):
    """Show balloons to guess and selection options"""
    # Don't fill the screen with white - we'll keep the camera background

    # Show progress (gray balloons with colored ones for completed guesses)
    sequence = color_sequence.get_sequence()
    total_width = len(sequence) * 60  # 50px per balloon + 10px spacing
    start_x = (screen_width - total_width) // 2

    for i in range(len(sequence)):
        # If the user has already guessed this position, show the actual color
        if i < current_index:
            color_name = user_sequence[i]
            color_idx = colors.index(color_name)
            balloon_img = color_images[color_idx]
        else:
            # Otherwise show gray
            balloon_img = color_images[-1]  # Gray is last

        screen.blit(balloon_img, (start_x + i * 60, screen_height // 2 - balloon_img.get_height() // 2 - 100))

    # Show color options at bottom with increased spacing
    color_option_rects = []
    balloon_width = color_images[0].get_width()
    spacing = 40  # Increased spacing between balloons
    total_option_width = (len(colors) - 1) * (balloon_width + spacing) - spacing
    option_start_x = (screen_width - total_option_width) // 2

    for i in range(len(colors) - 1):  # Exclude gray
        color_img = color_images[i]
        rect = color_img.get_rect()
        # Position with increased spacing
        x_pos = option_start_x + i * (balloon_width + spacing)
        rect.topleft = (x_pos, screen_height - color_img.get_height() - 50)
        screen.blit(color_img, rect)
        color_option_rects.append((rect, colors[i]))

    # Draw level and lives with contrasting backgrounds for visibility
    level_bg = pygame.Surface((100, 30), pygame.SRCALPHA)
    level_bg.fill((255, 255, 255, 180))
    screen.blit(level_bg, (20, 20))

    lives_bg = pygame.Surface((100, 30), pygame.SRCALPHA)
    lives_bg.fill((255, 255, 255, 180))
    screen.blit(lives_bg, (20, 50))

    level_text = font.render(f'Level: {level}', True, (0, 0, 0))
    lives_text = font.render(f'Lives: {lives}', True, (0, 0, 0))
    screen.blit(level_text, (20, 20))
    screen.blit(lives_text, (20, 50))

    return color_option_rects

def name_input_screen(screen, name=""):
    """Screen for entering player name"""
    screen.fill((255, 255, 255))
    
    title_text = large_font.render('Enter Your Name:', True, (0, 0, 0))
    name_text = large_font.render(name, True, (0, 0, 0))
    instruction_text = font.render('Press ENTER when done', True, (0, 0, 0))
    
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 3))
    screen.blit(name_text, (screen_width // 2 - name_text.get_width() // 2, screen_height // 2))
    screen.blit(instruction_text, (screen_width // 2 - instruction_text.get_width() // 2, 2 * screen_height // 3))

def game_over_screen(screen, score, reason):
    """Game over screen"""
    screen.fill((255, 255, 255))
    
    title_text = large_font.render('Game Over!', True, (0, 0, 0))
    reason_text = font.render(reason, True, (0, 0, 0))
    score_text = large_font.render(f'Score: {score}', True, (0, 0, 0))
    continue_text = font.render('Click anywhere to continue', True, (0, 0, 0))
    
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 3))
    screen.blit(reason_text, (screen_width // 2 - reason_text.get_width() // 2, screen_height // 3 + 50))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2))
    screen.blit(continue_text, (screen_width // 2 - continue_text.get_width() // 2, 2 * screen_height // 3))

def start_new_game():
    """Initialize a new game"""
    global color_sequence, level, lives, score, user_sequence, current_color_index, camera_manager
    
    level = 1
    lives = 3
    score = 0
    color_sequence = ColorSequence(level + 2)  # Start with 3 colors
    user_sequence = []
    current_color_index = 0
    
    # Initialize camera if needed
    if camera_manager is None:
        camera_manager = CameraManager()

def check_hand_selection(color_option_rects):
    """Check if hand is closed over any color option"""
    if camera_manager and camera_manager.pulse_detected:
        # Get hand position directly from camera manager
        hand_pos = camera_manager.get_hand_position()
        
        if hand_pos:
            x, y = hand_pos
            
            # Convert camera coordinates to screen coordinates
            if camera_manager.current_frame is not None:
                frame_h, frame_w = camera_manager.current_frame.shape[:2]
                
                # Flip coordinates
                
                # Flip x coordinate horizontally and scale coordinates
                screen_x = int((frame_w - x) * screen_width / frame_w)  # Flip x coordinate
                screen_y = int(y * screen_height / frame_h)
                
                # Debug visualization - draw a marker at detected position
                pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), 15, 4)
                
                # Check if hand position is over any color option
                for rect, color in color_option_rects:
                    if rect.collidepoint(screen_x, screen_y):
                        # Reset detection to avoid multiple selections
                        camera_manager.pulse_detected = False
                        # Visual feedback
                        pygame.draw.rect(screen, (0, 255, 0), rect, 4)
                        pygame.display.update()
                        pygame.time.delay(2000)  # Briefly show selection
                        return color
    
    return None
def camera_frame_to_pygame(frame):
    """Convert OpenCV camera frame to Pygame surface"""
    if frame is None:
        return None

    # Convert from BGR (OpenCV) to RGB (Pygame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Transpose dimensions to match Pygame's format
    frame = np.rot90(frame)

    # Create Pygame surface
    pygame_surface = pygame.surfarray.make_surface(frame)

    # Scale to fit screen
    pygame_surface = pygame.transform.scale(pygame_surface, (screen_width, screen_height))

    return pygame_surface

    
# Main game loop
running = True
clock = pygame.time.Clock()
    
while running:
        # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == STATE_MENU:
                    running = False
                else:
                    state = STATE_MENU

            # Handle name input
            if state == STATE_NAME_INPUT:
                if event.key == pygame.K_RETURN:
                    if player_name:
                        score_table.add_score(player_name, score)
                        state = STATE_MENU
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    # Add character if it's alphanumeric and name isn't too long
                    if event.unicode.isalnum() and len(player_name) < 10:
                        player_name += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == STATE_MENU:
                play_rect, score_rect = menu_buttons()
                if play_rect.collidepoint(event.pos):
                    start_new_game()
                    state = STATE_PLAY
                    # Show sequence after a short delay
                    pygame.display.flip()
                    pygame.time.delay(1000)
                    show_sequence(screen, color_sequence)
                elif score_rect.collidepoint(event.pos):
                    state = STATE_SCORE

            elif state == STATE_SCORE:
                back_rect = draw_score_table(screen, score_table)
                if back_rect.collidepoint(event.pos):
                    state = STATE_MENU

            elif state == STATE_GAME_OVER:
                state = STATE_NAME_INPUT

    # First, display camera feed as background if available
    if camera_manager and camera_manager.get_current_frame() is not None:
        camera_frame = camera_manager.get_current_frame()
        camera_surface = camera_frame_to_pygame(camera_frame)
        if camera_surface:
            screen.blit(camera_surface, (0, 0))
    else:
        screen.fill((255, 255, 255))  # Fallback to white if camera not available
    
        # Add semi-transparent overlay for better readability
    if state != STATE_MENU:  # Keep menu without overlay for better camera visibility
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 150))  # White with alpha
        screen.blit(overlay, (0, 0))
    
        # Now render the current game state on top of the camera feed
    if state == STATE_MENU:
        # Draw title with contrasting shadow for visibility
        title = large_font.render('Balloon Sequence Game', True, (0, 0, 0))
        shadow = large_font.render('Balloon Sequence Game', True, (255, 255, 255))
        screen.blit(shadow, (screen_width // 2 - title.get_width() // 2 + 2, screen_height // 4 + 2))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, screen_height // 4))
        menu_buttons()

    elif state == STATE_SCORE:
        draw_score_table(screen, score_table)
    
    elif state == STATE_PLAY:
        # Show balloons and check for selections
        color_option_rects = show_balloons_to_guess(screen, color_sequence, current_color_index)
    
        # Check if user made a selection with hand gesture
        selected_color = check_hand_selection(color_option_rects)
    
        if selected_color:
            user_sequence.append(selected_color)
    
        # Check if the selection is correct
            if selected_color != color_sequence.get_sequence()[current_color_index]:
                lives -= 1
                if lives <= 0:
                    game_over_reason = "Out of lives!"
                    state = STATE_GAME_OVER
                else:
                    # Reset current sequence to try again
                    user_sequence = []
                    current_color_index = 0
                    # Show correct sequence again
                    pygame.time.delay(500)
                    show_sequence(screen, color_sequence)
            else:
                current_color_index += 1
    
                # Check if sequence is complete
                if current_color_index >= color_sequence.get_length():
                    score += level * 10  # Award points
                    level += 1  # Increase level
    
                    # Create new sequence for next level
                    color_sequence = ColorSequence(level + 2)
                    user_sequence = []
                    current_color_index = 0
    
                    # Show new sequence after a short delay
                    pygame.time.delay(1000)
                    show_sequence(screen, color_sequence)
    
    elif state == STATE_NAME_INPUT:
        name_input_screen(screen, player_name)
    
    elif state == STATE_GAME_OVER:
        game_over_screen(screen, score, game_over_reason)
    
    pygame.display.flip()
    clock.tick(30)

# Clean up
if camera_manager is not None:
    camera_manager.stop()
pygame.quit()