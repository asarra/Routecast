from methods import *
import place


place1 = place.Place()
place2 = place.Place()

placeTerm = "wortmann hüllhors"
place1.x, place1.y, place1.name = getXYName(placeTerm)

placeTerm = "Lübbecke Berufskoll"
place2.x, place2.y, place2.name = getXYName(placeTerm)

place1.clouds, place1.temp = getWeather(place1.x, place1.y)
place2.clouds, place2.temp = getWeather(place2.x, place2.y)

distance, duration, steps, polygon = getDirection(place1.x, place1.y, place2.x, place2.y)

createMap(place1, place2, distance, duration, steps, polygon)