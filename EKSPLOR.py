from os import sep
import pandas as pd
import streamlit as st 
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
from hydralit import HydraHeadApp

class eda_app(HydraHeadApp):
    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self):
        #Eksplor Data
        @st.cache
        def load_xlsx(x):
            df = pd.read_excel(x, engine='openpyxl')
            return df
        def load_csv(x):
            df = pd.read_csv(x,sep=',')
            return df
        st.title('Aplikasi Eksplorasi Analisis Data')
        
        format = st.selectbox('Format data',['.xlsx','.csv'])
        if format == '.xlsx':
            data = st.file_uploader('Masukkan Data')
            st.caption('Pastikan data .xlsx, tidak memiliki merge kolom dan kolom paling atas nama kolom')
            if data is not None:
                df = load_xlsx(data)
                pr = ProfileReport(df)
                st_profile_report(pr,progress_bar = True)
            else:
                st.info('Menunggu Data Anda Upload')
        elif format == '.csv':
            data = st.file_uploader('Masukkan Data')
            st.caption('Pastikan file csv dengan separator (,)')
            if data is not None:
                df = load_csv(data)
                pr = ProfileReport(df)
                st_profile_report(pr)
            else:
                st.info('Menunggu Data Anda Upload')