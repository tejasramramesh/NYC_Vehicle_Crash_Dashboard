import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_PATH = (
"/Users/tejasramramesh/Documents/NYC_Vehicle_Crashes/Motor_Vehicle_Collisions_-_Crashes.csv"
)


st.title("Streamlit NYC Vehicle Collision Dashboard")
st.markdown(" StreamLit dashboard for NYC Vehicle Collision, it can help us analyse and monitor the car crashes 🗽🚗💥")

@st.cache(persist = True)
def load_data(nrows):
    data = pd.read_csv(DATA_PATH,nrows = nrows, parse_dates = [['CRASH DATE','CRASH TIME']])
    data.dropna(subset = ['LATITUDE','LONGITUDE'],inplace = True) #cannot have null values in these two columns as we will use map visualization
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={"crash date_crash time":"date/time"},inplace = True)
    data.columns =[column.replace(" ", "_") for column in data.columns] #data.query method does not work with spaces hence we do this
    return data
def data_clean(data):
    #data = pd.read_csv(DATA_PATH,nrows = nrows, parse_dates = [['CRASH DATE','CRASH TIME']])
    data.dropna(subset = ['LATITUDE','LONGITUDE'],inplace = True) #cannot have null values in these two columns as we will use map visualization
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={"crash date_crash time":"date/time"},inplace = True)
    data.columns =[column.replace(" ", "_") for column in data.columns] #data.query method does not work with spaces hence we do this
    return data

#https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/ for column.replace action above
#USE BELOW FUNCTION IF WE ARE USING ENTIRE DATASET  BUT BUT IT INCREASES COMPUTATION
# @st.cache(persist = True)
# def max_injured_person():
#     data = pd.read_csv(DATA_PATH)
#     data.dropna(subset = ['LATITUDE','LONGITUDE'],inplace = True)
#     number = data['NUMBER OF PERSONS INJURED'].max()
#     return int(number)
all_data = pd.read_csv("/Users/tejasramramesh/Documents/NYC_Vehicle_Crashes/Motor_Vehicle_Collisions_-_Crashes.csv")
original_data = data_clean(all_data)
data = load_data(100000)


st.header("Where are most people injured in NYC ?")
injured_people = st.slider("Number of people injured in Vehicle Collision: ", 0, int( data['number_of_persons_injured'].max() ) )
st.map(data.query(" number_of_persons_injured > @injured_people ")[["latitude","longitude"]].dropna(how = "any"))


st.header("How many collisions occur at a given time of the day ?")
hour = st.slider(" Hour to look at: ", 0,23)
data = data[data['date/time'].dt.hour == hour]
st.markdown("Vehicle Collisions between %i:00 and %i:00"%(hour,(hour+1)%24))

midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
    "latitude": midpoint[0],
    "longitude": midpoint[1],
    "zoom": 11,
    "pitch": 50,

    },
    layers = [
    pdk.Layer(
    "HexagonLayer",
    data = data[['date/time','latitude','longitude']],
    get_position = ['longitude','latitude'],
    radius = 100, # radius of points in meters
    extruded = True, # gives 3d effect
    pickable = True,
    elevation_scale = 4,
    elevation_range = [0,1000],
    )
    ]
))

st.subheader("Breakdown by minute between between %i:00 and %i:00"%(hour,(hour+1)%24))
data_tile = data[
    (data['date/time'].dt.hour >= hour)& (data['date/time'].dt.hour < (hour+1))
]
histogram = np.histogram(data_tile['date/time'].dt.minute,bins = 60, range =(0, 60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':histogram})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data = ['minute','crashes'],height = 400 )
st.write(fig)

st.header("Top 5 dangerous streets by affected people")
select = st.selectbox('Type of the affected people', ['Pedestrains','Cyclists','Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("number_of_pedestrians_injured >=1 ")[["on_street_name","number_of_pedestrians_injured"]].sort_values(by=["number_of_pedestrians_injured"], ascending = False).dropna(how = "any"))
if select == 'Cyclists':
    st.write(original_data.query("number_of_cyclist_injured >=1 ")[["on_street_name","number_of_cyclist_injured"]].sort_values(by=["number_of_cyclist_injured"], ascending = False).dropna(how = "any"))
if select == 'Motorists':
    st.write(original_data.query("number_of_motorist_injured >=1 ")[["on_street_name","number_of_motorist_injured"]].sort_values(by=["number_of_motorist_injured"], ascending = False).dropna(how = "any"))



if st.checkbox("Show Raw Data ",False):

    st.subheader('Raw Data')
    st.write(data)
