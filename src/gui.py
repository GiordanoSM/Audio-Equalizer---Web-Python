import PySimpleGUI as sg
import os
import audio as au
import numpy as np
from scipy.io.wavfile import read, write
import time

def runGUI (Fs):

  M = 1000

  frame_count= 4410

  filters = au.getFilters(Fs,M)

  file_list_line = [
    [
      [sg.Text("Wav file:"), sg.In(size=(50,1), enable_events=True, key="-FILE-"),sg.Text(size =(10,2),key="-FEEDBACK-")],
      [sg.FileBrowse(target=(-1,1)),sg.OK(key="-OK-")]
    ]
  ]

  sliders_line = [
    [
      sg.Column([[sg.Text("dB")], [sg.Button("Reset values", key="-RESET-")]]),
      sg.Column(bandSlide("32")),
      sg.Column(bandSlide("64")),
      sg.Column(bandSlide("125")),
      sg.Column(bandSlide("250")),
      sg.Column(bandSlide("500")),
      sg.Column(bandSlide("1k")),
      sg.Column(bandSlide("2k")),
      sg.Column(bandSlide("4k")),
      sg.Column(bandSlide("8k")),
      sg.Column(bandSlide("16k")),
    ]
  ]

  bars_line = [
    [
      sg.Column([[sg.Text(key="-VBARMAX-")]]),
      sg.Column([[bandBar("32")]]),
      sg.Column([[bandBar("64")]]),
      sg.Column([[bandBar("125")]]),
      sg.Column([[bandBar("250")]]),
      sg.Column([[bandBar("500")]]),
      sg.Column([[bandBar("1k")]]),
      sg.Column([[bandBar("2k")]]),
      sg.Column([[bandBar("4k")]]),
      sg.Column([[bandBar("8k")]]),
      sg.Column([[bandBar("16k")]])
    ]
]

  layout = [
    [file_list_line],
    [sg.Frame("Bands", bars_line, key='-FRAME_BARS-')],
    [sg.Frame("None",sliders_line, key="-FRAME-")],
    [ImageButton('play', '-PLAY-'), ImageButton('stop', '-STOP-')],
    [
      sg.Button("Debug (On/Off)",border_width=0, key='-DEBUG-', button_color= "red"),
      sg.VSeparator(), 
      sg.Exit(key="Exit")
    ]
  ]
  #layout = [[sg.Text("Hello here")], [sg.Button("OK")]]

  window = sg.Window(title= "Equalizador 10 faixas", layout=layout, margins= (100, 50), element_justification='center', resizable= True)

  ready=False

  debug=False

  stream=None

  data=[]

  stream=None

  p=None

  thr=None

  while True:
    event, values = window.read(250)

    au.mutex_mult.acquire()
    au.mult_obj.value = [au.IfromDB(values["-SLIDER32-"]), au.IfromDB(values["-SLIDER64-"]), au.IfromDB(values["-SLIDER125-"]),
              au.IfromDB(values["-SLIDER250-"]), au.IfromDB(values["-SLIDER500-"]), au.IfromDB(values["-SLIDER1k-"]),
              au.IfromDB(values["-SLIDER2k-"]), au.IfromDB(values["-SLIDER4k-"]), au.IfromDB(values["-SLIDER8k-"]), au.IfromDB(values["-SLIDER16k-"])]
    au.mutex_mult.release()

    if event == "Exit" or event == sg.WIN_CLOSED:
      if stream != None:
        stream.stop_stream()
        stream.close()
      au.mutex_alive.acquire()
      au.alive=False
      au.mutex_alive.release()

      if p != None:
        p.terminate()
      break

    if event == "-FILE-":
      window["-FEEDBACK-"].update("")
    
    elif event == "-OK-":
      try:
        fname = values["-FILE-"]
        filename = fname if os.path.isfile(fname) and fname.lower().endswith(".wav") else ""
        
        if filename == "":
          window["-FEEDBACK-"].update("Formato não suportado!")
          raise WrongFormat()
        else: 
          window["-FEEDBACK-"].update("OK")
          filename_ready = filename
          window["-FRAME-"].update(filename_ready)
          Fs, data = read(filename)
          if data.ndim > 1 :
            data = data[:,0]
          ready=True

      except WrongFormat:
        window["-FEEDBACK-"].update("Formato não suportado!")
      
      except IOError:
        window["-FEEDBACK-"].update("Arquivo não encontrado!")

    elif event == "-PLAY-":
      
      if au.alive: 
        print("Press stop first.")

      elif ready:
        stream, p = au.setStream(filters, Fs, window, frame_count)

        pad_data = np.pad(data, ((int(np.floor(M/2)), int(np.floor(M/2))))).tolist()

        thr = au.Processing(pad_data, M, Fs, frame_count, filters)
        au.mutex_data.acquire()
        au.alive=True
        au.mutex_data.release()

        thr.start()

        time.sleep(0.2)
        
        stream.start_stream()

    elif event == "-RESET-":
      resetSliders(window)

    elif event == "-STOP-":
      window["-FRAME-"].update("None")
      ready = False
      if stream != None:
        stream.stop_stream()
        stream.close()

      au.mutex_data.acquire()
      au.alive = False

      au.data_out_obj.value = np.array([])
      au.mutex_data.release()

      stream = None
      data=[]

    elif event == "-DEBUG-":
      debug = not debug
      window["-DEBUG-"].update(button_color="green" if debug else "red")

  tr.join()

  window.close()

#------------------------------------

class WrongFormat(Exception):
  pass

def bandSlide (name):
  slider_column = [
    [
      sg.Slider((-20, 20), 0, 1,
                orientation="v",
                size=(7,15),
                key="-SLIDER{}-".format(name),
                enable_events=False
                )
    ],
    [
      sg.Text("   " + name)
    ]
  ]

  return slider_column

#--------------------------------------

def ImageButton(title, key):
  return sg.Button(title,
                  border_width=0, key=key)

#--------------------------------------

def resetSliders(window):
  window["-SLIDER32-"].update(0)
  window["-SLIDER64-"].update(0)
  window["-SLIDER125-"].update(0)
  window["-SLIDER250-"].update(0)
  window["-SLIDER500-"].update(0)
  window["-SLIDER1k-"].update(0)
  window["-SLIDER2k-"].update(0)
  window["-SLIDER4k-"].update(0)
  window["-SLIDER8k-"].update(0)
  window["-SLIDER16k-"].update(0)

#----------------------------------------

def bandBar (name):
  progBar = sg.ProgressBar(1, orientation='v', key='-BAR{}-'.format(name), size=(20,20))
  return progBar

#-------------------------------------

def updateBandBars (window, band_values):
  names=["32", "64", "125", "250", "500", "1k", "2k", "4k", "8k", "16k"]
  max_v = np.max(band_values)
  for i in range(len(names)):
    window["-BAR{}-".format(names[i])].update(band_values[i], max= max_v)

  #window["-VBARMAX-".format(names[i])].update(int(band_values[i]))
#----------------------------------

if __name__ == "__main__":
  runGUI(44100)