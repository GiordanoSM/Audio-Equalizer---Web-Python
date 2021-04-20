import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlb
from scipy.io.wavfile import read, write
from numpy.fft import fft, fftfreq

def main ():
  Fs, data = read('Grave.wav')

  data = data[:,0]
  print("Sampling Frequency is", Fs)

  plt.figure(1)
  plt.plot(data)
  plt.xlabel('Sample Index')
  plt.ylabel('Amplitude')
  plt.title('Waveform of Test Audio')

  fft_data = fft(data)
  freq = fftfreq(data.size,d=1/Fs)[0:data.size//2]

  plt.figure(2)
  plt.plot(freq, np.absolute(fft_data)[0:data.size//2])
  plt.xlabel('Frequência (rad/sample)')
  plt.ylabel('Amplitude')
  plt.title('FFT')

  #plt.figure(3)
  #plt.magnitude_spectrum(data, Fs=Fs, scale='dB',window= mlb.window_none)

  #plt.figure(4)
  #plt.phase_spectrum(data, Fs=Fs, window= mlb.window_none)
  #plt.show()

  M = 50
  window = np.hamming(M+1)

  filter_16k = makePassBandFilter(omega_c1= 10665, omega_c2= 21335, omega_s= Fs, ordemM= M, window= window) #(faixa = 10665 a 21335)
  filter_8k = makePassBandFilter(omega_c1= 5335, omega_c2= 10665, omega_s= Fs, ordemM= M, window= window) #(faixa = 5335 a 10665)
  filter_4k = makePassBandFilter(omega_c1= 2665, omega_c2= 5335, omega_s= Fs, ordemM= M, window= window) #(faixa = 2665 a 5335)
  filter_2k = makePassBandFilter(omega_c1= 1335, omega_c2= 2665, omega_s= Fs, ordemM= M, window= window) #(faixa = 1335 a 2665)
  filter_1k = makePassBandFilter(omega_c1= 665, omega_c2= 1335, omega_s= Fs, ordemM= M, window= window) #(faixa = 665 a 1335)
  filter_500 = makePassBandFilter(omega_c1= 335, omega_c2= 665, omega_s= Fs, ordemM= M, window= window) #(faixa = 335 a 665)
  filter_250 = makePassBandFilter(omega_c1= 165, omega_c2= 335, omega_s= Fs, ordemM= M, window= window) #(faixa = 165 a 335)
  filter_125 = makePassBandFilter(omega_c1= 85, omega_c2= 165, omega_s= Fs, ordemM= M, window= window) #(faixa = 85 a 165)
  filter_64 = makePassBandFilter(omega_c1= 43, omega_c2= 85, omega_s= Fs, ordemM= M, window= window) #(faixa = 43 a 85)
  filter_32 = makePassBandFilter(omega_c1= 21, omega_c2= 43, omega_s= Fs, ordemM= M, window= window) #(faixa = 21 a 43)

  filters = [filter_32, filter_64, filter_125, filter_250, filter_500, filter_1k, filter_2k, filter_4k, filter_8k, filter_16k]

  freq2 = range(0, Fs//2)
  
  i = 5

  filters_sum = [0]*(M+1)

  for f in filters:
    A = fft(f, Fs)
    mag = np.abs(A)[0:A.size//2]

    plt.figure(i)
    plt.plot(freq2, mag)
    plt.xlabel('Frequência (rad/sample)')
    plt.ylabel('Amplitude')
    plt.title('FFT Filtro {}'.format(i-5))
    plt.show()
    i += 1 
    filters_sum = [x + y for x,y in zip(f, filters_sum)]
  
  A = fft(filters_sum, Fs)
  mag = np.abs(A)[0:A.size//2]

  plt.figure(i)
  plt.plot(freq2, mag)
  plt.xlabel('Frequência (rad/sample)')
  plt.ylabel('Amplitude')
  plt.title('FFT Filtro Somado')
  plt.show()
  i += 1 

  write('out.wav', Fs, data)

def makePassBandFilter (omega_c1, omega_c2, omega_s, ordemM, window = None):
  
  wc1 = 2 * np.pi * omega_c1/omega_s
  wc2 = 2 * np.pi * omega_c2/omega_s
  print(wc1, wc2)

  n = list(range(1, ordemM//2))

  h0 = (wc2-wc1)/np.pi

  haux = list(map(lambda x: (np.sin(wc2*x)-np.sin(wc1*x))/(np.pi*x), n))

  filtro_rect = haux[::-1] + [h0] + haux

  return [x * y for x,y in zip(filtro_rect, window)] if window is not None else filtro_rect

if __name__ == "__main__":
  main()