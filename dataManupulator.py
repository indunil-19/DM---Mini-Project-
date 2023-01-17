import csv
import json


def csv_to_json(csvFilePath, jsonFilePath):
	jsonArray = []

	# read csv file
	with open(csvFilePath, encoding='utf-8') as csvf:
		# load csv file data using csv library's dictionary reader
		csvReader = csv.DictReader(csvf)

		# convert each csv row into python dict
		for row in csvReader:
			# add this python dict to json array
			jsonArray.append(row)

	# convert python jsonArray to JSON String and write to file
	with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
		jsonString = json.dumps(jsonArray, indent=4)
		jsonf.write(jsonString)


csvFilePath = r'data.csv'
jsonFilePath = r'data.json'
csv_to_json(csvFilePath, jsonFilePath)



def get_songs_data():
	list_songs = get_songs_list()
	with open ('song-corpus/songs.json','w+') as f:
		f.write(json.dumps(list_songs))


def get_songs_list():
    list_songs=[]
    return list_songs

