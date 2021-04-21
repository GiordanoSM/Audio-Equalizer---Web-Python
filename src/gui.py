import PySimpleGUI as sg
import os
import audio

def runGUI (Fs, filters):

  file_list_line = [
    [
      [sg.Text("Wav file:"), sg.In(size=(50,1), enable_events=True, key="-FILE-"),sg.Text(size =(10,2),key="-FEEDBACK-")],
      [sg.FileBrowse(target=(-1,1)),sg.OK(key="-OK-")]
    ]
  ]

  sliders_line = [
    [
      sg.Text("dB"),
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

  layout = [
    [file_list_line],
    [sg.Frame("None",sliders_line, key="-FRAME-")],
    [ImageButton('play', '-PLAY-'), ImageButton('pause', '-PAUSE-'), ImageButton('stop', '-STOP-')],
    [
      sg.VSeparator()
    ]
  ]
  #layout = [[sg.Text("Hello here")], [sg.Button("OK")]]

  window = sg.Window(title= "Equalizador 10 faixas", layout=layout, margins= (100, 50), element_justification='center', resizable= True)

  ready=False


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
        data_out = audio.process_audio(filename, filters, Fs, mult)

      #window["-FILE LIST-"].update(values=fnames)

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