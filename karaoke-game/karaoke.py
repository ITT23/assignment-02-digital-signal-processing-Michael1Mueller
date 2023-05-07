import random

import numpy.fft
import pyaudio
import numpy as np
from matplotlib import pyplot as plt
from scipy import signal
import pyglet
from pyglet import window
from constants import WINDOW_HEIGHT, WINDOW_WIDTH, RATE, FORMAT, CHANNELS, CHUNK_SIZE, batch, path_background, FONT_SIZE, \
                      ACCEPTANCE_RANGE, path_wave
import wave

p = pyaudio.PyAudio()
window = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)


background = pyglet.graphics.Group(0)
foreground = pyglet.graphics.Group(1)

freq_to_reach = 440
actual_freq = 0

# background img from
# https://c8.alamy.com/comp/HN8HK3/music-notes-border-musical-background-music-style-round-shape-frame-HN8HK3.jpg
background_img = pyglet.image.load(path_background)
background = pyglet.sprite.Sprite(background_img, x=0, y=0, batch=batch, group=background)

freq_to_reach_label = pyglet.text.Label(text=f"Diese Frequenz gilt es zu erreichen: {freq_to_reach}Hz", x=10, y=380,
                                    color=(0, 0, 0, 255), batch=batch, group=foreground)

freq_actual_label_static = pyglet.text.Label(text="Deine aktuelle Frequenz: ", x=110, y=220,
                                             color=(0, 0, 0, 255), batch=batch, group=foreground)

freq_actual_label = pyglet.text.Label(text=f"{actual_freq} Hz", x=160, y=160, font_size=FONT_SIZE,
                                      color=(0, 0, 0, 255), batch=batch, group=foreground)

exit_label = pyglet.text.Label(text="Press Q to Exit Game", x=10, y=20,
                               color=(0, 0, 0, 255), batch=batch, group=foreground)


@window.event
def on_draw():
    window.clear()
    batch.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        window.close()


def get_random_freq():
    global freq_to_reach
    rand_freq = random.randint(200, 1400)
    freq_to_reach = rand_freq
    freq_to_reach_label.text = f"Diese Frequenz gilt es zu erreichen: {freq_to_reach}Hz"


def compare_freqs(current_freq):
    if freq_to_reach-ACCEPTANCE_RANGE < current_freq < freq_to_reach+ACCEPTANCE_RANGE:
        get_random_freq()
        play_sound()


# https://stackoverflow.com/questions/6951046/how-to-play-an-audiofile-with-pyaudio
def play_sound():
    # sound from https://mixkit.co/free-sound-effects/game/
    wf = wave.open(path_wave, "rb")
    wav_stream = p.open(format=
                        p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

    # read data (based on the chunk size)
    data = wf.readframes(CHUNK_SIZE)

    # play stream (looping from beginning of file to the end)
    while data:
        # writing to the stream is what *actually* plays the sound.
        wav_stream.write(data)
        data = wf.readframes(CHUNK_SIZE)

    wf.close()

# print info about audio devices
# let user select audio device
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

print('select audio device:')
input_device = int(input())

# open audio input stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                input_device_index=input_device)


kernel = signal.gaussian(20, 10)  # create a kernel
kernel /= np.sum(kernel)  # normalize the kernel so it does not affect the signal's amplitude


# continuously capture and plot audio signal
def read_audio_stream(dt):
    global actual_freq
    # Read audio data from stream
    data = stream.read(CHUNK_SIZE)

    # Convert audio data to numpy array
    data = np.frombuffer(data, dtype=np.int16)
    data_noise_reduction = np.convolve(data, kernel, 'same')  # apply the kernel to the signal

    spectrum = np.abs(np.fft.fft(data_noise_reduction))

    frequencies = np.fft.fftfreq(len(data_noise_reduction), 1/RATE)

    mask = frequencies >= 0

    spectrum = spectrum[mask]
    frequencies = frequencies[mask]

    main_freq_index = np.argmax(spectrum)
    actual_freq = frequencies[main_freq_index]
    compare_freqs(actual_freq)
    freq_actual_label.text = f"{int(actual_freq)} Hz"


pyglet.clock.schedule_interval(read_audio_stream, 0.01)

pyglet.app.run()