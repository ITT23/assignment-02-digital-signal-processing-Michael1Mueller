import pyaudio
import numpy as np
from matplotlib import pyplot as plt
import pyglet
from pyglet import window
from scipy import signal

# Set up audio stream
# reduce chunk size and sampling rate for lower latency
CHUNK_SIZE = 1024  # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Audio sampling rate (Hz)
# Pyglet initialization
WINDOW_WIDTH = 100
WINDOW_HEIGHT = 300

# freq array for comparing values
freq_array = []


p = pyaudio.PyAudio()
window = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
batch = pyglet.graphics.Batch()


class Rect:
    rectangles = []

    def __init__(self, x, y, width=66, height=33):
        self.x = x
        self.y = y
        self.color = (255, 0, 0)  # standard color
        self.checked_color = (0, 255, 0)  # color when checked
        self.shape = pyglet.shapes.Rectangle(self.x, self.y, width, height, color=self.color, batch=batch)
        self.checked = False

    def draw_rects():
        for rect in Rect.rectangles:
            rect.draw()

    def create_rect(x, y):
        Rect.rectangles.append(Rect(x, y))


    def change_check(self):
        if self.checked:
            self.checked = False
            self.shape.color = self.color
        else:
            self.checked = True
            self.shape.color = self.checked_color
        Rect.draw_rects()

    def get_index_of_checked():
        for rect in Rect.rectangles:
            if rect.checked:
                for i in range(len(Rect.rectangles)):
                    if Rect.rectangles[i] == rect:
                        return i

    def draw(self):
        self.shape.draw()


@window.event
def on_draw():
    window.clear()
    batch.draw()


def create_rectangles():
    x_pos = WINDOW_WIDTH/4
    y_pos = WINDOW_HEIGHT/7
    for i in range(5):
        Rect.create_rect(x_pos, y_pos)
        print(f"Stelle: {i} y: {y_pos}")
        y_pos += x_pos * 2
    Rect.draw_rects()
    Rect.rectangles[0].check()
    print(len(Rect.rectangles))


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
        if freq_array[i] <= freq_array[i+1]:
            ascending_counter += 1
            if ascending_counter == len(freq_array)-1:
                change_rect_level_ascending()
                # clear array, in order to call level function only once at a time
                freq_array.clear()
        elif freq_array[i] >= freq_array[i+1]:
            descending_counter += 1
            if descending_counter == len(freq_array)-1:
                change_rect_level_descending()
                # clear array, in order to call level function only once at a time
                freq_array.clear()


def change_rect_level_ascending():
    checked_rect_index = Rect.get_index_of_checked()

    if checked_rect_index == 4:
        return

    Rect.change_check(Rect.rectangles[checked_rect_index])
    Rect.change_check(Rect.rectangles[checked_rect_index+1])


def change_rect_level_descending():
    checked_rect_index = Rect.get_index_of_checked()

    if checked_rect_index == 0:
        return

    Rect.change_check(Rect.rectangles[checked_rect_index])
    Rect.change_check(Rect.rectangles[checked_rect_index-1])


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

# set up interactive plot
fig = plt.figure()
ax = plt.gca()
line, = ax.plot(np.zeros(CHUNK_SIZE))
ax.set_ylim(-30000, 30000)

plt.ion()
plt.show()

kernel = signal.gaussian(20, 10)  # create a kernel
kernel /= np.sum(kernel)  # normalize the kernel so it does not affect the signal's amplitude

# continuously capture and plot audio singal
def read_audio_stream(dt):
    # Read audio data from stream
    data = stream.read(CHUNK_SIZE)

    # Convert audio data to numpy array
    data = np.frombuffer(data, dtype=np.int16)
    data2 = np.convolve(data, kernel, 'same')  # apply the kernel to the signal
    line.set_ydata(data2)
    # print(f"data: {data}")
    spectrum = np.abs(np.fft.fft(data2))

    frequencies = np.fft.fftfreq(len(data2), 1 / CHUNK_SIZE)

    mask = frequencies >= 0

    spectrum = spectrum[mask]
    frequencies = frequencies[mask]
    # print(f"spectrum: {spectrum}")
    # print(f"frequencies: {frequencies}")

    main_freq_index = np.argmax(spectrum)
    # print(f"main Index: {main_freq_index}")
    freq = frequencies[main_freq_index]

    fill_freq_array(freq)
    print(freq_array)
    check_whistle()

    # Redraw plot
    fig.canvas.draw()
    fig.canvas.flush_events()


pyglet.clock.schedule_interval(read_audio_stream, 0.01)


pyglet.app.run()