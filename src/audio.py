import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlb
from scipy.io.wavfile import read, write
from numpy.fft import fft, fftfreq
from scipy import signal
import pyaudio
import gui
import threading as th

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
  #print(mult)

  filters_sum = np.sum(filters, axis=0)

  data_out = np.sum(np.array(data) * filters_sum)

  mutex_data.acquire()
  data_out_obj.value = np.append(data_out_obj.value, np.int16(data_out))
  mutex_data.release()

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

def setStream(filters, Fs, window, frame_count):
  p = pyaudio.PyAudio()

  stream = p.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=Fs,
                  output=True,
                  frames_per_buffer= frame_count,
                  stream_callback=callback_maker(filters, Fs, window, frame_count)
                  )
                  
  return stream, p

#-----------------------------------

def callback_maker(filters, Fs, window, frame_count):
    def callback(in_data, frame_count, time_info, status_flags):

        mutex_data.acquire()
        data_out = data_out_obj.value[:frame_count]

        band_values = getBandValues(data_out, Fs)
        gui.updateBandBars(window, band_values)

        data_out_obj.value = data_out_obj.value[frame_count:]
        cond_proc.notify()
        mutex_data.release()
        #print(data_out)

        return (data_out.tobytes(), pyaudio.paContinue)
    return callback

#------------------------------------

def readData (filename):

  Fs, data = read(filename)
  data = np.array(data[:,0])
  return data, Fs

#------------------------------------
class FooWrapper(object):
    def __init__(self, value):
         self.value = value
#------------------------------------
def checkData (data):
  #Changing the WAV type to int 16bits PCM
  if np.max(data) > 1:
    if np.min(data) >= 0 and np.max(data)<= 255:
      raise Exception("formato WAV 8-bit PCM não suportado! Use 16-bit PCM ou 32-bit floating-point.")
    elif np.max(data) > 32767 or np.min(data) < -32767:
      raise Exception("formato WAV 32-bit PCM não suportado! Use 16-bit PCM ou 32-bit floating-point.")
  else: 
    data = 32767*data
#------------------------------------
class Processing(th.Thread):

  def __init__(self, data, M, Fs, frame_count, filters):
    super().__init__()
    self.data = data
    self.M = M
    self.frame_count = frame_count
    self.filters = filters
    self.Fs = Fs

  def run(self):
    while(len(self.data) > self.M):
      mutex_mult.acquire()
      processAudio(self.data[:self.M+1], self.filters, self.Fs, mult_obj.value, False)
      mutex_mult.release()
      self.data = self.data[1:]

      mutex_data.acquire()
      if not alive: break

      #print(data_out_obj.value.size)
      while data_out_obj.value.size >= self.frame_count:
        cond_proc.wait()
      mutex_data.release()


#------------------------------------
mutex_data = th.Lock()
mutex_mult = th.Lock()
mutex_alive = th.Lock()

cond_proc = th.Condition(mutex_data)

mult_obj = FooWrapper([])
data_out_obj = FooWrapper(np.array([]))
alive = False