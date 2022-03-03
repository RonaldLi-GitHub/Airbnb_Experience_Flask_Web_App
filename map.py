import folium
from folium.plugins import MousePosition
from folium.map import Marker
from folium.features import ClickForMarker, LatLngPopup


def map_init():
    start_coords = (32.7157, -117.1611)
    m = folium.Map(location=start_coords, zoom_start=17)
    m.add_child(ClickForMarker())
    m.add_child(LatLngPopup())

    marker = folium.Marker(
    location=[34.0522, -118.2437],
    popup="<stong>Allianz Arena</stong>",
    tooltip="OK")
    marker.add_to(m)
    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"

    MousePosition(
    position="topright",
    separator=" | ",
    empty_string="NaN",
    lng_first=True,
    num_digits=20,
    prefix="Coordinates:",
    lat_formatter=formatter,
    lng_formatter=formatter,
    ).add_to(m)

    return m
    