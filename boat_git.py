#This is mainly meant to be run in a jupyter notebook

"""
             |    |    |                 
             )_)  )_)  )_)              
            )___))___))___)\            
           )____)____)_____)\\
         _____|____|____|____\\\__
---------\                   /---------
  ^^^^^ ^^^^^^^^^^^^^^^^^^^^^
    ^^^^      ^^^^     ^^^    ^^
        ^^^^      ^^^
What is going on with port 7?
"""

#Test to make sure pd.to_datetime is working
"""
import pandas as pd
df = pd.read_csv('../voyages.csv')
pd.to_datetime(df['begin_date'])
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas 
from haversine import haversine, Unit
import plotly.express as px
import geopandas as gpd
import plotly.graph_objects as go

ports = pd.read_csv('Desktop/trackboat/ports.csv')  
tracking = pd.read_csv('Desktop/trackboat/tracking.csv') 
ports.rename({"lat": "latitude", 
           "long": "longitude"}, 
          axis = "columns", inplace = True)

tracking.rename({"lat": "latitude", 
           "long": "longitude"}, 
          axis = "columns", inplace = True)

#ports
#tracking #if we want to print to notebook

#blank map we're using
#countries = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
#countries.plot(color="lightgrey")

geo_df = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))

#px.set_mapbox_access_token(open(".mapbox_token").read())
px.set_mapbox_access_token("pk.eyJ1IjoidG9vc29vbiIsImEiOiJja2JrYWwydWswM3VnMnhvNmNjaXFsazdoIn0.nqcTxoxYqCKJN4jjVG51hA")

"""
#if we just want to map the ports
fig = px.scatter_geo(ports,
                    lat=ports.latitude,
                    lon=ports.longitude,
                    hover_name="port")


fig.show()
"""
#haversine is the distance calc method we're using
def find_haversine(travel_lat,travel_long, port_lat,port_long):
    travel_point = (travel_lat, travel_long)
    port_point = (port_lat, port_long)
    return haversine(travel_point, port_point, unit=Unit.MILES)

#finds the closest port for every boat location
def closest_port(x,y):
    ports['test_distance'] = ports.apply(lambda row : find_haversine(x, y, row['latitude'], row['longitude'] ), axis = 1)
    ports.sort_values(by=['test_distance'])
    
    #short_port = ports.sort_values(by=['test_distance'])
    short_port2 = ports[ports.test_distance == ports.test_distance.min()]
    
    closest_port = short_port2['port'].iloc[0]
    closest_port_distance_mi = short_port2['test_distance'].iloc[0]
    return closest_port, closest_port_distance_mi

#The Strait of Malacca has ports very close the narrow passageway
#I want to treat those differently so we only count those that come to a complete stop (instead of slow)
def is_MACC_Straight(nearest_port):
    MACC_Straight_Ports = [168,115,54]
    if nearest_port in MACC_Straight_Ports:
        return "Yes"
    else:
        return "No"

#some boats were stopping too far away from port lat.long location to trigger my methods
def is_inland_port(inland_port):
    inland_ports = [34,38]
    if inland_port in inland_ports:
        return "Yes"
    else:
        return "No"

#Don't steal my token please!
px.set_mapbox_access_token("pk.eyJ1IjoidG9vc29vbiIsImEiOiJja2JrYWwydWswM3VnMnhvNmNjaXFsazdoIn0.nqcTxoxYqCKJN4jjVG51hA")

current_vessel = 1 #this is whatever vessel we're tracking (can be looped or individual)
track_boat = tracking.loc[tracking['vessel'] == current_vessel ]
track_boat = track_boat.loc[ (track_boat['datetime'] >= '2019-01-01') & (track_boat['datetime'] <= '2019-12-31')]

#mapping the ports
fig = px.scatter_geo(ports,
                    lat=ports.latitude,
                    lon=ports.longitude,
                    hover_name="port",
                    #color="port"
                    color_discrete_sequence=['#ff0000'],
                    text=ports["port"])

#mapping the movements
fig2 = px.scatter_geo(track_boat,
                    lat=track_boat.latitude,
                    lon=track_boat.longitude,
                    hover_data = [track_boat.speed],
                    hover_name="datetime")


fig.update_layout(
    autosize=False,
    width=2000,
    height=1000
)

ig.add_trace(fig2.data[0]) # adds the line trace to the first figure

fig.show()

#appling the methods to the dataframe
track_boat['nearest_port'] =  track_boat.apply(lambda row : closest_port(row['latitude'], row['longitude'] )[0], axis = 1) 
track_boat['port_distance_mi'] =  track_boat.apply(lambda row : closest_port(row['latitude'], row['longitude'] )[1], axis = 1)
track_boat['straigh_port'] = track_boat.apply(lambda row : is_MACC_Straight(row['nearest_port']), axis = 1)
track_boat['inland_port'] = track_boat.apply(lambda row : is_inland_port(row['nearest_port']), axis = 1)

track_boat = track_boat.sort_values(by=['datetime'])
pd.set_option('display.max_rows', 4500)
track_boat = track_boat.loc[ track_boat['port_distance_mi'] <= 20]

def highlight(val):
    yellow = 'background-color: green' if val < 5 else ''
    return yellow
def highlight_binary(val):
    yellow = 'background-color: green' 
    if val == 'yes': 
        return yellow

track_boat = track_boat.reset_index(drop=True)
track_boat_styled = track_boat.style.applymap(highlight, subset=pd.IndexSlice[:, ['port_distance_mi', 'speed']])
#track_boat = track_boat.style.applymap(highlight_binary, subset=pd.IndexSlice[:, ['straigh_port', 'inland_port']])

#can uncomment the below for a more detailed view 
#track_boat_styled


###########################
"""ABOVE IS JUST EXPLORATORY!
    AGGREGATION STUFF IS BELOW

            ,'"       "-._
        ,'              "-._ _._
        ;              __,-'/   |
       ;|           ,-' _,'"'._,.
       |:            _,'      |\ `.
       : \       _,-'         | \  `.
        \ \   ,-'             |  \   
         \ '.         .-.     |       
          \  \         "      |        :
           `. `.              |        |
             `. "-._          |        ;
             / |`._ `-._      L       /
            /  | \ `._   "-.___    _,'
           /   |  \_.-"-.___   
           \   :            /
            `._\_       __.'_
       __,--''_ ' "--'''' \_  `-._
 __,--'     .' /_  |   __. `-._   `-._
<            `.  `-.-''  __,-'     _,-'
 `.            `.   _,-'"      _,-'
   `.            ''"       _,-'
     `.                _,-'
       `.          _,-'
         `.   __,'"
           `'"

"""
##########################


#We're going to aggregate it below!
pd.set_option('display.width', 1000)
collection = [0]
arrival_collection = []
departure_collection = []

#I group everything together by "Sequential Nearest Port"
#This is to avoid doublecounting as boats are starting and stopping near the ports
for k, v in track_boat.groupby((track_boat['nearest_port'].shift() != track_boat['nearest_port']).cumsum()):
    arrived = []
    departure = []
    port = str(v['nearest_port'].min())
    if v['speed'].min() >3 and v['port_distance_mi'].min() > 10:
        pass
    elif v['speed'].min() >= 3.4:
        pass
    elif v['straigh_port'].min() == 'Yes':
        pass
    #elif v['speed'].min() >= 0.9 and v['nearest_port'].min() == 7:
    #    pass
    #elif v['nearest_port'].min() in [72] and v['port_distance_mi'].min() > 5:
    #    pass
    elif len(v.index) <3:
        pass
        
    else:
        for i, j in v.iterrows():
            #2.7 is just my best guesstimate
            if j['speed'] <= 2.7 and j['port_distance_mi'] < 12.5 and j['straigh_port'] == "No":
                arrived.append(j['datetime'])
            #We boost the distance for those inland ports
            elif j['speed'] <= 2.7 and j['port_distance_mi'] < 20 and j['straigh_port'] == "No" and j['inland_port'] == "Yes":
                arrived.append(j['datetime'])
            #hardcoded this one because it was breaking my script
            elif j['speed'] <= 1.0 and j['port_distance_mi'] < 20 and j['nearest_port'] in [7]:
                arrived.append(j['datetime'])
            if len(arrived) == 0:
                pass
            else:
                if j['speed'] > 2.7 and j['port_distance_mi'] > 1:
                    departure.append(j['datetime'])
        if len(departure) == 0:
                    #departure.append(v['datetime'].iloc[-1])
                departure.append(v['datetime'].iloc[-1])
                    
          
        #You can view all the groups if you'd like
         """ 
        print(f'[group {k}]')            
        print(v)
        print("port:" + port)
        print("arrived: " + arrived[0])
        print("departure: " + departure[0])
         """ 
        collection.append(["arrived", port, arrived[0]])
        collection.append(["departure", port, departure[0]])
        arrival_collection.append(dict({'arrp': "arrived", 'end_port_id': port, 'end_date': arrived[0] }))
        departure_collection.append(dict({'arrp': "departure", 'begin_port_id': port, 'begin_date': departure[0] }))
        #print("")
        
                        
#Have to do this for formatting (I think)
del arrival_collection[0]
del departure_collection[-1]

depart_counter = 0
for x in departure_collection:
    x["count"] = depart_counter
    depart_counter = depart_counter +1

arrival_counter = 0
for x in arrival_collection:
    x["count"] = arrival_counter
    arrival_counter = arrival_counter +1


dep_df = pd.DataFrame.from_dict(departure_collection)
arr_df = pd.DataFrame.from_dict(arrival_collection)

#I keep the arrivals and deps seperate and then merge it for formatting at the end
xxx = dep_df.merge(arr_df, how='left', on='count')
xxx = xxx[['begin_date', 'end_date', 'begin_port_id', 'end_port_id']]

#This is our final answer that we write to csv (or jupyter notebook)
xxx