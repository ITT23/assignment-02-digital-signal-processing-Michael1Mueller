import numpy.fft
import pyaudio
import numpy as np
from matplotlib import pyplot as plt
from scipy import signal

# Set up audio stream
# reduce chunk size and sampling rate for lower latency
CHUNK_SIZE = 1024   # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Audio sampling rate (Hz)
p = pyaudio.PyAudio()


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

print(f"kernel: {kernel}")
# continuously capture and plot audio signal
while True:
    # Read audio data from stream
    data = stream.read(CHUNK_SIZE)

    # Convert audio data to numpy array
    data = np.frombuffer(data, dtype=np.int16)
    data2 = np.convolve(data, kernel, 'same')  # apply the kernel to the signal
    line.set_ydata(data2)
    # print(f"data: {data}")
    spectrum = np.abs(np.fft.fft(data2))

    frequencies = np.fft.fftfreq(len(data2), 1/CHUNK_SIZE)

    mask = frequencies >= 0

    spectrum = spectrum[mask]
    frequencies = frequencies[mask]
    # print(f"spectrum: {spectrum}")
    # print(f"frequencies: {frequencies}")

    main_freq_index = np.argmax(spectrum)
    # print(f"main Index: {main_freq_index}")
    print(f"main Frequency: {frequencies[main_freq_index]}")


    # Redraw plot
    fig.canvas.draw()
    fig.canvas.flush_events()
