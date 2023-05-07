import pyaudio
import numpy as np
import pyglet
from pyglet import window
from scipy import signal
from pynput.keyboard import Key, Controller
from Rect import Rect
from constants import batch, WINDOW_HEIGHT, WINDOW_WIDTH, RATE, FORMAT, CHUNK_SIZE, CHANNELS

# freq array for comparing values
freq_array = []

# for pynput
keyboard = Controller()

p = pyaudio.PyAudio()
window = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)


@window.event
def on_draw():
    window.clear()
    batch.draw()


def create_rectangles():
    x_pos = WINDOW_WIDTH/4
    y_pos = WINDOW_HEIGHT/7
    for i in range(5):
        Rect.create_rect(x_pos, y_pos)
        y_pos += x_pos * 2
    Rect.draw_rects()
    Rect.rectangles[0].change_check()


create_rectangles()


def fill_freq_array(freq):
    if len(freq_array) == 8:
        freq_array.pop(0)
        freq_array.append(freq)
    else:
        freq_array.append(freq)


def check_whistle():
    ascending_counter = 0
    descending_counter = 0

    if len(freq_array) < 8:
        return

    for i in range(len(freq_array)-1):
        if freq_array[i] < freq_array[i+1]:
            ascending_counter += 1
            if ascending_counter == len(freq_array)-1:
                change_rect_level_ascending()
                # clear array, in order to call change_level function only once at a time
                freq_array.clear()
        elif freq_array[i] > freq_array[i+1]:
            descending_counter += 1
            if descending_counter == len(freq_array)-1:
                change_rect_level_descending()
                # clear array, in order to call change_level function only once at a time
                freq_array.clear()


def change_rect_level_ascending():
    checked_rect_index = Rect.get_index_of_checked()

    if checked_rect_index == 4:
        return

    Rect.change_check(Rect.rectangles[checked_rect_index])
    Rect.change_check(Rect.rectangles[checked_rect_index+1])

    # change for example PowerPoint-Slide to next one
    keyboard.press(Key.right)
    keyboard.release(Key.right)


def change_rect_level_descending():
    checked_rect_index = Rect.get_index_of_checked()

    if checked_rect_index == 0:
        return

    Rect.change_check(Rect.rectangles[checked_rect_index])
    Rect.change_check(Rect.rectangles[checked_rect_index-1])

    # change for example PowerPoint-Slide to previous one
    keyboard.press(Key.left)
    keyboard.release(Key.left)


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


# from exercise notebook
kernel = signal.gaussian(20, 10)
kernel /= np.sum(kernel)


# continuously capture and plot audio singal
def read_audio_stream(dt):
    # Read audio data from stream
    data = stream.read(CHUNK_SIZE)

    # Convert audio data to numpy array
    data = np.frombuffer(data, dtype=np.int16)

    # kernel, to remove noise of signal -> in order for "detection is robust against background noise"
    data_noise_reduction = np.convolve(data, kernel, 'same')

    # apply fft
    spectrum = np.abs(np.fft.fft(data_noise_reduction))
    frequencies = np.fft.fftfreq(len(data_noise_reduction), 1 / RATE)

    # only positive frequencies
    mask = frequencies >= 0

    # apply mask
    spectrum = spectrum[mask]
    frequencies = frequencies[mask]

    # get main frequency
    main_freq_index = np.argmax(spectrum)
    freq = frequencies[main_freq_index]

    # add to frequency array
    fill_freq_array(freq)

    # check whether whistle frequency is ascending or descending
    check_whistle()


pyglet.clock.schedule_interval(read_audio_stream, 0.01)

pyglet.app.run()