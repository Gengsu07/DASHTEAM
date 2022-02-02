
from mysql.connector import connection
import pandas as pd
from selenium import webdriver
from sqlalchemy import create_engine
from sqlalchemy import *
import streamlit as st 
from hydralit import HydraHeadApp
from streamlit.legacy_caching.caching import _write_to_cache
from selenium.webdriver import Chrome, chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


class update_db(HydraHeadApp):
    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):
      db_conn = create_engine('mysql://sugengw07:sgwi2341@127.0.0.1:3306/mpninfo')
      connection = db_conn.raw_connection()

      with open(r'F:\STREAMLIT\DASHTEAM\sql\netto2021.sql','r') as kueri:
        netto2021 = kueri.read()
        
      with open(r'F:\STREAMLIT\DASHTEAM\sql\netto2022.sql','r') as kueri:
        netto2022 = kueri.read()

      def update2021(x):
        netto = pd.read_sql(x,db_conn)
        netto['FULL'] = netto.npwp+netto.kpp+netto.cabang
        netto['FULL'] = netto['FULL'].astype('str')

        netto.drop(['admin', 'npwp', 'kpp', 'cabang'],axis=1,inplace=True)
        kestring = ['tanggalbayar','bulanbayar', 'tahunbayar'] 
        for i in kestring:
            netto[i] = netto[i].astype('str')

        mf = pd.read_sql('select * from dashteam_mf;',con=db_conn)

        kdmap = pd.read_sql('select * from dashteam_map',con=db_conn)
        netto = pd.merge(netto,mf,left_on='FULL',right_on='NPWP',how='left')
        netto = pd.merge(netto,kdmap,left_on='kdmap',right_on='KD MAP',how='left')
        netto.drop('kdmap',axis=1,inplace=True)

        kosong = ['NAMA_WP', 'NAMA_AR', 'SEKSI', 'NAMA_KLU']
        for i in kosong:
            netto[i].fillna('Non WP Madtim',inplace=True)

        netto.to_sql(con=db_conn,name='netto2021',if_exists='replace',index=False)

      def update2022(x):
        netto = pd.read_sql(x,db_conn)
        netto['FULL'] = netto.npwp+netto.kpp+netto.cabang
        netto['FULL'] = netto['FULL'].astype('str')

        netto.drop(['admin', 'npwp', 'kpp', 'cabang'],axis=1,inplace=True)
        kestring = ['tanggalbayar','bulanbayar', 'tahunbayar'] 
        for i in kestring:
            netto[i] = netto[i].astype('str')

        mf = pd.read_sql('select * from dashteam_mf;',con=db_conn)

        kdmap = pd.read_sql('select * from dashteam_map',con=db_conn)
        netto = pd.merge(netto,mf,left_on='FULL',right_on='NPWP',how='left')
        netto = pd.merge(netto,kdmap,left_on='kdmap',right_on='KD MAP',how='left')
        netto.drop('kdmap',axis=1,inplace=True)

        kosong = ['NAMA_WP', 'NAMA_AR', 'SEKSI', 'NAMA_KLU']
        for i in kosong:
            netto[i].fillna('Non WP Madtim',inplace=True)

        netto.to_sql(con=db_conn,name='netto2022',if_exists='replace',index=False)
      

      st.markdown('___')
      
      st.title('Update Data Netto')
      
      if st.button('Netto 2022 Update Sini hu',key=1):
        st.warning('Silakan Tunggu')
        update2022(netto2022)
        st.success('Sukses hu')
      
      if st.button('Netto 2021 Update Sini hu',key=1):
        st.warning('Silakan Tunggu')
        update2021(netto2021)
        st.success('Sukses hu')

     
          
        
      return super().run()



