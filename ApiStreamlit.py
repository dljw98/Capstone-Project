### pip install streamlit before running this file ###

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import requests
import json
import urllib
import urllib.request        
from flask import Flask, request, render_template
from flask_restful import Resource, Api, reqparse
from marshmallow import Schema, fields
import re
import xlsxwriter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import streamlit as st
from FeatureEngineering import create_time_matrix
from MatchingAlgorithm import run_algorithm, reverse_getVacancy_algorithm
from ApiFirebase import upload_phleb
import copy
import firebase_admin
from firebase_admin import firestore
import pyrebase

config = {
    "apiKey": "", # Firebase API key
    "authDomain": "bt4103-capstone-e15b0.firebaseapp.com",
    "projectId": "bt4103-capstone-e15b0",
    "storageBucket": "bt4103-capstone-e15b0.appspot.com",
    "messagingSenderId": "534528759196",
    "appId": "1:534528759196:web:990717960c3b7a0e02e459",
    "measurementId": "G-EN6GENJ15Y",
    "databaseURL": "https://bt4103-capstone-e15b0-default-rtdb.asia-southeast1.firebasedatabase.app/" # additional parameter: required
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

def get_catchment():
    all_data = db.child("catchment").get()
    keys = []
    for data in all_data:
        keys.append(data.key())

    dfs = []    
    for key in keys:
        data = db.child('catchment').child(key).get().val()
        data = pd.DataFrame.from_dict([data])
        dfs.append(data)

    catchment = dfs[0]
    for df in dfs[1:]:
        catchment = pd.concat([catchment, df], axis=0)

    catchment.reset_index(inplace=True, drop=True)
    return catchment

def get_phleb():
    all_data = db.child("phlebotomists").get()
    keys = []
    for data in all_data:
        keys.append(data.key())
    keys_copy = copy.deepcopy(keys)

    dfs = []    
    for index in range(len(keys_copy)):
        key = keys_copy[index]
        data = db.child('phlebotomists').child(key).get().val()
        if (data == None):
            keys.remove(key)
        else:
            data = pd.DataFrame.from_dict([data])
            dfs.append(data)

    phleb = dfs[0]
    for df in dfs[1:]:
        phleb = pd.concat([phleb, df], axis=0)

    phleb.reset_index(drop=True, inplace=True)
    phleb.index.name=None
    return phleb

def convert_to_csv(df):
    df = df.to_csv(index=False)
    return df

def convert_to_df(csv):
    df = pd.read_csv(csv)
    return df

def get_routes_api(orders, catchment, phleb, API_key, isMultiEnds):
    result = requests.get("http://127.0.0.1:8000/routes", 
                          params={'orders':orders, 'catchment':catchment, 'phleb':phleb, 'API_key':API_key, 'isMultiEnds':isMultiEnds})
    return result.json()['route']

st.title('TATA 1mg Matching Algorithm API')
st.text("")
st.text("")

tab1, tab2, tab3 = st.tabs(['Get Available Timeslots', 'Get Output', 'Get Output (3 CSV)'])

st.text("")
st.text("")

with tab1:
    col1, col2 = st.columns([1,1])
    lat = col1.text_input("Please input your latitude information", "")
    long = col2.text_input("Please input your longitude information", "")
    routes = st.file_uploader('Please upload routes data', type='json', accept_multiple_files=False, key='upload_routes_1')
    if (len(lat) != 0) and (len(long) != 0) and (routes is not None):
        routes = json.load(routes)
        routes = json.dumps(routes)
        API_key = st.text_input("Please enter your API Key", "", key='api_key_timewindow')
        col1_, col2_, col3_ = st.columns([1,1,1])
        premium = col1_.button('Premium', use_container_width=True)
        regular = col2_.button('Regular', use_container_width=True)
        special = col3_.button('Special', use_container_width=True)
        if (len(lat) != 0) and (len(long) != 0) and (len(API_key) != 0) and ((premium) or (regular) or (special)):
            order_coord = lat + ',' + long
            service_time = None
            required_expertise = []
            if premium:
                service_time = 3
                required_expertise.append('expertise_premium')
            elif regular:
                service_time = 2
                required_expertise.append('expertise_regular')
            else:
                service_time = 4
                required_expertise.append('expertise_special')
            string_result = reverse_getVacancy_algorithm(order_coord, service_time, required_expertise, routes, API_key)
            json_result = json.loads(string_result)
            df_result = pd.DataFrame.from_dict(json_result)
            st.write(df_result)
        
with tab2:
    orders = st.file_uploader('Please upload order data', type='csv', accept_multiple_files=False, key='upload_orders')
    API_key = st.text_input("Please enter your API Key", "", key='api_key_getoutput')

    st.text("")
    st.text("")

    if (len(API_key) != 0) and (orders is not None):
        API_key = API_key
        
        orders_df = pd.read_csv(orders)
        orders = orders_df.to_csv()
        
        catchment = get_catchment()
        catchment = catchment.to_csv()
        
        phleb = get_phleb()
        phleb = phleb.to_csv()
        
        st.download_button(
            label="Get Optimal Routes",
            data=get_routes_api(orders, catchment, phleb, API_key, False),
            file_name="routes.json",
            mime="text",
            key="routes_download",
        )
        
with tab3:
    col1_3, col2_3, col3_3 = st.columns([1,1,1])
    phleb = col1_3.file_uploader('Please upload phlebotomist data', type='csv', accept_multiple_files=False, key='upload_phleb_3')
    catchment = col2_3.file_uploader('Please upload catchment data', type='csv', accept_multiple_files=False, key='upload_catchment_3')
    orders = col3_3.file_uploader('Please upload order data', type='csv', accept_multiple_files=False, key='upload_orders_3')
    API_key = st.text_input("Please enter your API Key", "", key='api_key_getoutput_3')
    
    if (len(API_key) != 0) and (phleb is not None) and (catchment is not None) and (orders is not None):
        
        orders_df = pd.read_csv(orders)
        orders = orders_df.to_csv()
        
        catchment_df = pd.read_csv(catchment)
        catchment = catchment_df.to_csv()
        
        phleb_df = pd.read_csv(phleb)
        phleb = phleb_df.to_csv()
        
        st.download_button(
            label="Get Optimal Routes",
            data=get_routes_api(orders, catchment, phleb, API_key, False),
            file_name="routes.json",
            mime="text",
            key="routes_download_3",
        )