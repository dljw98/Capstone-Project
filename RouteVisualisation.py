import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

import geopandas as gpd
from shapely.geometry import Point, LineString
import plotly_express as px
import networkx as nx
import osmnx as ox
import folium
import folium.plugins as plugins

def to_time(time_window):
    """
    Converts a time window into a presentable string format

    Arguments:
        time_window: list containing 2 elements - start and end of time window in minutes passed since 12am
    """
    start = divmod(time_window[0], 60) # returns (hour, minutes)
    end = divmod(time_window[1], 60)
    
    return(f"{start[0]:02d}:{start[1]:02d}  - {end[0]:02d}:{end[1]:02d}")

def create_popup(text):
    iframe = folium.IFrame(text)
    popup = folium.Popup(iframe,
                        min_width=300,
                        max_width=300)
    return popup

def visualise_routes(json_result, polygon):
    """
    Visualise realistic routes for each phlebotomist and saves them to a .html file

    Arguments:
        json_result: json output from Run Algorithm.ipynb (matching.json)
        polygon: geojson polygon provided by TATA
        addressess_list: list of addressess compiled - refer to Run Algorithm.ipynb 
    """
    locations = json_result['Metadata']['Locations']

    # create base graph
    x_min, y_min, x_max, y_max = polygon.total_bounds
    G = ox.graph_from_bbox(north=y_max, south=y_min, east=x_max, west=x_min, network_type='drive')

    # colour and opacity of routes and markers
    colours = [
        'blue',
        'gray',
        'orange',
        'darkblue',
        'lightblue',
        'purple',
        'darkpurple',
        'pink',
        'cadetblue',
        'lightgray',
        'black',
        'darkgreen'
    ]

    colours_cycle = cycle(colours)

    alpha = 0.5

    # catchment area 
    catchment_popup_text = "Catchment Area"
    catchment_coords = locations[0]['Coordinate'].split(',')
    catchment_lat, catchment_long = float(catchment_coords[0]), float(catchment_coords[1])

    for j in range(len(json_result['Routes'])):
        phleb = json_result['Routes'][j]
        phleb_id = phleb['Phlebotomist Index']
        print(f"Creating route travelled by Phlebotomist ID #{phleb_id}")

        locations_sequence = phleb['Locations Sequence']
        print(locations_sequence)
        last_order_index = len(locations_sequence) - 2

        start_times = phleb['Start Times Sequence']
        end_times = phleb['End Times Sequence']

        colour = next(colours_cycle)

        sequence_counter = 0
        for i in range(len(locations_sequence)-1):

            start = locations[locations_sequence[i]]['Coordinate'].split(',')
            end = locations[locations_sequence[i+1]]['Coordinate'].split(',')
            start_lat, start_long = float(start[0]), float(start[1])
            end_lat, end_long = float(end[0]), float(end[1])
            print(f"Coords: {start_lat},{start_long}")

            start_node = ox.distance.nearest_nodes(G, Y=start_lat, X=start_long)
            end_node = ox.distance.nearest_nodes(G, Y=end_lat, X=end_long)
            print("Node: ", start_node, end_node)

            route = nx.shortest_path(G, start_node, end_node, weight='distance')
            print("Route: ",route)

            arrival_time = f"Arrival:{to_time(start_times[i])}"
            departure_time = f"Departure:{to_time(end_times[i])}"

            location_number = locations_sequence[i]
            order_id = json_result['Metadata']['Locations'][location_number]['Order Id']

            if start_node == end_node:
                print("Warning: Start and end node are the same")

            # plotting route from phlebotomist home
            if i == 0:
                print(f"Drawing Phlebotomist ID #{phleb_id}'s route...")
                if j == 0:
                    print("Map created")
                    # create map if map has not been created
                    route_map = ox.plot_route_folium(G, route, route_linewidth=6, node_size=0, color=colour, opacity=alpha)
                elif start_node != end_node: 
                    route_map = ox.plot_route_folium(G, route, route_linewidth=6, node_size=0, route_map=route_map, color=colour, opacity=alpha)
                # create markers
                start_marker = folium.Marker(
                    location=(start_lat, start_long), # only accepts coords in tuple form
                    popup=create_popup(f"Phlebotomist #{phleb_id} Home<br>{departure_time}"),
                    icon = folium.Icon(color='green', icon='house', prefix='fa')
                )
                start_marker.add_to(route_map)
            else:
                # if map has been created, add onto route map
                if start_node != end_node:
                    route_map = ox.plot_route_folium(G, route, route_linewidth=6, node_size=0, route_map=route_map, color=colour, opacity=alpha)
                start_marker = folium.Marker(
                    location=(start_lat, start_long), # only accepts coords in tuple form
                    popup=create_popup(f'Order #{order_id}<br>{arrival_time}<br>{departure_time}'),
                    # icon = folium.Icon(color=colour, icon='user', prefix='fa'),
                    icon = plugins.BeautifyIcon(
                            icon="arrow-down", icon_shape="marker",
                            number=sequence_counter,
                            border_color=colour,
                            background_color=colour,
                            text_color='white'
                    )
                )
                start_marker.add_to(route_map)
                sequence_counter += 1

                if i == last_order_index:
                    print(f"Phlebotomist ID #{phleb_id}'s route has been drawn")
                    catchment_popup_text += f"<br>Phlebotomist #{phleb_id} Arrival:{to_time(start_times[i+1])}"
                    print(f"Last order for Phlebotomist ID #{phleb_id} fulfilled")
                    # save map at the end of last order
                    print(f"Route travelled by Phlebotomist ID #{phleb_id} saved")
            
    catchment_marker = folium.Marker(
                    location=(catchment_lat, catchment_long), # only accepts coords in tuple form
                    popup=create_popup(f'{catchment_popup_text}'),
                    icon = folium.Icon(color='red', icon='vial', prefix='fa')
                )
    catchment_marker.add_to(route_map)
    route_map.save(f"Route Visualisations/Route.html")

####################################################################################################

def create_grid_df(size, selected_dots):
    grid = pd.DataFrame()
    size += 1
    grid['x'] = np.repeat(np.arange(0, size), size)
    grid['y'] = np.tile(np.arange(0, size), size)
    grid['Location'] = 0

    for location_type, coords_list in selected_dots.items():
        for coord in coords_list:
            grid.loc[(grid['x'] == coord[0]) & (grid['y'] == coord[1]), 'Location'] = location_type
            print(location_type)

    print(grid)
    return grid

def create_addressess_list(selected_dots):
    pass

def visualise_boxdot():
    pass


# for testing purposes
if __name__ == "__main__":
    # test visualise_routes()
    with open("Route Visualisations/matching1.json", "r") as read_file:
        json_result = json.load(read_file)
    json_result = json.loads(json_result)

    polygon = gpd.read_file("Simulation\Gurugram_sample_Polygon.geojson")
    
    visualise_routes(json_result, polygon)

    # # test visualise_boxdot
    # scenario_1 = {
    #     "Customer Orders":[(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(1,4),(3,3),(3,4),(4,3),(4,4),(5,3),(5,4)],
    #     "Phlebotomist Home":[(1,1),(5,5)],
    #     "Catchment Area":[(2,3)]
    # }

    # create_grid_df(5, scenario_1)
