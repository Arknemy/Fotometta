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

#---------------------------------------------------------------------------------------------------------------------------------
sample = 'sample3.jpg'

roster = cv.imread('input/' + sample, 0)
rosterCopy = cv.imread('input/' + sample)
faceRef = cv.imread('operator_icon/chenskin1.jpg', 0)
faceMatch = 0

rosterDim = rosterCopy.shape
leftSide = rosterCopy[0:int(rosterDim[0]), 0:int(rosterDim[1] / 2)]
rightSide = rosterCopy[0:int(rosterDim[0]), int(rosterDim[1] / 2):int(rosterDim[1])]

readName = leftSide
readName = cv.cvtColor(readName, cv.COLOR_BGR2GRAY)
ret, nameThresh = cv.threshold(readName, 200, 255, cv.THRESH_BINARY)
nameReader = easyocr.Reader(['en'])
nameList = nameReader.readtext(nameThresh, detail = 0)
nameList2 = nameReader.readtext(readName, detail = 0)
readSkills = rightSide
skillList = nameReader.readtext(readSkills)
skillList2 = nameReader.readtext(readSkills, detail = 0)

plt.imshow(nameThresh)
plt.waitforbuttonpress()
print(nameList)
print('')
print(nameList2)



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

opjson.close()

for name in nameList:
	if name != 'Ranged' and name != 'Range' and name != 'DPS' and name != 'Slow' and name != 'Trust':
		compare = process.extractOne(name, opList, scorer = fuzz.ratio)

		if int(compare[1]) > nameMatch:
			nameMatch = int(compare[1])
			opName = compare[0]



print(opName)

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

if promoDim == [0, 0]:
	opPromotion = 'Unrecognized'
else: 
	croppedPromo = rightSide[promoDim[0][1]:promoDim[1][1], promoDim[0][0]:promoDim[1][0]]
	croppedPromo = cv.cvtColor(croppedPromo, cv.COLOR_BGR2GRAY)

	for e in os.listdir('elite_icon'):
		elite = cv.imread('elite_icon/' + e, 0)

		for x in range(-5, 5):
			eResize = cv.resize(elite, (0, 0), fx = 1 - 0.1 * x, fy = 1 - 0.1 * x)

			if eResize.shape[0] < croppedPromo.shape[0] and eResize.shape[1] < croppedPromo.shape[1]:
				eliteComp = cv.matchTemplate(croppedPromo, eResize, cv.TM_CCORR_NORMED)

				if np.amax(eliteComp) > np.amax(eliteProb):
					eliteProb = eliteComp
					opPromotion = e[:-4].upper()

# READ SKILL MASTERY--------------------------------------------------------------------------------------------------------------
rankProb = 0
rankDim = [0, 0]

for (bbox, text, prob) in skillList:
	(tl, tr, br, bl) = bbox

	if rankProb < fuzz.ratio(text, 'RANK'):
		rankProb = fuzz.ratio(text, 'RANK')
		rankDim = [(int(tl[0] - 5), int(tl[1]) - 10), (int(br[0] + 20), int(br[1] + 5))]

	# plt.imshow(rightSide[rankDim[0][1]:rankDim[1][1], rankDim[0][0]:rankDim[1][0]])
	# plt.waitforbuttonpress()

croppedRank = rightSide[rankDim[0][1]:rankDim[1][1], rankDim[0][0]:rankDim[1][0]]
ret, rankThresh = cv.threshold(croppedRank, 127, 255, cv.THRESH_BINARY)
skillRank = pytesseract.image_to_string(rankThresh, config = '')
skillRank = skillRank.rstrip()

# plt.imshow(rankThresh)
# plt.waitforbuttonpress()

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

# READ POTENTIAL------------------------------------------------------------------------------------------------------------------
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

	for p in os.listdir('potential_icon'):
		potential = cv.imread('potential_icon/' + p, 0)

		for x in range(-5, 5):
			pResize = cv.resize(potential, (0, 0), fx = 1 - 0.1 * x, fy = 1 - 0.1 * x)

			if pResize.shape[0] < croppedPot.shape[0] and pResize.shape[1] < croppedPot.shape[1]:
				potComp = cv.matchTemplate(croppedPot, pResize, cv.TM_CCORR_NORMED)

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
	# level = nameReader.readtext(croppedLv, detail = 0)
	ret, lvThresh = cv.threshold(croppedLv, 200, 255, cv.THRESH_BINARY)
	level2 = nameReader.readtext(lvThresh, detail = 0)

	for l in level2:
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
elif opRarity == 2 and opPromotion == 'E0':
	maxLevel = 40
elif opRarity == 1 or opRarity == 0:
	opPromotion = 'E0'
	maxLevel = 30

#---------------------------------------------------------------------------------------------------------------------------------

opFields = ["Name", "Rarity", "Level", "Promotion", "Potential", "Skill", "S1", "S2", "S3"]
opInput = [opName, str(opRarity + 1), str(opLevel) + "/" + str(maxLevel), opPromotion, str(opPotential), skillRank, opS1, opS2, opS3]

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
