""" This is a learning game template """

# --- import modules ---
import os
import json
import io
import pygame
import random
from gtts import gTTS

# --- Global Constants and Configuration ---
CONFIG_FILE_PATH = "game_config.json"
SOUND_ACTION_FILE = "assets/mouse_click.wav"
SOUND_ERROR_FILE = "assets/nogood.wav"
FULLSCREEN_RESOLUTION = (1920, 1080)
WINDOWED_RESOLUTION = (1024, 768)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_RED = "darkred"
DARK_GREEN = "darkgreen"
DARK_BLUE = "darkblue"
DARK_GRAY = "darkgray"
LIGHT_GRAY = (220, 220, 220)
LIGHT_YELLOW = (255, 255, 200)
BOX_BG_COLOR = LIGHT_GRAY
PROMPT_BOX_COLOR =  BOX_BG_COLOR
HIGHLIGHT_COLOR = YELLOW
TEXT_COLOR = BLACK
TEXT_BOX_COLOR = WHITE

# --- Helper Functions ---
def load_config():
    """Loads configuration from JSON file or uses default values."""
    try:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = json.load(config_file)
    except Exception as e:
        print(f"Error loading configuration. Using default lists. {e}")
        config = {}
    return config

def toggle_fullscreen(screen, screen_width, screen_height, fullscreen):
    """Toggles between fullscreen and windowed mode."""
    is_fullscreen = screen.get_flags() & pygame.FULLSCREEN
    if not is_fullscreen:
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((screen_width, screen_height))
    fullscreen = not is_fullscreen
    return fullscreen, screen

def load_sound(filepath):
    """Loads a sound file and handles potential errors."""
    try:
        sound = pygame.mixer.Sound(filepath)
        return sound
    except pygame.error as e:
        print(f"Error loading sound: {e}")
        return None

def generate_speech_sound(text):
    """Generates and returns a Pygame sound object from text using gTTS."""
    buffer = io.BytesIO()
    tts = gTTS(text=text, lang='en')
    tts.write_to_fp(buffer)
    buffer.seek(0)
    sound = pygame.mixer.Sound(buffer)
    return sound

def generate_speech_sound2(filepath, text):
    # generate only once
    if os.path.exists(filepath):
        print(f"Loading from sound file \"{filepath}\"...")
        try:
            sound = pygame.mixer.Sound(filepath)
            return sound
        except pygame.error as e:
            print(f"Error loading sound: {e}")
            return None
    else:
        print(f"Sound file, {filepath} doesn't exists, generating...")
        tts = gTTS(text=text, lang='en')
        tts.save(filepath)
        pygame.time.wait(500)
        sound = pygame.mixer.Sound(filepath)
        return sound

def render_text_wrapped(text, font, color, max_width):
    """Renders text wrapped to a given width."""
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        test_width, _ = font.size(test_line)
        if test_width <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))

    surfaces = []
    total_height = 0
    for line in lines:
        line_surface = font.render(line, True, color)
        surfaces.append(line_surface)
        total_height += line_surface.get_height() + 5

    combined_surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
    y = 0
    for line_surface in surfaces:
        combined_surface.blit(line_surface, (0, y))
        y += line_surface.get_height() + 5

    return combined_surface

class Styled_Text_Box:
    def __init__(self, surface, rect, text_surface, bg_color, padding=15, border_width=2, border_color=BLACK):
        self.surface = surface
        self.rect = rect
        self.bg_color = bg_color
        self.border_width = border_width
        self.border_color = border_color
        self.text_surface = text_surface
        self.padding = padding

    def draw(self):
        pygame.draw.rect(self.surface, self.bg_color, self.rect) # Background
        pygame.draw.rect(self.surface, self.border_color, self.rect, self.border_width) # Border
        text_rect = self.text_surface.get_rect(topleft=(self.rect.x + self.padding, self.rect.y + self.padding)) # Position text with padding
        self.surface.blit(self.text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Button:
    """Button UI element."""
    def __init__(self, x, y, text, width=200, height=50, color=DARK_GREEN):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.color = color
        self.text_color = WHITE
        self.text = text
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        rendered_text = font.render(self.text, True, self.text_color)
        text_rect = rendered_text.get_rect(center=self.rect.center) # Center the text in the button
        screen.blit(rendered_text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# --- Game Class ---
class MainGame:
    """Main class to manage the Game."""
    def __init__(self):
        pygame.init()

        # graphics init
        self.screen_width = FULLSCREEN_RESOLUTION[0]
        self.screen_height = FULLSCREEN_RESOLUTION[1]
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        # self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Game Title")
        self.fullscreen = True

        # fonts init
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 36)
        self.game_font = pygame.font.SysFont("arial", 52)

        # common variables init
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_mode = "menu"
        self.play_welcome_sound = True

        # --- start of game variables ---

        # Fonts
        self.normal_font = pygame.font.Font(None, 74)
        self.big_font = pygame.font.Font(None, 96)
        self.button_font = pygame.font.Font(None, 50)
        self.score_font = pygame.font.Font(None, 50)

        # Game variables
        self.num_choices = 2 # Customizable number of choices
        self.min_num_choices = 1 # Minimum number of choices
        self.max_num_choices = 5 # Maximum number of choices
        self.square_size = self.screen_width // self.max_num_choices - 10  # Square size based on max number of choices

        self.well_done_sound = generate_speech_sound("You did it! Good job!")
        self.click_sound = pygame.mixer.Sound("assets/mouse_click.wav")
        self.right_sounds = [
            generate_speech_sound("Awesome!"),
            generate_speech_sound("Excellent!"),
            generate_speech_sound("Good!"),
            generate_speech_sound("Great!"),
            generate_speech_sound("Right!"),
            generate_speech_sound("Very good!"),
            generate_speech_sound("Yes!")
            ]
        self.wrong_sounds = [
            generate_speech_sound("Bad!"),
            generate_speech_sound("No!"),
            generate_speech_sound("Not good!"),
            generate_speech_sound("Wrong!"),
            generate_speech_sound("No good!"),
            generate_speech_sound("Not right!")
        ]

        self.happy_face = pygame.image.load("assets/happy_face.png") 
        self.sad_face = pygame.image.load("assets/red_sad_face.png")     
        self.happy_face = pygame.transform.scale(self.happy_face, (200, 200))  
        self.sad_face = pygame.transform.scale(self.sad_face, (200, 200))      

        self.color_items = {}
        self.color_items = {
            "black": { 
                "value" : (0, 0, 0),
                "sound" : pygame.mixer.Sound("assets/black.wav"),
                "toggle" : True
            },
            "white": { 
                "value" : (255, 255, 255),
                "sound" : pygame.mixer.Sound("assets/white.wav"),
                "toggle" : True
            },
            "red": { 
                "value" : (255, 0, 0),
                "sound" : pygame.mixer.Sound("assets/red.wav"),
                "toggle" : False
            },
            "green": { 
                "value" : (0, 255, 0),
                "sound" : pygame.mixer.Sound("assets/green.wav"),
                "toggle" : False
            },
            "blue": { 
                "value" : (0, 0, 255),
                "sound" : pygame.mixer.Sound("assets/blue.wav"),
                "toggle" : False
            },
            "yellow": { 
                "value" : (255, 255, 0),
                "sound" : pygame.mixer.Sound("assets/yellow.wav"),
                "toggle" : False
            },
            "purple": { 
                "value" : (128, 0, 128),
                "sound" : pygame.mixer.Sound("assets/purple.wav"),
                "toggle" : False
            },
            "pink": { 
                "value" : (255, 182, 193),
                "sound" : pygame.mixer.Sound("assets/pink.wav"),
                "toggle" : False
            }
        }


                # --- end of game variables ---

        self.COLOR_NAMES = list(self.color_items.keys())
        self.force_correct_color = None
    def run(self):
        """Main game loop."""
        while self.running:
            if self.game_mode == "menu":
                print(self.game_mode)
                self.run_menu()
            elif self.game_mode == "colors":
                self.run_colors()
            elif self.game_mode == "options":
                self.run_options()
            self.clock.tick(60)
        pygame.quit()

    def run_menu(self):
        """Handles the main menu loop."""
        # Title text top center
        title_text = self.title_font.render("The Learning Colors Game", True, DARK_BLUE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 8))

        # Prompt text lower left corner
        prompt_text = self.text_font.render("Hint: Tap or click on a button to start.", True, WHITE)
        prompt_rect = prompt_text.get_rect(bottomleft=(20, self.screen_height - 20))

        # Arrange buttons in a vertical stack centered on screen
        button_width = 300
        button_height = 50
        spacing = 20
        total_height = 4 * button_height + 3 * spacing
        start_y = self.screen_height // 2 - total_height // 2
        center_x = self.screen_width // 2 - button_width // 2

        menu_colors_button = Button(center_x, start_y, "Find Colors", button_width, button_height, DARK_GREEN)
        menu_options_button = Button(center_x, start_y + (button_height + spacing), "Options", button_width, button_height, DARK_GREEN)
        menu_quit_button = Button(center_x, start_y + (button_height + spacing) * 2, "Quit", button_width, button_height, DARK_RED)

        play_menu_sound = False
        while self.game_mode == "menu" and self.running:
            self.clock.tick(60)
            self.screen.fill(DARK_GRAY)

            # Draw title and prompt at the top
            pygame.draw.rect(self.screen, LIGHT_YELLOW, title_rect.inflate(20, 10))
            self.screen.blit(title_text, title_rect)
            self.screen.blit(prompt_text, prompt_rect)

            # Draw buttons in center
            menu_colors_button.draw(self.screen, self.button_font)
            menu_options_button.draw(self.screen, self.button_font)
            menu_quit_button.draw(self.screen, self.button_font)

            pygame.display.flip()

            # Play welcome sound once
            if self.play_welcome_sound:
                welcome_sound = generate_speech_sound("Welcome to Learning Colors Game!")
                welcome_sound.play()
                self.play_welcome_sound = False

            if play_menu_sound:
                menu_sound = generate_speech_sound("Menu screen sound goes here...")
                menu_sound.play()
                play_menu_sound = False
                while pygame.mixer.get_busy():
                    self.clock.tick(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT:
                        self.fullscreen, self.screen = toggle_fullscreen(self.screen, self.screen_width, self.screen_height, self.fullscreen)
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_colors_button.is_clicked(event.pos):
                        self.click_sound.play()
                        self.game_mode = "options"
                    elif menu_options_button.is_clicked(event.pos):
                        self.click_sound.play()
                        self.game_mode = "options"
                    elif menu_quit_button.is_clicked(event.pos):
                        self.click_sound.play()
                        self.running = False

    def run_options(self):
        """Handles the words mode loop."""
        # Prompt text lower left corner
        prompt_text = self.text_font.render("Hint: Adjust the goal of the game.", True, WHITE)
        prompt_rect = prompt_text.get_rect(bottomleft=(20, self.screen_height - 20))
        options_back_button = Button(self.screen_width - 200 - 20, 20, "Back", 200, 50, DARK_RED)

        # --- Start of game mode init section ---

        ok_button = Button(self.screen_width // 2 - 100, self.screen_height * 4 // 5, "OK", 200, 50, "darkgreen")
        opt_rect = {}
        force_opt_rect = {}
        opt_size = 50
        i = 0
        for acolor in self.COLOR_NAMES:
            opt_rect[acolor] = pygame.Rect((self.screen_width - opt_size * 1.25 * len(self.COLOR_NAMES)) // 2 + (i * opt_size * 1.25), self.screen_height * 2 // 5, opt_size, opt_size)
            force_opt_rect[acolor] = pygame.Rect((self.screen_width - opt_size * 1.25 * len(self.COLOR_NAMES)) // 2 + (i * opt_size * 1.25), self.screen_height * 3 // 5, opt_size, opt_size)
            i += 1

        # --- End of game mode init section ---

        while self.game_mode == "options" and self.running:
            self.clock.tick(60)
            self.screen.fill(DARK_GRAY)
            self.screen.blit(prompt_text, prompt_rect)
            options_back_button.draw(self.screen, self.button_font)

            # --- Start of frame creation ---

            # Section 0: Options title
            title_text = self.normal_font.render("Options", True, (0, 0, 0))
            self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 50))

            # Section 1. Option for number of choices
            num_choices_prompt_text = self.button_font.render(f"Number of choices: ", True, "white")
            self.screen.blit(num_choices_prompt_text, (self.screen_width // 2 - num_choices_prompt_text.get_width() // 2, self.screen_height * 1 // 5 - 50))
            num_choices_text = self.button_font.render(f"{self.num_choices}", True, "darkred")
            self.screen.blit(num_choices_text, (self.screen_width // 2 - num_choices_text.get_width() // 2, self.screen_height * 1 // 5 + 10))

            # Draw "+" button
            plus_button = Button(self.screen_width // 2 - 25 + 50, self.screen_height * 1 // 5, "+", 50, 50, "darkred")
            plus_button.draw(self.screen, self.button_font)
            # Draw "-" button
            minus_button = Button(self.screen_width // 2 - 25 - 50, self.screen_height * 1 // 5, "-", 50, 50, "darkred")
            minus_button.draw(self.screen, self.button_font)

            # Section 2. Option for available colors
            available_choices_text = self.button_font.render("Available choices: ", True, "white")
            self.screen.blit(available_choices_text, (self.screen_width // 2 - available_choices_text.get_width() // 2, self.screen_height * 2 // 5 - 50))
            # Draw option checkboxes
            for acolor in self.COLOR_NAMES:
                pygame.draw.rect(self.screen, acolor, opt_rect[acolor], 4)
                if self.color_items[acolor]["toggle"]:
                    # draw smaller box
                    pygame.draw.rect(self.screen, acolor, opt_rect[acolor].inflate(-10, -10))
                pygame.draw.rect(self.screen, acolor, force_opt_rect[acolor], 4)
                if self.force_correct_color == acolor:
                    # draw smaller box
                    pygame.draw.rect(self.screen, acolor, force_opt_rect[acolor].inflate(-10, -10))

            # Section 3: Option to force only 1 possible right color
            only_choice_text = self.button_font.render("Force choice: ", True, "white")
            self.screen.blit(only_choice_text, (self.screen_width // 2 - only_choice_text.get_width() // 2, self.screen_height * 3 // 5 - 50))

            # Section 4: Draw "OK" button
            ok_button.draw(self.screen, self.button_font)

            # --- End of frame creation ---

            pygame.display.flip()

            # --- Event handlers ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # Toggle between fullscreen and windowed modes
                    if event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT:
                        self.fullscreen, self.screen = toggle_fullscreen(self.screen, self.screen_width, self.screen_height, self.fullscreen)
                    elif event.key == pygame.K_ESCAPE:
                            self.game_mode = "menu"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if options_back_button.is_clicked(event.pos):
                        self.click_sound.play()
                        self.game_mode = "menu"
                    if ok_button.rect.collidepoint(x, y):
                        # Return to the title screen
                        self.click_sound.play()
                        self.game_mode = "colors"
                        # return
                    if plus_button.rect.collidepoint(x, y):
                        # Increase the number of choices
                        self.click_sound.play()
                        self.num_choices = min(self.num_choices + 1, self.max_num_choices)
                    if minus_button.rect.collidepoint(x, y):
                        # Decrease the number of choices
                        self.click_sound.play()
                        self.num_choices = max(self.num_choices - 1, self.min_num_choices)
                    for acolor in self.COLOR_NAMES:
                        if opt_rect[acolor].collidepoint(x, y):
                            self.click_sound.play()
                            self.color_items[acolor]["toggle"] = not self.color_items[acolor]["toggle"]
                            num_available_colors = sum(1 for item in self.color_items.values() if item["toggle"])
                            if num_available_colors < self.num_choices:
                                self.color_items[acolor]["toggle"] = not self.color_items[acolor]["toggle"]
                            if not self.color_items[acolor]["toggle"] and self.force_correct_color == acolor:
                                self.force_correct_color = None
                        if force_opt_rect[acolor].collidepoint(x, y):
                            self.click_sound.play()
                            if self.force_correct_color == acolor:
                                self.force_correct_color = None
                            elif self.color_items[acolor]["toggle"]:
                                self.force_correct_color = acolor

    def generate_square_positions(self, num_choices):
        positions = []
        # Dynamic layout for numbers of choices
        spacing = self.screen_width // num_choices - self.square_size
        total_width = num_choices * self.square_size + (num_choices - 1) * spacing
        start_x = (self.screen_width - total_width) // 2
        start_y = self.screen_height // 2 - self.square_size
        for i in range(num_choices):
            x = start_x + i * (self.square_size + spacing)
            y = start_y
            positions.append((x, y))
        return positions

    # Function to generate squares with only one correct choice
    def generate_squares(self, num_choices):
        really_available_colors = [c for c in self.COLOR_NAMES if self.color_items[c]["toggle"]]
        if self.force_correct_color:
            correct_color = self.force_correct_color
        else:
            correct_color = random.choice(really_available_colors)
        # Ensure the correct color is only present once
        incorrect_colors = random.sample([c for c in really_available_colors if c != correct_color], num_choices - 1)  # Pick incorrect colors
        square_colors = incorrect_colors + [correct_color]  # Combine incorrect and correct colors
        random.shuffle(square_colors)  # Shuffle to randomize positions
        return correct_color, square_colors

    def run_colors(self):
        """Handles the words mode loop."""
        # Back button upper right corner
        colors_back_button = Button(self.screen_width - 200 - 20, 20, "Back", 200, 50, DARK_RED)

        # Prompt text lower left corner
        prompt_text = self.text_font.render("Hint: Tap or click on a color square to answer.", True, WHITE)
        prompt_rect = prompt_text.get_rect(bottomleft=(20, self.screen_height - 20))

        # --- Start of game mode init section ---

        # new game variables
        question_num = 0
        real_score = 0
        target_question_num = 10
        wrong_answer = False
        round_over = False
        new_question = True
        result = None
        show_next_button = False
        highlight_x, highlight_y = 0, 0

        # Initialize the first question
        square_positions = self.generate_square_positions(self.num_choices)
        correct_color, square_colors = self.generate_squares(self.num_choices)

        # Button definitions
        next_button = Button(self.screen_width - 200 - 20, self.screen_height - 50 - 20, "Next", 200, 50)
        new_game_button = Button(self.screen_width // 2 - 200 - 10, self.screen_height // 2 + 50, "New Game", 200, 50)
        exit_game_button = Button(self.screen_width // 2 + 10, self.screen_height // 2 + 50, "Exit Game", 200, 50, "darkred")


        # --- End of game mode init section ---

        while self.game_mode == "colors" and self.running:
            self.clock.tick(60)
            self.screen.fill(DARK_GRAY)
            self.screen.blit(prompt_text, prompt_rect)
            colors_back_button.draw(self.screen, self.button_font)

            # --- Start of frame creation ---
            # Display the score
            score_text = self.score_font.render(f"Question {question_num + 1: >2}", True, (0, 0, 0))
            self.screen.blit(score_text, (20, 20))

            # Display the color name to select
            game_text = self.normal_font.render(f"Find Color {correct_color.capitalize()}", True, "black")
            game_rect = pygame.Rect(self.screen_width // 2 - game_text.get_width() // 2 - 2, 50 - 2, game_text.get_width() + 4, game_text.get_height() + 4)
            pygame.draw.rect(self.screen, "gold", game_rect.inflate(0, 0))
            self.screen.blit(game_text, (self.screen_width // 2 - game_text.get_width() // 2, 50))

            # Draw the squares
            for i, pos in enumerate(square_positions):
                pygame.draw.rect(self.screen, self.color_items[square_colors[i]]["value"], (*pos, self.square_size, self.square_size))

            # Display result
            if result is not None:
                pygame.draw.rect(self.screen, "brown", (highlight_x - 10, highlight_y - 10, self.square_size + 20, self.square_size + 20),5)    
                result_text = self.big_font.render(result, True, pygame.Color("green" if result == "RIGHT !" else "red"))
                self.screen.blit(result_text, (self.screen_width // 2 - result_text.get_width() // 2, self.screen_height - self.screen_height // 9))
                # Display emoji based on result
                if result == "RIGHT !":
                    self.screen.blit(self.happy_face, (self.screen_width // 2 - 100, self.screen_height // 2 + 50))
                else:
                    self.screen.blit(self.sad_face, (self.screen_width // 2 - 100, self.screen_height // 2 + 50))

            # Draw the "Next" button if the round is over
            if show_next_button and not round_over:
                next_button.draw(self.screen, self.button_font)

            # Play voice prompt
            if new_question:
                new_question = False
                question_prompt = random.choice([f"Find {correct_color}!", f"Where is {correct_color}?", f"Point to {correct_color}!"])
                generate_speech_sound(question_prompt).play()
                # pygame.time.delay(250)
                # self.title_sound.play() 
                # pygame.time.delay(500)
                # self.color_items[correct_color]["sound"].play() 

            if round_over:
                # Display the game over screen
                pygame.time.delay(1000)
                self.screen.fill((128, 128, 128))
                final_score_text = self.score_font.render(f"Final Score: {round(real_score / 10 * 100)} %", True, pygame.Color("black"))
                self.screen.blit(final_score_text, (self.screen_width // 2 - final_score_text.get_width() // 2, self.screen_height * 1 // 5))
                well_done_text = self.normal_font.render("Well Done!", True, pygame.color.Color("gold"))
                self.screen.blit(well_done_text, (self.screen_width // 2 - well_done_text.get_width() // 2, self.screen_height // 2 - 50))
                self.well_done_sound.play()
                new_game_button.draw(self.screen, self.button_font)
                exit_game_button.draw(self.screen, self.button_font)
                pygame.display.flip()

                # Event handling for game over screen
                round_over_waiting = True
                while round_over_waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            x, y = event.pos
                            if new_game_button.rect.collidepoint(x, y):
                                # Reset the game
                                self.click_sound.play()
                                self.result = None
                                question_num = 0
                                real_score = 0 
                                round_over = False
                                self.game_mode = "options"
                                correct_color, square_colors = self.generate_squares(self.num_choices)
                                show_next_button = False
                                round_over_waiting = False
                            elif exit_game_button.rect.collidepoint(x, y):
                                self.click_sound.play()
                                self.running = False  # Exit the game
                                round_over_waiting = False
                                
            # --- End of frame creation ---

            # --- Event handlers ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # Toggle between fullscreen and windowed modes
                    if event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT:
                        self.fullscreen, self.screen = toggle_fullscreen(self.screen, self.screen_width, self.screen_height, self.fullscreen)
                    elif event.key == pygame.K_ESCAPE:
                        self.game_mode = "menu"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if colors_back_button.is_clicked(event.pos):
                        self.click_sound.play()
                        self.game_mode = "menu"
                    x, y = event.pos
                    if show_next_button and next_button.rect.collidepoint(x, y):
                        # Proceed to the next round
                        print('click next button')
                        self.click_sound.play()
                        show_next_button = False
                        wrong_answer = False
                        result = None
                        correct_color, square_colors = self.generate_squares(self.num_choices)
                        new_question = True
                    elif not show_next_button:
                        for i, pos in enumerate(square_positions):
                            if pos[0] <= x <= pos[0] + self.square_size and pos[1] <= y <= pos[1] + self.square_size:
                                # set highlight pos for draw_screen()
                                highlight_x, highlight_y = pos
                                if square_colors[i] == correct_color:
                                    result = "RIGHT !"
                                    random.choice(self.right_sounds).play()
                                    show_next_button = True
                                    question_num += 1  # Increase score
                                    if not wrong_answer:
                                        real_score += 1 
                                    if question_num >= target_question_num:
                                        round_over = True
                                    else:
                                        next_button.draw(self.screen, self.button_font)
                                else:
                                    result = "WRONG !"
                                    random.choice(self.wrong_sounds).play()
                                    show_next_button = False
                                    wrong_answer = True

            pygame.display.flip()

if __name__ == '__main__':
    game = MainGame()
    game.run()
