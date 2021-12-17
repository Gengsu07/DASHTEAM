from enum import auto
from os import path, sep
from pathlib import WindowsPath
from re import LOCALE
from threading import local
from altair.vegalite.v4.api import value
from altair.vegalite.v4.schema.channels import Color, StrokeDash
from altair.vegalite.v4.schema.core import LabelOverlap
from attr import field
from numpy import column_stack, datetime64
from numpy.core.defchararray import index, title
from numpy.core.fromnumeric import sort
import pandas as pd
from pandas.core.indexes import period
from pandas.core.reshape.melt import wide_to_long
from pandas.core.reshape.reshape import stack
from pandas.io.sql import execute
from six import with_metaclass
from streamlit.elements import metric
from chart_studio import plotly
import streamlit as st
from PIL import Image
import plotly.express as px
from plotly import graph_objects as go
import plotly.figure_factory as ff
from toolz.itertoolz import groupby
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
import altair as alt
from datetime import *
import numpy as np
from hydralit import HydraHeadApp
from sqlalchemy import create_engine
import mysql.connector as mysql
import plotly.figure_factory as ff


alt.themes.enable('urbaninstitute')
#Koneksi Database
db_conn = mysql.connect(host = '10.4.19.215', user = 'sugengw07', password= 'sgwi2341',
database = 'mpninfo',port = '3306')

@st.cache(allow_output_mutation=True)
def netto21(x):
    data = pd.read_sql(x,db_conn)
    return data

kueri = '''SELECT nama, kdbayar, datebayar, nominal, ket, `FULL`, NPWP, NAMA_WP, NAMA_AR, SEKSI, NAMA_KLU, `MAP`
FROM netto2021;'''
penerimaan = netto21(kueri)

colseksi,colar,colmap,coltgl1,coltgl2 = st.columns([1,1,1,1,1])
now = datetime.now()
awaltahun = datetime(now.year,1,1)
with coltgl1:
    mulai = st.date_input('Tanggal Mulai',awaltahun)
with coltgl2:
    akhir = st.date_input('Tanggal Akhir',datetime.now())
penerimaan['datebayar'] = pd.to_datetime(penerimaan['datebayar'])
if (mulai is not None) & (akhir is not None):
    mulai = pd.to_datetime(mulai)
    akhir = pd.to_datetime(akhir)
    penerimaan_slice = penerimaan[penerimaan['datebayar'].isin(pd.date_range(mulai,akhir))]
with colmap:
    kdmap = penerimaan_slice['MAP'].unique()
    jenis_pajak = st.selectbox('Jenis Pajak',np.insert(kdmap,0,'Semua'))
    if (jenis_pajak != 'Semua'):
        penerimaan_slice = penerimaan_slice[penerimaan_slice['MAP']==jenis_pajak]
with colseksi:
    seksi = st.selectbox('Seksi',['Semua','Pengawasan I','Pengawasan II','Pengawasan III',
    'Pengawasan IV','Pengawasan V','Pengawasan VI'])
    if (seksi != 'Semua') :
        penerimaan_slice = penerimaan_slice[penerimaan_slice['SEKSI'] == seksi]
with colar:
    nama_ar = penerimaan_slice['NAMA_AR'].unique()
    ar = st.selectbox('Account Representative',np.insert(nama_ar,0,'Semua'))
    if (ar != 'Semua')&(seksi != 'Semua'):
        penerimaan_slice = penerimaan_slice[penerimaan_slice['NAMA_AR']== ar]


data_kecil = penerimaan_slice
kontribusi = data_kecil['nominal'].sum()/(penerimaan['nominal'].sum())*100
data_over = data_kecil.groupby(['NAMA_WP']).sum().sort_values(by='nominal',ascending=False).reset_index()
over1,over2,over3,colhead = st.columns([4,4,3,3])
with over1:
    st.metric(label='Total',value='{:,.0f}'.format(data_kecil['nominal'].sum()))
    #st.subheader('Total',value=ata_over['nominal'].sum())
    #st.subheader('{:,.0f}'.format(data_over['nominal'].sum()))
with over2:
    st.metric(label=data_over['NAMA_WP'].iloc[0],value='{:,.0f}'.format(data_over['nominal'].max()))
    #st.subheader('Tertinggi')
    #st.metric(label=data_over['NAMA_WP'].iloc[0],value= '{:,.0f}'.format(data_over['nominal'].max()))
with over3:
    st.metric(label=data_over['NAMA_WP'].iloc[-1],value='{:,.0f}'.format(data_over['nominal'].min()))
    #st.subheader('Terendah')
    #st.metric(label =data_over['NAMA_WP'].iloc[-1], value='{:,}'.format(data_over['nominal'].min()))
with colhead:
    st.metric(label='Kontribusi',value="%.2f" %kontribusi)


dataline = data_kecil.filter(['datebayar','nominal'])
line = alt.Chart(dataline).mark_line().encode(
    x = alt.X('datebayar:T', title='Tanggal Bayar'),
    y = alt.Y('sum(nominal)', title='Nominal',scale=alt.Scale(domain=[0,dataline['nominal'].max()])),
    tooltip = ['datebayar','nominal']
).properties( title = 'Trendline Pembayaran',
    width = 1080,
    height = 640
).configure_axis(grid=False).configure_title(fontSize=20
).interactive()

st.altair_chart(line)
st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)

data_bar = data_kecil.filter(['datebayar','ket','nominal'])
#data_bar['datebayar'] = data_bar['datebayar'].dt.month
#data_bar = data_bar.groupby(['datebayar','ket']).sum().reset_index()
bulan = alt.Chart(data_bar).mark_bar().encode(
    x = alt.X('sum(nominal):Q',title='Nominal'),
    y = alt.Y('month(datebayar):N',title='Bulan'),
    color = alt.Color('ket:N',legend=None),
    tooltip = ['ket','sum(nominal):Q']
).properties(width = 640,height=640,title='Jenis Penerimaan Per Bulan').configure_axis(grid = False
).interactive()

data_bulan = data_bar

data_bulan = data_bulan.groupby(data_bulan.datebayar.dt_strftime('B')['nominal'].sum())
#data_bulan = data_bulan.groupby(['datebayar']).sum().reset_index()
#bulan_ket = ff.create_table(data_bulan)

data_map = data_kecil.groupby(['SEKSI','MAP','NAMA_AR']).sum().reset_index()
data_map = data_map[data_map['nominal']>0]
map = px.treemap(data_map,names='MAP',path=['SEKSI','MAP','NAMA_AR'],values='nominal',height=640,width = 1280,
title='Proporsi Penerimaan')
map.update_layout({'showlegend' : True,'plot_bgcolor':'rgba(0, 0, 0,0)','paper_bgcolor': 'rgba(0, 0, 0,0)',
'margin_t':1 ,'margin_l':1})

coljenis, colket = st.columns(2)
with coljenis:
    st.altair_chart(bulan)
with colket:
    st.table(data_bulan)

st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)
st.plotly_chart(map)
