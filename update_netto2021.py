
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
      kueri = '''
        SELECT admin,
       npwp,
       kpp,
       cabang,
       nama,
       kdmap,
       kdbayar,
       masa,
       tahun,
       tanggalbayar,
       bulanbayar,
       tahunbayar,
       datebayar,
       nominal,
       ntpn,
       bank,
       nosk,
       nospm,
       tipe,
       source,
       extra,
       billing,
       nop,
       pembuat,
       CASE
         WHEN SOURCE = 1 THEN 'MPN'
         ELSE 'SPM'
       END AS ket
      FROM MPN
      WHERE (tahunbayar) = '2021'
      UNION ALL
      SELECT admin,
       npwp,
       kpp,
       cabang,
       '',
       kdmap,
       '',
       '',
       '',
       DAY(tanggal) AS TANGGALBAYAR,
       BULAN,
       TAHUN,
       tanggal,
       NOMINAL*-1,
       '',
       '',
       '',
       '',
       '',
       3 AS SOURCE,
       '',
       '',
       '',
       '',
       'SPMKP' AS ''
      FROM spmkp
      WHERE (TAHUN) = '2021'
      UNION ALL
      SELECT A.admin,
       A.npwp,
       A.kpp,
       A.cabang,
       A.nama,
       kdmap,
       kdbayar,
       masapajak,
       tahunpajak,
       DAY(TANGGALDOC) AS TANGGALBAYAR,
       MONTH(TANGGALDOC) BULAN,
       YEAR(TANGGALDOC) TAHUN,
       TANGGALDOC,
       NOMINAL*-1,
       ntpn,
       '',
       nopbk,
       '',
       '',
       4 AS SOURCE,
       '',
       '',
       '',
       '',
       'PBK KIRIM' AS ''
      FROM PBK A
        INNER JOIN MASTERFILE B ON A.NPWP = B.NPWP
      WHERE YEAR(TANGGALDOC) = '2021'
      AND   A.KPP = B.KPP
      AND   A.CABANG = B.CABANG
      UNION ALL
      SELECT A.ADMIN,
       npwp2,
       kpp2,
       cabang2,
       nama2,
       kdmap2,
       kdbayar2,
       masapajak2,
       tahunpajak2,
       DAY(TANGGALDOC) AS TANGGALBAYAR,
       MONTH(TANGGALDOC) BULAN,
       YEAR(TANGGALDOC) TAHUN,
       TANGGALDOC,
       NOMINAL,
       ntpn,
       '',
       nopbk,
       '',
       '',
       5 AS SOURCE,
       '',
       '',
       '',
       '',
       'PBK TERIMA' AS ''
      FROM PBK A
        INNER JOIN MASTERFILE B ON A.NPWP2 = B.NPWP
      WHERE YEAR(TANGGALDOC) = '2021'
      AND   A.KPP2 = B.KPP
      AND   A.CABANG2 = B.CABANG;'''
      def update(x):
        netto2021 = pd.read_sql(x,db_conn)
        netto2021['FULL'] = netto2021.npwp+netto2021.kpp+netto2021.cabang
        netto2021['FULL'] = netto2021['FULL'].astype('str')

        netto2021.drop(['admin', 'npwp', 'kpp', 'cabang'],axis=1,inplace=True)
        kestring = ['tanggalbayar','bulanbayar', 'tahunbayar'] 
        for i in kestring:
            netto2021[i] = netto2021[i].astype('str')

        mf = pd.read_excel(r'F:\STREAMLIT\DASHTEAM\MFWP\MFWP+klu.xlsx',
        usecols=['NPWP','NAMA_WP','NAMA_AR','SEKSI','NAMA_KLU'],
        dtype={'NPWP':'str'},engine='openpyxl')

        kdmap = pd.read_excel('D:\DATA KANTOR\MASTERFILE\KODE_MAP_FILTERED.xlsx', dtype={'KD MAP':'str'})
        netto2021 = pd.merge(netto2021,mf,left_on='FULL',right_on='NPWP',how='left')
        netto2021 = pd.merge(netto2021,kdmap,left_on='kdmap',right_on='KD MAP',how='left')
        netto2021.drop('kdmap',axis=1,inplace=True)

        kosong = ['NAMA_WP', 'NAMA_AR', 'SEKSI', 'NAMA_KLU']
        for i in kosong:
            netto2021[i].fillna('Non WP Madtim',inplace=True)

        netto2021.to_sql(con=db_conn,name='netto2021',if_exists='replace',index=False)

      def capaian():
        #Penerimaan
        @st.cache(allow_output_mutation=True)
        def netto21(x):
          data = pd.read_sql(x,db_conn)
          return data
          
        netto2021 = netto21('select sum(nominal) as netto from netto2021;')['netto'].sum()
        capaian = (netto2021/10171068857000)*100
        
        data = pd.DataFrame(capaian)
        data.to_sql(con=connection,name='capaian2021',if_exists='replace',index=False)
       

      st.markdown('___')
      
      st.title('Update Data Netto')
      if st.button('Update Sini hu',key=1):
        st.warning('Silakan Tunggu')
        update(kueri)
        st.success('Sukses hu')
      st.title('Update Data Capaian')
      if st.button('Update Sini hu',key=2):
        st.warning('Silakan Tunggu')
        capaian = capaian()
        st.success('Sukses hu')
          
        
      return super().run()



