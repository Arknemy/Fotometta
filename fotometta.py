import os
import sys
import easyocr
import concurrent.futures
import json
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from fuzzywuzzy import fuzz
from assistant import *

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#HOUSEKEEPING--------------------------------------------------------------------------------------------------

style = open('ui_asset/darkorange.qss').read()
font = QFont('Roboto', 10)

datajson = json.load(open('json_files/character_table.json', encoding = "utf8"))
opList = []
rarityList = []
userRoster = []

for key in list(datajson):
	if datajson[key]['subProfessionId'] != 'notchar1' and datajson[key]['subProfessionId'] != 'notchar2':
		opList.append(datajson[key]['name'])
		rarityList.append(datajson[key]['rarity'])

#--------------------------------------------------------------------------------------------------------------

class addOpWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setStyleSheet(style)
		# self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		
	def getNewOP(self, message):
		newOp = message.lower()

		self.opName = ""
		self.opRarity = 0
		self.opPromotion = 'E0'
		self.opPotential = 1
		self.opLevel = 0
		self.skillRank = ""
		self.opS1 = ""
		self.opS2 = ""
		self.opS3 = ""
		self.opModule = ""

		newOpData = []

		for key in list(datajson):
			if datajson[key]['name'].lower() == newOp:
				newOpData = datajson[key]
				self.opName = datajson[key]['name']
				self.opRarity = datajson[key]['rarity']

		if self.opRarity == 5 or self.opRarity == 4:
			self.maxLevel = 50
		elif self.opRarity == 3:
			self.maxLevel = 45
		elif self.opRarity == 2:
			self.maxLevel = 40
		else:
			self.maxLevel = 30

		self.opImage = QtWidgets.QLabel(self)
		self.icon = QPixmap('ui_asset/op_icon/' + newOp + '1.png').scaled(90, 90, QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.opImage.resize(self.icon.width() + 10, 100)
		self.opImage.setAlignment(Qt.AlignCenter)
		self.opImage.setStyleSheet("background-color: #282828")
		self.opImage.setPixmap(self.icon)
		self.opImage.move(10, 12)

		stars = ''

		for i in range(0, newOpData['rarity'] + 1):
			stars += '★'

		self.opRarityLabel = QtWidgets.QLabel(self)
		self.opRarityLabel.setText(stars)
		self.opRarityLabel.setAlignment(Qt.AlignCenter)
		self.opRarityLabel.resize(90, 20)
		self.opRarityLabel.move(15, 115)

		self.opNameLabel = QtWidgets.QLabel(self)
		self.opNameLabel.setFont(QFont('Roboto', 13))
		self.opNameLabel.setText(self.opName)
		self.opNameLabel.adjustSize()
		# print(self.opNameLabel.size().width()) # IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT 
		self.opNameLabel.move(125, 53)

		self.eliteButton = QtWidgets.QPushButton(self)
		self.eliteButton.setStyleSheet("background-image : url(ui_asset/button_icon/e0.png);")
		self.eliteButton.setGeometry(125 + self.opNameLabel.size().width() + 13, 13, 70, 70)
		self.eliteButton.clicked.connect(self.updateElite)

		self.opLevelLabel = QtWidgets.QLabel(self)
		self.opLevelLabel.setFont(QFont('Roboto', 11))
		self.opLevelLabel.setText('Lv.')
		self.opLevelLabel.adjustSize()
		self.opLevelLabel.move(125 + self.opNameLabel.size().width() + 17, 98)

		self.levelCombo = QtWidgets.QComboBox(self)
		self.levelCombo.setGeometry(125 + self.opNameLabel.size().width() + 39, 93, 40, 29)
		for i in range(1, self.maxLevel + 1):
			self.levelCombo.addItem(str(i))
		self.levelCombo.activated[str].connect(self.updateLevel)  

		self.s1Button = QtWidgets.QPushButton(self)
		self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.s1Button.setGeometry(125 + self.opNameLabel.size().width() + 95, 72, 50, 50)
		self.s1Button.clicked.connect(self.updateS1)

		self.s2Button = QtWidgets.QPushButton(self)
		self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.s2Button.setGeometry(125 + self.opNameLabel.size().width() + 155, 72, 50, 50)
		self.s2Button.clicked.connect(self.updateS2)

		self.s3Button = QtWidgets.QPushButton(self)
		self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.s3Button.setGeometry(125 + self.opNameLabel.size().width() + 215, 72, 50, 50)
		self.s3Button.clicked.connect(self.updateS3)

		self.s1Button.setEnabled(False)
		self.s2Button.setEnabled(False)
		self.s3Button.setEnabled(False)

		self.potentialButton = QtWidgets.QPushButton(self)
		self.potentialButton.setStyleSheet("background-image : url(ui_asset/button_icon/p1.png);")
		self.potentialButton.setGeometry(125 + self.opNameLabel.size().width() + 95, 13, 50, 50)
		self.potentialButton.clicked.connect(self.updatePotential)





		self.setGeometry(0, 0, 500 + self.opNameLabel.size().width() , 140)
		self.setFixedSize(500 + self.opNameLabel.size().width(), 140)
		self.setWindowTitle('Edit Selection')
		self.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
		qtRec = self.frameGeometry()
		centre = QDesktopWidget().availableGeometry().center()
		qtRec.moveCenter(centre)
		self.move(qtRec.topLeft())




		# opFields = ["Name", "Rarity", "Level", "Promotion", "Potential", "Skill", "S1", "S2", "S3", 'Module']
		# opInput = [opName, str(opRarity + 1), str(opLevel) + "/" + str(maxLevel), opPromotion, str(opPotential), skillRank, opS1, opS2, opS3, opModule]

		# d = dict(zip(opFields, opInput))

	def updateElite(self):
		if self.opPromotion == 'E0' and self.opRarity > 1:
			self.eliteButton.setStyleSheet("background-image : url(ui_asset/button_icon/e1.png);")
			self.eliteButton.update()
			self.opPromotion = 'E1'
		elif self.opPromotion == 'E1' and self.opRarity > 2:
			self.eliteButton.setStyleSheet("background-image : url(ui_asset/button_icon/e2.png);")
			self.eliteButton.update()
			self.opPromotion = 'E2'
		elif self.opPromotion == 'E1' and self.opRarity <= 2 or self.opPromotion == 'E2':
			self.eliteButton.setStyleSheet("background-image : url(ui_asset/button_icon/e0.png);")
			self.eliteButton.update()
			self.opPromotion = 'E0'

		if self.opPromotion == 'E0' or self.opPromotion == 'E1':
			self.icon = QPixmap('ui_asset/op_icon/' + self.opName.lower() + '1.png').scaled(90, 90, QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)
			self.opImage.setPixmap(self.icon)
			self.opImage.update()
		else:
			self.icon = QPixmap('ui_asset/op_icon/' + self.opName.lower() + '2.png').scaled(90, 90, QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)
			self.opImage.setPixmap(self.icon)
			self.opImage.update()

		if self.opPromotion == 'E0':
			if self.opRarity == 5 or self.opRarity == 4:
				self.maxLevel = 50
			elif self.opRarity == 3:
				self.maxLevel = 45
			elif self.opRarity == 2:
				self.maxLevel = 40
			else:
				self.maxLevel = 30
		elif self.opPromotion == 'E1':
			if self.opRarity == 5:
				self.maxLevel = 80
			elif self.opRarity == 3:
				self.maxLevel = 70
			elif self.opRarity == 3:
				self.maxLevel = 60
			elif self.opRarity == 2:
				self.maxLevel = 55
			else:
				self.maxLevel = 30
		elif self.opPromotion == 'E2':
			if self.opRarity == 5:
				self.maxLevel = 90
			elif self.opRarity == 3:
				self.maxLevel = 80
			elif self.opRarity == 3:
				self.maxLevel = 70
			elif self.opRarity == 2:
				self.maxLevel = 55
			else:
				self.maxLevel = 30

		self.levelCombo.clear()

		for i in range(1, self.maxLevel + 1):
			self.levelCombo.addItem(str(i))

		self.levelCombo.update()
		self.opLevel = 1

		self.s1Button.setEnabled(False)
		self.s2Button.setEnabled(False)
		self.s3Button.setEnabled(False)
		self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.opS1 = ''
		self.opS2 = ''
		self.opS3 = ''

		if self.opPromotion == 'E2':
			if self.opRarity == 5:
				self.s1Button.setEnabled(True)
				self.s2Button.setEnabled(True)
				self.s3Button.setEnabled(True)
			elif self.opRarity == 4 or self.opRarity == 3:
				self.s1Button.setEnabled(True)
				self.s2Button.setEnabled(True)

		self.s1Button.update()
		self.s2Button.update()
		self.s3Button.update()


	def updateLevel(self, text):
		self.opLevel = text
		print(self.opLevel)

	def updateS1(self):
		if self.opS1 == '':
			self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/m1.png);")
			self.opS1 = 'M1'
		elif self.opS1 == 'M1':
			self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/m2.png);")
			self.opS1 = 'M2'
		elif self.opS1 == 'M2':
			self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/m3.png);")
			self.opS1 = 'M3'
		else:
			self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
			self.opS1 = ''

		self.s1Button.update()

	def updateS2(self):
		if self.opS2 == '':
			self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/m1.png);")
			self.opS2 = 'M1'
		elif self.opS2 == 'M1':
			self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/m2.png);")
			self.opS2 = 'M2'
		elif self.opS2 == 'M2':
			self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/m3.png);")
			self.opS2 = 'M3'
		else:
			self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
			self.opS2 = ''

		self.s2Button.update()

	def updateS3(self):
		if self.opS3 == '':
			self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/m1.png);")
			self.opS3 = 'M1'
		elif self.opS3 == 'M1':
			self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/m2.png);")
			self.opS3 = 'M2'
		elif self.opS3 == 'M2':
			self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/m3.png);")
			self.opS3 = 'M3'
		else:
			self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
			self.opS3 = ''

		self.s3Button.update()

	def updatePotential(self):
		if self.opPotential >= 1 and self.opPotential <= 5:
			self.opPotential += 1
			pot = 'p' + str(self.opPotential) + '.png'
			self.potentialButton.setStyleSheet("background-image : url(ui_asset/button_icon/" + pot + ");")
		else:
			self.opPotential = 1
			self.potentialButton.setStyleSheet("background-image : url(ui_asset/button_icon/p1.png);")

		self.potentialButton.update()

	def closeEvent(self, event):
		try:
			self.opRarityLabel.hide()
			self.opNameLabel.hide()
			self.eliteButton.hide()
			self.levelCombo.hide()
			self.opLevelLabel.hide()
			self.s1Button.hide()
			self.s2Button.hide()
			self.s3Button.hide()
		except:
			print('not all defined')
		else:
			self.opRarityLabel.hide()
			self.opNameLabel.hide()
			self.eliteButton.hide()
			self.levelCombo.hide()
			self.opLevelLabel.hide()
			self.s1Button.hide()
			self.s2Button.hide()
			self.s3Button.hide()
		finally:
			self.close()

#--------------------------------------------------------------------------------------------------------------

class rosterTable(QMainWindow):
	def __init__(self):
		super(rosterTable, self).__init__()
		self.setStyleSheet(style)
		jsonTable = json.loads(open('fotometta_output/output_dict.txt', 'r').read())
		row = len(jsonTable.keys())
		col = len(jsonTable[list(jsonTable.keys())[0]]) + 1
		tableWidth = 0
		minDim = 50
		height = 558

		self.table = QtWidgets.QTableWidget(self)
		self.table.setFont(QFont('Roboto', 11))
		self.table.setRowCount(row)
		self.table.setColumnCount(col)
		headers = ['Icon']

		self.table.clear()

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
					userRoster.append(data)

				if data == 'M0':
					self.table.setCellWidget(i, skip, self.getImageQt('m0.png', mSize))
				elif data == 'M1':
					self.table.setCellWidget(i, skip, self.getImageQt('m1.png', mSize))
				elif data == 'M2':
					self.table.setCellWidget(i, skip, self.getImageQt('m2.png', mSize))
				elif data == 'M3':
					self.table.setCellWidget(i, skip, self.getImageQt('m3.png', mSize))
				elif temp == 'Potential':
					pot = 'p' + str(data) +'.png'
					self.table.setCellWidget(i, skip, self.getImageQt(pot, mSize))
				elif data == 'E0':
					self.table.setCellWidget(i, skip, self.getImageQt('e0.png', mSize))
					fileName += '1.png'
				elif data == 'E1':
					self.table.setCellWidget(i, skip, self.getImageQt('e1.png', mSize))
					if fileName == 'amiya':
						fileName += '2.png'
					else:
						fileName += '1.png'
				elif data == 'E2':
					self.table.setCellWidget(i, skip, self.getImageQt('e2.png', mSize))
					if fileName == 'amiya':
						fileName += '3.png'
					else:
						fileName += '2.png'
				elif temp == 'Rarity':
					stars = ''

					for k in range (0, int(data)):
						stars += '★'

					self.table.setItem(i, skip, QTableWidgetItem(stars))
				elif temp == 'Module':
					if data != 'None':
						self.table.setCellWidget(i, skip, self.getImageQt('module_icon/' + data + '.png', mSize))
				else:
					self.table.setItem(i, skip, QTableWidgetItem(data))

				if j == 9:
					self.table.setCellWidget(i, 0, self.getImageQt('op_icon/' + fileName, minDim))

			self.table.setRowHeight(i, minDim)

		self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
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

		if tableHeight > height:
			tableWidth += 15

		self.text1 = QtWidgets.QLabel(self)
		self.text1.setText('Filter:')
		self.text1.setFont(QFont('Roboto', 11))
		self.text1.setFixedWidth(self.width())
		self.text1.move(8, -1)

		self.inputText = QLineEdit(self)
		self.inputText.resize(250, 20)
		self.inputText.move(45, 5)
		self.inputText.textChanged.connect(self.filter)

		self.addButton = QtWidgets.QPushButton(self)
		self.addButton.setText('Add')
		self.addButton.setFixedWidth(120)
		self.addButton.setFixedHeight(40)
		self.addButton.move(tableWidth + 15, 28)
		self.addButton.clicked.connect(self.addOperator)

		self.editButton = QtWidgets.QPushButton(self)
		self.editButton.setText('Edit')
		self.editButton.setFixedWidth(120)
		self.editButton.setFixedHeight(40)
		self.editButton.move(tableWidth + 15, 83)
		self.editButton.clicked.connect(self.closeEvent)

		self.outputJsonButton = QtWidgets.QPushButton(self)
		self.outputJsonButton.setText('Output to Image')
		self.outputJsonButton.setFixedWidth(120)
		self.outputJsonButton.setFixedHeight(40)
		self.outputJsonButton.move(tableWidth + 15, 390)
		self.outputJsonButton.clicked.connect(self.outputImage)

		self.closeButton = QtWidgets.QPushButton(self)
		self.closeButton.setText('Close')
		self.closeButton.setFixedWidth(120)
		self.closeButton.setFixedHeight(40)
		self.closeButton.move(tableWidth + 15, 445)
		self.closeButton.clicked.connect(self.closeEvent)


		self.table.setGeometry(QtCore.QRect(0, 30, tableWidth, height - 30))
		self.setGeometry(0, 0, tableWidth + 150, height)
		self.setFixedSize(tableWidth + 150, height)
		self.setWindowTitle('Roster')
		self.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
		qtRec = self.frameGeometry()
		centre = QDesktopWidget().availableGeometry().center()
		qtRec.moveCenter(centre)
		self.move(qtRec.topLeft())

		self.addOpW = addOpWindow()

	def getImageQt(self, path, scale):
		label = QLabel(self)
		icon = QPixmap('ui_asset/' + path).scaled(scale, scale, QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)
		label.setStyleSheet("background-color: duron grizzle gray")
		label.setAlignment(Qt.AlignCenter)
		label.setPixmap(icon)
		return label

	def filter(self):
		if self.inputText.text() != '' and self.inputText.text().isalpha() == True:
			search = self.inputText.text().lower()

			for i in range(0, self.table.rowCount()):
				item = self.table.item(i, 1).text().lower()

				if search not in item:
					self.table.setRowHidden(i, True)
				else: 
					self.table.setRowHidden(i, False)

		else:
			for i in range(0, self.table.rowCount()):
				self.table.setRowHidden(i, False)

	def addOperator(self):
		popup = QInputDialog(self)
		popup.setWindowFlags(popup.windowFlags() & ~Qt.WindowContextHelpButtonHint)
		popup.setWindowTitle("Input")
		popup.setLabelText("Enter Operator Name:")
		popup.setFixedSize(300, 0)

		if popup.exec_() == QDialog.Accepted:
			inputName = popup.textValue()
		else:
			inputName = 'Cancel'

		if inputName.lower() in (name.lower() for name in opList):
			if inputName.lower() not in (name2.lower() for name2 in userRoster):
				self.addOpW.getNewOP(inputName)
				self.addOpW.show()
			else:
				popup2 = QMessageBox()
				popup2.setStyleSheet(style)
				popup2.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
				popup2.setWindowTitle('Warning')
				popup2.setText('Operator already added.')
				popup2.setFont(QFont('Roboto', 11))
				popup2.setIconPixmap(QPixmap('ui_asset/prtswarning.png'))
				popup2.setStandardButtons(QMessageBox.Ok)
				popup2.buttons()[0].setFixedSize(QtCore.QSize(100, 30))
				popup2.setDefaultButton(QMessageBox.Ok)
				popup2.exec_()
		elif inputName != 'Cancel':
			popup2 = QMessageBox()
			popup2.setStyleSheet(style)
			popup2.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
			popup2.setWindowTitle('Warning')
			popup2.setText('Operator not found.')
			popup2.setFont(QFont('Roboto', 11))
			popup2.setIconPixmap(QPixmap('ui_asset/prtswarning.png'))
			popup2.setStandardButtons(QMessageBox.Ok)
			popup2.buttons()[0].setFixedSize(QtCore.QSize(100, 30))
			popup2.setDefaultButton(QMessageBox.Ok)
			popup2.exec_()

	def outputImage(self):
		tw, th = 0, 4

		for i in range(self.table.columnCount()):
			tw += self.table.columnWidth(i) + 3

		for i in range(self.table.rowCount()):
			th += self.table.rowHeight(i) + 1

		self.table.setFixedSize(tw, th)
		self.table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		pic = QtGui.QPixmap(self.table.size())
		self.table.render(pic)
		pic.save('fotometta_output/roster.jpg')

		self.close()

	def closeEvent(self, event):
		# QApplication.closeAllWindows()
		self.addOpW.close()
		self.close()

#--------------------------------------------------------------------------------------------------------------

w = 356
h = 393

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
		self.openRosterButton.setStyleSheet("QPushButton { font-size: 15px; }")
		self.openRosterButton.setFixedWidth(180)
		self.openRosterButton.setFixedHeight(50)
		self.openRosterButton.move(88, self.icon.height())
		self.openRosterButton.clicked.connect(self.showRoster)

		self.text1 = QtWidgets.QLabel(self)
		self.text1.setText('Select the folder that contains your roster:')
		self.text1.setFont(QFont('Roboto', 13))
		self.text1.setFixedWidth(self.width())
		self.text1.setAlignment(Qt.AlignCenter)
		self.text1.move(0, self.icon.height() + 55)

		self.folderText = QLineEdit(self)
		self.folderText.resize(250, 25)
		self.folderText.move(20, self.icon.height() + 95)

		self.folderButton = QtWidgets.QPushButton(self)
		self.folderButton.setText('Browse')
		self.folderButton.setFixedWidth(60)
		self.folderButton.move(276, self.icon.height() + 92)
		self.folderButton.clicked.connect(self.browseFolder)

		self.createNewButton = QtWidgets.QPushButton(self)
		self.createNewButton.setText('Create New Roster')
		self.createNewButton.setFixedWidth(150)
		self.createNewButton.setFixedHeight(40)
		self.createNewButton.move(25, self.icon.height() + 135)
		self.createNewButton.clicked.connect(self.createNew)

		self.updateExistingButton = QtWidgets.QPushButton(self)
		self.updateExistingButton.setText('Update Existing')
		self.updateExistingButton.setFixedWidth(140)
		self.updateExistingButton.setFixedHeight(40)
		self.updateExistingButton.move(191, self.icon.height() + 135)
		self.updateExistingButton.clicked.connect(self.updateExisting)


	def showRoster(self):
		if os.stat('fotometta_output/output_dict.txt').st_size != 0:
			self.openRosterWindow = rosterTable()
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

			if os.stat('fotometta_output/output_dict.txt').st_size != 0:
				popup = QMessageBox()
				popup.setStyleSheet(style)
				popup.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
				popup.setWindowTitle('Warning')
				popup.setText('Warning: you have an existing roster saved.\nProceeding will overwrite your previous roster.')
				popup.setFont(QFont('Roboto', 11))
				popup.setIconPixmap(QPixmap('ui_asset/prtswarning.png'))
				popup.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
				popup.setDefaultButton(QMessageBox.Cancel)
				p = popup.exec_()

				if p == QMessageBox.Ok:
					confirm = True

			if os.stat('fotometta_output/output_dict.txt').st_size == 0 or confirm == True:
				nameReader = easyocr.Reader(['en'])
				open('fotometta_output/output_dict.txt', 'w').close()
				resizeRoster(selectedFolder)

				finalData = {}
				fileNum = 0

				for i in os.listdir('fotometta_input'):
					fileNum += 1

				with concurrent.futures.ThreadPoolExecutor() as executor:
					cfResults = [executor.submit(arkAssist, i, nameReader) for i in os.listdir('fotometta_input')]
					key = 0

					for f in concurrent.futures.as_completed(cfResults):
						key += 1
						finalData['sample' + str(key)] = f.result()

				finalData = assembleDict(finalData)

				with open('fotometta_output/output_dict.txt', 'w') as file:
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
				cfResults = [executor.submit(arkAssist, i, nameReader) for i in os.listdir('fotometta_input')]

				if os.stat('fotometta_output/output_dict.txt').st_size == 0:
					key = 0

					for f in concurrent.futures.as_completed(cfResults):
						key += 1
						finalData['sample' + str(key)] = f.result()

				else:
					jsonTable = json.loads(open('fotometta_output/output_dict.txt', 'r').read())
					key = len(jsonTable.keys())
					
					for f in concurrent.futures.as_completed(cfResults):
						key += 1
						finalData['sample' + str(key)] = f.result()

			with open('fotometta_output/output_dict.txt', 'r+') as file:
				if os.stat('fotometta_output/output_dict.txt').st_size == 0:
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
		#self.openRosterWindow.close()
		QApplication.closeAllWindows()
		self.close()

#--------------------------------------------------------------------------------------------------------------

def startup():
	app = QApplication(sys.argv)
	QApplication.instance().setFont(font)
	win = mainWindow()

	win.show()
	sys.exit(app.exec_())

startup()