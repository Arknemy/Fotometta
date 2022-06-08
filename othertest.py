import json

datajson = json.load(open('json_files/character_table.json', encoding = "utf8"))


for key in list(datajson):
    if datajson[key]['name'] == 'Amiya':
        print(datajson[key]["subProfessionId"])