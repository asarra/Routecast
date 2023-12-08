import sys
sys.dont_write_bytecode = True # disables pycache generation

import folium, requests, json
from folium import Element

ors_api_key = "5b3ce3597851110001cf62488cb0bdac946244b18bfdcbac9887e8b5"
weather_api_key = "ae2549fa15d56163a63130ef24a8820e"

# From https://giscience.github.io/openrouteservice/documentation/Geometry-Decoding.html#python
def decode_polyline(polyline, is3d=False):
    """Decodes a Polyline string into a GeoJSON geometry.
    :param polyline: An encoded polyline, only the geometry.
    :type polyline: string
    :param is3d: Specifies if geometry contains Z component.
    :type is3d: boolean
    :returns: GeoJSON Linestring geometry
    :rtype: dict
    """
    points = []
    index = lat = lng = z = 0

    while index < len(polyline):
        result = 1
        shift = 0
        while True:
            b = ord(polyline[index]) - 63 - 1
            index += 1
            result += b << shift
            shift += 5
            if b < 0x1F:
                break
        lat += (~result >> 1) if (result & 1) != 0 else (result >> 1)

        result = 1
        shift = 0
        while True:
            b = ord(polyline[index]) - 63 - 1
            index += 1
            result += b << shift
            shift += 5
            if b < 0x1F:
                break
        lng += ~(result >> 1) if (result & 1) != 0 else (result >> 1)

        if is3d:
            result = 1
            shift = 0
            while True:
                b = ord(polyline[index]) - 63 - 1
                index += 1
                result += b << shift
                shift += 5
                if b < 0x1F:
                    break
            if (result & 1) != 0:
                z += ~(result >> 1)
            else:
                z += result >> 1

            points.append(
                [
                    round(lng * 1e-5, 6),
                    round(lat * 1e-5, 6),
                    round(z * 1e-2, 1),
                ]
            )

        else:
            points.append([round(lng * 1e-5, 6), round(lat * 1e-5, 6)])

    geojson = {u"type": u"LineString", u"coordinates": points}

    return geojson


# Automatically completes the search term
def getXYName(placeTerm):
    global weather_api_key
    placeTerm = placeTerm.replace(" ", "%20")

    response = requests.get("https://api.openrouteservice.org/geocode/autocomplete?api_key=" + ors_api_key + "&text=" + placeTerm)

    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type',''):
        rj = json.loads(response.text)
        if rj["features"] == []:
            throw("Nichts gefunden. Eingabe fehlerhaft")
        else:
            # Bewusst umgetauscht
            y,x = rj["features"][0]["geometry"]["coordinates"]
            full_name = rj["features"][0]["properties"]["name"]
            return (x,y,full_name)


def getDirection(m1_x, m1_y, m2_x, m2_y):
    global weather_api_key
    response = requests.post("https://api.openrouteservice.org/v2/directions/driving-car/json",
                                # Erneut Koordinaten zurückgetauscht
                                data = "{\"coordinates\":[[%s,%s],[%s,%s]]}"%(m1_y, m1_x, m2_y, m2_x),
                                headers = {
                                    "Authorization" : ors_api_key,
                                    "Content-Type": "application/json",
                                    })
    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type',''):
        rj = json.loads(response.text)
        distance = rj["routes"][0]["summary"]["distance"]
        duration = rj["routes"][0]["summary"]["duration"]
        steps = rj["routes"][0]["segments"][0]["steps"]
        polygon = decode_polyline(rj["routes"][0]["geometry"])
        return (distance, duration, steps, polygon)


def getWeather(x, y):
    global ors_api_key
    response = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=" + str(x) + "&lon=" + str(y) + "&appid=" + weather_api_key + "&units=metric")

    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type',''):
        rj = json.loads(response.text)
        clouds = rj["weather"][0]["main"]
        temp = rj["main"]["temp"]
        return (clouds, temp)


def createMap(place1, place2, distance, duration, steps, polygon):
    m = folium.Map((place1.x, place1.y), tiles="OpenStreetMap", zoom_start=12)

    folium.Marker(
        location=[place1.x, place1.y],
        popup="%s:%s - %s Celsius"%(place1.name, place1.clouds, place1.temp),
        icon=folium.Icon(icon="blue"),
    ).add_to(m)

    folium.Marker(
        location=[place2.x, place2.y],
        popup="%s:%s - %s Celsius"%(place2.name, place2.clouds, place2.temp),
        icon=folium.Icon(color="green"),
    ).add_to(m)

    folium.GeoJson(polygon).add_to(m)

    steps_list = ""
    for _s in steps:
        steps_list += f'<h4>{_s["instruction"]} ({str(_s["distance"])} m / {str(_s["duration"])} s)</h4>'

    # inject html into the map html
    m.get_root().html.add_child(folium.Element("""
    <div style="position: fixed;
                background-color: white;
                padding: 5px;
                border: 1px solid #333;
                border-radius: 15px;
                z-index: 9999;
                width: 30em;
                bottom: 0;
                overflow: scroll;
                right: 0;
                ">
        <h1>Routeninformationen</h1><br>
        <h3>Entfernung: %s m</h3>
        <h3>Reisedauer: %s s</h3>
        <h3>Schritte:</h3>
        %s
    </div>
    """%(distance, duration, steps_list)))

    m.save("./static/index.html")
