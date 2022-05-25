import cv2 as cv
import numpy as np
import os
from os import listdir
import matplotlib.pyplot as plt
import easyocr
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'

def arkAssist(input, nameReader):
	opName = ''
	opRarity = 0
	opPromotion = ''
	opPotential = 0
	opLevel = 0
	opTrust = 0
	skillRank = ''
	opS1 = ''
	opS2 = ''
	opS3 = ''
	opModule = ''

	#---------------------------------------------------------------------------------------------------------------------------------
	sample = input

	roster = cv.imread('input/' + sample, 0)
	rosterCopy = cv.imread('input/' + sample)
	faceRef = cv.imread('operator_icon/chenskin1.jpg', 0)
	faceMatch = 0

	rosterDim = rosterCopy.shape
	leftSide = rosterCopy[0:int(rosterDim[0]), 0:int(rosterDim[1] / 2)]
	rightSide = rosterCopy[0:int(rosterDim[0]), int(rosterDim[1] / 2):int(rosterDim[1])]

	readName = leftSide
	
	nameList = nameReader.readtext(readName, detail = 0)
	readSkills = rightSide
	skillList = nameReader.readtext(readSkills)
	skillList2 = nameReader.readtext(readSkills, detail = 0)

	# plt.imshow(rightSide)
	# plt.waitforbuttonpress()
	# print(skillList2)

	#---------------------------------------------------------------------------------------------------------------------------------
	opjson = open('json_files/character_table.json', encoding = "utf8")
	datajson = json.load(opjson)
	keyList = list(datajson)
	opList = []
	rarityList = []
	nameMatch = 0
	rarityIndex = 0

	for key in keyList:
		opList.append(datajson[key]['name'])
		rarityList.append(datajson[key]['rarity'])

	for name in nameList:
		if name != 'Ranged' and name != 'Range' and name != 'DPS' and name != 'Slow' and name != 'Trust':
			compare = process.extractOne(name, opList, scorer = fuzz.ratio)

			if int(compare[1]) > nameMatch:
				nameMatch = int(compare[1])
				opName = compare[0]

	for key in keyList:
		if datajson[key]['name'] == opName:
			opRarity = datajson[key]['rarity']

	# READ PROMOTION------------------------------------------------------------------------------------------------------------------
	promoProb, eliteProb = 0, 0
	promoDim = [0, 0]

	for (bbox, text, prob) in skillList:
		(tl, tr, br, bl) = bbox

		if promoProb < fuzz.partial_ratio(text, 'Promotion'):
			promoProb = fuzz.partial_ratio(text, 'Promotion')
			promoDim = [(int(tl[0] + 70), int(tl[1]) - 40), (int(br[0] + 110), int(br[1] + 30))]

	croppedPromo = rightSide[promoDim[0][1]:promoDim[1][1], promoDim[0][0]:promoDim[1][0]]
	croppedPromo = cv.cvtColor(croppedPromo, cv.COLOR_BGR2GRAY)

	for e in os.listdir('elite_icon'):
		elite = cv.imread('elite_icon/' + e, 0)
		eliteComp = cv.matchTemplate(croppedPromo, elite, cv.TM_CCORR_NORMED)

		if np.amax(eliteComp) > np.amax(eliteProb):
			eliteProb = eliteComp
			opPromotion = e[:-4].upper()

	# READ SKILL MASTERY--------------------------------------------------------------------------------------------------------------
	rankProb = 0
	rankDim = [0, 0]

	for (bbox, text, prob) in skillList:
		(tl, tr, br, bl) = bbox

		if rankProb < fuzz.partial_ratio(text, 'RANK'):
			rankProb = fuzz.partial_ratio(text, 'RANK')
			rankDim = [(int(tl[0] - 5), int(tl[1]) - 10), (int(br[0] + 20), int(br[1] + 5))]

	croppedRank = rightSide[rankDim[0][1]:rankDim[1][1], rankDim[0][0]:rankDim[1][0]]
	tessImg = cv.cvtColor(croppedRank, cv.COLOR_BGR2GRAY)
	skillRank = pytesseract.image_to_string(tessImg, config = '')
	skillRank = skillRank.rstrip()

	if skillRank == 'RANK ]' or skillRank == 'RANK |':
		skillRank = 'RANK 1'

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

		for m in os.listdir('mastery_icon'):
			mastery = cv.imread('mastery_icon/' + m, 0)

			for x in range(-5, 5):
				mResize = cv.resize(mastery, (0, 0), fx = 1 - 0.1 * x, fy = 1 - 0.1 * x)
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

	# READ POTENTIAL------------------------------------------------------------------------------------------------------------------
	potProb, potNum = 0, 0
	potDim = [0, 0]

	for (bbox, text, prob) in skillList:
		(tl, tr, br, bl) = bbox

		if potProb < fuzz.partial_ratio(text, 'Potential'):
			potProb = fuzz.partial_ratio(text, 'Potential')
			potDim = [(int(tl[0] + 40), int(tl[1]) - 80), (int(br[0] + 140), int(br[1] + 70))]

	croppedPot = rightSide[potDim[0][1]:potDim[1][1], potDim[0][0]:potDim[1][0]]
	croppedPot = cv.cvtColor(croppedPot, cv.COLOR_BGR2GRAY)

	for p in os.listdir('potential_icon'):
		potential = cv.imread('potential_icon/' + p, 0)

		for x in range(-5, 5):
			pResize = cv.resize(potential, (0, 0), fx = 1 - 0.1 * x, fy = 1 - 0.1 * x)
			potComp = cv.matchTemplate(pResize, croppedPot, cv.TM_CCORR_NORMED)

			if np.amax(potComp) > np.amax(potNum):
				potNum = potComp
				opPotential = p[:-4]

	# READ LEVEL----------------------------------------------------------------------------------------------------------------------
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
		level = nameReader.readtext(croppedLv, detail = 0)

		for l in level:
			if lvNum > fuzz.partial_ratio(l, 'LV'):
				lvNum = fuzz.partial_ratio(l, 'LV')
				lvtemp = l

		if lvtemp == '' or lvtemp == ']' or lvtemp == '|':
			lvtemp = '1'

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
	elif opRarity == 2 and opPromotion == 'E0':
		maxLevel = 40


	#---------------------------------------------------------------------------------------------------------------------------------

	# print(opName)
	# print('Rarity:', (opRarity + 1))
	# print('Level: ' + str(opLevel) + '/' + str(maxLevel))
	# print('Elite:', opPromotion[-1:])
	# print('Potential:', opPotential)
	# print('Skill', skillRank.lower())

	# if skillRank == 'RANK 7' and opRarity > 2:
	# 	print('S1:', opS1)

	# 	if opRarity > 3:
	# 		print('S2:', opS2)

	# 	if opRarity > 4 or opName == 'Amiya':
	# 		print('S3:', opS3)


	outputText = open('output/output_text.txt', 'a')

	if os.stat('output/output_text.txt').st_size != 0:
		outputText.write('\n')

	if skillRank == 'RANK 7' and opRarity > 4  or opName == 'Amiya':
		outputText.write(str(opName) + '    Rarity: ' + str(opRarity + 1) + '    Level: ' + str(opLevel) + '/' + str(maxLevel) + '    Elite: ' + str(opPromotion[-1:]) + '    Potential: ' + str(opPotential) + '    Skill ' + str(skillRank.lower()) + '    S1: ' + opS1 + '    S2: ' + opS2 + '    S3: ' + opS3)
	elif skillRank == 'RANK 7' and opRarity > 3:
		outputText.write(str(opName) + '    Rarity: ' + str(opRarity + 1) + '    Level: ' + str(opLevel) + '/' + str(maxLevel) + '    Elite: ' + str(opPromotion[-1:]) + '    Potential: ' + str(opPotential) + '    Skill ' + str(skillRank.lower()) + '    S1: ' + opS1 + '    S2: ' + opS2)
	elif skillRank == 'RANK 7' and opRarity > 2:
		outputText.write(str(opName) + '    Rarity: ' + str(opRarity + 1) + '    Level: ' + str(opLevel) + '/' + str(maxLevel) + '    Elite: ' + str(opPromotion[-1:]) + '    Potential: ' + str(opPotential) + '    Skill ' + str(skillRank.lower()) + '    S1: ' + opS1)
	else:
		outputText.write(str(opName) + '    Rarity: ' + str(opRarity + 1) + '    Level: ' + str(opLevel) + '/' + str(maxLevel) + '    Elite: ' + str(opPromotion[-1:]) + '    Potential: ' + str(opPotential) + '    Skill ' + str(skillRank.lower()))
