from mysql.connector import connection
import pandas as pd
from selenium import webdriver
from sqlalchemy import create_engine
from sqlalchemy import *
import streamlit as st 
from hydralit import HydraHeadApp

class report2021_app(HydraHeadApp):
    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):
        padding = 0
        st.markdown(f""" <style>.reportview-container .main .block-container{{
            padding-top: {padding}rem;
            padding-right: {1}rem;
            padding-left: {1}rem;
            padding-bottom: {padding}rem;}} </style> """, unsafe_allow_html=True)

        st.markdown('''
        <iframe title="1.Laporan Penerimaan 2021 - TPR_SR" width="1140" height="541.25" src="https://app.powerbi.com/reportEmbed?reportId=64000438-494c-4c21-acc1-f16e4fc3ed7d&autoAuth=true&ctid=b2e7bf22-070a-4364-b049-4d31669854c4&config=eyJjbHVzdGVyVXJsIjoiaHR0cHM6Ly93YWJpLXNvdXRoLWVhc3QtYXNpYS1iLXByaW1hcnktcmVkaXJlY3QuYW5hbHlzaXMud2luZG93cy5uZXQvIn0%3D" frameborder="0" allowFullScreen="true"></iframe>''',
        unsafe_allow_html=True)