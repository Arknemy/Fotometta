import os
import sys
import easyocr
import concurrent.futures
import json
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from assistant import *

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#--------------------------------------------------------------------------------------------------------------

w = 356
h = 363
style = open('ui_asset/darkorange.qss').read()
font = QFont('Roboto', 10)

class addOperatorBox(QMainWindow):
	def __init__(self):
		super(addOperatorBox, self).__init__()
		self.setStyleSheet(style)
		self.setGeometry(0, 0, 300, 100)
		self.setFixedSize(300, 105)
		self.setWindowTitle('Enter Operator Name')
		self.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
		qtRec = self.frameGeometry()
		centre = QDesktopWidget().availableGeometry().center()
		qtRec.moveCenter(centre)
		self.move(qtRec.topLeft())

		self.textbox = QLineEdit(self)
		self.textbox.move(20, 20)
		self.textbox.resize(260,25)

		self.createNewButton = QtWidgets.QPushButton(self)
		self.createNewButton.setText('Confirm')
		self.createNewButton.setFixedWidth(100)
		self.createNewButton.move(40, 60)
		self.createNewButton.clicked.connect(self.closeEvent)

		self.updateExistingButton = QtWidgets.QPushButton(self)
		self.updateExistingButton.setText('Cancel')
		self.updateExistingButton.setFixedWidth(100)
		self.updateExistingButton.move(160, 60)
		self.updateExistingButton.clicked.connect(self.closeEvent)

	# def confirmOperator(self):





	def closeEvent(self, event):
		self.close()

#--------------------------------------------------------------------------------------------------------------

class rosterTable(QMainWindow):
	def __init__(self):
		super(rosterTable, self).__init__()
		self.setStyleSheet(style)
		jsonTable = json.loads(open('output/output_dict.txt', 'r').read())
		row = len(jsonTable.keys())
		col = len(jsonTable[list(jsonTable.keys())[0]]) + 1
		tableWidth = 0
		minDim = 50

		self.table = QtWidgets.QTableWidget(self)
		self.table.setFont(QFont('Roboto', 11))
		self.table.setRowCount(row)
		self.table.setColumnCount(col)
		headers = ['Icon']

		for index, (i, j) in enumerate(jsonTable[list(jsonTable.keys())[0]].items()):
			headers.append(i)

		self.table.setHorizontalHeaderLabels(headers)
		self.table.horizontalHeader().setStyleSheet("QHeaderView { font-size: 10pt; font-weight: bold;}")

		for i, valr in enumerate(jsonTable.keys()):
			fileName = ''
			for j, (temp, data) in enumerate(jsonTable[list(jsonTable.keys())[i]].items()):
				skip = j + 1
				mSize = minDim - int(minDim * 0.1)

				if temp == 'Name':
					fileName = data.lower()

				if data == 'M0':
					self.table.setCellWidget(i, skip, self.getImageQt('m0.png', mSize))
				elif data == 'M1':
					self.table.setCellWidget(i, skip, self.getImageQt('m1.png', mSize))
				elif data == 'M2':
					self.table.setCellWidget(i, skip, self.getImageQt('m2.png', mSize))
				elif data == 'M3':
					self.table.setCellWidget(i, skip, self.getImageQt('m3.png', mSize))
				elif temp == 'Potential' and data =='1':
					self.table.setCellWidget(i, skip, self.getImageQt('p1.png', mSize))
				elif temp == 'Potential' and data =='2':
					self.table.setCellWidget(i, skip, self.getImageQt('p2.png', mSize))
				elif temp == 'Potential' and data =='3':
					self.table.setCellWidget(i, skip, self.getImageQt('p3.png', mSize))
				elif temp == 'Potential' and data =='4':
					self.table.setCellWidget(i, skip, self.getImageQt('p4.png', mSize))
				elif temp == 'Potential' and data =='5':
					self.table.setCellWidget(i, skip, self.getImageQt('p5.png', mSize))
				elif temp == 'Potential' and data =='6':
					self.table.setCellWidget(i, skip, self.getImageQt('p6.png', mSize))
				elif data == 'E0':
					self.table.setCellWidget(i, skip, self.getImageQt('e0.png', mSize))
					fileName += '1'
				elif data == 'E1':
					self.table.setCellWidget(i, skip, self.getImageQt('e1.png', mSize))

					if fileName == 'amiya':
						fileName += '2'
					else:
						fileName += '1'
				elif data == 'E2':
					self.table.setCellWidget(i, skip, self.getImageQt('e2.png', mSize))
					if fileName == 'amiya':
						fileName += '3'
					else:
						fileName += '2'
				elif temp == 'Rarity':
					stars = ''

					for k in range (0, int(data)):
						stars += '★'

					self.table.setItem(i, skip, QTableWidgetItem(stars))

				else:
					self.table.setItem(i, skip, QTableWidgetItem(data))

				if j == 8:
					fileName += '.png'
					# self.table.setCellWidget(i, 0, self.getImageQt('op_icon/' + fileName, minDim))

			self.table.setRowHeight(i, minDim)

		self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
		self.table.resizeColumnsToContents()
		self.table.verticalScrollBar().setStyleSheet("QScrollBar:vertical { width: 15px; }")
		self.table.horizontalScrollBar().setStyleSheet("QScrollBar:horizontal { height: 15px; }")
		tableWidth = self.table.verticalHeader().size().width()
		tableHeight = self.table.horizontalHeader().size().height()

		for i in range(0, col):
			if self.table.columnWidth(i) < minDim:
				self.table.setColumnWidth(i, minDim)

		for i in range(self.table.columnCount()):
			tableWidth += self.table.columnWidth(i)

		for i in range(self.table.rowCount()):
			tableHeight += self.table.rowHeight(i) + 1

		tableWidth += 2 #scrollbar width

		if tableHeight > 500:
			tableWidth += 15

		self.addButton = QtWidgets.QPushButton(self)
		self.addButton.setText('Add')
		self.addButton.setFixedWidth(120)
		self.addButton.move(tableWidth + 15, 15)
		self.addButton.clicked.connect(self.addOperator)
		self.addOpWindow = addOperatorBox()

		self.editButton = QtWidgets.QPushButton(self)
		self.editButton.setText('Edit')
		self.editButton.setFixedWidth(120)
		self.editButton.move(tableWidth + 15, 55)
		self.editButton.clicked.connect(self.closeEvent)

		self.closeButton = QtWidgets.QPushButton(self)
		self.closeButton.setText('Close')
		self.closeButton.setFixedWidth(120)
		self.closeButton.move(tableWidth + 15, 455)
		self.closeButton.clicked.connect(self.closeEvent)

		self.table.setGeometry(QtCore.QRect(0, 0, tableWidth, 500))
		self.setGeometry(0, 0, tableWidth + 150, 500)
		self.setFixedSize(tableWidth + 150, 500)
		self.setWindowTitle('Roster')
		self.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
		qtRec = self.frameGeometry()
		centre = QDesktopWidget().availableGeometry().center()
		qtRec.moveCenter(centre)
		self.move(qtRec.topLeft())

	def getImageQt(self, path, scale):
		label = QLabel(self)
		icon = QPixmap('ui_asset/' + path).scaled(scale, scale, QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)
		label.setStyleSheet("background-color: duron grizzle gray")
		label.setAlignment(Qt.AlignCenter)
		label.setPixmap(icon)
		return label

	def addOperator(self):
		self.addOpWindow.show()

	def closeEvent(self, event):
		self.addOpWindow.close()
		self.close()

#---------------------------------------------------------------------------------------------------------------------------------

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
		self.openRosterWindow = rosterTable()

		self.text1 = QtWidgets.QLabel(self)
		self.text1.setText('Select the folder that contains your roster:')
		self.text1.setFont(QFont('Roboto', 13))
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

		self.updateExistingButton = QtWidgets.QPushButton(self)
		self.updateExistingButton.setText('Update Existing')
		self.updateExistingButton.setFixedWidth(140)
		self.updateExistingButton.move(191, self.icon.height() + 115)
		self.updateExistingButton.clicked.connect(self.updateExisting)

	def showRoster(self):
		if os.stat('output/output_dict.txt').st_size != 0:
			self.openRosterWindow.show()
		else:
			self.folderText.setText('You have no existing rosters')

	def browseFolder(self):
		self.folderpath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		self.folderText.setText(str(self.folderpath))

	def createNew(self):
		selectedFolder = self.folderText.text()

		if os.path.isdir(selectedFolder) == False:
			self.folderText.setText('Select a folder first')

		elif os.path.isdir(selectedFolder) == True:
			confirm = False

			if os.stat('output/output_dict.txt').st_size != 0:
				self.popup = QMessageBox()
				self.popup.setStyleSheet(style)
				self.popup.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
				self.popup.setWindowTitle('Warning')
				self.popup.setText('Warning: you have an existing roster saved.\n\nProceeding will overwrite your previous roster.')
				self.popup.setIcon(QMessageBox.Warning)
				self.popup.setIconPixmap(QPixmap('ui_asset/prtswarning.png'))
				self.popup.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
				self.popup.setDefaultButton(QMessageBox.Cancel)
				p = self.popup.exec_()

				if p == QMessageBox.Ok:
					confirm = True

			if os.stat('output/output_dict.txt').st_size == 0 or confirm == True:
				nameReader = easyocr.Reader(['en'])
				open('output/output_dict.txt', 'w').close()
				resizeRoster(selectedFolder)

				finalData = {}
				fileNum = 0

				for i in os.listdir('input'):
					fileNum += 1

				with concurrent.futures.ThreadPoolExecutor() as executor:
					cfResults = [executor.submit(arkAssist, i, nameReader) for i in os.listdir('input')]
					key = 0

					for f in concurrent.futures.as_completed(cfResults):
						key += 1
						finalData['sample' + str(key)] = f.result()

				finalData = assembleDict(finalData)

				with open('output/output_dict.txt', 'w') as file:
					file.write(json.dumps(finalData))

				self.showRoster()

	def updateExisting(self):
		selectedFolder = self.folderText.text()

		if os.path.isdir(selectedFolder) == False:
			self.folderText.setText('Select a folder first')

		elif os.path.isdir(selectedFolder) == True:
			nameReader = easyocr.Reader(['en'])
			resizeRoster(selectedFolder)

			finalData = {}

			with concurrent.futures.ThreadPoolExecutor() as executor:
				cfResults = [executor.submit(arkAssist, i, nameReader) for i in os.listdir('input')]

				if os.stat('output/output_dict.txt').st_size == 0:
					key = 0

					for f in concurrent.futures.as_completed(cfResults):
						key += 1
						finalData['sample' + str(key)] = f.result()

				else:
					jsonTable = json.loads(open('output/output_dict.txt', 'r').read())
					key = len(jsonTable.keys())
					
					for f in concurrent.futures.as_completed(cfResults):
						key += 1
						finalData['sample' + str(key)] = f.result()

			with open('output/output_dict.txt', 'r+') as file:
				if os.stat('output/output_dict.txt').st_size == 0:
					finalData = assembleDict(finalData)
					file.write(json.dumps(finalData))
				else:
					tableData = json.loads(file.read())
					a1, a2 = [], []

					for entry in tableData:
						a1.append(tableData[entry])

					for entry in finalData:
						a2.append(finalData[entry])

					a1.extend(a2)
					finalData = arrToDict(a1)
					finalData = assembleDict(finalData)
					file.seek(0)
					file.truncate()
					file.write(json.dumps(finalData))

			self.showRoster()

	def closeEvent(self, event):
		self.openRosterWindow.close()
		self.close()

#--------------------------------------------------------------------------------------------------------------

def startup():
	app = QApplication(sys.argv)
	QApplication.instance().setFont(font)
	win = mainWindow()

	win.show()
	sys.exit(app.exec_())

startup()