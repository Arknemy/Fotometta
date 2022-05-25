import os
import easyocr
import threading
import cv2 as cv
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from os import listdir
from assistant import arkAssist

def popupWindow():
	popup1 = [[sg.Text('Warning: you have an existing roster saved.\nProceeding will overwrite your previous roster.', font = font, key = '-TEXT-')], [sg.Button('Confirm', font = font), sg.Button('Cancel', font = font)]]
	return sg.Window('Warning', popup1, element_justification = 'c', icon = 'ui_asset/taskbaricon.ico')

sg.theme('DarkGray5')
font = ('Helvetica', 13)
browseFolder = [[sg.Text('Folder', font = font), sg.In(size = (25,1), enable_events = True ,key = '-FOLDER-'), sg.FolderBrowse(font = font)]]
mainWindow = [[sg.Image(filename = 'ui_asset/icon.png')], [sg.Button('Open Roster', font = font)], [sg.Text('Select the folder that contains your roster:', font = font, key = '-TEXT-')], [sg.Column(browseFolder, element_justification='c')], [sg.Button('Create New File', font = font), sg.Button('Add to Existing', font = font)]]

window = sg.Window('Fotometta', mainWindow, element_justification = 'c', icon = 'ui_asset/taskbaricon.ico')

while True:
	event, values = window.read()

	if event == 'Open Roster':
		os.system('notepad.exe output/output_text.txt')

	if event == 'Create New File' and values['-FOLDER-'] != '':
		confirm = False
		selectedFolder = values['-FOLDER-']

		if os.stat('output/output_text.txt').st_size != 0:
			popup = popupWindow()

			while True:
				popevent, values = popup.read()

				if popevent == 'Confirm':
					confirm = True
					popup.close()
					break
				elif popevent == 'Cancel' or popevent == sg.WIN_CLOSED:
					popup.close()
					break

		if os.stat('output/output_text.txt').st_size == 0 or confirm == True:
			nameReader = easyocr.Reader(['en'])
			window['-TEXT-'].update('Processing... please do not close the window')
			open('output/output_text.txt', 'w').close()

			for i in os.listdir('input'):
				os.remove(os.path.join('input', i))

			reso = 1500
			index = 1

			for rawImg in os.listdir(selectedFolder):
				original = cv.imread(selectedFolder + '/' + rawImg)
				oDim = original.shape
				destination = 'input/sample' + str(index) + '.jpg'
				index = index + 1

				if oDim[1] > reso:
					ratio = reso / oDim[1]
					resized = cv.resize(original, (0, 0), fx = ratio, fy = ratio)
					cv.imwrite(destination, resized)
				else:
					cv.imwrite(destination, original, [int(cv.IMWRITE_JPEG_QUALITY), 100])

			threads = []

			for i in os.listdir('input'):
				t = threading.Thread(target = arkAssist, args = [i, nameReader])
				t.start()
				threads.append(t)
				# arkAssist(i, nameReader)

			for thread in threads:
				thread.join()

			window.close()
			os.system('notepad.exe output/output_text.txt')
			break

	#-------------------------------------------------------------------------------------------------------------------------------------

	if event == 'Add to Existing' and values['-FOLDER-'] != '':
		selectedFolder = values['-FOLDER-']
		nameReader = easyocr.Reader(['en'])
		window['-TEXT-'].update('Processing... please do not close the window')

		for i in os.listdir('input'):
			os.remove(os.path.join('input', i))

		reso = 1500
		index = 1

		for rawImg in os.listdir(selectedFolder):
			original = cv.imread(selectedFolder + '/' + rawImg)
			oDim = original.shape
			destination = 'input/sample' + str(index) + '.jpg'
			index = index + 1

			if oDim[1] > reso:
				ratio = reso / oDim[1]
				resized = cv.resize(original, (0, 0), fx = ratio, fy = ratio)
				cv.imwrite(destination, resized)
			else:
				cv.imwrite(destination, original, [int(cv.IMWRITE_JPEG_QUALITY), 100])

		threads = []

		for i in os.listdir('input'):
			t = threading.Thread(target = arkAssist, args = [i, nameReader])
			t.start()
			threads.append(t)
			# arkAssist(i, nameReader)

		for thread in threads:
			thread.join()

		window.close()
		os.system('notepad.exe output/output_text.txt')
		break

	if event == sg.WIN_CLOSED:
		window.close()
		break