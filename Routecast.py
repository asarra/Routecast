import folium
import requests
import json

m1_name = None
m1_temp = None
m1_clouds = None
m1_x = None
m1_y = None

m2_name = None
m2_temp = None
m2_clouds = None
m2_x = None
m2_y = None


# Automatically completes the search term
def getXYName(place):
    ors_api_key = "5b3ce3597851110001cf62488cb0bdac946244b18bfdcbac9887e8b5"

    place = place.replace(" ", "%20")

    response = requests.get("https://api.openrouteservice.org/geocode/autocomplete?api_key="+ ors_api_key +"&text=" + place)

    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type',''):
        rj = json.loads(response.text)
        # Bewusst umgetauscht
        y,x = rj["features"][0]["geometry"]["coordinates"]
        full_name = rj["features"][0]["properties"]["name"]
        return (x,y,full_name)


def getWeather(x, y):
    apikey = "ae2549fa15d56163a63130ef24a8820e"

    response = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=" + str(x) + "&lon=" + str(y) + "&appid=" + apikey + "&units=metric")

    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type',''):
        rj = json.loads(response.text)
        clouds = rj["weather"][0]["main"]
        temp = rj["main"]["temp"]
        return (clouds, temp)

def getDirection(m1_x, m1_y, m2_x, m2_y):
    ors_api_key = "5b3ce3597851110001cf62488cb0bdac946244b18bfdcbac9887e8b5"

    response = requests.post("https://api.openrouteservice.org/v2/directions/driving-car/json",
                             data = "{\"coordinates\":[[%s,%s],[%s,%s]]}"%(m1_x, m1_y, m2_x, m2_y),
                             headers = {
                                 "Authorization" : ors_api_key,
                                 "Content-Type": "application/json",
                                 })
    print(response)
    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type',''):
        rj = json.loads(response.text)
        distance = rj["routes"]["summary"]["distance"]
        duration = rj["routes"]["summary"]["duration"]
        route = rj["routes"]["segments"]["steps"]
        return (distance, duration, route)

def createMap(m1_x, m1_y, m1_name, m1_clouds, m1_temp, m2_x, m2_y, m2_name, m2_clouds, m2_temp):
    m = folium.Map((m1_x, m1_y), tiles="cartodb positron", zoom_start=12)

    folium.Marker(
        location=[m1_x, m1_y],
        popup="%s:%s - %s Celsius"%(m1_name, m1_clouds, m1_temp),
        icon=folium.Icon(icon="blue"),
    ).add_to(m)

    folium.Marker(
        location=[m2_x, m2_y],
        popup="%s:%s - %s Celsius"%(m2_name, m2_clouds, m2_temp),
        icon=folium.Icon(color="green"),
    ).add_to(m)

    m.save("index.html")





place = "Berufskolleg Lübbec"
m1_x, m1_y, m1_name = getXYName(place)


place = "Hahlerstr 62b lübbecke"
m2_x, m2_y, m2_name = getXYName(place)







m1_clouds, m1_temp = getWeather(m1_x, m1_y)
m2_clouds, m2_temp = getWeather(m2_x, m2_y)



print(getDirection(m1_x, m1_y, m2_x, m2_y))
# distance, duration, route = getDirection(m1_x, m1_y, m2_x, m2_y)
# print(distance, duration, route)


# createMap(m1_x, m1_y, m1_name, m1_clouds, m1_temp, m2_x, m2_y, m2_name, m2_clouds, m2_temp)

