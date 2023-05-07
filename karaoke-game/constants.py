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

ACCEPTANCE_RANGE = 30

path_background = os.path.join(".", "images", "singing.png")
path_wave = os.path.join(".", "sounds", "correct.wav")

batch = pyglet.graphics.Batch()