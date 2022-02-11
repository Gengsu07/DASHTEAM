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
        <iframe title="1.Laporan Penerimaan 2021 - TPR_SR" width="1366" height="768" src="https://app.powerbi.com/reportEmbed?reportId=9064d0ce-e0f5-4c28-a153-9bd95785884f&autoAuth=true&ctid=b2e7bf22-070a-4364-b049-4d31669854c4&config=eyJjbHVzdGVyVXJsIjoiaHR0cHM6Ly93YWJpLXNvdXRoLWVhc3QtYXNpYS1iLXByaW1hcnktcmVkaXJlY3QuYW5hbHlzaXMud2luZG93cy5uZXQvIn0%3D" frameborder="0" allowFullScreen="true"></iframe>''',
        unsafe_allow_html=True)