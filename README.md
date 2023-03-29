# NUS // TATA 1mg - 2 Side Demand Supply Matching

# Project Overview:
- Introduction to Project
- Purpose

# Set Up:
- Dependencies
- How to configure the project (external APIs)

# Requirements:
- Functional
- Non-functional

# Matching Algorithm:
- Overview (how it works)
- Features

# API and Proof of Concept
## Files and Back-End
The files for our API and Proof of Concept (POC) Streamlit interface are as follows:
- <b>ApiFlask.py</b>
- <b>ApiStreamlit.py</b>

ApiFlask contains the code required for locally hosting a Flask web application. The algorithm and output generated are called from the ApiStreamlit file, and this involves calling the API hosted by launching the ApiFlask file.

ApiStreamlit contains the code for the Streamlit interface. It contains several tabs, each with different functionality, such as amending and getting data, namely Phlebotomist data, Catchment Area data, and Optimal Route data. We are using a Firebase Realtime Database as the back-end storage. This storage contains the Phlebotomist and Catchment Area data. We retrieve data from this secure database in order to run our Matching Algorithm. Below are the functions contained in the ApiStreamlit.py file and what they return

```get_catchment()``` takes no arguments and retrieves the Catchment area data from Firebase and returns a Pandas DataFrame object containing the Catchment Area data

```get_phleb()``` takes no arguments and retrieves the Phlebotomist data from Firebase and returns a Pandas DataFrame object containing the Phlebotomist data

```get_routes_api(orders, catchment, phleb, API_key, isMultiEnds)``` takes 4 arguments. 
-```orders``` refers to a <b>csv</b> file that will require the user to input. We do not store order data on Firebase as order data contains data that changes each day, and even during the day
- '''catchment``` refers to the Catchment Area data which will be retrieved from Firebase using the aforementioned ```get_catchment()``` function
- '''phleb``` refers to the Phlebotomist data which will be retrieved from Firebase using the aforementioned ```get_phleb()``` function
- ```API_key``` is ```String``` which refers to the user's Google Maps API key
- ```isMultiEnds``` is a Boolean ```True``` or ```False``` indicating to the Matching Algorithm on whether to use Multi-Ending catchments or not to generate the optimal Phlebotomist routes


## Before Running
Ensure that you are using version 3.20.1 of protobuf, as newer/older versions may experience compatibility issues with the packages used in the API files. This can be done in the command line using:
```
pip install protobuf=3.20.1
```

## Running the API and Streamlit Interface
To run and interact with the Streamlit interface, first run the ApiFlask.py file. This can be done in the command line using:
```
cd PATH_TO_FILE_DIRECTORY
python ApiFlask.py
```
This begins locally hosting the Flask web application, which will enable the Streamlit interface to call the Matching Algorithm functions from the API.
Once done, open another command prompt and type the following:
```
cd PATH_TO_FILE_DIRECTORY
python ApiStreamlit.py
```
This will launch the tabular Streamlit interface

## Streamlit Features
Tab 1 of the interface is titled "Amend Data with CSV", which allows you to change Phlebotomist data using a CSV file. The tab contains a widget that requires a <b> single file CSV </b> input. The file must contain the same columns as the data contained in Firebase. If the data in Firebase has the columns ```[A, B, C]```, then a file with ```[C, A, B]``` suffices, but ```[A, B, D]``` will not, and  ```[A, B]``` will not either. Once an acceptable file has been inputted, a "Confirm" button will appear. Clicking it will send the file to Firebase and update the data there. If the user inputted file contains rows with <b>new</b> Phlebotomists, Firebase will create new keys containing these information. If the user inputted file contains rows with <b>existing</b> Phlebotomists, Firebase will update those keys with the information provided in the file. Both can be done concurrently (using the same file).

Tab 2 of the interface is titled "Amend Data Manually", which allows you to change the information of any one Phlebotomist. Enter the Phlebotomist ```ID``` into the user input box and click Enter. Text containers will appear containing all the pertinent information of the Phlebotomist with that particular ID. Change the desired fields and click the "Confirm" button to immediately update the Firebase Realtime Database to reflect the changes.

Tab 3 of the interface is titled "Delete Data", which allows you to delete the information of any one Phlebotomist. Enter the Phlebotomist ```ID``` into the user input box and click Enter. Firebase will remove the Phlebotomist with that ```ID``` from the database. The changes will be reflected immediately.

Tab 4 of the interface is titled "Get Available Timeslots", which allows you to obtain the available timeslots of

Tab 5 of the interface is titled "Get Output", which allows you to obtain the optimal routes of the Phlebotomists in ```JSON``` format. To generate the routes, you are required to provide a CSV file containing the orders data, as well as a Google Maps API key. Once that has been provided, the Streamlit interface will call the API from the Flask application and run the Matching Algorithm. Depending on the size of the order CSV data file provided, the algorithm may take up to a couple of minutes to run. Once it has completed the algorithm, a button "Get Optimal Routes" will appear. Clicking it will download the routes generated as a JSON to your computer.
