from flask import flash, render_template, request, redirect, jsonify
from flask import Flask

from search import search_query

app = Flask(__name__)
global_search = "dada"


global_search = "songs"

@app.route('/', methods=['GET', 'POST'])
def index():
    global global_search

    if request.method == 'POST':
        if 'form_1' in request.form:
            if request.form['query']:
                search = request.form['query']
                global_search = search
            else :
                search = global_search
            list_songs, artists, lyricist, lyrics = search_query(search)

        return render_template('index.html', songs = list_songs)
    return render_template('index.html', songs = '', artists = '',  lyricist = '',  lyrics = '')


if __name__ == '__main__':
    app.run()
