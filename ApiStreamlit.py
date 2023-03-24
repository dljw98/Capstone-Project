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

def get_routes_api(orders, catchment, phleb, API_key):
    result = run_algorithm(orders, catchment, phleb, API_key)
    return result

st.title('TATA 1mg Matching Algorithm API')
st.text("")
st.text("")

tab1, tab2, tab3, tab4, tab5 = st.tabs(['Amend Data with CSV', 'Amend Data Manually', 'Delete Data', 
                                        'Get Available Timeslots', 'Get Output'])

st.text("")
st.text("")

with tab1:
    uploaded_phleb = st.file_uploader('Please upload Phlebotomist data: New Phlebotomists in your data will be added to the database, existing Phlebotomists in your data will have their database information updated', type='csv', accept_multiple_files=False)
    if uploaded_phleb is not None:
        uploaded_phleb = convert_to_df(uploaded_phleb)
        if sorted(uploaded_phleb.columns.tolist()) == get_phleb().columns.tolist():
            confirm = st.button('Confirm')
            if confirm:
                keys = get_phleb()['phleb_id'].tolist()
                for index in range(len(uploaded_phleb)):
                    phleb_id = uploaded_phleb['phleb_id'].iloc[index]
                    json = uploaded_phleb.iloc[index].to_dict()
                    if phleb_id not in keys:
                        db.child('phlebotomists').child(phleb_id).set(json)
                    else:
                        db.child("phlebotomists").child(phleb_id).update(json)

with tab2:
    
    changed_phleb = st.text_input('Please enter Phlebotomist with information to be changed', '')
    if len(changed_phleb) != 0:
        keys = get_phleb()['phleb_id'].tolist()
        if float(changed_phleb) not in keys:
            st.write('Phlebotomist is not currently registered in the database')
        else:
            st.text("")
            st.text("")
            data = db.child('phlebotomists').child(changed_phleb).get().val()
            
            col1, col2, col3, col4 = st.columns([1,1,1,1])
            
            phleb_id = col1.text_input('phleb_id', data['phleb_id'], key='phleb_id')
            shift_start = col2.text_input('Shift Start', data['shift_start'], key='shift_start')
            shift_end = col3.text_input('Shift End', data['shift_end'], key='shift_end')
            break_start = col4.text_input('Break Start', data['break_start'], key='break_start')
            
            capacity = col1.text_input('Capacity', data['capacity'], key='capacity')
            cost = col2.text_input('Cost', data['cost'], key='cost')
            expertise_artTest = col3.text_input('Expertise ART Test', data['expertise_artTest'], key='expertise_artTest')
            expertise_pathology = col4.text_input('Expertise Pathology', data['expertise_pathology'], key='expertise_pathology')
            
            expertise_vaccination = col1.text_input('Expertise Vaccination', data['expertise_vaccination'], key='expertise_vaccination')
            home_lat = col2.text_input('Home Latitude', data['home_lat'], key='home_lat')
            home_long = col3.text_input('Home Longitude', data['home_long'], key='home_long')
            service_rating = col4.text_input('Service Rating', data['service_rating'], key='service_rating')
            
            st.text("")
            st.text("")
            
            confirm = st.button('Confirm changes')
            if confirm:
                data['phleb_id'] = float(phleb_id)
                data['shift_start'] = float(shift_start)
                data['shift_end'] = float(shift_end)
                data['break_start'] = float(break_start)
                
                data['capacity'] = float(capacity)
                data['cost'] = float(cost)
                data['expertise_artTest'] = float(expertise_artTest)
                data['expertise_pathology'] = float(expertise_pathology)
                
                data['expertise_vaccination'] = float(expertise_vaccination)
                data['home_lat'] = float(home_lat)
                data['home_long'] = float(home_long)
                data['service_rating'] = float(service_rating)
                
                db.child("phlebotomists").child(changed_phleb).update(data)
                

with tab3:
    phleb_id = st.text_input('Please enter Phlebotomist ID to be deleted from Database', '')
    if len(phleb_id) != 0:
        phleb = get_phleb()
        db.child('phlebotomists').child(phleb_id).remove()

with tab4:
    col1, col2 = st.columns([1,1])
    lat = col1.text_input("Please input your latitude information", "")
    long = col2.text_input("Please input your longitude information", "")
    if (len(lat) != 0) and (len(long) != 0):
        col1_, col2_, col3_ = st.columns([1,1,1])
        vaccination = col1_.button('Vaccination', use_container_width=True)
        art = col2_.button('ART Test', use_container_width=True)
        pathology = col3_.button('Pathology', use_container_width=True)
        #API_key = st.text_input("Please enter your API Key", "", key='api_key_timewindow')
    if (len(lat) != 0) and (len(long) != 0) and ((vaccination) or (pathology) or (art)):
        st.write('success')
        order_coord = lat + ',' + long
        service_time = None
        required_expertise = []
        if vaccination:
            service_time = 12
            required_expertise.append('expertise_vaccination')
        elif pathology:
            service_time = 15
            required_expertise.append('expertise_pathology')
        else:
            service_time = 20
            required_expertise.append('expertise_artTest')
        routes = db.child('routes_placeholder').get().val()
        string_result = reverse_getVacancy_algorithm(order_coord, service_time, required_expertise, routes,
                                                    '')
        json_result = json.loads(string_result)
        df_result = pd.DataFrame.from_dict(json_result)
        st.write(service_time)
        st.write(df_result)
        
with tab5:
    orders = st.file_uploader('Please upload order data', type='csv', accept_multiple_files=False, key='upload_orders')
    API_key = st.text_input("Please enter your API Key", "", key='api_key_getoutput')

    st.text("")
    st.text("")

    st.download_button(
        label="Get Phlebotomist Data",
        data=convert_to_csv(get_phleb()),
        file_name="phleb.csv",
        mime="text/csv",
        key="phleb_download",
    )

    st.download_button(
        label="Get Catchment Data",
        data=convert_to_csv(get_catchment()),
        file_name="catchment.csv",
        mime="text/csv",
        key="catchment_download",
    )

    if (len(API_key) != 0) and (orders is not None):
        orders = convert_to_df(orders)
        st.download_button(
            label="Get Optimal Routes",
            data=get_routes_api(orders, get_catchment().iloc[:1], get_phleb(), API_key),
            file_name="routes.json",
            mime="text",
            key="routes_download",
        )
