import csv
import json
from googletrans import Translator

translator = Translator();


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


csvFilePath = r'song-corpus/songs.csv'
jsonFilePath = r'song-corpus/songs.json'


def translateJson():
    new_list = []
    with open('song-corpus/songs.json') as f:
        list_songs = json.loads(f.read())
        songs = list_songs
        for song in songs:
            translated = {}
            for k, v in song.items():
                translated[k] = v
                if k in ["Title", "Album", "Metaphor"]:
                    translated[k + "_en"] = translator.translate(v, dest="en").text
            new_list.append(translated)
    with open('song-corpus/songs_final.json', 'w+') as f:
        f.write(json.dumps(new_list))


def translateString(data):
    global translator
    if isinstance(data, dict):
        return {k + "_en": translateString(v) for k, v in data.items()}
    else:
        return translator.translate(data, dest="en").text


# def get_songs_list():
# 	with open('song-corpus/songs.json') as f:
# 		list_songs = json.loads(f.read())
#      	return list_songs


def metaData():
    metaData = {"title": [], "artist": [], "album": [], "lyricist": [], "metaphor": [], "meaning": [], "source": [],
                "target": []}
    with open('song-corpus/songs.json') as f:
        list_songs = json.loads(f.read())
        songs = list_songs
        for song in songs:
            metaData["title"].append(song["Title"])
            metaData["artist"].append(song["Artist"])
            metaData["album"].append(song["Album"])
            metaData["lyricist"].append(song["Lyricist"])
            metaData["metaphor"].append(song["Metaphor"])
            metaData["meaning"].append(song["Meaning"])
            metaData["source"].append(song["Source"])
            metaData["target"].append(song["Target"])
        with open('song-corpus/songs_metadata.json', 'w+') as f1:
            f1.write(json.dumps(metaData))


if __name__ == "__main__":
    # csv_to_json(csvFilePath, jsonFilePath)
    # translateJson()
    metaData()
