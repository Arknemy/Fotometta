import os
import sys
import easyocr
import concurrent.futures
import json
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from assistant import arkAssist

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#---------------------------------------------------------------------------------------------------------------------------------

w = 356
h = 363
style = open('ui_asset/darkorange.qss').read()

class rosterTable(QMainWindow):
	def __init__(self):
		super(rosterTable, self).__init__()
		self.setStyleSheet(style)
		self.setGeometry(0 , 0, 500, 300)
		self.setFixedSize(1000, 600)
		self.setWindowTitle('Roster')
		self.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))

		qtRec = self.frameGeometry()
		centre = QDesktopWidget().availableGeometry().center()
		qtRec.moveCenter(centre)
		self.move(qtRec.topLeft())

		# box = QVBoxLayout()
		jsonTable = json.load(open('output/output_table.json', 'r'))
		row = len(jsonTable.keys()) + 1
		col = len(jsonTable[list(jsonTable.keys())[0]])

		print(jsonTable[list(jsonTable.keys())[0]])

		self.table = QTableWidget()
		self.table.setRowCount(row)
		self.table.setColumnCount(col)

		for index, (i, j) in enumerate(jsonTable[list(jsonTable.keys())[0]].items()):
			self.table.setItem(0, index, QTableWidgetItem(i))

		for i, valr in enumerate(jsonTable.keys()):
			for j, (temp, data) in enumerate(jsonTable[list(jsonTable.keys())[i]].items()):
				self.table.setItem(i + 1, j, QTableWidgetItem(data))

		# box.addWidget(self.table)
		# self.setLayout(box)

		self.setCentralWidget(self.table)
















class mainWindow(QMainWindow):
	def __init__(self):
		super(mainWindow, self).__init__()
		self.setStyleSheet(style)
		self.setGeometry(0 , 0, w, h)
		self.setFixedSize(w, h)
		self.setWindowTitle('Fotometta')
		self.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))

		qtRec = self.frameGeometry()
		centre = QDesktopWidget().availableGeometry().center()
		qtRec.moveCenter(centre)
		self.move(qtRec.topLeft())

		self.initGUI()

	def initGUI(self):
		self.iconLabel = QtWidgets.QLabel(self)
		self.iconLabel.setAlignment(Qt.AlignCenter)
		self.icon = QPixmap('ui_asset/icon.png')
		self.iconLabel.setPixmap(self.icon)
		self.iconLabel.resize(w, self.icon.height())

		self.openRosterButton = QtWidgets.QPushButton(self)
		self.openRosterButton.setText('Open Roster')
		self.openRosterButton.setFixedWidth(self.width() - 230)
		self.openRosterButton.move(115, self.icon.height())
		self.openRosterButton.clicked.connect(self.showRoster)

		self.text1 = QtWidgets.QLabel(self)
		self.text1.setText('Select the folder that contains your roster:')
		self.text1.setFont(QFont('Helvetica', 13))
		self.text1.setFixedWidth(self.width())
		self.text1.setAlignment(Qt.AlignCenter)
		self.text1.move(0, self.icon.height() + 35)

		self.folderText = QLineEdit(self)
		self.folderText.resize(250, 25)
		self.folderText.move(20, self.icon.height() + 75)

		self.folderButton = QtWidgets.QPushButton(self)
		self.folderButton.setText('Browse')
		self.folderButton.setFixedWidth(60)
		self.folderButton.move(276, self.icon.height() + 72)
		self.folderButton.clicked.connect(self.browseFolder)

		self.createNewButton = QtWidgets.QPushButton(self)
		self.createNewButton.setText('Create New Roster')
		self.createNewButton.setFixedWidth(150)
		self.createNewButton.move(25, self.icon.height() + 115)
		self.createNewButton.clicked.connect(self.createNew)

		self.addExistingButton = QtWidgets.QPushButton(self)
		self.addExistingButton.setText('Add to Existing')
		self.addExistingButton.setFixedWidth(140)
		self.addExistingButton.move(191, self.icon.height() + 115)
		self.addExistingButton.clicked.connect(self.addExisting)

	def showRoster(self):
		self.t = rosterTable()
		self.t.show()

	def browseFolder(self):
		self.folderpath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		self.folderText.setText(str(self.folderpath))

	def createNew(self):
		selectedFolder = self.folderText.text()

		if os.path.isdir(selectedFolder) == False:
			self.folderText.setText('Select a folder first')

		elif os.path.isdir(selectedFolder) == True:
			confirm = False

			if os.stat('output/output_table.json').st_size != 0:
				self.popup = QMessageBox()
				self.popup.setStyleSheet(style)
				self.popup.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
				self.popup.setWindowTitle('Warning')
				self.popup.setText('Warning: you have an existing roster saved.\nProceeding will overwrite your previous roster.')
				self.popup.setIcon(QMessageBox.Warning)
				self.popup.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
				self.popup.setDefaultButton(QMessageBox.Cancel)
				p = self.popup.exec_()

				if p == QMessageBox.Ok:
					confirm = True

			if os.stat('output/output_table.json').st_size == 0 or confirm == True:
				nameReader = easyocr.Reader(['en'])
				open('output/output_table.json', 'w').close()

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

				opDict = {} 

				with concurrent.futures.ThreadPoolExecutor() as executor:
					cfResults = [executor.submit(arkAssist, i, nameReader) for i in os.listdir('input')]
					i = 1

					for f in concurrent.futures.as_completed(cfResults):
						key = 'sample' + str(i)
						opDict[key] = f.result()
						i = i + 1

				with open('output/output_table.json', 'w') as file:
					json.dump(opDict, file, indent = 4)

				self.showRoster()

	def addExisting(self):
		selectedFolder = self.folderText.text()

		if os.path.isdir(selectedFolder) == False:
			self.folderText.setText('Select a folder first')

		elif os.path.isdir(selectedFolder) == True:
			nameReader = easyocr.Reader(['en'])

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

			opDict = {} 

			with concurrent.futures.ThreadPoolExecutor() as executor:
				cfResults = [executor.submit(arkAssist, i, nameReader) for i in os.listdir('input')]
				i = 1

				if os.stat('output/output_table.json').st_size != 0:
					tempjson = open('output/output_table.json', 'r')
					tempdata = json.load(tempjson)
					i = int(list(tempdata)[-1][-1:]) + 1
					tempjson.close()

				for f in concurrent.futures.as_completed(cfResults):
					key = 'sample' + str(i)
					opDict[key] = f.result()
					i = i + 1

			with open('output/output_table.json', 'r+') as file:
				if os.stat('output/output_table.json').st_size == 0:
					json.dump(opDict, file, indent = 4)
				else:
					tableData = json.load(file)
					finalData = {**tableData, **opDict}
					file.seek(0)
					json.dump(finalData, file, indent = 4)

			self.showRoster()

def startup():
	app = QApplication(sys.argv)
	win = mainWindow()

	win.show()
	sys.exit(app.exec_())

startup()