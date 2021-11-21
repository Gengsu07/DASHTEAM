from enum import auto
from os import path, sep
from pathlib import WindowsPath
from altair.vegalite.v4.api import value
from altair.vegalite.v4.schema.channels import Color, StrokeDash
from altair.vegalite.v4.schema.core import Align, LabelOverlap
from ipython_genutils.py3compat import with_metaclass
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
from hydralit import HydraHeadApp
import mysql.connector as mysql
import plotly.graph_objects as go


class mpn_app(HydraHeadApp):
    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

        
    def run(self):
        alt.themes.enable('urbaninstitute')
        #Penerimaan
        @st.cache(allow_output_mutation=True)
        def netto():
            db_conn = mysql.connect(host = '10.4.19.215', user = 'sugengw07', password= 'sgwi2341',
            database = 'mpninfo',port = '3306')
            with open(r'sql\mpnspmpbkspmkp.sql','r') as query:
                penerimaan = query.read()
            data = pd.read_sql(penerimaan,db_conn)
            data['NPWP_FULL'] = data.npwp+data.kpp+data.cabang
            mf = mfwp()
            data = pd.merge(data,mf, left_on='NPWP_FULL',right_on='NPWP', how='left')
            data.drop(['nama', 'ntpn', 'bank', 'nosk', 'nospm', 'tipe', 'source', 'extra', 'billing','nop', 'pembuat',],axis=1,inplace=True)
            return data

        #MFWP
        @st.cache
        def mfwp():
            mf = pd.read_excel(r'MFWP\MFWP+klu.xlsx',usecols=['NPWP','NAMA_WP','NAMA_AR','SEKSI',
            'NAMA_KLU'],
            dtype={'NPWP':'str','NPWP_FULL':'str'},engine='openpyxl')
            return mf


        penerimaan = netto()
        capaian = (penerimaan['nominal'].sum()/10171068857000)*100

        colseksi,colar,coltgl1,coltgl2 = st.columns([1,1,1,1])
        with coltgl1:
            mulai = st.date_input('Tanggal Mulai',datetime.date(2021,1,1))
        with coltgl2:
            akhir = st.date_input('Tanggal Akhir',datetime.date.today())
        penerimaan['datebayar'] = pd.to_datetime(penerimaan['datebayar'])
        if (mulai is not None) & (akhir is not None):
            mulai = pd.to_datetime(mulai)
            akhir = pd.to_datetime(akhir)
            penerimaan_slice = penerimaan[penerimaan['datebayar'].isin(pd.date_range(mulai,akhir))]
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

        data_kecil = penerimaan_slice.filter(['NPWP_FULL','NAMA_WP','datebayar','nominal','ket','kdmap','SEKSI','NAMA_AR','NAMA_KLU','JENIS_WP'])
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
            st.metric(label='Capaian',value="%.2f" %capaian)

        data_area = data_kecil.groupby(['datebayar']).sum().reset_index()
        kumulatif = alt.Chart(data_area).transform_window(kumulatifsum = 'sum(nominal)',
        sort=[{'field':'datebayar'}]).mark_area().encode(
            x = 'datebayar:T',
            y= alt.Y('kumulatifsum:Q',title='Kumulatif',scale = alt.Scale(domain=[0,data_area['nominal'].sum()])),
            tooltip = ['datebayar','kumulatifsum:Q']
        ).properties(width=1080,height=640,title={'text':'Penerimaan Kumulatif',
        'subtitle':'Grafik meningkat tajam berarti ada pembayaran besar, sebaliknya lembah berarti ada SPMKP',
        'color':'white','subtitleColor':'grey'}
        ).interactive()

        area = alt.Chart(data_area).mark_line().encode(
            x = alt.X('datebayar:T', title='Tanggal Bayar'),
            y = alt.Y('sum(nominal)', title='Nominal',scale=alt.Scale(domain=[0,data_area['nominal'].max()])),
            tooltip = ['datebayar','nominal']
        ).properties( title = 'Trendline Pembayaran',
            width = 1080,
            height = 640
        ).interactive()
        trend = alt.vconcat(kumulatif,area).configure_axis(grid=False).configure_title(fontSize=20
        )
        st.altair_chart(trend)
        st.markdown('___')

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

        data_map = data_kecil.groupby(['SEKSI','kdmap','NAMA_AR']).sum().reset_index()
        data_map = data_map[data_map['nominal']>0]
        map = px.treemap(data_map,names='kdmap',path=['SEKSI','kdmap','NAMA_AR'],values='nominal',height=640,width = 1280,
        title='Proporsi Penerimaan')

        data_klu = data_kecil.groupby(['NAMA_KLU']).sum().reset_index()
        topklu = data_klu.nlargest(10,'nominal').sort_values(by='nominal',ascending=False)
        topwp = data_over.nlargest(10,'nominal').sort_values(by='nominal',ascending=False)

        klu = alt.Chart(topklu).mark_bar().encode(
            x=alt.X('sum(nominal):Q',title='Nominal'),
            y =alt.Y('NAMA_KLU:N', sort='-x'),
            color = 'NAMA_KLU:O',
            tooltip = ['NAMA_KLU','sum(nominal):N']
        ).properties(width=640, height=640).interactive()
        colbulan,colmap = st.columns([1,1])
        with colbulan:
            st.altair_chart(bulan)
        with colmap:
            st.altair_chart(klu)
        st.plotly_chart(map)

        return super().run()
