import pygame
import random
import cv2
import numpy as np
from src.ColorSequence import ColorSequence
from src.CloseHand import CameraManager
from src.ScoreTable import ScoreTable

# Inicialización de Pygame
pygame.init()

# Definir tamaño de la pantalla
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Secuencia de Globos")

# Fuente para los botones
font = pygame.font.SysFont('Arial', 24)

# Importar los colores y el neutro
colors = ['red', 'green', 'blue', 'yellow', 'pink', 'gray']
for i, color in enumerate(colors):
	colors[i] = pygame.image.load(f'images/Colors/{color}.png')  #colors[i] = pygame.transform.scale(colors[i], (colors[i].get_width() // 2, colors[i].get_height() // 2))

"""# Prueba de puntajes
score_table = ScoreTable()
score_table.add_score('Player1', 100)
score_table.add_score('Player2', 200)
score_table.add_score('Player3', 150)
score_table.add_score('Player4', 300)
score_table.add_score('Player5', 250)
"""


# Función para dibujar los botones con sus etiquetas
def menu_buttons():
	play_button = pygame.image.load('images/Buttons/play.png')
	play_button = pygame.transform.scale(play_button, (play_button.get_width() * 2, play_button.get_height() * 2))
	screen.blit(play_button, (screen_width // 4 - play_button.get_width() // 2, screen_height - play_button.get_height() - 50))
	score_button = pygame.image.load('images/Buttons/score.png')
	score_button = pygame.transform.scale(score_button, (score_button.get_width() * 2, score_button.get_height() * 2))
	screen.blit(score_button, (3 * screen_width // 4 - score_button.get_width() // 2, screen_height - score_button.get_height() - 50))


# Función para dibujar la tabla de puntajes
def draw_score_table(screen, score_table):
	# Define fonts and colors
	title_font = pygame.font.SysFont('Arial', 36)
	score_font = pygame.font.SysFont('Arial', 24)
	title_color = (0, 0, 0)
	score_color = (0, 0, 0)

	# Draw title
	title_text = title_font.render('Score Table', True, title_color)
	screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

	# Draw scores for top 5 levels
	score_table.order_scores()
	top_scores = score_table.get_top_scores(5)
	for i, (name, score) in enumerate(top_scores.items()):
		level_text = score_font.render(f'TOP {i + 1}: {name} - {score}', True, score_color)
		screen.blit(level_text, (screen_width // 2 - level_text.get_width() // 2, 150 + i * 50))


# Función para introducir nombre


# Función para mostrar la secuencia de colores
def show_sequence(screen, color_sequence):
	# Mostrar al centro de la pantalla durante x segundos cada imagen
	sequence = color_sequence.get_sequence()
	for color_name in sequence:
		# Show color
		screen.fill((255, 255, 255))
		color_idx = ['red', 'green', 'blue', 'yellow', 'pink', 'gray'].index(color_name)
		color_img = colors[color_idx]
		screen.blit(color_img, (screen_width // 2 - color_img.get_width() // 2, screen_height // 2 - color_img.get_height() // 2))
		pygame.display.flip()
		pygame.time.delay(1000)  # Show for 1 second

		# Hide color (white screen)
		screen.fill((255, 255, 255))
		pygame.display.flip()
		pygame.time.delay(1000)


# Función para mostrar la cantidad de globos a adivinar y los posibles colores a seleccionar
def show_balloons_to_guess(screen, color_sequence):
	# Mostrar al centro de la pantalla x globos grises, dependiendo la longitud de la secuencia
	sequence = color_sequence.get_sequence()
	for i in range(len(sequence)):
		# Show gray balloon
		color_img = colors[-1]
		screen.blit(color_img, (screen_width // 2 - color_img.get_width() // 2 + i * 50 - (len(sequence) - 1) * 25, screen_height // 2 - color_img.get_height() // 2 - 50))

	# Mostrar En la parte inferior de la pantalla todos los colores menos el gris
	for i in range(len(colors) - 1):
		color_img = colors[i]
		screen.blit(color_img, (i * color_img.get_width() + (screen_width - (len(colors) - 1) * color_img.get_width()) // 2, screen_height - color_img.get_height() - 50))
	pygame.display.flip()



# Función principal del juego
def game_loop():
	color_sequence = ColorSequence(9)
	show_sequence_once = True
	running = True
	while running:
		screen.fill((255, 255, 255))  # Rellenar la pantalla con blanco

		#Prueba de botones
		#menu_buttons()

		#Prueba de puntajes
		#draw_score_table(screen, score_table)

		#Prueba de secuencia de colores
		"""
		if show_sequence_once:
			show_sequence(screen, color_sequence)
			again_font = pygame.font.SysFont('Arial', 36)
			again_text = again_font.render('Again', True, (0, 0, 0))
			screen.blit(again_text, (screen_width // 2 - again_text.get_width() // 2,
	                         screen_height // 2 + 100))
			pygame.display.flip()
			show_sequence(screen, color_sequence)
			show_sequence_once = False
		"""

		# Prueba de globos a adivinar
		#	show_balloons_to_guess(screen, color_sequence)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		pygame.display.flip()  # Actualizar la pantalla

	pygame.quit()


# Iniciar el juego
game_loop()
