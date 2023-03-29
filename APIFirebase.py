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
import streamlit as st # "conda install protobuf=3.20.1" (dependency package), newer versions wont work w streamlit, older versions wont work w ortools
from FeatureEngineering import create_time_matrix
from MatchingAlgorithm import run_algorithm

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

phleb = pd.read_csv("Simulated Data/phleb_data_1576.csv")
catchment = pd.read_csv("Simulated Data/catchment_data_1576.csv")

def upload_phleb(df):
    for index in range(len(df)):
        phleb_id = df['phleb_id'].iloc[index]
        json = df.iloc[index].to_dict()
        db.child('phlebotomists').child(phleb_id).set(json)

def upload_catchment(df):
    catchment_counter = 0
    for index in range(len(df)):
        json = df.iloc[index].to_dict()
        db.child('catchment').child(catchment_counter).set(json)
        catchment_counter += 1

upload_phleb(phleb)
upload_catchment(catchment)