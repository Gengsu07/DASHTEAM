import pandas as pd
import streamlit as st 
from hydralit import HydraHeadApp

class penerimaan2022_app(HydraHeadApp):
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
       <iframe title="penerimaan2022 - Page 1" width="1366" height="820" src="https://app.powerbi.com/reportEmbed?reportId=a5562237-2283-4041-b823-dc21c7452072&autoAuth=true&ctid=b2e7bf22-070a-4364-b049-4d31669854c4&config=eyJjbHVzdGVyVXJsIjoiaHR0cHM6Ly93YWJpLXNvdXRoLWVhc3QtYXNpYS1iLXByaW1hcnktcmVkaXJlY3QuYW5hbHlzaXMud2luZG93cy5uZXQvIn0%3D" frameborder="0" allowFullScreen="true"></iframe>''',
        unsafe_allow_html=True)