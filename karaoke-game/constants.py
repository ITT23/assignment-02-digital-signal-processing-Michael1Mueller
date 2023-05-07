import pyglet
import pyaudio
import os

# Set up audio stream
# reduce chunk size and sampling rate for lower latency --> already low latency on my device
CHUNK_SIZE = 1024  # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Audio sampling rate (Hz)
# Pyglet initialization
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

FONT_SIZE = 32
FONT_SIZE_SMALL = 8
# range for detect similarity
ACCEPTANCE_RANGE = 10

# guitar strings frequencies https://de.wikipedia.org/wiki/Stimmen_einer_Gitarre
HIGH_E = 330
H = 246
G = 196
D = 146
A = 110
LOW_E = 82

path_background = os.path.join(".", "images", "singing.png")
path_wave = os.path.join(".", "sounds", "correct.wav")

batch = pyglet.graphics.Batch()