import PySimpleGUI as sg
import os
import audio
import numpy as np

def runGUI (Fs, filters):

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
    [ImageButton('play', '-PLAY-'), ImageButton('pause', '-PAUSE-'), ImageButton('stop', '-STOP-')],
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

  while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
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
          ready=True

      except WrongFormat:
        window["-FEEDBACK-"].update("Formato não suportado!")
      
      except IOError:
        window["-FEEDBACK-"].update("Arquivo não encontrado!")

    elif event == "-PLAY-":
      
      if ready:
        mult = [audio.IfromDB(values["-SLIDER32-"]), audio.IfromDB(values["-SLIDER64-"]), audio.IfromDB(values["-SLIDER125-"]),
                audio.IfromDB(values["-SLIDER250-"]), audio.IfromDB(values["-SLIDER500-"]), audio.IfromDB(values["-SLIDER1k-"]),
                audio.IfromDB(values["-SLIDER2k-"]), audio.IfromDB(values["-SLIDER4k-"]), audio.IfromDB(values["-SLIDER8k-"]), audio.IfromDB(values["-SLIDER16k-"])]
        print(mult)        
        data_out, wav_type = audio.processAudio(filename, filters, Fs, mult, debug)
        band_values = audio.getBandValues(data_out, Fs, wav_type)
        updateBandBars(window, band_values)
        print(band_values)

    elif event == "-RESET-":
      resetSliders(window)

    elif event == "-STOP-":
      window["-FRAME-"].update("None")
      ready = False

    elif event == "-DEBUG-":
      debug = not debug
      window["-DEBUG-"].update(button_color="green" if debug else "red")

  window.close()

#------------------------------------

class WrongFormat(Exception):
  pass

def bandSlide (name):
  slider_column = [
    [
      sg.Slider((-30, 10), 0, 1,
                orientation="v",
                size=(7,15),
                key="-SLIDER{}-".format(name)
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
  max_v = np.max(band_values)
  window["-BAR32-"].update(band_values[0], max= max_v)
  window["-BAR64-"].update(band_values[1], max= max_v)
  window["-BAR125-"].update(band_values[2], max= max_v)
  window["-BAR250-"].update(band_values[3], max= max_v)
  window["-BAR500-"].update(band_values[4], max= max_v)
  window["-BAR1k-"].update(band_values[5], max= max_v)
  window["-BAR2k-"].update(band_values[6], max= max_v)
  window["-BAR4k-"].update(band_values[7], max= max_v)
  window["-BAR8k-"].update(band_values[8], max= max_v)
  window["-BAR16k-"].update(band_values[9], max= max_v)