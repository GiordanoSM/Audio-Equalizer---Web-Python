import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlb
from scipy.io.wavfile import read, write
from numpy.fft import fft, fftfreq
from scipy import signal
import pyaudio
import gui

def getFilters(Fs, M):

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

  return filters


def processAudio (data, filters, Fs, mult, debug):

  filters = [x * np.array(y) for x, y in zip(mult, filters)]
  print(mult)

  freq2 = range(0, Fs//2)
  
  i = 10

  filters_sum = [0]*filters[0].size

  somas = []

  if debug:
    plt.figure(6)

  for f in filters:
    if debug:
      #plt.figure(i)
      A = fft(f, Fs)
      mag = np.abs(A)[0:A.size//2]
      mag2 = [20*np.log10(x) for x in mag]
      plt.plot(freq2, mag2)
      somas.append(sum(f))
      #plt.xlabel('Frequência')
      #plt.ylabel('Amplitude [dB]')
      #plt.title('FFT Filtro {}'.format(i-10))

      i += 1
      

    filters_sum = [x + y for x,y in zip(f, filters_sum)]

  #Changing the WAV type to int 16bits PCM
  if np.max(data) > 1:
    if np.min(data) >= 0 and np.max(data)<= 255:
      raise Exception("formato WAV 8-bit PCM não suportado! Use 16-bit PCM ou 32-bit floating-point.")
    elif np.max(data) > 32767 or np.min(data) < -32767:
      raise Exception("formato WAV 32-bit PCM não suportado! Use 16-bit PCM ou 32-bit floating-point.")
  else: 
    data = 32767*data

  data_out = signal.convolve(data, filters_sum, mode='same')
  data_out = data_out.astype(np.int16)

  if debug:

    plt.xlabel('Frequência')
    plt.ylabel('Amplitude [dB]')
    plt.title('FFT Filtros')

    #plt.figure(1)
    #plt.plot(data)
    #plt.xlabel('Sample Index')
    #plt.ylabel('Amplitude')
    #plt.title('Waveform of Test Audio')

    fft_data = fft(data)
    freq = fftfreq(len(data),d=1/Fs)[0:len(data)//2]

    plt.figure(2)
    plt.plot(freq, np.absolute(fft_data)[0:len(data)//2])
    plt.xlabel('Frequência (rad/sample)')
    plt.ylabel('Amplitude')
    plt.title('FFT')

    #plt.figure(3)
    #plt.magnitude_spectrum(data, Fs=Fs, scale='dB',window= mlb.window_none)

    #plt.figure(4)
    #plt.phase_spectrum(data, Fs=Fs, window= mlb.window_none)
    #plt.show()

    A = fft(filters_sum, Fs)
    mag = np.abs(A)[0:A.size//2]
    mag2 = [20*np.log10(x) for x in mag]

    plt.figure(3)
    plt.plot(freq2, mag2)
    plt.xlabel('Frequência (rad/sample)')
    plt.ylabel('Amplitude (dB)')
    plt.title('FFT Filtro Somado')

    #plt.figure(4)
    #plt.plot(data_out)
    #plt.xlabel('Sample Index')
    #plt.ylabel('Amplitude')
    #plt.title('Waveform of Test Audio Output')

    fft_data_out = fft(data_out)
    freq_out = fftfreq(data_out.size,d=1/Fs)[0:data_out.size//2]

    plt.figure(5)
    plt.plot(freq_out, np.absolute(fft_data_out)[0:data_out.size//2])
    plt.xlabel('Frequência (rad/sample)')
    plt.ylabel('Amplitude')
    plt.title('FFT out')

    plt.show()

  #print(data.size)
  #print(np.max(data_out))

  #play_obj.wait_done()
  #write('out.wav', Fs, data_out)

  return data_out

#------------------------------------

def makePassBandFilter (omega_c1, omega_c2, omega_s, ordemM, window = None):
  
  wc1 = 2 * np.pi * omega_c1/omega_s
  wc2 = 2 * np.pi * omega_c2/omega_s

  n = list(range(1, ordemM//2 + 1))

  h0 = (wc2-wc1)/np.pi

  haux = list(map(lambda x: (np.sin(wc2*x)-np.sin(wc1*x))/(np.pi*x), n))

  filtro_rect = haux[::-1] + [h0] + haux

  return [x * y for x,y in zip(filtro_rect, window)] if window is not None else filtro_rect

#------------------------------------

def IfromDB (value):
  return 10**(value/20)

#------------------------------------

def getBandValues (data_out, Fs):
  
  band_values = []
  fft_values = fft(data_out, Fs)

  band_values.append(np.mean(np.abs(fft_values[21:43])))
  band_values.append(np.mean(np.abs(fft_values[43:85])))
  band_values.append(np.mean(np.abs(fft_values[85:165])))
  band_values.append(np.mean(np.abs(fft_values[165:335])))
  band_values.append(np.mean(np.abs(fft_values[335:665])))
  band_values.append(np.mean(np.abs(fft_values[665:1335])))
  band_values.append(np.mean(np.abs(fft_values[1335:2665])))
  band_values.append(np.mean(np.abs(fft_values[2665:5335])))
  band_values.append(np.mean(np.abs(fft_values[5335:10665])))
  band_values.append(np.mean(np.abs(fft_values[10665:21334])))

  return band_values

#----------------------------------

def setStream(data, filters, Fs, window, debug):
  p = pyaudio.PyAudio()

  stream = p.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=Fs,
                  output=True,
                  frames_per_buffer=4410,
                  stream_callback=callback_maker(data, filters, Fs, window, debug)
                  )
                  
  return stream, p

#-----------------------------------

def callback_maker(data, filters, Fs, window, debug):
    def callback(in_data, frame_count, time_info, status_flags):
        data_out = processAudio(data[:frame_count], filters, Fs, gui.mult_obj.value, debug)
        band_values = getBandValues(data_out, Fs)
        gui.updateBandBars(window, band_values)
        del data[:frame_count]
        return (data_out.tobytes(), pyaudio.paContinue)
    return callback

#------------------------------------

def readData (filename):

  Fs, data = read(filename)
  data = np.array(data[:,0])
  return data, Fs

#------------------------------------

if __name__ == "__main__":
  gui.runGUI(44100)