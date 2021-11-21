from hydralit import HydraHeadApp
from enum import auto
from os import path, sep
from pathlib import WindowsPath
from altair.vegalite.v4.api import value
from altair.vegalite.v4.schema.channels import Color, StrokeDash
from altair.vegalite.v4.schema.core import LabelOverlap
from numpy import column_stack, datetime64
from numpy.core.defchararray import index, title
from numpy.core.fromnumeric import sort
import pandas as pd
from pandas.core.indexes import period
from pandas.core.reshape.melt import wide_to_long
from pandas.core.reshape.reshape import stack
from streamlit.elements import metric
from chart_studio import plotly
import streamlit as st
from PIL import Image
import plotly.express as px
from toolz.itertoolz import groupby
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
import altair as alt
import datetime
import numpy as np
import mysql.connector as mysql

class ppmpkm_app(HydraHeadApp):
    def __init__(self, title = 'PPMPKM', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):
        #PPM PKM
        @st.cache(allow_output_mutation=True)
        def data_ppmpkm():
            db_conn = mysql.connect(host = '10.4.19.215', user = 'sugengw07', password= 'sgwi2341',
            database = 'mpninfo',port = '3306')
            with open(r'sql\PPM_PKM_2021.sql','r') as query:
                ppmpkm = query.read()
            data = pd.read_sql(ppmpkm,db_conn)
            mf = mfwp()
            data.drop('NAMA_AR',axis=1,inplace=True)
            data['NPWP'] = data['NPWP'].astype('str')
            data = pd.merge(data,mf, left_on='NPWP',right_on='NPWP', how='left')
            data.drop(['NAMA_SEKSI','NPWP_FULL'],axis=1,inplace=True)
            return data
        #MFWP
        @st.cache
        def mfwp():
            mf = pd.read_excel(r'MFWP/MFWP.xlsx',usecols=[
            'NPWP','NPWP_FULL','NAMA_WP','NAMA_AR','SEKSI'], dtype={'NPWP':'str','NPWP_FULL':'str'},engine='openpyxl')
            return mf
        #PROGRAM
        ppmpkm = data_ppmpkm()
        ppmpkm['DATEBAYAR'] = pd.to_datetime(ppmpkm['DATEBAYAR'])
        colseksi,colar,coltgl1,coltgl2 = st.columns([1,1,1,1])
        with colseksi:
            seksi = st.selectbox('Seksi',['Semua','Pengawasan I','Pengawasan II','Pengawasan III',
            'Pengawasan IV','Pengawasan V','Pengawasan VI'])
            if (seksi != 'Semua') : 
                ppmpkm = ppmpkm[ppmpkm['SEKSI'] == seksi]
        with colar:
            nama_ar = ppmpkm['NAMA_AR'].unique()
            ar = st.selectbox('Account Representative',np.insert(nama_ar,0,'Semua'))
            if (ar != 'Semua'):
                ppmpkm = ppmpkm[ppmpkm['NAMA_AR']== ar]
        with coltgl1:
            mulai = st.date_input('Tanggal Mulai',datetime.date(2021,5,24))
        with coltgl2:
            akhir = st.date_input('Tanggal Akhir',datetime.date.today())
        ppmpkm['DATEBAYAR'] = pd.to_datetime(ppmpkm['DATEBAYAR'])
        if (mulai is not None) & (akhir is not None):
            mulai = pd.to_datetime(mulai)
            akhir = pd.to_datetime(akhir)
            ppmpkm_slice= ppmpkm[ppmpkm['DATEBAYAR'].isin(pd.date_range(mulai,akhir))]
            ppmpkm_slice['NOMINAL'] = ppmpkm_slice['NOMINAL'].astype('int')
            

        ppm = ppmpkm_slice[ppmpkm_slice['FLAG_PPM_PKM']=='PPM'].groupby(['DATEBAYAR']).sum().reset_index()
        ppmtree_data = ppmpkm_slice[ppmpkm_slice['FLAG_PPM_PKM']=='PPM'].groupby(['SEKSI','NAMA_AR','KDMAP','DATEBAYAR']).sum().reset_index()
        pkm = ppmpkm_slice[ppmpkm_slice['FLAG_PPM_PKM']=='PKM'].groupby(['DATEBAYAR']).sum().reset_index()
        pkmtree_data = ppmpkm_slice[ppmpkm_slice['FLAG_PPM_PKM']=='PKM'].groupby(['SEKSI','NAMA_AR','KDMAP','DATEBAYAR']).sum().reset_index()
        ppmarea  = alt.Chart(ppm).mark_area().encode(
            x='DATEBAYAR:T',
            y = alt.Y('NOMINAL:Q',scale=alt.Scale(domain=[0,ppm['NOMINAL'].max()])),
            tooltip = ['DATEBAYAR','NOMINAL']    
        ).properties(width = 1280, height = 640,title={'text':'PPM',
        'subtitle':'Trendline Penerimaan PPM',
        'color':'white','subtitleColor':'grey'}).configure_axis(grid=False).interactive()

        ppmtree_data = ppmtree_data[ppmtree_data['NOMINAL']>0]
        ppmtree = px.treemap(ppmtree_data,path=['SEKSI','NAMA_AR','KDMAP'],values='NOMINAL', width=1280,
        title='Proporsi PPM')

        pkmarea= alt.Chart(pkm).mark_area().encode(
            x='DATEBAYAR:T',
            y = alt.Y('NOMINAL:Q',scale=alt.Scale(domain=[0,pkm['NOMINAL'].max()])),
            tooltip = ['DATEBAYAR','NOMINAL']  
        ).properties(width = 1280, height = 640,title={'text':'PKM','subtitle':'Trendline Penerimaan PKM','color':'white','subtitleColor':'grey'}
        ).configure_axis(grid=False).interactive()

        pkmtree_data = pkmtree_data[pkmtree_data['NOMINAL']>0]
        pkmtree = px.treemap(pkmtree_data,path=['SEKSI','NAMA_AR','KDMAP'],values='NOMINAL', width=1280,title='Proporsi PKM')

        st.altair_chart(ppmarea)
        st.plotly_chart(ppmtree)   
        st.altair_chart(pkmarea)
        st.plotly_chart(pkmtree)
        
        return super().run()