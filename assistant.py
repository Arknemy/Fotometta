import cv2 as cv
import numpy as np
import os
import re
from os import listdir
import matplotlib.pyplot as plt
import easyocr
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pytesseract

# pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'

def arkAssist(input, nameReader):
	opName = ""
	opRarity = 0
	opPromotion = ""
	opPotential = 0
	opLevel = 0
	opTrust = 0
	skillRank = ""
	opS1 = ""
	opS2 = ""
	opS3 = ""
	opModule = ""

#--------------------------------------------------------------------------------------------------------------

	sample = input

	roster = cv.imread('fotometta_input/' + sample, 0)
	rosterCopy = cv.imread('fotometta_input/' + sample)
	faceRef = cv.imread('operator_icon/chenskin1.jpg', 0)
	faceMatch = 0

	rosterDim = rosterCopy.shape
	leftSide = rosterCopy[0:int(rosterDim[0]), 0:int(rosterDim[1] / 2)]
	rightSide = rosterCopy[0:int(rosterDim[0]), int(rosterDim[1] / 2):int(rosterDim[1])]

	readName = leftSide
	readName = cv.cvtColor(readName, cv.COLOR_BGR2GRAY)
	ret, nameThresh = cv.threshold(readName, 200, 255, cv.THRESH_BINARY)
	nameList = nameReader.readtext(nameThresh, detail = 0)
	nameList2 = nameReader.readtext(readName, detail = 0)
	readSkills = rightSide
	skillList = nameReader.readtext(readSkills)

#--------------------------------------------------------------------------------------------------------------

	datajson = json.load(open('json_files/character_table.json', encoding = "utf8"))
	opList = []
	rarityList = []
	nameMatch = 0
	rarityIndex = 0

	for key in list(datajson):
		if datajson[key]['subProfessionId'] != 'notchar1' and datajson[key]['subProfessionId'] != 'notchar2':
			opList.append(datajson[key]['name'])
			rarityList.append(datajson[key]['rarity'])

	for name in nameList:
		if name != 'Ranged' and name != 'Range' and name != 'DPS' and name != 'Slow' and name != 'Trust':
			compare = process.extractOne(name, opList, scorer = fuzz.ratio)

			if int(compare[1]) > nameMatch:
				nameMatch = int(compare[1])
				opName = compare[0]

	for name in nameList2:
		if name != 'Ranged' and name != 'Range' and name != 'DPS' and name != 'Slow' and name != 'Trust':
			compare = process.extractOne(name, opList, scorer = fuzz.ratio)

			if int(compare[1]) > nameMatch:
				nameMatch = int(compare[1])
				opName = compare[0]

	for key in list(datajson):
		if datajson[key]['name'] == opName:
			opRarity = datajson[key]['rarity']

# READ PROMOTION-----------------------------------------------------------------------------------------------

	promoProb, eliteProb = 0, 0
	promoDim = [0, 0]

	for (bbox, text, prob) in skillList:
		(tl, tr, br, bl) = bbox

		if promoProb < fuzz.partial_ratio(text, 'Promotion'):
			promoProb = fuzz.partial_ratio(text, 'Promotion')
			promoDim = [(int(tl[0] + 70), int(tl[1]) - 40), (int(br[0] + 110), int(br[1] + 30))]

	if promoDim == [0, 0]:
		opPromotion = 'Unrecognized'
	else: 
		croppedPromo = rightSide[promoDim[0][1]:promoDim[1][1], promoDim[0][0]:promoDim[1][0]]
		croppedPromo = cv.cvtColor(croppedPromo, cv.COLOR_BGR2GRAY)

		for e in os.listdir('image_matching/elite_icon'):
			elite = cv.imread('image_matching/elite_icon/' + e, 0)

			for x in range(-5, 5):
				eResize = cv.resize(elite, (0, 0), fx = 1 - 0.1 * x, fy = 1 - 0.1 * x)

				if eResize.shape[0] < croppedPromo.shape[0] and eResize.shape[1] < croppedPromo.shape[1]:
					eliteComp = cv.matchTemplate(croppedPromo, eResize, cv.TM_CCORR_NORMED)

					if np.amax(eliteComp) > np.amax(eliteProb):
						eliteProb = eliteComp
						opPromotion = e[:-4].upper()

# READ SKILL MASTERY-------------------------------------------------------------------------------------------

	rankProb = 0
	rankDim = [0, 0]

	for (bbox, text, prob) in skillList:
		(tl, tr, br, bl) = bbox

		if rankProb < fuzz.ratio(text, 'RANK'):
			rankProb = fuzz.ratio(text, 'RANK')
			rankDim = [(int(tl[0] - 5), int(tl[1]) - 10), (int(br[0] + 20), int(br[1] + 5))]

	croppedRank = rightSide[rankDim[0][1]:rankDim[1][1], rankDim[0][0]:rankDim[1][0]]
	ret, rankThresh = cv.threshold(croppedRank, 127, 255, cv.THRESH_BINARY)
	tessImg = cv.cvtColor(rankThresh, cv.COLOR_BGR2GRAY)
	tessImg2 = cv.cvtColor(croppedRank, cv.COLOR_BGR2GRAY)
	skillRank = pytesseract.image_to_string(tessImg, config = '')
	skillRank2 = pytesseract.image_to_string(tessImg2, config = '')
	skillRank = skillRank.rstrip()
	skillRank2 = skillRank2.rstrip()

	if skillRank[-1] == ']' or skillRank[-1] == '|':
		skillRank = 'RANK 1'

	if skillRank2[-1] == ']' or skillRank2[-1] == '|':
		skillRank2 = 'RANK 1'

	if any(char.isdigit() for char in skillRank2) == True and any(char.isdigit() for char in skillRank) == False:
		skillRank = skillRank2
	elif any(char.isdigit() for char in skillRank2) == True and any(char.isdigit() for char in skillRank) == True:
		if int(skillRank2[-1]) > int(skillRank[-1]):
			skillRank = skillRank2

	if skillRank == 'RANK 7' and opRarity > 2 and opPromotion == 'E2':
		croppedMastery = rightSide[(rankDim[0][1] - 20):(rankDim[1][1] + 20), (rankDim[0][0] + 80):(rankDim[1][0] + 240)]
		croppedMastery = cv.cvtColor(croppedMastery, cv.COLOR_BGR2GRAY)
		imLength = croppedMastery.shape[1]
		divide3 = int(imLength / 3)
		s1 = croppedMastery[0:croppedMastery.shape[0], 0:divide3]
		s2 = croppedMastery[0:croppedMastery.shape[0], divide3 + 1:2 * divide3]
		s3 = croppedMastery[0:croppedMastery.shape[0], 2 * divide3 + 1:3 * divide3]
		s1Match, s2Match, s3Match = 0, 0, 0
		s1m, s2m, s3m = '', '', ''

		for m in os.listdir('image_matching/mastery_icon'):
			mastery = cv.imread('image_matching/mastery_icon/' + m, 0)

			for x in range(-5, 5):
				mResize = cv.resize(mastery, (0, 0), fx = 1 - 0.1 * x, fy = 1 - 0.1 * x)

				if mResize.shape[0] < s1.shape[0] and mResize.shape[1] < s1.shape[1]:
					s1Comp = cv.matchTemplate(s1, mResize, cv.TM_CCORR_NORMED)
					s2Comp = cv.matchTemplate(s2, mResize, cv.TM_CCORR_NORMED)
					s3Comp = cv.matchTemplate(s3, mResize, cv.TM_CCORR_NORMED)

					if np.amax(s1Comp) > np.amax(s1Match):
						s1Match = s1Comp
						s1m = m

					if np.amax(s2Comp) > np.amax(s2Match):
						s2Match = s2Comp
						s2m = m

					if np.amax(s3Comp) > np.amax(s3Match):
						s3Match = s3Comp
						s3m = m

		opS1 = s1m[:-4].upper()
		opS2 = s2m[:-4].upper()
		opS3 = s3m[:-4].upper()

# READ POTENTIAL-----------------------------------------------------------------------------------------------

	potProb, potNum = 0, 0
	potDim = [0, 0]

	for (bbox, text, prob) in skillList:
		(tl, tr, br, bl) = bbox

		if potProb < fuzz.partial_ratio(text, 'Potential'):
			potProb = fuzz.partial_ratio(text, 'Potential')
			potDim = [(int(tl[0] + 40), int(tl[1]) - 80), (int(br[0] + 140), int(br[1] + 70))]

	if potDim == [0 ,0]:
		opPotential = -1
	else: 
		croppedPot = rightSide[potDim[0][1]:potDim[1][1], potDim[0][0]:potDim[1][0]]
		croppedPot = cv.cvtColor(croppedPot, cv.COLOR_BGR2GRAY)

		for p in os.listdir('image_matching/potential_icon'):
			potential = cv.imread('image_matching/potential_icon/' + p, 0)

			for x in range(-5, 5):
				pResize = cv.resize(potential, (0, 0), fx = 1 - 0.1 * x, fy = 1 - 0.1 * x)

				if pResize.shape[0] < croppedPot.shape[0] and pResize.shape[1] < croppedPot.shape[1]:
					potComp = cv.matchTemplate(croppedPot, pResize, cv.TM_CCORR_NORMED)

					if np.amax(potComp) > np.amax(potNum):
						potNum = potComp
						opPotential = p[:-4]

# READ LEVEL---------------------------------------------------------------------------------------------------

	lvProb1, lvProb2, lvNum, lvtemp = 0, 0, 1, ''
	lvDim = [0, 0]

	for (bbox, text, prob) in skillList:
		(tl, tr, br, bl) = bbox

		if lvProb1 < fuzz.partial_ratio(text, 'EXP'):
			lvProb1 = fuzz.partial_ratio(text, 'EXP')
			lvDim = [(int(tl[0] - 130), int(tl[1]) - 40), (int(br[0] - 30), int(br[1] + 50))]

	if lvProb1 < 0.9:
		for (bbox, text, prob) in skillList:
			(tl, tr, br, bl) = bbox

			for lv in range(1, 90):
				if lvProb2 < fuzz.partial_ratio(text, str(lv)):
					lvProb2 = fuzz.partial_ratio(text, str(lv))
					lvtemp = text

	if lvProb1 > lvProb2:
		croppedLv = rightSide[lvDim[0][1]:lvDim[1][1], lvDim[0][0]:lvDim[1][0]]
		croppedLv = cv.cvtColor(croppedLv, cv.COLOR_BGR2GRAY)
		ret, lvThresh = cv.threshold(croppedLv, 200, 255, cv.THRESH_BINARY)
		level = nameReader.readtext(lvThresh, detail = 0)

		for l in level:
			if lvNum > fuzz.partial_ratio(l, 'LV'):
				lvNum = fuzz.partial_ratio(l, 'LV')
				lvtemp = l

		if lvtemp == '' or lvtemp == ']' or lvtemp == '|':
			lvtemp = '1'

	lvtemp = re.sub("[^0-9]", "", lvtemp)
	opLevel = int(lvtemp)
	maxLevel = 90

	if opRarity == 5 and opPromotion == 'E1' or opRarity == 4 and opPromotion == 'E2':
		maxLevel = 80
	elif opRarity == 4 and opPromotion == 'E1' or opRarity == 3 and opPromotion == 'E2':
		maxLevel = 70
	elif opRarity == 3 and opPromotion == 'E1':
		maxLevel = 60
	elif opRarity == 2 and opPromotion == 'E1':
		maxLevel = 55
	elif opRarity == 5 and opPromotion == 'E0' or opRarity == 4 and opPromotion == 'E0':
		maxLevel = 50
	elif opRarity == 3 and opPromotion == 'E0':
		maxLevel = 45
	elif opRarity == 2 and opPromotion == 'E0':
		maxLevel = 40
	elif opRarity == 1 or opRarity == 0:
		opPromotion = 'E0'
		maxLevel = 30

# READ MODULE--------------------------------------------------------------------------------------------------

	modProb, modtemp = 0, ''
	modDim = [0, 0]

	for (bbox, text, prob) in skillList:
		(tl, tr, br, bl) = bbox

		if modProb < fuzz.ratio(text, 'Module'):
			modProb = fuzz.ratio(text, 'Module')
			modDim = [(int(tl[0] + 20), int(tl[1]) - 80), (int(br[0] + 170), int(br[1] + 80))]

	croppedMod = rightSide[modDim[0][1]:modDim[1][1], modDim[0][0]:modDim[1][0]]
	croppedMod = cv.cvtColor(croppedMod, cv.COLOR_BGR2GRAY)

	modProb = 0

	for m in os.listdir('image_matching/module_icon'):
		modImg = cv.imread('image_matching/module_icon/' + m, 0)

		for x in range(-5, 5):
			modResize = cv.resize(modImg, (0, 0), fx = 1 - 0.1 * x, fy = 1 - 0.1 * x)

			if modResize.shape[0] < croppedMod.shape[0] and modResize.shape[1] < croppedMod.shape[1]:
				modComp = cv.matchTemplate(croppedMod, modResize, cv.TM_CCORR_NORMED)

				if np.amax(modComp) > modProb:
					modProb = np.amax(modComp)
					modtemp = m

	print(modtemp)

	if modtemp == 'originalmodule.jpg' or modtemp == 'nomodule.jpg':
		opModule = 'None'
	else:
		opModule = 'True'

# OUTPUT-------------------------------------------------------------------------------------------------------

	opFields = ["Name", "Rarity", "Level", "Promotion", "Potential", "Skill", "S1", "S2", "S3", 'Module']
	opInput = [opName, str(opRarity + 1), str(opLevel) + "/" + str(maxLevel), opPromotion, str(opPotential), skillRank, opS1, opS2, opS3, opModule]

	if skillRank == "RANK 7" and opRarity == 4:
		opInput[8] = ""
	elif skillRank == "RANK 7" and opRarity == 3:
		opInput[8] = ""
	elif skillRank == "RANK 7" and opRarity < 3:
		opInput[8] = ""
		opInput[7] = ""
		opInput[6] = ""

	opDict = {}
	print(dict(zip(opFields, opInput)))
	return dict(zip(opFields, opInput))

#--------------------------------------------------------------------------------------------------------------

def resizeRoster(selectedFolder):
	for i in os.listdir('fotometta_input'):
		os.remove(os.path.join('fotometta_input', i))

	reso = 1500
	index = 1

	for rawImg in os.listdir(selectedFolder):
		original = cv.imread(selectedFolder + '/' + rawImg)
		oDim = original.shape
		destination = 'fotometta_input/sample' + str(index) + '.jpg'
		index = index + 1

		if oDim[1] > reso:
			ratio = reso / oDim[1]
			resized = cv.resize(original, (0, 0), fx = ratio, fy = ratio)
			cv.imwrite(destination, resized)
		else:
			cv.imwrite(destination, original, [int(cv.IMWRITE_JPEG_QUALITY), 100])

#--------------------------------------------------------------------------------------------------------------

def sortRoster(d):
	def part(l, r, arr):
	    pivot, ptr = arr[r]['Name'], l

	    for i in range(l, r):
	        if arr[i]['Name'] <= pivot:
	            arr[i], arr[ptr] = arr[ptr], arr[i]
	            ptr += 1

	    arr[ptr], arr[r] = arr[r], arr[ptr]
	    return ptr
	 
	def quicksort(l, r, arr):
	    if len(arr) == 1:
	        return arr

	    if l < r:
	        pi = part(l, r, arr)
	        quicksort(l, pi - 1, arr)
	        quicksort(pi + 1, r, arr)

	    return arr

	masterDict = {}
	rarityDict = {}
	masterArray = []
	rarityArray = []
	tempE0, tempE1, tempE2 = {}, {}, {}
	temp1, temp2, temp3, temp4, temp5, temp6 = {}, {}, {}, {}, {}, {}

	for entry in list(d):
		if d[entry]['Promotion'] == 'E0':
			tempE0[entry] = d[entry]
		elif d[entry]['Promotion'] == 'E1':
			tempE1[entry] = d[entry]
		else:
			tempE2[entry] = d[entry]

	masterDict[0] = tempE2
	masterDict[1] = tempE1
	masterDict[2] = tempE0

	for i in range (0, 3):
		for entry in masterDict[i]:
			if masterDict[i][entry]['Rarity'] == '6':
				temp6[entry] = masterDict[i][entry]
			elif masterDict[i][entry]['Rarity'] == '5':
				temp5[entry] = masterDict[i][entry]
			elif masterDict[i][entry]['Rarity'] == '4':
				temp4[entry] = masterDict[i][entry]
			elif masterDict[i][entry]['Rarity'] == '3':
				temp3[entry] = masterDict[i][entry]
			elif masterDict[i][entry]['Rarity'] == '2':
				temp2[entry] = masterDict[i][entry]
			elif masterDict[i][entry]['Rarity'] == '1':
				temp1[entry] = masterDict[i][entry]

		rarityDict[0] = temp6
		rarityDict[1] = temp5
		rarityDict[2] = temp4
		rarityDict[3] = temp3
		rarityDict[4] = temp2
		rarityDict[5] = temp1
			
		for j in range(0, 6):
			for entry in rarityDict[j]:
				rarityArray.append(rarityDict[j][entry])

			quicksort(0, len(rarityArray) - 1, rarityArray)
			masterArray.extend(rarityArray)
			rarityArray.clear()

		temp1.clear()
		temp2.clear()
		temp3.clear()
		temp4.clear()
		temp5.clear()
		temp6.clear()
		rarityDict.clear()

	return masterArray

#--------------------------------------------------------------------------------------------------------------

def removeDupes(d):
	newRoster = {}

	for entry in list(d):
		if newRoster == {}:
			newRoster[entry] = d[entry]
		else:
			isDupe = False

			for entry2 in list(newRoster):
				if newRoster[entry2]['Name'] == d[entry]['Name']:
					isDupe = True
					newRoster[entry2] = d[entry]

			if isDupe == False:
				newRoster[entry] = d[entry]

	finalArray = []
	finalArray = sortRoster(newRoster)
	return finalArray

#--------------------------------------------------------------------------------------------------------------

def arrToDict(a):
	datajson = json.load(open('json_files/character_table.json', encoding = "utf8"))
	modulejson = json.load(open('json_files/uniequip_table.json', encoding = "utf8"))
	finalData = {}

	for i in range(1, len(a) + 1):
		charCode = ''
		modCode = ''

		for key, value in datajson.items():
			if datajson[key]['name'] == a[i - 1]['Name']:
				finalData[key] = a[i - 1]
				charCode = key
				break;

		for key, value in modulejson.items():
			if key != 'missionList' and key != 'subProfDict' and key != 'charEquip':
				for key2, value2 in modulejson[key].items():
					if modulejson[key][key2]['charId'] == charCode and a[i - 1]['Promotion'] == 'E2':
						if a[i - 1]['Module'] == 'None':
							a[i - 1]['Module'] = 'original'
						elif a[i - 1]['Module'] == 'True' and modulejson[key][key2]['typeIcon'] != 'original':
							a[i - 1]['Module'] = modulejson[key][key2]['typeIcon']

			if a[i - 1]['Module'] != 'None' and a[i - 1]['Module'] != 'True':
				break;

	return finalData

#--------------------------------------------------------------------------------------------------------------

def assembleDict(d):
	finalData = {}
	a = []
	a = removeDupes(d)
	finalData = arrToDict(a)
	
	return finalData

#--------------------------------------------------------------------------------------------------------------

def getMaxLevel(promotion, rarity):
	if promotion == 'E0':
		if rarity == 5 or rarity == 4:
			maxLevel = 50
		elif rarity == 3:
			maxLevel = 45
		elif rarity == 2:
			maxLevel = 40
		else:
			maxLevel = 30
	elif promotion == 'E1':
		if rarity == 5:
			maxLevel = 80
		elif rarity == 4:
			maxLevel = 70
		elif rarity == 3:
			maxLevel = 60
		elif rarity == 2:
			maxLevel = 55
		else:
			maxLevel = 30
	elif promotion == 'E2':
		if rarity == 5:
			maxLevel = 90
		elif rarity == 4:
			maxLevel = 80
		elif rarity == 3:
			maxLevel = 70
		elif rarity == 2:
			maxLevel = 55
		else:
			maxLevel = 30

	return maxLevel

#--------------------------------------------------------------------------------------------------------------

def changeStatsToFit(d):
	for key in list(d):
		rarity = int(d[key]['Rarity']) - 1
		promotion = d[key]['Promotion']
		level = int(d[key]['Level'].split('/')[0])

		maxLevel = getMaxLevel(promotion, rarity)

		if level > maxLevel:
			level = maxLevel
		
		d[key]['Level'] = str(level) + '/' + str(maxLevel)

		if promotion == 'E0' or promotion == 'E1':
			d[key]['S1'] = ''
			d[key]['S2'] = ''
			d[key]['S3'] = ''
			d[key]['Module'] = 'None'
		elif promotion == 'E2' and d[key]['Skill'] == 'RANK 7':
			d[key]['S1'] = 'M0'
			d[key]['S2'] = 'M0'
			d[key]['S3'] = 'M0'

		if promotion == 'E0' and d[key]['Skill'] > 'RANK 4':
			d[key]['Skill'] = 'RANK 4'

	return d