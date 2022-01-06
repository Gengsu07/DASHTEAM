from codecs import StreamWriter
from enum import auto
from os import name, path, sep, times
from pathlib import WindowsPath
from re import LOCALE
from threading import local
from altair.vegalite.v4.api import value
from altair.vegalite.v4.schema.channels import Y, Color, StrokeDash
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
from sqlalchemy.sql.expression import label, text
from streamlit.elements import metric, plotly_chart
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
import datetime
import numpy as np
from hydralit import HydraHeadApp
from sqlalchemy import create_engine
import mysql.connector as mysql
from st_card import st_card



class dashboard(HydraHeadApp):
    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):
        alt.themes.enable('urbaninstitute')
        db_conn = mysql.connect(host = '10.4.19.215', user = 'sugengw07', password= 'sgwi2341',
        database = 'mpninfo',port = '3306')
        padding = 0
        st.markdown(f""" <style>.reportview-container .main .block-container{{
            padding-top: {padding}rem;
            padding-right: {1}rem;
            padding-left: {1}rem;
            padding-bottom: {padding}rem;}} </style> """, unsafe_allow_html=True)

        #Penerimaan
        @st.cache(allow_output_mutation=True)
        def netto21(x):
            data = pd.read_sql(x,db_conn,parse_dates=['datebayar'])
            return data

        @st.cache(allow_output_mutation=True)
        def netto20(x):
            data = pd.read_sql(x,db_conn,parse_dates=['TGL_SETOR'])
            return data


        netto2021 = netto21('select sum(nominal) as netto from netto2021;')['netto'].sum()
        netto2020 = netto20('select sum(JML_SETOR) as netto from netto2020;')['netto'].sum()
        delta_netto = ((netto2021-netto2020)/netto2020)*100
        netto_bulanini = netto21('select sum(nominal)as netto from netto2021 where month(datebayar) = month(curdate());')['netto'].sum()
        netto_bulanlalu = netto21('select sum(nominal)as netto from netto2021 where month(datebayar) = month(curdate()-interval 1 month);')['netto'].sum()
        delta_netto_bulan = ((netto_bulanini-netto_bulanlalu)/netto_bulanlalu)*100
        capaian = (netto2021/10171068857000)*100

        bruto21_kueri = '''select sum(nominal) as jumlah from netto2021
        where ket  <> 'SPMKP'
        and datebayar <= curdate() ;'''

        bruto_bulanini = netto21('''select sum(nominal) as jumlah from netto2021
        where ket  <> 'SPMKP' and month(datebayar) = month(curdate()) ;''')['jumlah'].sum()

        bruto_bulanlalu = netto21('''select sum(nominal) as jumlah from netto2021
        where ket  <> 'SPMKP'and month(datebayar) = month(curdate()-interval 1 month) ;''')['jumlah'].sum()

        bruto20_kueri = '''select sum(JML_SETOR) as jumlah from netto2020
        where Jenis IN('MPN','SPM','PBK TERIMA SEKANTOR','PBK KIRIM SEKANTOR','PBK KIRIM BEDA KANTOR',
        'PBK TERIMA BEDA KANTOR','VALAS')
        and TGL_SETOR <= date_sub(curdate(),interval 1 year);'''

        bruto21 = pd.read_sql(bruto21_kueri,db_conn)['jumlah'].sum()
        bruto20 = pd.read_sql(bruto20_kueri,db_conn)['jumlah'].sum()
        delta_bruto = ((bruto21-bruto20)/bruto20)*100
        delta_bruto_bulan = ((bruto_bulanini-bruto_bulanlalu)/bruto_bulanlalu)*100

        spmkp20_k = netto20('''select abs(sum(JML_SETOR)) as jumlah from netto2020
        where Jenis = 'SPMKP dari SIDJP' and
        TGL_SETOR <= date_sub(curdate(),interval 1 year);''')['jumlah'].sum()

        spmkp21_k = netto21('''select sum(nominal) as jumlah from netto2021
        where ket = 'SPMKP' and
        datebayar > '2020-12-31' and
        datebayar <= curdate();''')['jumlah'].sum()*-1

        spmkp_bulanini = netto21(''' select sum(nominal) as jumlah from netto2021 where ket='SPMKP' and month(datebayar) = month(curdate()); ''')['jumlah'].sum()*-1
        spmkp_bulanlalu = netto21('''select sum(nominal) as jumlah from netto2021 where ket = 'SPMKP' and month(datebayar) = month(curdate()-interval 1 month);''')['jumlah'].sum()*-1
        delta_spmkp_bulan = ((spmkp_bulanini-spmkp_bulanlalu)/spmkp_bulanlalu)*100
        delta_spmkp = ((spmkp21_k-spmkp20_k)/spmkp20_k)*100

        tgl_mpn = netto21('SELECT  MAX(datebayar) as Tanggal_update FROM netto2021 where ket ="MPN";')
        tgl_spm = netto21('SELECT  MAX(datebayar) as Tanggal_update FROM netto2021 where ket ="SPM";')

        #KPI
        colkpi1,colkpi2,colkpi3,colkpi4 = st.columns([2,2,2,1])
        with colkpi1:
            st.subheader('Bruto')
            st.metric(label = 's.d Sekarang', value='{}T'.format(str(bruto21/1000000000000)[:5]),
            delta='{}%'.format(str(delta_bruto)[:4]))
            st.metric(label = 'Bulan ini', value= '{} M'.format(str(bruto_bulanini/1000000000)[:3]),
            delta='{}%'.format(str(delta_bruto_bulan)[:4]))
        with colkpi2:
            st.subheader('SPMKP')
            st.metric(label = 's.d Sekarang', value='{}T'.format(str(spmkp21_k/1000000000000)[:5]),
            delta='{}%'.format(delta_spmkp.round(decimals =2)))
            st.metric(label= 'Bulan ini', value= '{} M'.format(str(spmkp_bulanini/1000000000)[:3]),
            delta='{}%'.format(delta_spmkp_bulan.round(decimals=2)))
        with colkpi3:
            st.subheader('Netto')
            st.metric(label='s.d Sekarang',value = '{} T'.format(str(netto2021/1000000000000)[:5]),
            delta ='{}%'.format(delta_netto.round(decimals=2)))
            st.metric(label='Bulan ini', value='{} M'.format(str(netto_bulanini/1000000000)[:3]),
            delta='{}%'.format(delta_netto_bulan.round(decimals=2)))
        with colkpi4:
            st.metric(label='Capaian',value="%.2f" %capaian)
            st.write('MPN:',tgl_mpn.loc[0,'Tanggal_update'])
            st.write('SPM:',tgl_spm.loc[0,'Tanggal_update'])
        st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)

        #PERSEKSI
        perseksi = netto21('select SEKSI, nominal from netto2021 where month(datebayar) = month (curdate()) ;').groupby('SEKSI').sum().reset_index()
        perseksi_copy = perseksi.copy()
        perseksi_copy.nominal = perseksi_copy.nominal.apply(lambda x:"{:,}".format(x))
        perseksi_tabel = ff.create_table(perseksi_copy)
        perseksi_tabel.layout.width = 480
        perseksi_bar = px.bar(perseksi,y='nominal',x='SEKSI')
        perseksi_bar.update_layout({'showlegend' : True,'plot_bgcolor':'rgba(0, 0, 0,0)','paper_bgcolor': 'rgba(0, 0, 0,0)',
        'margin_t':1 ,'margin_l':1})
        colseksi,coltabelseksi = st.columns([2,3])
        with colseksi:
            st.title('Per Seksi(Netto)')
            st.plotly_chart(perseksi_tabel)
        with coltabelseksi:
            st.plotly_chart(perseksi_bar)
        st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)

        #PER JENIS PAJAK
        perjenis = netto21('''select `MAP` , nominal from netto2021
        where month(datebayar)=month(curdate()) ;''').groupby('MAP').sum().reset_index().sort_values(by='nominal',ascending=False)
        perjenis_copy = perjenis.copy()
        perjenis_copy.nominal = perjenis_copy.nominal.apply(lambda x:"{:,}".format(x))
        perjenis_tabel = ff.create_table(perjenis_copy)
        perjenis_tree = px.treemap(perjenis,path=['MAP'],values='nominal',color='MAP',height=680,
        color_discrete_sequence=px.colors.qualitative.Pastel)
        perjenis_tree.update_layout({'margin_t':1 ,'margin_l':1})
        coljenistree,coljenistabel = st.columns([3,2])
        with coljenistree:
            st.plotly_chart(perjenis_tree)
        with coljenistabel:
            st.title('Per MAP(Netto)')
            st.plotly_chart(perjenis_tabel)
        
        st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)

        data_bulan = pd.read_sql('select datebayar, ket, nominal from netto2021;',con=db_conn)
        data_bulan.datebayar = pd.to_datetime(data_bulan.datebayar)
        data_bulan.datebayar = data_bulan.datebayar.dt.month_name()
        data_bulan = data_bulan.groupby(['datebayar','ket']).sum().reset_index()
        data_bulan.datebayar = data_bulan.datebayar.astype('str')
        namabulan = ['January',	'February',	'March',	'April',	'May',	'June',	'July',	'August',	'September',	'October',	'November',	'December']
        data_bulan.datebayar = pd.Categorical(data_bulan.datebayar,categories=namabulan,ordered=True)
        data_bulan = data_bulan.sort_values(by='datebayar')
        data_bulan = data_bulan.pivot_table(index=['datebayar'],columns='ket',values='nominal').reset_index()
        data_bulan['Netto'] = data_bulan.MPN+data_bulan['PBK KIRIM']+data_bulan['PBK TERIMA']+data_bulan.SPM+data_bulan.SPMKP
        for col in data_bulan.columns[1:]:
            data_bulan[col] = data_bulan[col].astype('int')
        for col in data_bulan.columns[1:]:
            data_bulan[col] = data_bulan[col].apply(lambda x:"{:,}".format(x))
        tabel_bulan = ff.create_table(data_bulan)
        #st.table(data_bulan.assign(hack='').set_index('hack'))
        st.plotly_chart(tabel_bulan)
      
        
        return super().run()
