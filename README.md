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

# 1.0 Data Simulation & Generation:
- Overview (how it works)
- Features

# 2.0 Feature Engineering:
The files for Feature Engineering are as follows:
- <b>FeatureEngineering.py</b>

Feature Engineering covers all the required data processing before running the Matching Algorithm. There are 2 main parts in the FeatureEngineering.py, namely Time Matrix and other Pre-processing codes. *Please note that Feature Engineering codes require the input dataframes (orders, catchments, and phlebotomists) to follow strictly the columnar formats as stipulated in the section "Data Simulation & Generation".

## 2.1 Time Matrix part:

```create_time_matrix(address_list, api)``` takes in a list of address_list, which can be generated using ```get_coordinates_list(orders_df, catchments_df, phlebs_df)``` from other Pre-processing codes, and a Google Map API key (refer to Requirements). This is the main function we will call. Output is a 2-D array consisting of the travel time between each locations in a square matrix format. This ```create_time_matrix``` is supported by the following functions:

- ```send_request(origin_addresses, dest_addresses, API_key)``` takes in a list of origin addresses, a list of destination addresses, and a Google Map API key, to actually send request to the Google Distance Matrix API and fetch the JSON result. Output is a dictionary of the fetched API result.

- ```secondsToMinutes(seconds)``` takes in a integer value of seconds, which is the default return unit of the Google Distance Matrix API, and converts it into minutes. Output is an integer value.

- ```build_time_matrix(response)``` takes in the dictionary response from ```send_request``` function and make it into the 2-D array output we see in the ```create_time_matrix``` function.

## 2.2 Pre-processing part:
Please note that all the functions under Pre-processing, except ```get_weightedRatingCost_list```, takes in 3 arguments, namely Orders dataframe, Catchments dataframe, and Phlebotomists dataframe. This is to simplify the input requirements, but not all dataframes are used within each function itself.

```get_coordinates_list(orders_df, catchments_df, phlebs_df)``` genets coordinates of locations in the format of "lat,long", which is the required format for Distance Matrix API in the ```create_time_matrix``` function. The generated coordinates are strictly in the following sequence: Catchment location/s, followed by Phlebotomists starting locations, and lastly Order locations.

```get_timeWindows_list(orders_df, catchments_df, phlebs_df)``` gets time windows of locations in the format of a tuple, consisting of start window (in minutes, e.g 6am would be 6*60 = 360) and end window (which is just 60 min + start window). The generated time windows are in the same sequence as ```get_coordinates_list```: Catchment, followed by Phlebotomists starting locations, and lastly Order locations. For catchment area, the time window is mostly trivial and set to be the working hour - e.g. 6am to 6pm (6 * 60, 18 * 60). Generally, if the orders' latest time windows are by 2pm, phlebotomists will return to the catchment area immediately after servicing the last order at 2pm regardless of catchment's end window. However, please feel free to change the end window of the catchment area to "force" phlebotomists to reach catchment area before the designated end window time. Phlebotomists' time windows are just his/her shift starting time. Orders' time windows are when the phlebotomists _must arrive_ within to service the order - note that the phlebotomists can _service_ over the time window (especially when the servicing time is long).

```get_servicingTimes_list(orders_df, catchments_df, phlebs_df)``` gets an array of the _servicing time + buffer time_ of locations. The sequence is again start with Catchment area (which is trivial and set as 0), followed by phlebotomists (trivial, set as 0), and lastly the orders'. 

```get_orderRevenues_list(orders_df, catchments_df, phlebs_df)``` gets an array of the "price"/revenue of locations. The sequence is again start with Catchment area (which is trivial and set as 1), followed by phlebotomists (trivial, set as 1), and lastly the orders'. 

```get_orderCapacities_list(orders_df, catchments_df, phlebs_df)``` gets an array of the capacities required in each locations. The sequence is again start with Catchment area (which is trivial and set as 0), followed by phlebotomists (trivial, set as 0), and lastly the orders'. Capacities required refer, for example, to the blood samples the phlebotomist need to carry from the order, represented by integer value. During the Matching Algorithm, the sum of order capacities cannot exceed phlebotomists' capacities which is obtained from ```get_phlebCapacities_list```. 

```get_phlebCapacities_list(orders_df, catchments_df, phlebs_df)``` gets an array of the maximum capacities a phlebotomist can carry in a single trip. 

```get_weightedRatingCost_list(phlebs_df, rating_weight = 1, cost_weight = 1)``` gets an array of weighted costs (salary cost + inversed service rating) of a phlebotomist. Depends on whether Service Quality is more prioritized or Cost is more prioritized, different weights can be inputted to the function to influence the weighted numbers. This array is used for Tertiary Objective function (described in section "Matching Algorithm").

```get_serviceExpertiseConstraint_list(orders_df, catchments_df, phlebs_df)``` gets an array of N-length array where N is the number of Phlebotomists 
with the relevant expertise required for the order location at the index of the array. Basically, for each order (represented by the index), there is an array consisting of phlebotomist index which can service that order. 

```get_metadata(orders_df, catchments_df, phlebs_df)``` gets a dictionary containing important information of the Orders and Phlebotomists (such as but not limited to, Order ID, Phleb ID, etc).

# 3.0 Matching Algorithm:
- Overview (how it works)
- Features

# 4.0 Prescriptive Analysis:
- Overview (how it works)
- Features

# 5.0 Scenario-based Testings on Algorithm:
- Overview (how it works)
- Features

# 6.0 Route Visualisation:
- Overview (how it works)
- Features

# 7.0 API and Proof of Concept
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


## 7.1 Before Running
Ensure that you are using version 3.20.1 of protobuf, as newer/older versions may experience compatibility issues with the packages used in the API files. This can be done in the command line using:
```
pip install protobuf=3.20.1
```

## 7.2 Running the API and Streamlit Interface
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

## 7.3 Streamlit Features
Tab 1 of the interface is titled "Amend Data with CSV", which allows you to change Phlebotomist data using a CSV file. The tab contains a widget that requires a <b> single file CSV </b> input. The file must contain the same columns as the data contained in Firebase. If the data in Firebase has the columns ```[A, B, C]```, then a file with ```[C, A, B]``` suffices, but ```[A, B, D]``` will not, and  ```[A, B]``` will not either. Once an acceptable file has been inputted, a "Confirm" button will appear. Clicking it will send the file to Firebase and update the data there. If the user inputted file contains rows with <b>new</b> Phlebotomists, Firebase will create new keys containing these information. If the user inputted file contains rows with <b>existing</b> Phlebotomists, Firebase will update those keys with the information provided in the file. Both can be done concurrently (using the same file).

Tab 2 of the interface is titled "Amend Data Manually", which allows you to change the information of any one Phlebotomist. Enter the Phlebotomist ```ID``` into the user input box and click Enter. Text containers will appear containing all the pertinent information of the Phlebotomist with that particular ID. Change the desired fields and click the "Confirm" button to immediately update the Firebase Realtime Database to reflect the changes.

Tab 3 of the interface is titled "Delete Data", which allows you to delete the information of any one Phlebotomist. Enter the Phlebotomist ```ID``` into the user input box and click Enter. Firebase will remove the Phlebotomist with that ```ID``` from the database. The changes will be reflected immediately.

Tab 4 of the interface is titled "Get Available Timeslots", which allows you to obtain an available timeslot of a Phlebotomist that can serve a customer, given the customer's latitude and longitude information. After inputting the latitude and longitude of the customer/order, you will be prompted to enter your Google Maps API key, as well as to select the type of service that the customer/order requires. Once all the above information has been provided, a dataframe containing the chosen available timeslot wil be displayed. This will show the Phlebotomist assigned to this order, as well as information about when the available timeslot will occur. The function displayed in this tab assumes that the optimal routes have already been generated for the day. If no routes are available for the day yet, there is no need to check the available time slots as there will be none.

Tab 5 of the interface is titled "Get Output", which allows you to obtain the optimal routes of the Phlebotomists in ```JSON``` format. To generate the routes, you are required to provide a CSV file containing the orders data, as well as a Google Maps API key. Once that has been provided, the Streamlit interface will call the API from the Flask application and run the Matching Algorithm. Depending on the size of the order CSV data file provided, the algorithm may take up to a couple of minutes to run. Once it has completed the algorithm, a button "Get Optimal Routes" will appear. Clicking it will download the routes generated as a JSON to your computer.
