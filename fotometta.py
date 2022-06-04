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
modulejson = json.load(open('json_files/uniequip_table.json', encoding = "utf8"))
opList = []
rarityList = []
userRoster = []

#--------------------------------------------------------------------------------------------------------------

def initOpList():
	opList.clear()
	rarityList.clear()

	for key in list(datajson):
		if datajson[key]['subProfessionId'] != 'notchar1' and datajson[key]['subProfessionId'] != 'notchar2':
			opList.append(datajson[key]['name'])
			rarityList.append(datajson[key]['rarity'])

#--------------------------------------------------------------------------------------------------------------

class addOpWindow(QMainWindow):
	submitted = QtCore.pyqtSignal(str)

	def __init__(self):
		super().__init__()
		self.setStyleSheet(style)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		
	def getNewOP(self, message):
		newOp = message.lower()

		self.opName = ""
		self.opRarity = 0
		self.opPromotion = 'E0'
		self.opPotential = 1
		self.opLevel = 1
		self.skillRank = "RANK 1"
		self.opS1 = ""
		self.opS2 = ""
		self.opS3 = ""
		self.opModule = "None"

		self.newOpData = []
		self.hasModule = []
		self.modName = []

		with open('fotometta_output/output_dict.txt', 'r+') as file:
			self.savedData = json.loads(file.read())

		for key in list(datajson):
			if datajson[key]['name'].lower() == newOp:
				self.newOpData = datajson[key]
				self.opName = datajson[key]['name']
				self.opRarity = datajson[key]['rarity']

		for key in list(self.savedData):
			if self.opName == self.savedData[key]['Name']:
				self.opPromotion = self.savedData[key]['Promotion']
				self.opLevel = int(self.savedData[key]['Level'].split('/')[0])
				self.opPotential = int(self.savedData[key]['Potential'])
				self.skillRank = self.savedData[key]['Skill']
				self.opS1 = self.savedData[key]['S1']
				self.opS2 = self.savedData[key]['S2']
				self.opS3 = self.savedData[key]['S3']
				self.opModule = self.savedData[key]['Module']
				break;

		for key, value in modulejson.items():
		    if key != 'missionList' and key != 'subProfDict' and key != 'charEquip':
		        for key2, value2 in modulejson[key].items():
		            if modulejson[key][key2]['uniEquipIcon'] == 'original':
		                self.hasModule.append(modulejson[key][key2]['uniEquipName'][:-8])
		            elif modulejson[key][key2]['uniEquipIcon'] != 'original':
		                self.modName.append(modulejson[key][key2]['typeIcon'])

		self.maxLevel = getMaxLevel(self.opPromotion, int(self.opRarity))

		if self.opPromotion == 'E2':
			newOp = self.opName.lower() + '2'
		else: 
			newOp = self.opName.lower() + '1'

		self.opImage = QtWidgets.QLabel(self)
		self.icon = QPixmap('ui_asset/op_icon/' + newOp + '.png').scaled(90, 90, QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.opImage.resize(self.icon.width() + 10, 100)
		self.opImage.setAlignment(Qt.AlignCenter)
		self.opImage.setStyleSheet("background-color: #282828")
		self.opImage.setPixmap(self.icon)
		self.opImage.move(10, 12)

		stars = ''
		for i in range(0, self.newOpData['rarity'] + 1):
			stars += '★'

		self.opRarityLabel = QtWidgets.QLabel(stars, self)
		self.opRarityLabel.setAlignment(Qt.AlignCenter)
		self.opRarityLabel.setGeometry(15, 115, 90, 20)

		self.opNameLabel = QtWidgets.QLabel(self.opName, self)
		self.opNameLabel.setFont(QFont('Roboto', 13))
		self.opNameLabel.adjustSize()
		self.opNameLabel.move(125, 53)

		self.eliteButton = QtWidgets.QPushButton(self)
		self.eliteButton.setStyleSheet("background-image : url(ui_asset/button_icon/" + self.opPromotion.lower() + ".png);")
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
		self.levelCombo.setCurrentIndex(self.opLevel - 1)
		self.levelCombo.activated[str].connect(self.updateLevel)  

		self.s1Button = QtWidgets.QPushButton(self)
		if self.opS1 == '':
			self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		else:
			self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/" + self.opS1.lower() + ".png);")
		self.s1Button.setGeometry(125 + self.opNameLabel.size().width() + 95, 72, 50, 50)
		self.s1Button.clicked.connect(self.updateS1)

		self.s2Button = QtWidgets.QPushButton(self)
		if self.opS2 == '':
			self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		else:
			self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/" + self.opS2.lower() + ".png);")
		self.s2Button.setGeometry(125 + self.opNameLabel.size().width() + 155, 72, 50, 50)
		self.s2Button.clicked.connect(self.updateS2)

		self.s3Button = QtWidgets.QPushButton(self)
		if self.opS3 == '':
			self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		else:
			self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/" + self.opS3.lower() + ".png);")
		self.s3Button.setGeometry(125 + self.opNameLabel.size().width() + 215, 72, 50, 50)
		self.s3Button.clicked.connect(self.updateS3)

		self.s1Button.setEnabled(False)
		self.s2Button.setEnabled(False)
		self.s3Button.setEnabled(False)

		if self.skillRank == 'RANK 7' and self.opPromotion == 'E2' and self.skillRank == 'RANK 7':
			self.s1Button.setEnabled(True)
			self.s2Button.setEnabled(True)
			self.s3Button.setEnabled(True)

		self.skillRankLabel = QtWidgets.QLabel(self)
		self.skillRankLabel.setFont(QFont('Roboto', 9))
		self.skillRankLabel.setText('Skill Rank')
		self.skillRankLabel.adjustSize()
		self.skillRankLabel.move(125 + self.opNameLabel.size().width() + 96, 15)

		self.skillRankCombo = QtWidgets.QComboBox(self)
		self.skillRankCombo.setGeometry(125 + self.opNameLabel.size().width() + 95, 33, 52, 30)
		for i in range(1, 5):
			self.skillRankCombo.addItem(str(i))
		if self.opPromotion == 'E1' or self.opPromotion == 'E2':
			for i in range(5, 8):
				self.skillRankCombo.addItem(str(i))
		self.skillRankCombo.setCurrentIndex(int(self.skillRank[-1]) - 1)
		self.skillRankCombo.activated[str].connect(self.updateSkillRank)

		if self.opRarity == 0 or self.opRarity == 1:
			self.skillRankCombo.setEnabled(False)

		self.potentialButton = QtWidgets.QPushButton(self)
		self.potentialButton.setStyleSheet("background-image : url(ui_asset/button_icon/p" + str(self.opPotential) + ".png);")
		self.potentialButton.setGeometry(125 + self.opNameLabel.size().width() + 155, 13, 50, 50)
		self.potentialButton.clicked.connect(self.updatePotential)

		self.moduleButton = QtWidgets.QPushButton(self)
		self.moduleButton.setStyleSheet("background-image : url(ui_asset/button_icon/original.png);")
		if self.opModule != 'None':
			self.moduleButton.setStyleSheet("background-image : url(ui_asset/button_icon/" + self.opModule + ".png);")
		self.moduleButton.setGeometry(125 + self.opNameLabel.size().width() + 215, 13, 50, 50)
		self.moduleButton.clicked.connect(self.updateModule)
		self.moduleButton.setEnabled(False)
		if self.opRarity == 3 and int(self.opLevel) >= 40:
			self.moduleButton.setEnabled(True)
		elif self.opRarity == 4 and int(self.opLevel) >= 50:
			self.moduleButton.setEnabled(True)
		elif self.opRarity == 5 and int(self.opLevel) >= 60:
			self.moduleButton.setEnabled(True)

		self.confirmButton = QtWidgets.QPushButton(self)
		self.confirmButton.setText('Confirm')
		self.confirmButton.setGeometry(125 + self.opNameLabel.size().width() + 285, 13, 70, 109)
		self.confirmButton.clicked.connect(self.confirmOp)
		self.confirmButton.clicked.connect(self.submitExit)

		self.setGeometry(0, 0, 493 + self.opNameLabel.size().width() , 140)
		self.setFixedSize(493 + self.opNameLabel.size().width(), 140)
		self.setWindowTitle('Edit Selection')
		self.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
		qtRec = self.frameGeometry()
		centre = QDesktopWidget().availableGeometry().center()
		qtRec.moveCenter(centre)
		self.move(qtRec.topLeft())

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

		self.maxLevel = getMaxLevel(self.opPromotion, int(self.opRarity))

		self.levelCombo.clear()
		for i in range(1, self.maxLevel + 1):
			self.levelCombo.addItem(str(i))
		self.levelCombo.update()
		self.opLevel = 1

		currentRank = self.skillRank[-1]

		if self.opPromotion == 'E1' or self.opPromotion == 'E2':
			self.skillRankCombo.clear()
			for i in range(1, 8):
				self.skillRankCombo.addItem(str(i))
			self.skillRankCombo.setCurrentIndex(int(currentRank) - 1)
		else:
			self.skillRankCombo.clear()
			for i in range(1, 5):
				self.skillRankCombo.addItem(str(i))
			if int(currentRank) > 4:
				currentRank = '4'
				self.skillRank = 'RANK 4'
				self.skillRankCombo.setCurrentIndex(int(currentRank) - 1)

		self.s1Button.setEnabled(False)
		self.s2Button.setEnabled(False)
		self.s3Button.setEnabled(False)
		self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.opS1 = ''
		self.opS2 = ''
		self.opS3 = ''

		if self.skillRank == 'RANK 7' and self.opPromotion == 'E2':
			if self.opRarity == 5:
				self.s1Button.setEnabled(True)
				self.s2Button.setEnabled(True)
				self.s3Button.setEnabled(True)
				self.opS1 = 'M0'
				self.opS2 = 'M0'
				self.opS3 = 'M0'
			elif self.opRarity == 4 or self.opRarity == 3:
				self.s1Button.setEnabled(True)
				self.s2Button.setEnabled(True)
				self.opS1 = 'M0'
				self.opS2 = 'M0'

		self.s1Button.update()
		self.s2Button.update()
		self.s3Button.update()

		if self.opName in self.hasModule and self.opPromotion == 'E2':
			if self.opRarity == 3 and int(self.opLevel) >= 40:
				self.moduleButton.setEnabled(True)
			elif self.opRarity == 4 and int(self.opLevel) >= 50:
				self.moduleButton.setEnabled(True)
			elif self.opRarity == 5 and int(self.opLevel) >= 60:
				self.moduleButton.setEnabled(True)
			else:
				self.moduleButton.setEnabled(False)
				self.moduleButton.setStyleSheet("background-image : url(ui_asset/button_icon/original.png);")
				self.opModule = 'None'
		else:
			self.moduleButton.setEnabled(False)
			self.moduleButton.setStyleSheet("background-image : url(ui_asset/button_icon/original.png);")
			self.opModule = 'None'

		self.moduleButton.update()

	def updateLevel(self, text):
		self.opLevel = text

		if self.opName in self.hasModule and self.opPromotion == 'E2':
			if self.opRarity == 3 and int(self.opLevel) >= 40:
				self.moduleButton.setEnabled(True)
			elif self.opRarity == 4 and int(self.opLevel) >= 50:
				self.moduleButton.setEnabled(True)
			elif self.opRarity == 5 and int(self.opLevel) >= 60:
				self.moduleButton.setEnabled(True)
			else:
				self.moduleButton.setEnabled(False)
				self.moduleButton.setStyleSheet("background-image : url(ui_asset/button_icon/original.png);")
				self.opModule = 'None'
		else:
			self.moduleButton.setEnabled(False)
			self.moduleButton.setStyleSheet("background-image : url(ui_asset/button_icon/original.png);")
			self.opModule = 'None'

		self.moduleButton.update()

	def updateSkillRank(self, text):
		self.skillRank = 'RANK ' + str(text)
		self.s1Button.setEnabled(False)
		self.s2Button.setEnabled(False)
		self.s3Button.setEnabled(False)
		self.s1Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.s2Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.s3Button.setStyleSheet("background-image : url(ui_asset/button_icon/m0.png);")
		self.opS1 = ''
		self.opS2 = ''
		self.opS3 = ''

		if self.skillRank == 'RANK 7' and self.opPromotion == 'E2':
			if self.opRarity == 5:
				self.s1Button.setEnabled(True)
				self.s2Button.setEnabled(True)
				self.s3Button.setEnabled(True)
				self.opS1 = 'M0'
				self.opS2 = 'M0'
				self.opS3 = 'M0'
			elif self.opRarity == 4 or self.opRarity == 3:
				self.s1Button.setEnabled(True)
				self.s2Button.setEnabled(True)
				self.opS1 = 'M0'
				self.opS2 = 'M0'

		self.s1Button.update()
		self.s2Button.update()
		self.s3Button.update()

	def updateS1(self):
		if self.opS1 == 'M0':
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
			self.opS1 = 'M0'

		self.s1Button.update()

	def updateS2(self):
		if self.opS2 == 'M0':
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
			self.opS2 = 'M0'

		self.s2Button.update()

	def updateS3(self):
		if self.opS3 == 'M0':
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
			self.opS3 = 'M0'

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

	def updateModule(self):
		if self.opModule == 'None' and self.opName in self.hasModule or self.opModule == 'original':
			for i in range(0, len(self.hasModule)):
				if self.hasModule[i] == self.opName:
					self.moduleButton.setStyleSheet("background-image : url(ui_asset/button_icon/" + self.modName[i] + ".png);")
			
			self.opModule = 'True'
		else:
			self.moduleButton.setStyleSheet("background-image : url(ui_asset/button_icon/original.png);")
			self.opModule = 'None'

		self.moduleButton.update()

	def confirmOp(self):
		opFields = ["Name", "Rarity", "Level", "Promotion", "Potential", "Skill", "S1", "S2", "S3", 'Module']
		opInput = [self.opName, str(self.opRarity + 1), str(self.opLevel) + "/" + str(self.maxLevel), self.opPromotion, str(self.opPotential), self.skillRank, self.opS1, self.opS2, self.opS3, self.opModule]
		d = dict(zip(opFields, opInput))
		finalData = {}
		finalData['sample1'] = d
		print(finalData)

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

	def submitExit(self):
		self.submitted.emit('close')
		self.close()

	def closeEvent(self, event):
		try:
			self.opRarityLabel.close()
		except:
			print('not all defined')
			pass
		else:
			self.opRarityLabel.close()
			self.opNameLabel.close()
			self.eliteButton.close()
			self.levelCombo.close()
			self.opLevelLabel.close()
			self.skillRankCombo.close()
			self.skillRankLabel.close()
			self.s1Button.close()
			self.s2Button.close()
			self.s3Button.close()
			self.potentialButton.close()
			self.moduleButton.close()
			self.confirmButton.close()
		finally:
			self.close()

#--------------------------------------------------------------------------------------------------------------

class rosterTable(QMainWindow):
	def __init__(self):
		super(rosterTable, self).__init__()
		self.setStyleSheet(style)

		self.table = QtWidgets.QTableWidget(self)
		self.tableWidth = 0
		self.minDim = 50
		self.height = 558
		self.opData = []
		self.mSize = 0

		self.initTable()
		self.centerWindow()

	def initTable(self):
		jsonTable = json.loads(open('fotometta_output/output_dict.txt', 'r').read())
		row = len(jsonTable.keys())
		col = len(jsonTable[list(jsonTable.keys())[0]]) + 1

		initOpList()

		self.table.clear()
		self.table.setFont(QFont('Roboto', 11))
		self.table.setRowCount(row)
		self.table.setColumnCount(col)
		headers = ['Icon']

		for index, (i, j) in enumerate(jsonTable[list(jsonTable.keys())[0]].items()):
			headers.append(i)

		self.table.setHorizontalHeaderLabels(headers)
		self.table.horizontalHeader().setStyleSheet("QHeaderView { font-size: 10pt; font-weight: bold;}")
		userRoster.clear()

		for i, valr in enumerate(jsonTable.keys()):
			fileName = ''
			for j, (temp, data) in enumerate(jsonTable[list(jsonTable.keys())[i]].items()):
				skip = j + 1
				self.mSize = self.minDim - int(self.minDim * 0.1)

				if temp == 'Name':
					fileName = data.lower()
					userRoster.append(data)

				if data == 'M0':
					self.table.setCellWidget(i, skip, self.getImageQt('m0.png', self.mSize))
				elif data == 'M1':
					self.table.setCellWidget(i, skip, self.getImageQt('m1.png', self.mSize))
				elif data == 'M2':
					self.table.setCellWidget(i, skip, self.getImageQt('m2.png', self.mSize))
				elif data == 'M3':
					self.table.setCellWidget(i, skip, self.getImageQt('m3.png', self.mSize))
				elif temp == 'Potential':
					pot = 'p' + str(data) +'.png'
					self.table.setCellWidget(i, skip, self.getImageQt(pot, self.mSize))
				elif data == 'E0':
					self.table.setCellWidget(i, skip, self.getImageQt('e0.png', self.mSize))
					fileName += '1.png'
				elif data == 'E1':
					self.table.setCellWidget(i, skip, self.getImageQt('e1.png', self.mSize))
					if fileName == 'amiya':
						fileName += '2.png'
					else:
						fileName += '1.png'
				elif data == 'E2':
					self.table.setCellWidget(i, skip, self.getImageQt('e2.png', self.mSize))
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
					if data != 'None' and data != 'True':
						self.table.setCellWidget(i, skip, self.getImageQt('module_icon/' + data + '.png', self.mSize))
				else:
					self.table.setItem(i, skip, QTableWidgetItem(data))

				if j == 9:
					self.table.setCellWidget(i, 0, self.getImageQt('op_icon/' + fileName, self.minDim))

			self.table.setRowHeight(i, self.minDim)

		self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
		self.table.resizeColumnsToContents()
		self.table.setColumnWidth(1, 220)
		self.table.verticalScrollBar().setStyleSheet("QScrollBar:vertical { width: 15px; }")
		self.table.horizontalScrollBar().setStyleSheet("QScrollBar:horizontal { height: 15px; }")
		self.tableWidth = self.table.verticalHeader().size().width()
		self.tableHeight = self.table.horizontalHeader().size().height()

		for i in range(0, col):
			if self.table.columnWidth(i) < self.minDim:
				self.table.setColumnWidth(i, self.minDim)

		for i in range(self.table.columnCount()):
			self.tableWidth += self.table.columnWidth(i)

		for i in range(self.table.rowCount()):
			self.tableHeight += self.table.rowHeight(i) + 1

		self.tableWidth += 2 #scrollbar width

		if self.tableHeight > self.height:
			self.tableWidth += 15

		self.filterLabel = QtWidgets.QLabel('Filter', self)
		self.filterLabel.setFont(QFont('Roboto', 11))
		self.filterLabel.setFixedWidth(self.width())
		self.filterLabel.move(8, -1)	

		self.inputText = QLineEdit(self)
		self.inputText.resize(250, 20)
		self.inputText.move(45, 5)
		self.inputText.textChanged.connect(self.filter)

		self.addButton = QtWidgets.QPushButton('Add/Update', self)
		self.addButton.setGeometry(self.tableWidth + 15, 28, 120, 40)
		self.addButton.clicked.connect(self.addOperator)

		self.outputImageButton = QtWidgets.QPushButton('Output to Image', self)
		self.outputImageButton.setGeometry(self.tableWidth + 15, 445, 120, 40)
		self.outputImageButton.clicked.connect(self.outputImage)

		self.closeButton = QtWidgets.QPushButton('Close', self)
		self.closeButton.setGeometry(self.tableWidth + 15, 500, 120, 40)
		self.closeButton.clicked.connect(self.closeEvent)

		self.fiaLabel = QtWidgets.QLabel(self)
		self.fiaLabel.setAlignment(Qt.AlignCenter)
		self.fiaIcon = QPixmap('ui_asset/icon.png')
		self.fiaLabel.setPixmap(self.fiaIcon)
		self.fiaLabel.setGeometry(self.tableWidth + 5, 265, self.fiaIcon.width() - 60, self.fiaIcon.height() - 30)

		self.table.setGeometry(QtCore.QRect(0, 30, self.tableWidth, self.height - 30))
		self.setFixedSize(self.tableWidth + 150, self.height)

		self.addOpW = addOpWindow()
		self.retrieveSignal = QtWidgets.QLineEdit(text = '')

	def centerWindow(self):
		self.setGeometry(0, 0, self.tableWidth + 150, self.height)
		self.setWindowTitle('Roster')
		self.setWindowIcon(QtGui.QIcon('ui_asset/taskbaricon.ico'))
		qtRec = self.frameGeometry()
		centre = QDesktopWidget().availableGeometry().center()
		qtRec.moveCenter(centre)
		self.move(qtRec.topLeft())

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

	@QtCore.pyqtSlot(str)
	def getReturn(self, text):
		userRoster.clear()
		self.table.clear()
		self.filterLabel.hide()
		self.inputText.hide()
		self.addButton.hide()
		self.fiaLabel.hide()
		self.outputImageButton.hide()
		self.closeButton.hide()
		self.initTable()
		self.filterLabel.update()
		self.inputText.update()
		self.addButton.update()
		self.fiaLabel.update()
		self.outputImageButton.update()
		self.closeButton.update()
		self.filterLabel.show()
		self.inputText.show()
		self.addButton.show()
		self.fiaLabel.show()
		self.outputImageButton.show()
		self.closeButton.show()

	def addOperator(self):
		self.addOpW.close()
		popup = QInputDialog(self)
		popup.setWindowFlags(popup.windowFlags() & ~Qt.WindowContextHelpButtonHint)
		popup.setWindowTitle("Input")
		popup.setLabelText("Enter Operator Name:")
		popup.setFixedSize(300, 0)

		if popup.exec_() == QDialog.Accepted:
			inputName = popup.textValue()
		else:
			inputName = 'Cancel'

		matchValue = 0

		for name in opList:
			if name.lower() == inputName.lower():
				matchName = name
				break
			if fuzz.partial_ratio(name.lower(), inputName.lower()) > matchValue:
				matchValue = fuzz.partial_ratio(name.lower(), inputName.lower())
				matchName = name

		if inputName != 'Cancel' and inputName != '':
			inputName = matchName
			self.inputText.setText('')
			self.addOpW.getNewOP(inputName)
			self.addOpW.show()
			self.addOpW.submitted.connect(self.getReturn)

	def getImageQt(self, path, scale):
		label = QLabel(self)
		icon = QPixmap('ui_asset/' + path).scaled(scale, scale, QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)
		label.setStyleSheet("background-color: duron grizzle gray")
		label.setAlignment(Qt.AlignCenter)
		label.setPixmap(icon)
		return label

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

		self.openRosterButton = QtWidgets.QPushButton('Open Roster', self)
		self.openRosterButton.setStyleSheet("QPushButton { font-size: 15px; }")
		self.openRosterButton.setFixedWidth(180)
		self.openRosterButton.setFixedHeight(50)
		self.openRosterButton.move(88, self.icon.height())
		self.openRosterButton.clicked.connect(self.showRoster)

		self.text1 = QtWidgets.QLabel('Select the folder that contains your roster:', self)
		self.text1.setFont(QFont('Roboto', 13))
		self.text1.setFixedWidth(self.width())
		self.text1.setAlignment(Qt.AlignCenter)
		self.text1.move(0, self.icon.height() + 55)

		self.folderText = QLineEdit(self)
		self.folderText.resize(250, 25)
		self.folderText.move(20, self.icon.height() + 95)

		self.folderButton = QtWidgets.QPushButton('Browse', self)
		self.folderButton.setFixedWidth(60)
		self.folderButton.move(276, self.icon.height() + 92)
		self.folderButton.clicked.connect(self.browseFolder)

		self.createNewButton = QtWidgets.QPushButton('Create New Roster', self)
		self.createNewButton.setFixedWidth(150)
		self.createNewButton.setFixedHeight(40)
		self.createNewButton.move(25, self.icon.height() + 135)
		self.createNewButton.clicked.connect(self.createNew)

		self.updateExistingButton = QtWidgets.QPushButton('Update Existing', self)
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
		QApplication.closeAllWindows()
		self.close()

#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------

def startup():
	app = QApplication(sys.argv)
	QApplication.instance().setFont(font)
	win = mainWindow()

	opToText()

	win.show()
	sys.exit(app.exec_())

startup()
