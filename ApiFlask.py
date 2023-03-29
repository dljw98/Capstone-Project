from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import requests
import json
import urllib
import urllib.request        
from flask import Flask, request, render_template
from flask_restful import Resource, Api, reqparse
from marshmallow import Schema, fields
import ast
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO

from FeatureEngineering import create_time_matrix
from MatchingAlgorithm import run_algorithm

###
app = Flask(__name__)
api = Api(app)

@app.route('/routes')
def get_routes():
    args = request.args
    orders = args.get('orders')
    ordersIO = StringIO(orders)
    orders_df = pd.read_csv(ordersIO, index_col=None)
    print(orders_df)
    
    catchment = args.get('catchment')
    catchmentIO = StringIO(catchment)
    catchment_df = pd.read_csv(catchmentIO, index_col=None)
    catchment_df.drop(columns=['Unnamed: 0'], inplace=True)
    print(catchment_df)

    phleb = args.get('phleb')
    phlebIO = StringIO(phleb)
    phleb_df = pd.read_csv(phlebIO, index_col=None)
    phleb_df.drop(columns=['Unnamed: 0'], inplace=True)
    print(phleb_df)
    
    API_key = args.get('API_key')
    isMultiEnds = args.get('isMultiEnds')
    
    result = run_algorithm(orders_df, catchment_df, phleb_df, API_key, isMultiEnds = False)
    
    return {'route': result}, 200
###

if __name__ == "__main__":
    app.run(port=8000)