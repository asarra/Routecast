from methods import *
import place
from flask import Flask, request, render_template


def createDetailedMap(placeTerm1, placeTerm2):
    place1 = place.Place()
    place2 = place.Place()

    # text = "wortmann hüllhors"
    place1.x, place1.y, place1.name = getXYName(placeTerm1)

    # text2 = "Lübbecke Berufskoll"
    place2.x, place2.y, place2.name = getXYName(placeTerm2)

    place1.clouds, place1.temp = getWeather(place1.x, place1.y)
    place2.clouds, place2.temp = getWeather(place2.x, place2.y)

    distance, duration, steps, polygon = getDirection(place1.x, place1.y, place2.x, place2.y)

    createMap(place1, place2, distance, duration, steps, polygon)


def openDetailedMap():
    import os
    os.system("start index.html")


app = Flask(__name__)

@app.route('/')
def detailedMap():
    return app.send_static_file('.\index.html')

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def form_post():
    placeTerm1 = request.form['text']
    placeTerm2 = request.form['text2']
    createDetailedMap(placeTerm1, placeTerm2)
    # openDetailedMap()
    # return app.send_static_file('.\index.html')
    ##  return form()
    return detailedMap()

app.run(host='127.0.0.1', port=5000)