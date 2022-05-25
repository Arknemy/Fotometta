import os
import easyocr
import cv2 as cv
import numpy as np
import PySimpleGUI as sg
from os import listdir
from assistant import arkAssist

sg.theme('DarkGray5')
font = ('Helvetica', 13)
browseFolder = [[sg.Text('Folder', font = font), sg.In(size = (25,1), enable_events = True ,key = '-FOLDER-'), sg.FolderBrowse(font = font)]]
layout = [[sg.Image(filename = 'ui_asset/icon.png')], [sg.Text('Select the folder that contains your roster:', font = font, key = '-TEXT-')], [sg.Column(browseFolder, element_justification='c')], [sg.Button('Select', font = font)]]

window = sg.Window('Fotometta', layout, element_justification = 'c')

while True:
	event, values = window.read()

	if event == 'Select' and values['-FOLDER-'] != '':
		nameReader = easyocr.Reader(['en'])
		window['-TEXT-'].update('Processing... please do not close the window')
		selectedFolder = values['-FOLDER-']
		open('output/output_text.txt', 'w').close()

		for i in os.listdir('input'):
			os.remove(os.path.join('input', i))

		reso = 1500

		for rawImg in os.listdir(selectedFolder):
				original = cv.imread(selectedFolder + '/' + rawImg)
				oDim = original.shape
				destination = 'input/' + rawImg[:-4] + '.jpg'

				if oDim[1] > reso:
					ratio = reso / oDim[1]
					resized = cv.resize(original, (0, 0), fx = ratio, fy = ratio)
					cv.imwrite(destination, resized)
				else:
					cv.imwrite(destination, original, [int(cv.IMWRITE_JPEG_QUALITY), 100])

		for i in os.listdir('input'):
			arkAssist(i, nameReader)

		window.close()
		os.system('notepad.exe output/output_text.txt')
		break

	if event == sg.WIN_CLOSED:
		window.close()
		break
