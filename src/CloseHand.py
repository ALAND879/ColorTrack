import cv2
import threading
import numpy as np
from cvzone.HandTrackingModule import HandDetector

class CameraManager:
	def __init__(self):
		self.cap = cv2.VideoCapture(0)
		self.detector = HandDetector(detectionCon=0.8, maxHands=1)
		self.pulse_detected = False
		self.running = True

		# Iniciar el hilo de detección
		self.thread = threading.Thread(target=self._detect_pulse, daemon=True)
		self.thread.start()

	def _detect_pulse(self):
		# Definir conexiones de los dedos (según Mediapipe)
		connections = [
			(0, 1), (1, 2), (2, 3), (3, 4),   # Pulgar
			(0, 5), (5, 6), (6, 7), (7, 8),   # Índice
			(0, 9), (9, 10), (10, 11), (11, 12),  # Medio
			(0, 13), (13, 14), (14, 15), (15, 16),  # Anular
			(0, 17), (17, 18), (18, 19), (19, 20)  # Meñique
		]

		while self.running:
			ret, frame = self.cap.read()
			if not ret:
				continue

			# Crear fondo negro (480x640)
			black_frame = np.zeros((480, 640, 3), dtype=np.uint8)

			hands, _ = self.detector.findHands(frame, draw=False)

			if hands:
				hand1 = hands[0]
				landmarks = hand1["lmList"]  # Lista de landmarks (x, y, z)

				# Dibujar puntos (landmarks)
				for x, y, _ in landmarks:
					cv2.circle(black_frame, (x, y), 5, (0, 255, 0), -1)

				# Dibujar conexiones (líneas entre landmarks)
				for p1, p2 in connections:
					x1, y1, _ = landmarks[p1]
					x2, y2, _ = landmarks[p2]
					cv2.line(black_frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

				# Detectar si la mano está cerrada
				fingers = self.detector.fingersUp(hand1)
				self.pulse_detected = all(f == 0 for f in fingers)

			# Mostrar la ventana con solo el esqueleto de la mano
			small_frame = cv2.resize(black_frame, (250, 200))  # Ajusta el tamaño según prefieras
			cv2.imshow("Hand Landmarks", small_frame)


			if cv2.waitKey(1) & 0xFF == ord('q'):
				self.stop()
				break

	def difficulty(self):
		while self.running:
			ret, frame = self.cap.read()
			if not ret:
				continue

			hands, _ = self.detector.findHands(frame, draw=False)

			if hands:
				hand1 = hands[0]
				fingers = self.detector.fingersUp(hand1)
				print(fingers)
				return fingers

			if cv2.waitKey(1) & 0xFF == ord('q'):
				self.stop()
				break

	def stop(self):
		"""Detiene la detección y libera la cámara"""
		self.running = False
		self.cap.release()
		cv2.destroyAllWindows()