import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlb
from scipy.io.wavfile import read, write
from numpy.fft import fft, ifft, fftfreq

Fs, data = read('Grave.wav')

data = data[:,0]
print("Sampling Frequency is", Fs)

plt.figure(1)
plt.plot(data)
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Waveform of Test Audio')

fft_data = fft(data)
freq = fftfreq(data.size,d=1/Fs)

plt.figure(2)
plt.plot(freq, np.absolute(fft_data))
plt.xlabel('Frequência (rad/sample)')
plt.ylabel('Amplitude')
plt.title('FFT')

plt.figure(3)
plt.magnitude_spectrum(data, Fs=Fs, scale='dB',window= mlb.window_none)

plt.figure(4)
plt.phase_spectrum(data, Fs=Fs, window= mlb.window_none)
plt.show()

write('out.wav', Fs, data)