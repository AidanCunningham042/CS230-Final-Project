"""
Name:       Aidan Cunningham 
CS230:      Section 2 
Data:       London Pubs 

Description:     
This program allows the user to choose a city in the UK and displays a map with all of the pubs in the chosen city. 
It displays a bar chart and a table of the total number of pubs in the chosen city, grouped by postal code. 
The program allows the user to choose a coordinate range and displays the percentage of pubs in the range using a pie chart.
It also lets the user search a pub's address and displays it on a map.
""" 

# import all packages globally to be used in functions
import pandas as pd
import streamlit as st
import pydeck as pdk
import numpy as np
import matplotlib.pyplot as plt

def getDF(): # function to retrieve data frame from csv file
    
    # read csv file into a data frame called df with the column names being the names list
    df = pd.read_csv("open_pubs_10000_sample.csv", names = ["FSA_ID", "Name", "Address", "Postal_Code", "Easting", "Northing", "Latitude", "Longitude", "Local_Authority"])
    
    df.replace("\\N", np.nan, inplace=True)  # replace \\N with NaN so that they can be removed using pandas
    
    df.dropna(subset=["Latitude", "Longitude"], inplace=True)  # [DA1] clean data frame by dropping NaN values from Latitude and Longitude columns
    
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors = "coerce") # convert Latitude values to numeric, if there is an error, set value to NaN
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors = "coerce") # convert Longitude values to numeric, if there is an error, set value to NaN
    
    return df

def selectArea(df): # function for user to select a neighborhood area using a select box
    
    listAreas = [] # [PY1] initialize empty list of UK areas
    
    for area in sorted(df["Local_Authority"]): # for each area in the Local_Authority column of df
        
        if area not in listAreas: # if the area is not already in listAreas
            
            listAreas.append(area) # append the area to listAreas
    
    inputArea = st.selectbox("Select an Area:", listAreas) # [ST1] create select box using listAreas
    
    return inputArea

def createPubsInAreaMap(df, inputArea): # function to list all of the pubs in a certain area
    
    selectedArea = df[df["Local_Authority"] == inputArea] # [DA2] store all pubs from df that are in inputArea
    
    # calculate average latitude and longitude of pubs so that map center can be set to those values
    mapCenterLat = selectedArea["Latitude"].mean() # [DA3]
    mapCenterLong = selectedArea["Longitude"].mean() 

    layer1 = pdk.Layer( # set conditions for scatter plot layer to be displayed on map
                        
        "ScatterplotLayer", # identifies the layer as a scatter plot layer
        
        data = selectedArea, # data for the dots is from selectedArea so that it only shows points in the specified area
        
        get_position = '[Longitude, Latitude]', # the position of the dots [x,y] is [Longitude,Latitude]
        
        get_radius = 150, # radius of the dots
        
        get_color = [0, 150, 255],  # Set color of map dots to blue
        
        pickable = True # have map dots be pickable so that the tool_tip displays when hovering over them
    )

    tool_tip = { # tool tip to be displayed when user hovers over map dots
        
        #format tool tip using HTML to display Pub Name, Address, FSA ID, Postal Code       
        "html": "Pub Name: <b>{Name}</b></br>"
    
                "Address: <b>{Address}</b></br>"
                
                "FSA ID: <b>{FSA_ID}</b></br>"
                
                "Postal Code: <b>{Postal_Code}</b></br>",
        
        #format tool tip using CSS to have the background color of the tool tip be steelblue and the font color be white        
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    pubMap = pdk.Deck(
        
        map_style = "light",
        
        initial_view_state = pdk.ViewState(latitude = mapCenterLat, longitude = mapCenterLong, zoom = 10), # set map center equal to previous averages and map zoom to 10
        
        layers = [layer1], # display scatter plot layer on map
       
        tooltip = tool_tip # display tool tip on map
    )

    st.pydeck_chart(pubMap) # [VIZ1] display map

def listPubsInArea(df , inputArea): # function to display a data frame of pub information sorted by area
    
    selectedArea = df[df["Local_Authority"] == inputArea] # select entries from data frame where Local_Authority is equal to inputArea
    
    dfPubs = selectedArea[["Name" , "Address" , "Postal_Code" , "Local_Authority"]] # display the Name, Address, Postal Code, and Local Authority of the selected entries

    st.write(dfPubs)

def coordinateRange(): # function to have user select a coordinate range using two double ended sliders
    
    #have user enter an Easting and Northing coordinate range using sliders
    eastingCoordRange = st.slider(label = "Select an Easting Coordinate Range: " , min_value = 0 , max_value = 700000 , step = 10000 , value = (100000 , 550000)) # [ST2]
    
    northingCoordRange = st.slider(label = "Select a Northing Coordinate Range: " , min_value = 0 , max_value = 1200000 , step = 10000 , value = (300000 , 900000)) # [ST3]
    
    return eastingCoordRange , northingCoordRange # [PY2]



def pubsInRangePieChart(df , eastingCoordRange , northingCoordRange): # function to create a pie chart based on the coordinate ranges enter by the user
    
    # get minimum and maximum coordinates from coordinate ranges
    minEasting , maxEasting = eastingCoordRange
    minNorthing , maxNorthing = northingCoordRange
    
    # filter df to only have pubs that are in the coordinate range and store in filteredPubs
    filteredPubs = df[(df["Easting"] >= minEasting) & (df["Easting"] <= maxEasting) & (df["Northing"] >= minNorthing) & (df["Northing"] <= maxNorthing)] # [DA4]
    
    # calculate total number of pubs
    totalPubs = len(df)
    
    # calculate number of pubs outside of the coordinate range
    pubsOutsideRange = totalPubs - len(filteredPubs)
    
    # Create a pie chart (Used https://www.geeksforgeeks.org/matplotlib-axes-axes-pie-in-python/ for help changing the pie chart axes)
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create pie chart of the number of pubs inside the coordinate range compared to pubs outside
    ax.pie([len(filteredPubs), pubsOutsideRange], labels=["Pubs In Coordinates", "Pubs Outside Coordinates"], autopct='%1.1f%%', startangle=90)
    
    ax.set_title("Pie Chart of Pubs Inside Coordinates") # Title of pie chart
    
    ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle
    
    st.pyplot(fig) # [VIZ2] Display pie chart

def numPubsBarChart(df , inputArea): # function to create a bar chart that displays the number of pubs in an area
    
    dfSpecifiedArea = df[df['Local_Authority'] == inputArea] # get only pubs that have Local_Authority equal to inputArea
    
    dfSpecifiedArea["Postal_Code"] = dfSpecifiedArea["Postal_Code"].str[:4] # slice Postal_Code so that it is only the first 4 characters

    # Group data by Postal Code and create a data frame with Name and Pub Count columns
    pubsByPostalCode = dfSpecifiedArea.groupby('Postal_Code')['Name'].count().reset_index() # Use reset_index() to reset the data frames indices back to 0, 1, 2, etc.
    pubsByPostalCode.rename(columns={'Name': 'Pub Count'}, inplace=True) # replace columns to be Name and Pub Count
    
    # Create a bar chart
    fig = plt.figure(figsize=(10, 6))
    
    plt.bar(pubsByPostalCode['Postal_Code'], pubsByPostalCode['Pub Count']) # set x-values equal to the postal codes and y-values equal to the pub counts
    
    plt.xlabel("Postal Code") # label x-axis as Postal Code
    
    plt.ylabel("Number of Pubs") # label y-axis as Number of Pubs
    
    plt.title(f"Pubs in {inputArea} by Postal Code") # title the chart as Pubs in the inputed area by Postal Code
    
    plt.xticks(rotation=90) # rotate x-axis labels so that they do not overlap
    
    st.pyplot(fig) # [VIZ3] display the bar chart



def findPubByAddress(df): # function to have user enter a pub's address and display that pub on a map
    
    listAddresses = [] # initialize listAddresses
    
    listAddresses = [address for address in df["Address"] if address not in listAddresses] # [PY3] go through each address in df and if it is not in listAddresses add it
    
    listAddresses = sorted(listAddresses) # sort listAddresses so that it is alphabetical (addresses that start with numbers will be first)
    
    pubAddress = st.selectbox("Enter the Address of a Pub: " , listAddresses) # display select box for user to enter addresses using listAddresses as the options # [ST4]
    
    selectedPub = df[df["Address"] == pubAddress] # store the information of the selected pub by addresses in data frame selectedPub
    
    # store the pubs latitude and longitude in two variables so that the center of the map can be set to those coordinates
    mapCenterLat = selectedPub["Latitude"].iloc[0] 
    mapCenterLong = selectedPub["Longitude"].iloc[0]

    layer1 = pdk.Layer(
        
        "ScatterplotLayer",
        
        data = selectedPub, # use data frame selectedPub as data for the map
        
        get_position = "[Longitude, Latitude]", # position of the dot is the longitude and latitude
        
        get_radius = 100, # dot radius is 100
        
        get_color = [255, 0, 0],  # Set color of map dot to blue
        
        pickable = True
    )

    tool_tip = {
        
        # Display the pub's Name, Address, and City when the user hovers over the dot
        "html": "Pub Name: <b>{Name}</b></br>"
    
                "Address: <b>{Address}</b></br>"
                
                "City: <b>{Local_Authority}</b></br>",
                
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    pubByAddressMap = pdk.Deck(
        
        map_style = "light",
        
        initial_view_state = pdk.ViewState(latitude = mapCenterLat, longitude = mapCenterLong, zoom = 12), # set map zoom equal to 12
        
        layers = [layer1],
        
        tooltip = tool_tip
    )

    st.pydeck_chart(pubByAddressMap) # [VIZ4] display map
    
    
def main():
    
    st.title("UK Pub Locations") # title of web page
    
    st.image("London_Pub_Image.jpg") # display image of a pub in London
    
    df = getDF() # store data frame in df
    
    st.header(f":blue[Map of Pub Locations by Neighborhood]" , divider = "blue") # header with blue text and underlined for map section
    
    inputArea = selectArea(df)
    
    createPubsInAreaMap(df, inputArea)
    
    listPubsInArea(df, inputArea)
    
    st.header(f":blue[Number of Pubs in {inputArea}]" , divider = "blue") # header for bar chart section
    
    numPubsBarChart(df, inputArea)
    
    st.header(":blue[Percentage of Pubs in Coordinate Area]" , divider = "blue") # header for pie chart section

    eastingCoordRange , northingCoordRange = coordinateRange()
    
    pubsInRangePieChart(df, eastingCoordRange, northingCoordRange)
    
    st.header(":blue[Find a Pub by Address]" , divider = "blue") # header for finding a pub by address and displaying on the map
    
    findPubByAddress(df)
    
main()
