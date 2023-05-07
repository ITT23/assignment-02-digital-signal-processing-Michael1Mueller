import random
import numpy.fft
import pyaudio
import numpy as np
from scipy import signal
import pyglet
from pyglet import window
from constants import WINDOW_HEIGHT, WINDOW_WIDTH, RATE, FORMAT, CHANNELS, CHUNK_SIZE, batch, path_background, FONT_SIZE, \
                      ACCEPTANCE_RANGE, path_wave, LOW_E, A, D, G, H, HIGH_E, FONT_SIZE_SMALL
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

guitar_label_1 = pyglet.text.Label(text="Mit den Zahlen 1-6 kannst du alle Frequenzen einer gestimmten Gitarre auswählen."
                                   , x=10, y=360, font_size=FONT_SIZE_SMALL, color=(0, 0, 0, 255), batch=batch,
                                   group=foreground)

guitar_label_2 = pyglet.text.Label(text="Die 1 repräsentiert dabei die Frequenz der obersten (tiefsten) Seite und "
                                   , x=10, y=340, font_size=FONT_SIZE_SMALL, color=(0, 0, 0, 255), batch=batch,
                                   group=foreground)

guitar_label_3 = pyglet.text.Label(text="die 6 die der Höchsten", x=10, y=320, font_size=FONT_SIZE_SMALL,
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
    global freq_to_reach
    if symbol == pyglet.window.key.Q:
        window.close()
    if symbol == pyglet.window.key._1:
        freq_to_reach = LOW_E
        freq_to_reach_label.text = f"Diese Frequenz gilt es zu erreichen: {freq_to_reach}Hz"
    if symbol == pyglet.window.key._2:
        freq_to_reach = A
        freq_to_reach_label.text = f"Diese Frequenz gilt es zu erreichen: {freq_to_reach}Hz"
    if symbol == pyglet.window.key._3:
        freq_to_reach = D
        freq_to_reach_label.text = f"Diese Frequenz gilt es zu erreichen: {freq_to_reach}Hz"
    if symbol == pyglet.window.key._4:
        freq_to_reach = G
        freq_to_reach_label.text = f"Diese Frequenz gilt es zu erreichen: {freq_to_reach}Hz"
    if symbol == pyglet.window.key._5:
        freq_to_reach = H
        freq_to_reach_label.text = f"Diese Frequenz gilt es zu erreichen: {freq_to_reach}Hz"
    if symbol == pyglet.window.key._6:
        freq_to_reach = HIGH_E
        freq_to_reach_label.text = f"Diese Frequenz gilt es zu erreichen: {freq_to_reach}Hz"


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

    data = wf.readframes(CHUNK_SIZE)

    while data:
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

    # get main frequency
    main_freq_index = np.argmax(spectrum)
    actual_freq = frequencies[main_freq_index]

    # check for similarity in signal
    compare_freqs(actual_freq)

    # update input frequency
    freq_actual_label.text = f"{int(actual_freq)} Hz"


pyglet.clock.schedule_interval(read_audio_stream, 0.01)

pyglet.app.run()