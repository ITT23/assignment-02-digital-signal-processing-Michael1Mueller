import pyglet
import pyaudio

# Set up audio stream
# reduce chunk size and sampling rate for lower latency --> already low latency on my device
CHUNK_SIZE = 1024  # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Audio sampling rate (Hz)
# Pyglet initialization
WINDOW_WIDTH = 100
WINDOW_HEIGHT = 300

batch = pyglet.graphics.Batch()