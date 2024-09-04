"""
A web app with interactive maps showing the global production of various minerals, ranked by country.
Created by Ryan McKay as a final project for CS50x: Introduction to Computer Science
"""
# to autogenerate requirements.txt with current versions: pip freeze > requirements.txt
# or for a more manageable requirements doc: pipreqs .

from flask import Flask, render_template
import folium
from folium import plugins
import pandas as pd
import geopandas as gpd

# Configure Flask application
def create_app():
    app = Flask(__name__)
    return app

app = create_app()

# Create index HTML ref
@app.route("/")
def index():
    return render_template("index.html")

# read the Excel sheet using pandas.
xls_2022 = pd.ExcelFile('6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx')
# 2021 data for future iterations of the app.
xls_2021 = pd.ExcelFile('6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx')

# base map used for all maps.
tile_layer = folium.TileLayer(
    tiles="https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    min_zoom=2,
    max_zoom=6,
    name='darkmatter',
    control=False,
    opacity=0.5
)

# Configure the style of the tooltip text.
style_function = lambda x: {
    'fillColor': '#ffffff',
    'color':'#000000',
    'fillOpacity': 0.1,
    'weight': 0.1}

highlight_function = lambda x: {
    'fillColor': '#000000',
    'color':'#000000',
    'fillOpacity': 0.50,
    'weight': 0.1}

# create variables to reference in the tooltips.
wmd_2022 = 'Production 2022'
wmd_2021 = 'Production 2021'
wmp = 'Share in %'

# Lists of the various mineral groupings.
type_ferro_alloy = ['Iron (Fe)', 'Chromium (Cr2O3)', 'Cobalt', 'Manganese', 'Molybdenum', 'Nickel', 'Niobium (Nb2O5)', 'Tantalum (Ta2O5)', 'Titanium (TiO2)', 'Tungsten (W)', 'Vanadium (V)']
type_non_ferrous = ['Aluminium', 'Antimony', 'Arsenic', 'Bauxite', 'Beryllium (conc.)', 'Bismuth', 'Cadmium', 'Copper', 'Gallium', 'Germanium', 'Indium', 'Lead', 'Lithium (Li2O)', 'Mercury', 'Rare Earths (REO)', 'Rhenium', 'Selenium', 'Tellurium', 'Tin', 'Zinc']
type_precious = ['Gold', 'Palladium', 'Platinum', 'Rhodium', 'Silver']
type_industrial = ['Asbestos', 'Baryte', 'Bentonite', 'Boron Minerals', 'Diamonds (Gem)', 'Diamonds (Ind)', 'Diatomite', 'Feldspar', 'Fluorspar', 'Graphite', 'Gypsum and Anhydrite', 'Kaolin (China-Clay)', 'Magnesite', 'Perlite', 'Phosphate Rock (P2O5)', 'Potash (K2O)', 'Salt (rock, brines, marine)', 'Sulfur (elementar & industrial)', 'Talc, Steatite & Pyrophyllite', 'Vermiculite', 'Zircon']
type_fuel = ['Steam Coal ', 'Coking Coal', 'Lignite', 'Natural Gas', 'Petroleum', 'Oil Sands (part of Petroleum)', 'Oil Shales', 'Uranium (U3O8)']

# Create a list of all sheets in the file
#print(xls_2022.sheet_names)
# ['Iron (Fe)', 'Chromium (Cr2O3)', ...]

# to read just one sheet to dataframe:
# read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
#df = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name=xls_2022.sheet_names[1], skiprows=[0])

# Use GeoPandas to read the JSON file with Country polygon geometries.
countries = gpd.read_file("world-countries.json")
#print(countries.columns.tolist())

# sheets that have < 6 countries, thus cannot apply 'use_jenks=True' which requires 6+ classes.
no_jenks = ['Vanadium (V)', 'Gallium', 'Germanium', 'Rhodium', 'Asbestos', 'Oil Sands (part of Petroleum)']


#print(xls_2022.sheet_names)
# for sheet_name in range(0, len(xls_2022.sheet_names)):
    #sheets_dict[i] = f"{xls_2022.sheet_names[i]}"
    # for sheet_name in xls_2022.sheet_names[0,10]:
    #     type_ferro_alloy.append(sheet_name)
    # for sheet_name in xls_2022.sheet_names[11,30]:
    #     type_non_ferrous.append(sheet_name)
    # for sheet_name in xls_2022.sheet_names[31,35]:
    #     type_precious.append(sheet_name)
    # for sheet_name in xls_2022.sheet_names[36,56]:
    #     type_industrial.append(sheet_name)
    # for sheet_name in xls_2022.sheet_names[57,64]:
    #     type_fuel.append(sheet_name)

# A dictionary for storing the generated maps under the name of the corresponding sheet in excel.
map_dict = {}
# for sheet in xls_2022.sheet_names:
#     map_dict["metal"] = map

# Set the 'Keys' of the dictionary to be the name of the excel sheet. The 'Value' will be the generated maps after each one is made.
map_dict = dict.fromkeys(xls_2022.sheet_names)
# print(map_dict)

# tab_id_dict = {}
# tab_id_dict = dict.fromkeys(xls_2022.sheet_names)



#________________________________________________________________________________________________
#________________________________________________________________________________________________
#________________________________________________________________________________________________
#________________________________________________________________________________________________
# ferro_alloy
# 'Iron (Fe)', 'Chromium (Cr2O3)', 'Cobalt', 'Manganese', 'Molybdenum', 'Nickel', 'Niobium (Nb2O5)', 'Tantalum (Ta2O5)', 'Titanium (TiO2)', 'Tungsten (W)', 'Vanadium (V)'
#________________________________________________________________________________________________

# Define a function for all minerals within one category.
@app.route("/ferro-alloy")
def ferro_alloy():

#______________________________________________________________
# 'Iron (Fe)'
#______________________________________________________________

    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_iron = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True)

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_iron)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_iron)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_iron = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Iron (Fe)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_iron = df_iron[df_iron['Country'] != 'Total']

    # round the Percent figure to 2 decimal places

    # round the Percent figure to 2 decimal places.
    df_iron['Share in %'] = round(df_iron['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_iron = countries.merge(df_iron,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_iron,
        data=merge_df_iron,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Iron (Fe) (% of Global Production)",
        name="Iron (Fe) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity=0.25,
        overlay=False,
        ).add_to(m_iron)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_iron,
        style_function=style_function,
        control=False,
        show=True,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_iron["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # df21_iron = pd.read_excel("6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx", sheet_name="Iron (Fe)", skiprows=[0])
    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    # df21_iron = df21_iron[df21_iron['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    # df21_iron['Share in %'] = round(df21_iron['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    # merge_df21_iron = countries.merge(df21_iron,on='Country')

    # # 2021 map. Don't immediately add_to.(m), must first delete the legend.
    # choropleth21_iron = folium.Choropleth(
    #     geo_data=merge_df21_iron,
    #     data=merge_df21_iron,
    #     columns=['Country', wmp],
    #     key_on='feature.properties.Country',
    #     fill_color='OrRd',
    #     fill_opacity=1,
    #     line_color='black',
    #     line_opacity=1,
    #     #legend_name="Iron (Fe) (% of Global Production)",
    #     name="Iron (Fe) Production 2021",
    #     highlight=True,
    #     use_jenks=True,
    #     #nan_fill_opacity=0.25,
    #     overlay=False,
    #     show=False,
    #     )

    # # delete the 2021 legend so that only one legend shows per map
    # for key in choropleth21_iron._children:
    #     if key.startswith('color_map'):
    #         del(choropleth21_iron._children[key])
    # choropleth21_iron.add_to(m_iron)
    # #.add_to(m_iron)

    # hoverText21 = folium.features.GeoJson(
    #     #geo_data=geo_json_data,
    #     data=merge_df21_iron,
    #     style_function=style_function,
    #     #show=True,
    #     control=False,
    #     highlight_function=highlight_function,
    #     tooltip=folium.features.GeoJsonTooltip(
    #         fields=['Country', 'Rank 2021', wmp, wmd_2021],
    #         aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df21_iron["unit"][1]}: '],
    #         style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"),
    #     )
    # )

    # m_iron.add_child(hoverText21)
    # m_iron.keep_in_front(hoverText21)

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_iron.add_child(hoverText)
    m_iron.keep_in_front(hoverText)

    # fig = branca.element.Figure(height='100%')
    # fig.add_child(m_iron)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_iron)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_iron = m_iron.get_root()._repr_html_()

    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Iron (Fe)"] = m_iron

    # define the tab-id used by jinja
    # tab_id_dict[f"{xls_2022.sheet_names[0]}"] = i


#______________________________________________________________
#'Chromium (Cr2O3)'
#______________________________________________________________

    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_chromium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_chromium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_chromium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_chromium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Chromium (Cr2O3)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_chromium = df_chromium[df_chromium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_chromium['Share in %'] = round(df_chromium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_chromium = countries.merge(df_chromium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_chromium,
        data=merge_df_chromium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Chromium (Cr2O3) (% of Global Production)",
        name="Chromium (Cr2O3) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_chromium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_chromium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_chromium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_chromium.add_child(hoverText)
    m_chromium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_chromium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_chromium = m_chromium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Chromium (Cr2O3)"] = m_chromium

#______________________________________________________________
#'Cobalt'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_cobalt = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_cobalt)


    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_cobalt)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_cobalt = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Cobalt", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_cobalt = df_cobalt[df_cobalt['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_cobalt['Share in %'] = round(df_cobalt['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_cobalt = countries.merge(df_cobalt,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_cobalt,
        data=merge_df_cobalt,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Cobalt (% of Global Production)",
        name="Cobalt Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_cobalt)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_cobalt,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_cobalt["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_cobalt.add_child(hoverText)
    m_cobalt.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_cobalt)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_cobalt = m_cobalt.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Cobalt"] = m_cobalt
#______________________________________________________________
#'Manganese'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_manganese = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_manganese)


    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_manganese)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_manganese = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Manganese", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_manganese = df_manganese[df_manganese['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_manganese['Share in %'] = round(df_manganese['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_manganese = countries.merge(df_manganese,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_manganese,
        data=merge_df_manganese,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Manganese (% of Global Production)",
        name="Manganese Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_manganese)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_manganese,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_manganese["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_manganese.add_child(hoverText)
    m_manganese.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_manganese)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_manganese = m_manganese.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Manganese"] = m_manganese
#______________________________________________________________
#'Molybdenum'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_molybdenum = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_molybdenum)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_molybdenum)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_molybdenum = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Molybdenum", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_molybdenum = df_molybdenum[df_molybdenum['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_molybdenum['Share in %'] = round(df_molybdenum['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_molybdenum = countries.merge(df_molybdenum,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_molybdenum,
        data=merge_df_molybdenum,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Molybdenum (% of Global Production)",
        name="Molybdenum Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_molybdenum)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_molybdenum,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_molybdenum["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_molybdenum.add_child(hoverText)
    m_molybdenum.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_molybdenum)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_molybdenum = m_molybdenum.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Molybdenum"] = m_molybdenum
#______________________________________________________________
#'Nickel'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_nickel = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_nickel)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_nickel)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_nickel = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Nickel", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_nickel = df_nickel[df_nickel['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_nickel['Share in %'] = round(df_nickel['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_nickel = countries.merge(df_nickel,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_nickel,
        data=merge_df_nickel,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Nickel (% of Global Production)",
        name="Nickel Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_nickel)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_nickel,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_nickel["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_nickel.add_child(hoverText)
    m_nickel.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_nickel)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_nickel = m_nickel.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Nickel"] = m_nickel
#______________________________________________________________
#'Niobium (Nb2O5)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_niobium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_niobium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_niobium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_niobium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Niobium (Nb2O5)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_niobium = df_niobium[df_niobium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_niobium['Share in %'] = round(df_niobium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_niobium = countries.merge(df_niobium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_niobium,
        data=merge_df_niobium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Niobium (Nb2O5) (% of Global Production)",
        name="Niobium (Nb2O5) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_niobium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_niobium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_niobium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_niobium.add_child(hoverText)
    m_niobium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_niobium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_niobium = m_niobium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Niobium (Nb2O5)"] = m_niobium
#______________________________________________________________
#'Tantalum (Ta2O5)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_tantalum = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_tantalum)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_tantalum)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_tantalum = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Tantalum (Ta2O5)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_tantalum = df_tantalum[df_tantalum['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_tantalum['Share in %'] = round(df_tantalum['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_tantalum = countries.merge(df_tantalum,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_tantalum,
        data=merge_df_tantalum,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Tantalum (Ta2O5) (% of Global Production)",
        name="Tantalum (Ta2O5) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_tantalum)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_tantalum,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_tantalum["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_tantalum.add_child(hoverText)
    m_tantalum.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_tantalum)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_tantalum = m_tantalum.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Tantalum (Ta2O5)"] = m_tantalum
#______________________________________________________________
#'Titanium (TiO2)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_titanium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_titanium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_titanium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_titanium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Titanium (TiO2)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_titanium = df_titanium[df_titanium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_titanium['Share in %'] = round(df_titanium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_titanium = countries.merge(df_titanium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_titanium,
        data=merge_df_titanium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Titanium (TiO2) (% of Global Production)",
        name="Titanium (TiO2) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_titanium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_titanium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_titanium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_titanium.add_child(hoverText)
    m_titanium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_titanium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_titanium = m_titanium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Titanium (TiO2)"] = m_titanium
#______________________________________________________________
#'Tungsten (W)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_tungsten = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_tungsten)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_tungsten)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_tungsten = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Tungsten (W)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_tungsten = df_tungsten[df_tungsten['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_tungsten['Share in %'] = round(df_tungsten['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_tungsten = countries.merge(df_tungsten,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_tungsten,
        data=merge_df_tungsten,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Tungsten (W) (% of Global Production)",
        name="Tungsten (W) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_tungsten)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_tungsten,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_tungsten["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_tungsten.add_child(hoverText)
    m_tungsten.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_tungsten)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_tungsten = m_tungsten.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Tungsten (W)"] = m_tungsten
#______________________________________________________________
#'Vanadium (V)' - turn off 'use_jenks=True'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_vanadium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_vanadium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_vanadium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_vanadium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Vanadium (V)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_vanadium = df_vanadium[df_vanadium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_vanadium['Share in %'] = round(df_vanadium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_vanadium = countries.merge(df_vanadium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_vanadium,
        data=merge_df_vanadium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='OrRd',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Vanadium (V) (% of Global Production)",
        name="Vanadium (V) Production 2022",
        highlight=True,
        use_jenks=False,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_vanadium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_vanadium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_vanadium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_vanadium.add_child(hoverText)
    m_vanadium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_vanadium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_vanadium = m_vanadium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Vanadium (V)"] = m_vanadium

    return render_template("ferro-alloy.html", map_dict=map_dict)

#________________________________________________________________________________________________
# non_ferrous
# 'Aluminium', 'Antimony', 'Arsenic', 'Bauxite', 'Beryllium (conc.)', 'Bismuth', 'Cadmium', 'Copper', 'Gallium', 'Germanium', 'Indium', 'Lead', 'Lithium (Li2O)', 'Mercury', 'Rare Earths (REO)', 'Rhenium', 'Selenium', 'Tellurium', 'Tin', 'Zinc'
#________________________________________________________________________________________________

@app.route("/non-ferrous")
def non_ferrous():

#______________________________________________________________
# 'Aluminium'
#______________________________________________________________

    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_aluminium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_aluminium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_aluminium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_aluminium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Aluminium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_aluminium = df_aluminium[df_aluminium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_aluminium['Share in %'] = round(df_aluminium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_aluminium = countries.merge(df_aluminium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_aluminium,
        data=merge_df_aluminium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Aluminium (% of Global Production)",
        name="Aluminium Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_aluminium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_aluminium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_aluminium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_aluminium.add_child(hoverText)
    m_aluminium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_aluminium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_aluminium = m_aluminium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Aluminium"] = m_aluminium

#______________________________________________________________
#'Antimony'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_antimony = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_antimony)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_antimony)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_antimony = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Antimony", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_antimony = df_antimony[df_antimony['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_antimony['Share in %'] = round(df_antimony['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_antimony = countries.merge(df_antimony,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_antimony,
        data=merge_df_antimony,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Antimony (% of Global Production)",
        name="Antimony Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_antimony)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_antimony,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_antimony["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_antimony.add_child(hoverText)
    m_antimony.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_antimony)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_antimony = m_antimony.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Antimony"] = m_antimony
#______________________________________________________________
#'Arsenic'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_arsenic = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_arsenic)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_arsenic)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_arsenic = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Arsenic", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_arsenic = df_arsenic[df_arsenic['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_arsenic['Share in %'] = round(df_arsenic['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_arsenic = countries.merge(df_arsenic,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_arsenic,
        data=merge_df_arsenic,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Arsenic (% of Global Production)",
        name="Arsenic Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_arsenic)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_arsenic,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_arsenic["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_arsenic.add_child(hoverText)
    m_arsenic.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_arsenic)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_arsenic = m_arsenic.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Arsenic"] = m_arsenic
#______________________________________________________________
#'Bauxite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_bauxite = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_bauxite)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_bauxite)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_bauxite = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Bauxite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_bauxite = df_bauxite[df_bauxite['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_bauxite['Share in %'] = round(df_bauxite['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_bauxite = countries.merge(df_bauxite,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_bauxite,
        data=merge_df_bauxite,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Bauxite (% of Global Production)",
        name="Bauxite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_bauxite)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_bauxite,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_bauxite["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_bauxite.add_child(hoverText)
    m_bauxite.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_bauxite)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_bauxite = m_bauxite.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Bauxite"] = m_bauxite
#______________________________________________________________
#'Beryllium (conc.)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_beryllium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_beryllium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_beryllium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_beryllium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Beryllium (conc.)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_beryllium = df_beryllium[df_beryllium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_beryllium['Share in %'] = round(df_beryllium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_beryllium = countries.merge(df_beryllium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_beryllium,
        data=merge_df_beryllium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Beryllium (conc.) (% of Global Production)",
        name="Beryllium (conc.) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_beryllium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_beryllium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_beryllium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_beryllium.add_child(hoverText)
    m_beryllium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_beryllium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_beryllium = m_beryllium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Beryllium (conc.)"] = m_beryllium
#______________________________________________________________
#'Bismuth'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_bismuth = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_bismuth)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_bismuth)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_bismuth = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Bismuth", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_bismuth = df_bismuth[df_bismuth['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_bismuth['Share in %'] = round(df_bismuth['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_bismuth = countries.merge(df_bismuth,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_bismuth,
        data=merge_df_bismuth,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Bismuth (% of Global Production)",
        name="Bismuth Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_bismuth)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_bismuth,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_bismuth["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_bismuth.add_child(hoverText)
    m_bismuth.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_bismuth)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_bismuth = m_bismuth.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Bismuth"] = m_bismuth
#______________________________________________________________
#'Cadmium'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_cadmium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_cadmium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_cadmium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_cadmium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Cadmium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_cadmium = df_cadmium[df_cadmium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_cadmium['Share in %'] = round(df_cadmium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_cadmium = countries.merge(df_cadmium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_cadmium,
        data=merge_df_cadmium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Cadmium (% of Global Production)",
        name="Cadmium Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_cadmium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_cadmium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_cadmium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_cadmium.add_child(hoverText)
    m_cadmium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_cadmium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_cadmium = m_cadmium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Cadmium"] = m_cadmium
#______________________________________________________________
#'Copper'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_copper = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_copper)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_copper)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_copper = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Copper", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_copper = df_copper[df_copper['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_copper['Share in %'] = round(df_copper['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_copper = countries.merge(df_copper,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_copper,
        data=merge_df_copper,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Copper (% of Global Production)",
        name="Copper Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_copper)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_copper,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_copper["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_copper.add_child(hoverText)
    m_copper.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_copper)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_copper = m_copper.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Copper"] = m_copper
#______________________________________________________________
#'Gallium' - set 'use_jenks=False' - fewer than 6 entries, can't use jenks.
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_gallium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_gallium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_gallium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_gallium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Gallium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_gallium = df_gallium[df_gallium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_gallium['Share in %'] = round(df_gallium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_gallium = countries.merge(df_gallium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_gallium,
        data=merge_df_gallium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Gallium (% of Global Production)",
        name="Gallium Production 2022",
        highlight=True,
        use_jenks=False,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_gallium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_gallium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_gallium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_gallium.add_child(hoverText)
    m_gallium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_gallium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_gallium = m_gallium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Gallium"] = m_gallium
#______________________________________________________________
#'Germanium' - set 'use_jenks=False' - fewer than 6 entries, can't use jenks.
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_germanium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_germanium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_germanium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_germanium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Germanium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_germanium = df_germanium[df_germanium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_germanium['Share in %'] = round(df_germanium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_germanium = countries.merge(df_germanium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_germanium,
        data=merge_df_germanium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Germanium (% of Global Production)",
        name="Germanium Production 2022",
        highlight=True,
        use_jenks=False,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_germanium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_germanium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_germanium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_germanium.add_child(hoverText)
    m_germanium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_germanium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_germanium = m_germanium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Germanium"] = m_germanium
#______________________________________________________________
# Indium
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_indium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_indium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_indium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_indium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Indium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_indium = df_indium[df_indium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_indium['Share in %'] = round(df_indium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_indium = countries.merge(df_indium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_indium,
        data=merge_df_indium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Indium (% of Global Production)",
        name="Indium Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_indium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_indium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_indium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_indium.add_child(hoverText)
    m_indium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_indium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_indium = m_indium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Indium"] = m_indium
#______________________________________________________________
#'Lead'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_lead = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_lead)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_lead)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_lead = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Lead", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_lead = df_lead[df_lead['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_lead['Share in %'] = round(df_lead['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_lead = countries.merge(df_lead,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_lead,
        data=merge_df_lead,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Lead (% of Global Production)",
        name="Lead Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_lead)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_lead,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_lead["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_lead.add_child(hoverText)
    m_lead.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_lead)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_lead = m_lead.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Lead"] = m_lead
#______________________________________________________________
#'Lithium (Li2O)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_lithium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_lithium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_lithium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_lithium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Lithium (Li2O)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_lithium = df_lithium[df_lithium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_lithium['Share in %'] = round(df_lithium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_lithium = countries.merge(df_lithium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_lithium,
        data=merge_df_lithium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Lithium (Li2O) (% of Global Production)",
        name="Lithium (Li2O) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_lithium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_lithium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_lithium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_lithium.add_child(hoverText)
    m_lithium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_lithium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_lithium = m_lithium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Lithium (Li2O)"] = m_lithium
#______________________________________________________________
#'Mercury'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_mercury = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_mercury)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_mercury)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_mercury = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Mercury", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_mercury = df_mercury[df_mercury['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_mercury['Share in %'] = round(df_mercury['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_mercury = countries.merge(df_mercury,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_mercury,
        data=merge_df_mercury,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Mercury (% of Global Production)",
        name="Mercury Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_mercury)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_mercury,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_mercury["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_mercury.add_child(hoverText)
    m_mercury.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_mercury)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_mercury = m_mercury.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Mercury"] = m_mercury
#______________________________________________________________
#'Rare Earths (REO)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_rare_earths = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_rare_earths)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_rare_earths)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_rare_earths = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Rare Earths (REO)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_rare_earths = df_rare_earths[df_rare_earths['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_rare_earths['Share in %'] = round(df_rare_earths['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_rare_earths = countries.merge(df_rare_earths,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_rare_earths,
        data=merge_df_rare_earths,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Rare Earths (REO) (% of Global Production)",
        name="Rare Earths (REO) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_rare_earths)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_rare_earths,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_rare_earths["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_rare_earths.add_child(hoverText)
    m_rare_earths.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_rare_earths)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_rare_earths = m_rare_earths.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Rare Earths (REO)"] = m_rare_earths
#______________________________________________________________
#'Rhenium'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_rhenium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_rhenium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_rhenium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_rhenium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Rhenium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_rhenium = df_rhenium[df_rhenium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_rhenium['Share in %'] = round(df_rhenium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_rhenium = countries.merge(df_rhenium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_rhenium,
        data=merge_df_rhenium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Rhenium (% of Global Production)",
        name="Rhenium Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_rhenium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_rhenium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_rhenium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_rhenium.add_child(hoverText)
    m_rhenium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_rhenium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_rhenium = m_rhenium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Rhenium"] = m_rhenium
#______________________________________________________________
#'Selenium'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_selenium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_selenium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_selenium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_selenium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Selenium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_selenium = df_selenium[df_selenium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_selenium['Share in %'] = round(df_selenium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_selenium = countries.merge(df_selenium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_selenium,
        data=merge_df_selenium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Selenium (% of Global Production)",
        name="Selenium Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_selenium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_selenium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_selenium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_selenium.add_child(hoverText)
    m_selenium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_selenium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_selenium = m_selenium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Selenium"] = m_selenium
#______________________________________________________________
#'Tellurium'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_tellurium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_tellurium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_tellurium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_tellurium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Tellurium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_tellurium = df_tellurium[df_tellurium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_tellurium['Share in %'] = round(df_tellurium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_tellurium = countries.merge(df_tellurium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_tellurium,
        data=merge_df_tellurium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Tellurium (% of Global Production)",
        name="Tellurium Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_tellurium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_tellurium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_tellurium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_tellurium.add_child(hoverText)
    m_tellurium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_tellurium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_tellurium = m_tellurium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Tellurium"] = m_tellurium
#______________________________________________________________
#'Tin'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_tin = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_tin)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_tin)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_tin = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Tin", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_tin = df_tin[df_tin['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_tin['Share in %'] = round(df_tin['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_tin = countries.merge(df_tin,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_tin,
        data=merge_df_tin,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Tin (% of Global Production)",
        name="Tin Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_tin)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_tin,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_tin["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_tin.add_child(hoverText)
    m_tin.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_tin)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_tin = m_tin.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Tin"] = m_tin
#______________________________________________________________
#'Zinc'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_zinc = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_zinc)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_zinc)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_zinc = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Zinc", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_zinc = df_zinc[df_zinc['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_zinc['Share in %'] = round(df_zinc['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_zinc = countries.merge(df_zinc,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_zinc,
        data=merge_df_zinc,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='PuBuGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Zinc (% of Global Production)",
        name="Zinc Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_zinc)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_zinc,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_zinc["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_zinc.add_child(hoverText)
    m_zinc.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_zinc)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_zinc = m_zinc.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Zinc"] = m_zinc


    return render_template("non-ferrous.html", map_dict=map_dict)

#________________________________________________________________________________________________
# precious
# 'Gold', 'Palladium', 'Platinum', 'Rhodium', 'Silver'
#________________________________________________________________________________________________

@app.route("/precious-metals")
def precious_metals():
#______________________________________________________________
#'Gold'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_gold = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_gold)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_gold)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_gold = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Gold", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_gold = df_gold[df_gold['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_gold['Share in %'] = round(df_gold['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_gold = countries.merge(df_gold,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_gold,
        data=merge_df_gold,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='plasma',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Gold (% of Global Production)",
        name="Gold Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_gold)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_gold,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_gold["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_gold.add_child(hoverText)
    m_gold.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_gold)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_gold = m_gold.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Gold"] = m_gold


#______________________________________________________________
#'Palladium'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_palladium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_palladium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_palladium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_palladium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Palladium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_palladium = df_palladium[df_palladium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_palladium['Share in %'] = round(df_palladium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_palladium = countries.merge(df_palladium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_palladium,
        data=merge_df_palladium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='plasma',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Palladium (% of Global Production)",
        name="Palladium Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_palladium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_palladium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_palladium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_palladium.add_child(hoverText)
    m_palladium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_palladium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_palladium = m_palladium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Palladium"] = m_palladium

#______________________________________________________________
#'Platinum'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_platinum = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_platinum)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_platinum)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_platinum = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Platinum", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_platinum = df_platinum[df_platinum['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_platinum['Share in %'] = round(df_platinum['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_platinum = countries.merge(df_platinum,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_platinum,
        data=merge_df_platinum,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='plasma',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Platinum (% of Global Production)",
        name="Platinum Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_platinum)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_platinum,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_platinum["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_platinum.add_child(hoverText)
    m_platinum.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_platinum)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_platinum = m_platinum.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Platinum"] = m_platinum

#______________________________________________________________
#'Rhodium' - turn off 'use_jenks=True'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_rhodium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_rhodium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_rhodium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_rhodium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Rhodium", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_rhodium = df_rhodium[df_rhodium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_rhodium['Share in %'] = round(df_rhodium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_rhodium = countries.merge(df_rhodium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_rhodium,
        data=merge_df_rhodium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='plasma',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Rhodium (% of Global Production)",
        name="Rhodium Production 2022",
        highlight=True,
        use_jenks=False,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_rhodium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_rhodium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_rhodium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_rhodium.add_child(hoverText)
    m_rhodium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_rhodium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_rhodium = m_rhodium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Rhodium"] = m_rhodium
#______________________________________________________________
#'Silver'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_silver = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_silver)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_silver)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_silver = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Silver", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_silver = df_silver[df_silver['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_silver['Share in %'] = round(df_silver['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_silver = countries.merge(df_silver,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_silver,
        data=merge_df_silver,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='plasma',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Silver (% of Global Production)",
        name="Silver Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_silver)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_silver,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_silver["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_silver.add_child(hoverText)
    m_silver.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_silver)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_silver = m_silver.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Silver"] = m_silver

    return render_template("precious-metals.html", map_dict=map_dict)

#________________________________________________________________________________________________
# industrial
# 'Asbestos', 'Baryte', 'Bentonite', 'Boron Minerals', 'Diamonds (Gem)', 'Diamonds (Ind)', 'Diatomite', 'Feldspar', 'Fluorspar', 'Graphite', 'Gypsum and Anhydrite', 'Kaolin (China-Clay)', 'Magnesite', 'Perlite', 'Phosphate Rock (P2O5)', 'Potash (K2O)', 'Salt (rock, brines, marine)', 'Sulfur (elementar & industrial)', 'Talc, Steatite & Pyrophyllite', 'Vermiculite', 'Zircon'
#________________________________________________________________________________________________
#______________________________________________________________
# 'Asbestos' - turn 'use_jenks' to False. Fewer than 6 entries.
#______________________________________________________________
@app.route("/industrial-minerals")
def industrial_minerals():

    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_asbestos = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_asbestos)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_asbestos)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_asbestos = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Asbestos", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_asbestos = df_asbestos[df_asbestos['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_asbestos['Share in %'] = round(df_asbestos['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_asbestos = countries.merge(df_asbestos,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_asbestos,
        data=merge_df_asbestos,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Asbestos (% of Global Production)",
        name="Asbestos Production 2022",
        highlight=True,
        use_jenks=False,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_asbestos)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_asbestos,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_asbestos["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_asbestos.add_child(hoverText)
    m_asbestos.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_asbestos)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_asbestos = m_asbestos.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Asbestos"] = m_asbestos

#______________________________________________________________
#'Baryte'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_baryte = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_baryte)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_baryte)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_baryte = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Baryte", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_baryte = df_baryte[df_baryte['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_baryte['Share in %'] = round(df_baryte['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_baryte = countries.merge(df_baryte,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_baryte,
        data=merge_df_baryte,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Baryte (% of Global Production)",
        name="Baryte Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_baryte)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_baryte,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_baryte["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_baryte.add_child(hoverText)
    m_baryte.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_baryte)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_baryte = m_baryte.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Baryte"] = m_baryte
#______________________________________________________________
#'Bentonite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_bentonite = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_bentonite)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_bentonite)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_bentonite = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Bentonite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_bentonite = df_bentonite[df_bentonite['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_bentonite['Share in %'] = round(df_bentonite['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_bentonite = countries.merge(df_bentonite,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_bentonite,
        data=merge_df_bentonite,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Bentonite (% of Global Production)",
        name="Bentonite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_bentonite)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_bentonite,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_bentonite["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_bentonite.add_child(hoverText)
    m_bentonite.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_bentonite)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_bentonite = m_bentonite.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Bentonite"] = m_bentonite
#______________________________________________________________
#'Boron Minerals'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_boron = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_boron)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_boron)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_boron = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Boron Minerals", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_boron = df_boron[df_boron['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_boron['Share in %'] = round(df_boron['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_boron = countries.merge(df_boron,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_boron,
        data=merge_df_boron,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Boron Minerals (% of Global Production)",
        name="Boron Minerals Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_boron)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_boron,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_boron["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_boron.add_child(hoverText)
    m_boron.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_boron)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_boron = m_boron.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Boron Minerals"] = m_boron
#______________________________________________________________
#'Diamonds (Gem)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_diamond_gem = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_diamond_gem)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_diamond_gem)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_diamond_gem = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Diamonds (Gem)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_diamond_gem = df_diamond_gem[df_diamond_gem['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_diamond_gem['Share in %'] = round(df_diamond_gem['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_diamond_gem = countries.merge(df_diamond_gem,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_diamond_gem,
        data=merge_df_diamond_gem,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Diamonds (Gem) (% of Global Production)",
        name="Diamonds (Gem) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_diamond_gem)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_diamond_gem,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_diamond_gem["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_diamond_gem.add_child(hoverText)
    m_diamond_gem.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_diamond_gem)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_diamond_gem = m_diamond_gem.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Diamonds (Gem)"] = m_diamond_gem
#______________________________________________________________
#'Diamonds (Ind)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_diamond_ind = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_diamond_ind)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_diamond_ind)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_diamond_ind = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Diamonds (Ind)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_diamond_ind = df_diamond_ind[df_diamond_ind['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_diamond_ind['Share in %'] = round(df_diamond_ind['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_diamond_ind = countries.merge(df_diamond_ind,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_diamond_ind,
        data=merge_df_diamond_ind,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Diamonds (Ind) (% of Global Production)",
        name="Diamonds (Ind) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_diamond_ind)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_diamond_ind,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_diamond_ind["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_diamond_ind.add_child(hoverText)
    m_diamond_ind.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_diamond_ind)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_diamond_ind = m_diamond_ind.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Diamonds (Ind)"] = m_diamond_ind
#______________________________________________________________
#'Diatomite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_diatomite = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_diatomite)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_diatomite)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_diatomite = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Diatomite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_diatomite = df_diatomite[df_diatomite['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_diatomite['Share in %'] = round(df_diatomite['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_diatomite = countries.merge(df_diatomite,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_diatomite,
        data=merge_df_diatomite,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Diatomite (% of Global Production)",
        name="Diatomite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_diatomite)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_diatomite,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_diatomite["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_diatomite.add_child(hoverText)
    m_diatomite.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_diatomite)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_diatomite = m_diatomite.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Diatomite"] = m_diatomite

#______________________________________________________________
#'Feldspar'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_feldspar = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_feldspar)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_feldspar)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_feldspar = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Feldspar", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_feldspar = df_feldspar[df_feldspar['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_feldspar['Share in %'] = round(df_feldspar['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_feldspar = countries.merge(df_feldspar,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_feldspar,
        data=merge_df_feldspar,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Feldspar (% of Global Production)",
        name="Feldspar Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_feldspar)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_feldspar,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_feldspar["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_feldspar.add_child(hoverText)
    m_feldspar.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_feldspar)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_feldspar = m_feldspar.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Feldspar"] = m_feldspar
#______________________________________________________________
#'Fluorspar'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_fluorspar = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_fluorspar)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_fluorspar)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_fluorspar = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Fluorspar", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_fluorspar = df_fluorspar[df_fluorspar['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_fluorspar['Share in %'] = round(df_fluorspar['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_fluorspar = countries.merge(df_fluorspar,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_fluorspar,
        data=merge_df_fluorspar,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Fluorspar (% of Global Production)",
        name="Fluorspar Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_fluorspar)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_fluorspar,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_fluorspar["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_fluorspar.add_child(hoverText)
    m_fluorspar.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_fluorspar)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_fluorspar = m_fluorspar.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Fluorspar"] = m_fluorspar

#______________________________________________________________
#'Graphite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_graphite = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_graphite)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_graphite)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_graphite = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Graphite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_graphite = df_graphite[df_graphite['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_graphite['Share in %'] = round(df_graphite['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_graphite = countries.merge(df_graphite,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_graphite,
        data=merge_df_graphite,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Graphite (% of Global Production)",
        name="Graphite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_graphite)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_graphite,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_graphite["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_graphite.add_child(hoverText)
    m_graphite.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_graphite)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_graphite = m_graphite.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Graphite"] = m_graphite
#______________________________________________________________
#'Gypsum and Anhydrite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_gypsum_anhydrite = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_gypsum_anhydrite)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_gypsum_anhydrite)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_gypsum_anhydrite = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Gypsum and Anhydrite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_gypsum_anhydrite = df_gypsum_anhydrite[df_gypsum_anhydrite['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_gypsum_anhydrite['Share in %'] = round(df_gypsum_anhydrite['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_gypsum_anhydrite = countries.merge(df_gypsum_anhydrite,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_gypsum_anhydrite,
        data=merge_df_gypsum_anhydrite,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Gypsum and Anhydrite (% of Global Production)",
        name="Gypsum and Anhydrite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_gypsum_anhydrite)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_gypsum_anhydrite,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_gypsum_anhydrite["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_gypsum_anhydrite.add_child(hoverText)
    m_gypsum_anhydrite.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_gypsum_anhydrite)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_gypsum_anhydrite = m_gypsum_anhydrite.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Gypsum and Anhydrite"] = m_gypsum_anhydrite
#______________________________________________________________
#'Kaolin (China-Clay)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_kaolin = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_kaolin)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_kaolin)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_kaolin = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Kaolin (China-Clay)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_kaolin = df_kaolin[df_kaolin['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_kaolin['Share in %'] = round(df_kaolin['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_kaolin = countries.merge(df_kaolin,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_kaolin,
        data=merge_df_kaolin,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Kaolin (China-Clay) (% of Global Production)",
        name="Kaolin (China-Clay) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_kaolin)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_kaolin,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_kaolin["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_kaolin.add_child(hoverText)
    m_kaolin.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_kaolin)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_kaolin = m_kaolin.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Kaolin (China-Clay)"] = m_kaolin
#______________________________________________________________
#'Magnesite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_magnesite = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_magnesite)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_magnesite)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_magnesite = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Magnesite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_magnesite = df_magnesite[df_magnesite['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_magnesite['Share in %'] = round(df_magnesite['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_magnesite = countries.merge(df_magnesite,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_magnesite,
        data=merge_df_magnesite,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Magnesite (% of Global Production)",
        name="Magnesite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_magnesite)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_magnesite,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_magnesite["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_magnesite.add_child(hoverText)
    m_magnesite.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_magnesite)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_magnesite = m_magnesite.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Magnesite"] = m_magnesite
#______________________________________________________________
#'Perlite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_perlite = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_perlite)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_perlite)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_perlite = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Perlite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_perlite = df_perlite[df_perlite['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_perlite['Share in %'] = round(df_perlite['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_perlite = countries.merge(df_perlite,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_perlite,
        data=merge_df_perlite,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Perlite (% of Global Production)",
        name="Perlite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_perlite)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_perlite,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_perlite["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_perlite.add_child(hoverText)
    m_perlite.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_perlite)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_perlite = m_perlite.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Perlite"] = m_perlite
#______________________________________________________________
#'Phosphate Rock (P2O5)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_phosphate = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_phosphate)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_phosphate)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_phosphate = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Phosphate Rock (P2O5)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_phosphate = df_phosphate[df_phosphate['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_phosphate['Share in %'] = round(df_phosphate['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_phosphate = countries.merge(df_phosphate,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_phosphate,
        data=merge_df_phosphate,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Phosphate Rock (P2O5) (% of Global Production)",
        name="Phosphate Rock (P2O5) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_phosphate)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_phosphate,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_phosphate["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_phosphate.add_child(hoverText)
    m_phosphate.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_phosphate)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_phosphate = m_phosphate.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Phosphate Rock (P2O5)"] = m_phosphate
#______________________________________________________________
#'Potash (K2O)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_potash = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_potash)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_potash)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_potash = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Potash (K2O)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_potash = df_potash[df_potash['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_potash['Share in %'] = round(df_potash['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_potash = countries.merge(df_potash,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_potash,
        data=merge_df_potash,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Potash (K2O) (% of Global Production)",
        name="Potash (K2O) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_potash)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_potash,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_potash["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_potash.add_child(hoverText)
    m_potash.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_potash)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_potash = m_potash.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Potash (K2O)"] = m_potash
#______________________________________________________________
#'Salt (rock, brines, marine)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_salt = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_salt)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_salt)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_salt = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Salt (rock, brines, marine)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_salt = df_salt[df_salt['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_salt['Share in %'] = round(df_salt['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_salt = countries.merge(df_salt,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_salt,
        data=merge_df_salt,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Salt (rock, brines, marine) (% of Global Production)",
        name="Salt (rock, brines, marine) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_salt)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_salt,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_salt["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_salt.add_child(hoverText)
    m_salt.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_salt)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_salt = m_salt.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Salt (rock, brines, marine)"] = m_salt
#______________________________________________________________
#'Sulfur (elementar & industrial)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_sulfur = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_sulfur)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_sulfur)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_sulfur = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Sulfur (elementar & industrial)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_sulfur = df_sulfur[df_sulfur['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_sulfur['Share in %'] = round(df_sulfur['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_sulfur = countries.merge(df_sulfur,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_sulfur,
        data=merge_df_sulfur,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Sulfur (elementar & industrial) (% of Global Production)",
        name="Sulfur (elementar & industrial) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_sulfur)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_sulfur,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_sulfur["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_sulfur.add_child(hoverText)
    m_sulfur.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_sulfur)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_sulfur = m_sulfur.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Sulfur (elementar & industrial)"] = m_sulfur
#______________________________________________________________
#'Talc, Steatite & Pyrophyllite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_talc_steatite_pyro = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_talc_steatite_pyro)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_talc_steatite_pyro)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_talc_steatite_pyro = pd.read_excel("6.5.Share_of_World_Mineral_Production_2022_by_Countries.xlsx",
    sheet_name="Talc, Steatite & Pyrophyllite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_talc_steatite_pyro = df_talc_steatite_pyro[df_talc_steatite_pyro['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_talc_steatite_pyro['Share in %'] = round(df_talc_steatite_pyro['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_talc_steatite_pyro = countries.merge(df_talc_steatite_pyro,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_talc_steatite_pyro,
        data=merge_df_talc_steatite_pyro,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Talc, Steatite & Pyrophyllite (% of Global Production)",
        name="Talc, Steatite & Pyrophyllite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_talc_steatite_pyro)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_talc_steatite_pyro,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_talc_steatite_pyro["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_talc_steatite_pyro.add_child(hoverText)
    m_talc_steatite_pyro.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_talc_steatite_pyro)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_talc_steatite_pyro = m_talc_steatite_pyro.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Talc, Steatite & Pyrophyllite"] = m_talc_steatite_pyro
#______________________________________________________________
#'Vermiculite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_vermiculite = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_vermiculite)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_vermiculite)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_vermiculite = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx",
    sheet_name="Vermiculite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_vermiculite = df_vermiculite[df_vermiculite['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_vermiculite['Share in %'] = round(df_vermiculite['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_vermiculite = countries.merge(df_vermiculite,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_vermiculite,
        data=merge_df_vermiculite,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Vermiculite (% of Global Production)",
        name="Vermiculite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_vermiculite)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_vermiculite,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_vermiculite["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_vermiculite.add_child(hoverText)
    m_vermiculite.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_vermiculite)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_vermiculite = m_vermiculite.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Vermiculite"] = m_vermiculite
#______________________________________________________________
#'Zircon'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_zircon = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_zircon)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_zircon)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_zircon = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Zircon", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_zircon = df_zircon[df_zircon['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_zircon['Share in %'] = round(df_zircon['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_zircon = countries.merge(df_zircon,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_zircon,
        data=merge_df_zircon,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='YlGn',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Zircon (% of Global Production)",
        name="Zircon Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_zircon)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_zircon,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_zircon["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_zircon.add_child(hoverText)
    m_zircon.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_zircon)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_zircon = m_zircon.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Zircon"] = m_zircon


    return render_template("industrial-minerals.html", map_dict=map_dict)

#____________________________________________________________________________________________________________________________
# Mineral Fuels
# 'Steam Coal ', 'Coking Coal', 'Lignite', 'Natural Gas', 'Petroleum', 'Oil Sands (part of Petroleum)', 'Oil Shales', 'Uranium (U3O8)'
#____________________________________________________________________________________________________________________________

@app.route("/mineral-fuels")
def mineral_fuels():

#______________________________________________________________
#'Steam Coal'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_steam_coal = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_steam_coal)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_steam_coal)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_steam_coal = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Steam Coal ", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_steam_coal = df_steam_coal[df_steam_coal['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_steam_coal['Share in %'] = round(df_steam_coal['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_steam_coal = countries.merge(df_steam_coal,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_steam_coal,
        data=merge_df_steam_coal,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='RdPu',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Steam Coal (% of Global Production)",
        name="Steam Coal Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_steam_coal)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_steam_coal,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_steam_coal["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_steam_coal.add_child(hoverText)
    m_steam_coal.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_steam_coal)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_steam_coal = m_steam_coal.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Steam Coal "] = m_steam_coal


#______________________________________________________________
#'Coking Coal'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_coking_coal = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_coking_coal)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_coking_coal)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_coking_coal = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Coking Coal", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_coking_coal = df_coking_coal[df_coking_coal['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_coking_coal['Share in %'] = round(df_coking_coal['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_coking_coal = countries.merge(df_coking_coal,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_coking_coal,
        data=merge_df_coking_coal,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='RdPu',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Coking Coal (% of Global Production)",
        name="Coking Coal Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_coking_coal)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_coking_coal,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_coking_coal["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_coking_coal.add_child(hoverText)
    m_coking_coal.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_coking_coal)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_coking_coal = m_coking_coal.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Coking Coal"] = m_coking_coal
#______________________________________________________________
#'Lignite'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_lignite = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_lignite)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_lignite)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_lignite = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Lignite", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_lignite = df_lignite[df_lignite['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_lignite['Share in %'] = round(df_lignite['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_lignite = countries.merge(df_lignite,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_lignite,
        data=merge_df_lignite,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='RdPu',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Lignite (% of Global Production)",
        name="Lignite Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_lignite)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_lignite,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_lignite["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_lignite.add_child(hoverText)
    m_lignite.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_lignite)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_lignite = m_lignite.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Lignite"] = m_lignite
#______________________________________________________________
#'Natural Gas'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_natural_gas = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_natural_gas)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_natural_gas)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_natural_gas = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Natural Gas", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_natural_gas = df_natural_gas[df_natural_gas['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_natural_gas['Share in %'] = round(df_natural_gas['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_natural_gas = countries.merge(df_natural_gas,on='Country')
    # override the default unit of the spreadsheet, which is "Mio m3"
    #merge_df_natural_gas["unit"][1] = "million m<sup>3</sup>"
    merge_df_natural_gas.loc[1, "unit"] = "million m<sup>3</sup>"

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_natural_gas,
        data=merge_df_natural_gas,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='RdPu',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Natural Gas (% of Global Production)",
        name="Natural Gas Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_natural_gas)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_natural_gas,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_natural_gas["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_natural_gas.add_child(hoverText)
    m_natural_gas.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_natural_gas)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_natural_gas = m_natural_gas.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Natural Gas"] = m_natural_gas
#______________________________________________________________
#'Petroleum'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_petroleum = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_petroleum)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_petroleum)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_petroleum = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Petroleum", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_petroleum = df_petroleum[df_petroleum['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_petroleum['Share in %'] = round(df_petroleum['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_petroleum = countries.merge(df_petroleum,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_petroleum,
        data=merge_df_petroleum,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='RdPu',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Petroleum (% of Global Production)",
        name="Petroleum Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_petroleum)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_petroleum,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_petroleum["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_petroleum.add_child(hoverText)
    m_petroleum.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_petroleum)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_petroleum = m_petroleum.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Petroleum"] = m_petroleum
#______________________________________________________________
#'Oil Sands (part of Petroleum)' - set 'use_jenks=False' (Fewer than 6 entries)
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_oil_sands = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_oil_sands)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_oil_sands)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_oil_sands = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Oil Sands (part of Petroleum)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_oil_sands = df_oil_sands[df_oil_sands['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_oil_sands['Share in %'] = round(df_oil_sands['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_oil_sands = countries.merge(df_oil_sands,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_oil_sands,
        data=merge_df_oil_sands,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='RdPu',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Oil Sands (part of Petroleum) (% of Global Production)",
        name="Oil Sands (part of Petroleum) Production 2022",
        highlight=True,
        use_jenks=False,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_oil_sands)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_oil_sands,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_oil_sands["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_oil_sands.add_child(hoverText)
    m_oil_sands.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_oil_sands)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_oil_sands = m_oil_sands.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Oil Sands (part of Petroleum)"] = m_oil_sands
#______________________________________________________________
#'Oil Shales'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_oil_shales = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_oil_shales)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_oil_shales)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_oil_shales = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Oil Shales", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_oil_shales = df_oil_shales[df_oil_shales['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_oil_shales['Share in %'] = round(df_oil_shales['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_oil_shales = countries.merge(df_oil_shales,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_oil_shales,
        data=merge_df_oil_shales,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='RdPu',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Oil Shales (% of Global Production)",
        name="Oil Shales Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_oil_shales)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_oil_shales,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_oil_shales["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_oil_shales.add_child(hoverText)
    m_oil_shales.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_oil_shales)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_oil_shales = m_oil_shales.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Oil Shales"] = m_oil_shales
#______________________________________________________________
#'Uranium (U3O8)'
#______________________________________________________________
    # Initiate a basic Folium map for this mineral. Set tiles=None for LayerControl, or make tile_layer separate to set "control=False".
    m_uranium = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

    # Configure the Full-screen plugin and add it to the map for this mineral.
    plugins.Fullscreen(
        position='bottomleft',
        title='Open full-screen map',
        title_cancel='Close full-screen map',
        force_separate_button=True
    ).add_to(m_uranium)

    # add the generic basemap to the Mineral map.
    tile_layer.add_to(m_uranium)

    # read an individual excel sheet to a Pandas dataframe variable. The sheet name corresponds to the mineral name.
    df_uranium = pd.read_excel("6.5. Share_of_World_Mineral_Production_2022_by_Countries.xlsx", sheet_name="Uranium (U3O8)", skiprows=[0])

    # remove the last row of the spreadsheet that contains the total, so that it is not included in the ranking.
    df_uranium = df_uranium[df_uranium['Country'] != 'Total']

    # round the Percent figure to 2 decimal places.
    df_uranium['Share in %'] = round(df_uranium['Share in %'],2)

    # merge the Pandas and GeoPandas dataframes, connecting them using the common item 'Country'.
    merge_df_uranium = countries.merge(df_uranium,on='Country')

    # configure the colour scale (chloropleth). Connect the dataframe and add the chloropleth to the Mineral map.
    folium.Choropleth(
        geo_data=merge_df_uranium,
        data=merge_df_uranium,
        columns=['Country', wmp],
        key_on='feature.properties.Country',
        fill_color='RdPu',
        fill_opacity=1,
        line_color='black',
        line_opacity=1,
        legend_name="Uranium (U3O8) (% of Global Production)",
        name="Uranium (U3O8) Production 2022",
        highlight=True,
        use_jenks=True,
        nan_fill_opacity = 0.25,
        overlay = False,
        ).add_to(m_uranium)

    # connect the dataframe to the tooltips and define the fields that will be displayed.
    hoverText = folium.features.GeoJson(
        #geo_data=geo_json_data,
        data=merge_df_uranium,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country', 'Rank 2022', wmp, wmd_2022],
            aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df_uranium["unit"][1]}: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )

    # add the tooltip hovertext to the Mineral map, and ensure it's not behind the map.
    m_uranium.add_child(hoverText)
    m_uranium.keep_in_front(hoverText)

    # add layercontrol toggle. This will allow future production datasets to be added to the maps (user toggles which dataset they will see).
    folium.LayerControl().add_to(m_uranium)

    # get the root URL or base path of the application(?). Useful for handling routing.
    m_uranium = m_uranium.get_root()._repr_html_()
    # add the map to a list of maps
    # map_list.append(m_iron)

    # Populate the Maps Dictionary with the completed Mineral map. The 'Key' is the name of the mineral (from the Spreadsheet name), and the 'Value' is the variable containing the actual map. Jinja will refer to this dictionary for populating tabs with the appropriate map.
    map_dict["Uranium (U3O8)"] = m_uranium

    return render_template("mineral-fuels.html", map_dict=map_dict)

