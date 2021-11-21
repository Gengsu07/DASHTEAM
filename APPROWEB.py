import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt 
from hydralit import HydraHeadApp

class approweb_app(HydraHeadApp):
    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
    def run(self):
        #Approweb
        @st.cache
        def aktivitas():
            df = pd.read_excel('DB\approweb_db.xlsx',engine='openpyxl')
            df = df.melt(id_vars=['AR','Periode'],var_name='Aktivitas' ,value_name='Nominal')
            df = df[~df.AR.str.contains('Pengawasan')]
            return df
        df = aktivitas()
        
        jenisdata = st.selectbox('Piih Jenis Data',df['Aktivitas'].unique())
        periode = st.multiselect('Pilih Periode',df.Periode.unique(),default=df.Periode.unique())
        df_slice = df.loc[(df['Aktivitas']==jenisdata) & (df['Periode'].isin(periode))].groupby(['AR','Periode']
        ).sum().reset_index().sort_values(by='Nominal')
        bar = px.bar(df_slice, x='Nominal', y='AR', barmode='group' ,height=1080, width=1280,
        color = 'Periode',template='ggplot2')
        #treemap = px.treemap(df_slice, path=['AR','Periode'], values='Nominal', color='Periode',
        #height=768,width=1280)
        
        col1,col2,col3 = st.columns(3)
        with col1:
            kolom1 = df.loc[(df.Periode=='Juni-Oktober')& (df.Aktivitas==jenisdata)]
            jumlah = kolom1['Nominal'].sum() 
            st.metric(label= 'Juni-Oktober', value='{:,}'.format(jumlah))
        with col2:
            kolom1 = (df.loc[(df.Periode=='Juni-Oktober')& (df.Aktivitas==jenisdata)])
            kolom3 = (df.loc[(df.Periode=='Juni-September')& (df.Aktivitas==jenisdata)])
            selisih = int(kolom1['Nominal'].sum())- int(kolom3['Nominal'].sum())
            st.metric(label= 'Selisih', value= '{:,}'.format(selisih))
            #st.subheader(kolom3)
        with col3:
            kolom3 = df.loc[(df.Periode=='Juni-September')& (df.Aktivitas==jenisdata)]
            jumlah = kolom3['Nominal'].sum() 
            st.metric(label= 'Juni-September', value='{:,}'.format(jumlah))

        st.markdown('___')
        #st.markdown('### Proporsi Persebaran Data')
        #st.plotly_chart(treemap)
        st.markdown('### Perbandingan Antar Periode')
        bar.update_layout(legend=dict(
            xanchor = 'left', x = 0.25, yanchor='bottom',y = 0.01))
        st.plotly_chart(bar)
        st.markdown('___')
        st.subheader('Detail Data')
        
        st.table(df)