from methods import *
import place
from flask import Flask, request, render_template
import os

flag = False

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



app = Flask(__name__)

@app.route('/')
def form():
    global flag
    if (flag):
        # os.system("start ./static/index.html")
        flag = False
        return app.send_static_file('index.html')
    return render_template('form.html')

@app.route('/', methods=['POST'])
def form_post():
    placeTerm1 = request.form['text']
    placeTerm2 = request.form['text2']
    # return (placeTerm1, placeTerm2)
    createDetailedMap(placeTerm1, placeTerm2)
    global flag
    flag = True
    return form()
    

app.run(host='127.0.0.1', port=3000)

# createDetailedMap(placeTerm1, placeTerm2)
