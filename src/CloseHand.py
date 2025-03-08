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
		self.current_frame = None
		self.hands_data = None

		# Start detection thread
		self.thread = threading.Thread(target=self._detect_pulse, daemon=True)
		self.thread.start()

	def _detect_pulse(self):
		while self.running:
			ret, frame = self.cap.read()
			if not ret:
				continue

			# Process frame with hand detector
			hands, processed_frame = self.detector.findHands(frame)

			# Store the current frame for main window to use
			self.current_frame = processed_frame
			self.hands_data = hands

			if hands:
				hand1 = hands[0]
				# Detect if the hand is closed
				fingers = self.detector.fingersUp(hand1)
				self.pulse_detected = all(f == 0 for f in fingers)

			# No need to show a separate window - we'll draw in main pygame window
			if cv2.waitKey(1) & 0xFF == ord('q'):
				self.stop()
				break

	def get_hand_position(self):
		"""Returns the current position of the hand if detected"""
		if self.hands_data:
			hand = self.hands_data[0]
			return hand["center"]  # Returns (x, y) of palm center
		return None

	def get_current_frame(self):
		"""Returns the current camera frame with hand detection overlay"""
		return self.current_frame

	def stop(self):
		"""Stops detection and releases camera"""
		self.running = False
		if self.cap.isOpened():
			self.cap.release()
		cv2.destroyAllWindows()