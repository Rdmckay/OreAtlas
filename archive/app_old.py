from flask import Flask, flash, redirect, render_template, request
import folium
import pandas as pd
import geopandas as gpd
import json
import requests
from jenkspy import JenksNaturalBreaks
import numpy as np
import openpyxl

# Configure application
def create_app():
    app = Flask(__name__)
    return app

app = create_app()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/maps")
def generate_map():


    # for CartoDB Positron:
    # # tiles = "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"
    # attr = (
    # '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    # 'contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
    # )

    wmd = 'Production 2021'
    wmp = 'Share in %'

    xls = pd.ExcelFile('6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx')

    #sheets_dict = {}

    type_ferro_alloy = ['Iron (Fe)', 'Chromium (Cr2O3)', 'Cobalt', 'Manganese', 'Molybdenum', 'Nickel', 'Niobium (Nb2O5)', 'Tantalum (Ta2O5)', 'Titanium (TiO2)', 'Tungsten (W)', 'Vanadium (V)']
    type_non_ferrous = ['Aluminium', 'Antimony', 'Arsenic', 'Bauxite', 'Beryllium (conc.)', 'Bismuth', 'Cadmium', 'Copper', 'Gallium', 'Germanium', 'Indium', 'Lead', 'Lithium (Li2O)', 'Mercury', 'Rare Earths (REO)', 'Rhenium', 'Selenium', 'Tellurium', 'Tin', 'Zinc']
    type_precious = ['Gold', 'Palladium', 'Platinum', 'Rhodium', 'Silver']
    type_industrial = ['Asbestos', 'Baryte', 'Bentonite', 'Boron Minerals', 'Diamonds (Gem)', 'Diamonds (Ind)', 'Diatomite', 'Feldspar', 'Fluorspar', 'Graphite', 'Gypsum and Anhydrite', 'Kaolin (China-Clay)', 'Magnesite', 'Perlite', 'Phosphate Rock (P2O5)', 'Potash (K2O)', 'Salt (rock, brines, marine)', 'Sulfur (elementar & industrial)', 'Talc, Steatite & Pyrophyllite', 'Vermiculite', 'Zircon']
    type_fuel = ['Steam Coal ', 'Coking Coal', 'Lignite', 'Natural Gas', 'Petroleum', 'Oil Sands (part of Petroleum)', 'Oil Shales', 'Uranium (U3O8)']

    #print(xls.sheet_names)
    # for sheet_name in range(0, len(xls.sheet_names)):
        #sheets_dict[i] = f"{xls.sheet_names[i]}"
        # for sheet_name in xls.sheet_names[0,10]:
        #     type_ferro_alloy.append(sheet_name)
        # for sheet_name in xls.sheet_names[11,30]:
        #     type_non_ferrous.append(sheet_name)
        # for sheet_name in xls.sheet_names[31,35]:
        #     type_precious.append(sheet_name)
        # for sheet_name in xls.sheet_names[36,56]:
        #     type_industrial.append(sheet_name)
        # for sheet_name in xls.sheet_names[57,64]:
        #     type_fuel.append(sheet_name)


    map_dict = {}
    # for sheet in xls.sheet_names:
    #     map_dict["metal"] = sheet

    map_dict = dict.fromkeys(xls.sheet_names)
    # print(map_dict)

    tab_id_dict = {}
    tab_id_dict = dict.fromkeys(xls.sheet_names)

    href_dict = {}
    href_dict = dict.fromkeys(xls.sheet_names)


    # Create a list of all sheets in the file
    #print(xls.sheet_names)
    # ['Iron (Fe)', 'Chromium (Cr2O3)', ...]

    # to read just one sheet to dataframe:
    #df = pd.read_excel("6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx", sheet_name=xls.sheet_names[1], skiprows=[0])

    # use to create hovering tooltip text:
    countries = gpd.read_file("world-countries.json")
    #print(countries.columns.tolist())



    # sheets that have < 6 countries, thus cannot apply 'use_jenks=True' which requires 6+ classes.
    no_jenks = ['Vanadium (V)', 'Gallium', 'Germanium', 'Rhodium', 'Asbestos', 'Oil Sands (part of Petroleum)']
    map_list = []

    # set first tab-id to 0, (+ 1 for each iteration)
    i = 0

    for sheet in xls.sheet_names: #len(xls.sheet_names)
        maperino = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

        tile_layer = folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            min_zoom=2,
            max_zoom=6,
            name='darkmatter',
            control=False,
            opacity=0.5
        )
        tile_layer.add_to(maperino)

        df = pd.read_excel("6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx", sheet_name=sheet, skiprows=[0]) #f"{sheets_dict[i]}"

        # remove the last row of the spreadsheet that contains the total
        df = df[df['Country'] != 'Total']
        df['Share in %'] = round(df['Share in %'],2)

        merge_df = countries.merge(df,on='Country')

        # if the sheet has <6 items, turn off 'use_jenks=True':
        if sheet in no_jenks:
            if sheet in type_ferro_alloy:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='OrRd',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)

            elif sheet in type_non_ferrous:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='PuBuGn',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)

            elif sheet in type_precious:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='plasma',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)

            elif sheet in type_industrial:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='YlGn',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)

            elif sheet in type_fuel:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='RdPu',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)

        # if sheet has > 6 items, 'use_jenks=True'
        else:
            if sheet in type_ferro_alloy:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='OrRd',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)
            elif sheet in type_non_ferrous:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='PuBuGn',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)

            elif sheet in type_precious:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='plasma',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)

            elif sheet in type_industrial:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='YlGn',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)

            elif sheet in type_fuel:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='RdPu',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(maperino)


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

        hoverText = folium.features.GeoJson(
            #geo_data=geo_json_data,
            data=merge_df,
            style_function=style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['Country', 'Rank 2021', wmp, wmd],
                aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df["unit"][1]}: '],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
            )
        )
        maperino.add_child(hoverText)
        maperino.keep_in_front(hoverText)
        folium.LayerControl().add_to(maperino)
        maperino = maperino.get_root()._repr_html_()
        # add the map to a list of maps
        map_list.append(maperino)
        map_dict[f"{sheet}"] = maperino

        # define the tab-id used by jinja
        tab_id_dict[f"{sheet}"] = f"{i}"
        href_dict[f"{sheet}"] = f"#{i}"
        i = i + 1

    return render_template("maps.html", map_list=map_list, map_dict=map_dict, tab_id_dict=tab_id_dict, href_dict=href_dict)








#________________________________________________________________________________________________
# Attempt at making individual maps, or iterating between all ferro-alloy metal maps
#________________________________________________________________________________________________


@app.route("/map_list")
def generate_m():

    # for CartoDB Positron:
    # # tiles = "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"
    # attr = (
    # '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    # 'contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
    # )

    wmd = 'Production 2021'
    wmp = 'Share in %'

    xls = pd.ExcelFile('6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx')

    #sheets_dict = {}

    type_ferro_alloy = ['Iron (Fe)', 'Chromium (Cr2O3)', 'Cobalt', 'Manganese', 'Molybdenum', 'Nickel', 'Niobium (Nb2O5)', 'Tantalum (Ta2O5)', 'Titanium (TiO2)', 'Tungsten (W)', 'Vanadium (V)']
    type_non_ferrous = ['Aluminium', 'Antimony', 'Arsenic', 'Bauxite', 'Beryllium (conc.)', 'Bismuth', 'Cadmium', 'Copper', 'Gallium', 'Germanium', 'Indium', 'Lead', 'Lithium (Li2O)', 'Mercury', 'Rare Earths (REO)', 'Rhenium', 'Selenium', 'Tellurium', 'Tin', 'Zinc']
    type_precious = ['Gold', 'Palladium', 'Platinum', 'Rhodium', 'Silver']
    type_industrial = ['Asbestos', 'Baryte', 'Bentonite', 'Boron Minerals', 'Diamonds (Gem)', 'Diamonds (Ind)', 'Diatomite', 'Feldspar', 'Fluorspar', 'Graphite', 'Gypsum and Anhydrite', 'Kaolin (China-Clay)', 'Magnesite', 'Perlite', 'Phosphate Rock (P2O5)', 'Potash (K2O)', 'Salt (rock, brines, marine)', 'Sulfur (elementar & industrial)', 'Talc, Steatite & Pyrophyllite', 'Vermiculite', 'Zircon']
    type_fuel = ['Steam Coal ', 'Coking Coal', 'Lignite', 'Natural Gas', 'Petroleum', 'Oil Sands (part of Petroleum)', 'Oil Shales', 'Uranium (U3O8)']

    #print(xls.sheet_names)
    # for sheet_name in range(0, len(xls.sheet_names)):
        #sheets_dict[i] = f"{xls.sheet_names[i]}"
        # for sheet_name in xls.sheet_names[0,10]:
        #     type_ferro_alloy.append(sheet_name)
        # for sheet_name in xls.sheet_names[11,30]:
        #     type_non_ferrous.append(sheet_name)
        # for sheet_name in xls.sheet_names[31,35]:
        #     type_precious.append(sheet_name)
        # for sheet_name in xls.sheet_names[36,56]:
        #     type_industrial.append(sheet_name)
        # for sheet_name in xls.sheet_names[57,64]:
        #     type_fuel.append(sheet_name)


    map_dict = {}
    # for sheet in xls.sheet_names:
    #     map_dict["metal"] = sheet

    map_dict = dict.fromkeys(xls.sheet_names)
    # print(map_dict)

    tab_id_dict = {}
    tab_id_dict = dict.fromkeys(xls.sheet_names)


    # Create a list of all sheets in the file
    #print(xls.sheet_names)
    # ['Iron (Fe)', 'Chromium (Cr2O3)', ...]

    # to read just one sheet to dataframe:
    #df = pd.read_excel("6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx", sheet_name=xls.sheet_names[1], skiprows=[0])

    # use to create hovering tooltip text:
    countries = gpd.read_file("world-countries.json")
    #print(countries.columns.tolist())



    # sheets that have < 6 countries, thus cannot apply 'use_jenks=True' which requires 6+ classes.
    no_jenks = ['Vanadium (V)', 'Gallium', 'Germanium', 'Rhodium', 'Asbestos', 'Oil Sands (part of Petroleum)']
    map_list = []

    # set first tab-id to 0, (+ 1 for each iteration)
    i = 0

    for sheet in xls.sheet_names: #len(xls.sheet_names)
        m = folium.Map(location=[40,0], zoom_start=2, tiles=None, max_bounds=True) # tiles None for LayerControl, make tile_layer separate to set "control=False".

        tile_layer = folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            min_zoom=2,
            max_zoom=6,
            name='darkmatter',
            control=False,
            opacity=0.5
        )
        tile_layer.add_to(m)

        df = pd.read_excel("6.5. Share_of_World_Mineral_Production_2021_by_Countries.xlsx", sheet_name=sheet, skiprows=[0]) #f"{sheets_dict[i]}"

        # remove the last row of the spreadsheet that contains the total
        df = df[df['Country'] != 'Total']
        df['Share in %'] = round(df['Share in %'],2)

        merge_df = countries.merge(df,on='Country')

        # if the sheet has <6 items, turn off 'use_jenks=True':
        if sheet in no_jenks:
            if sheet in type_ferro_alloy:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='OrRd',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)

            elif sheet in type_non_ferrous:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='PuBuGn',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)

            elif sheet in type_precious:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='plasma',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)

            elif sheet in type_industrial:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='YlGn',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)

            elif sheet in type_fuel:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='RdPu',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    #use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)

        # if sheet has > 6 items, 'use_jenks=True'
        else:
            if sheet in type_ferro_alloy:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='OrRd',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)
            elif sheet in type_non_ferrous:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='PuBuGn',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)

            elif sheet in type_precious:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='plasma',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)

            elif sheet in type_industrial:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='YlGn',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)

            elif sheet in type_fuel:
                folium.Choropleth(
                    geo_data=merge_df,
                    data=merge_df,
                    columns=['Country', wmp],
                    key_on='feature.properties.Country',
                    fill_color='RdPu',
                    fill_opacity=1,
                    line_color='black',
                    line_opacity=1,
                    legend_name=f"{sheet} (% of Global Production)",
                    name=sheet,
                    highlight=True,
                    use_jenks=True,
                    nan_fill_opacity = 0.25,
                    overlay = False,
                    ).add_to(m)


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

        hoverText = folium.features.GeoJson(
            #geo_data=geo_json_data,
            data=merge_df,
            style_function=style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['Country', 'Rank 2021', wmp, wmd],
                aliases=['Country: ', 'Rank: ', 'Share in %: ', f'{merge_df["unit"][1]}: '],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
            )
        )
        m.add_child(hoverText)
        m.keep_in_front(hoverText)
        folium.LayerControl().add_to(m)
        m = m.get_root()._repr_html_()
        # add the map to a list of maps
        map_list.append(m)
        map_dict[f"{sheet}"] = m

        # define the tab-id used by jinja
        tab_id_dict[f"{sheet}"] = i
        i = i + 1

    return render_template("map_list.html", map_list=map_list, map_dict=map_dict, tab_id_dict=tab_id_dict)































if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000, threaded=True)
