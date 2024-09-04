import plotly.express as px
import pandas as pd
import geopandas as gpd
import openpyxl
import folium
from folium.plugins import HeatMap
import json
import requests
import webbrowser

# import folium
# from folium import plugins
# import ipywidgets
# import geocoder
# import geopy
# import numpy as np
# import pandas as pd
# from vega_datasets import data as vds


# xls = pd.ExcelFile('6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx')
# df1 = pd.read_excel(xls, 'Iron (Fe)') # first sheet only
# df2 = pd.read_excel(xls, 'Chromium (Cr2O3)') # second sheet only


wb = openpyxl.load_workbook(filename = '6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx')
print(wb.sheetnames)


# borders = gpd.read_file('world-administrative-boundaries.geojson')









# m = folium.Map(tiles="cartodbpositron")

# geojson_data = requests.get(
#     "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/world_countries.json"
# ).json()

# folium.GeoJson(geojson_data, name="countries").add_to(m)

# folium.LayerControl().add_to(m)

# display(m)

























# countries = json.load(open("world-administrative-boundaries.geojson", 'r'))
# #print(countries['features'][10])

# df = pd.read_excel("6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx")
# #print(df.head)

# # map
# map_geojson = folium.Map(location=[39.77, -86.15], zoom_start=2) #location=[39.77, -86.15] in brackets

# #add geojson file to map
# # https://public.opendatasoft.com/explore/dataset/world-administrative-boundaries/export/?dataChart=eyJxdWVyaWVzIjpbeyJjb25maWciOnsiZGF0YXNldCI6IndvcmxkLWFkbWluaXN0cmF0aXZlLWJvdW5kYXJpZXMiLCJvcHRpb25zIjp7fX0sImNoYXJ0cyI6W3siYWxpZ25Nb250aCI6dHJ1ZSwidHlwZSI6ImNvbHVtbiIsImZ1bmMiOiJDT1VOVCIsInNjaWVudGlmaWNEaXNwbGF5Ijp0cnVlLCJjb2xvciI6IiNGRjUxNUEifV0sInhBeGlzIjoic3RhdHVzIiwibWF4cG9pbnRzIjo1MCwic29ydCI6IiJ9XSwidGltZXNjYWxlIjoiIiwiZGlzcGxheUxlZ2VuZCI6dHJ1ZSwiYWxpZ25Nb250aCI6dHJ1ZX0%3D&location=2,40.76075,0.00845&basemap=jawg.dark
# folium.GeoJson("world-administrative-boundaries.geojson", name='geojson world').add_to(map_geojson)
# # add layer control
# folium.LayerControl().add_to(map_geojson)
# folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(map_geojson)
# #display map
# map_geojson.save(r'C:\\Users\\Ryan McKay\\Downloads\\map.html')
# map_geojson.save('/Users/rmcka/Desktop/map_geojson.html')


# gdf = gpd.read_file("6.1. Total_World_Production.xlsx") # should be a geojson. COmbine file with geojoson and then try this.






# # Using Folium with Geopandas 16:00
# fname = [filename.gpkg]

# fiona.listlayers(fname)

# m = None

# for layer in fiona.listlayers(fname):
#     gdf = gpd.read_file(fname, layer=layer) [['Top 5', 'Region', 'geometry', 'Most Common']]
#     gdf['geometry' = gdf.simplify(0.001) #simplify geopandas geometries, reduces filesize

#     title = f"{layer.title()} Most Common"
#     gdf.columns= ['Top 5', 'Region', 'geometry', title]

#     if m: # if we've initialized a map already
#         gdf.explore(m=m, column=title, name=layer)
#     else:
#         m = gdf.explore(column=title, name=layer)
# folium.LayerControl().add_to(m)
