import pandas as pd
import streamlit as st
import plotly.express as px 
import altair as alt
from hydralit import HydraHeadApp

class Pemanfaatan_App(HydraHeadApp):
    def __init__(self, title = 'Hydralit Explorer', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        
    def run(self):
        @st.cache
        def pemanfaatan():
            df = pd.read_excel('DB\rekap_pemanfaatandata11okt.xlsx', engine='openpyxl')
            seleksi = ['Data Awal Data Pemicu Jumlah Data','Belum Tindak Lanjut Data Pemicu Jumlah Data','Tindak Lanjut WP Data Pemicu Jumlah Data',
            'Tindak Lanjut AR Data Pemicu Jumlah Data','Data Awal Data Pemicu Nilai Data','Belum Tindak Lanjut Data Pemicu Nilai Data',
            'Tindak Lanjut WP Data Pemicu Nilai Data','Tindak Lanjut AR Data Pemicu Nilai Data','Data Awal Data Penguji Jumlah Data',
            'Belum Tindak Lanjut Data Penguji Jumlah Data','Tindak Lanjut AR Data Penguji Jumlah Data','AR','Seksi']
            df = df.filter(seleksi)
            df = df.melt(id_vars=['AR','Seksi'], var_name='Pemanfaatan Data',value_name='Nominal')
            return df
        df = pemanfaatan()
        pilihan = st.selectbox('Pilih Jenis Data',['Pemicu','Penguji'])
        st.markdown('___')
        seleksi = df.loc[df['Pemanfaatan Data'].str.contains(pilihan)]
        seleksi = seleksi.loc[~seleksi['Pemanfaatan Data'].str.contains('Data Awal')]
        seleksi_jumlah = seleksi.loc[seleksi['Pemanfaatan Data'].str.contains('Jumlah')]
        jmldata = alt.Chart(seleksi_jumlah).mark_bar().encode(
            x = alt.X('sum(Nominal)', stack='normalize',title='Persentase Nominal'),
            y = 'AR',
            color = 'Pemanfaatan Data',
            tooltip = ['Pemanfaatan Data:N','sum(Nominal)'],
            ).properties(width = 1080, height = 640, title = 'Tindak Lanjut Jumlah Data {}'.format(pilihan)
            ).interactive()
        st.altair_chart(jmldata)

        seleksi_nilai = seleksi.loc[seleksi['Pemanfaatan Data'].str.contains('Nilai')]
        nilaidata = alt.Chart(seleksi_nilai).mark_bar().encode(
            x = alt.X('sum(Nominal)', stack='normalize',title='Persentase Nominal'),
            y = 'AR',
            color = 'Pemanfaatan Data',
            tooltip = ['Pemanfaatan Data:N','sum(Nominal)'],
            ).properties(width = 1080, height = 640, title = 'Tindak Lanjut Nilai Data {}'.format(pilihan)
            ).interactive()
        st.altair_chart(nilaidata)
        st.markdown('___')
        df_slice1 =seleksi_jumlah.groupby(['Seksi','AR']).sum().reset_index().sort_values(by='Nominal')
        df_slice2 =seleksi_nilai.groupby(['Seksi','AR']).sum().reset_index().sort_values(by='Nominal')
        pie1 = px.pie(df_slice1, names = 'Seksi', values='Nominal',color='Seksi', width=600)
        pie2 = px.pie(df_slice2, names = 'Seksi', values='Nominal',color='Seksi', width=600)
        col6,col7 = st.columns(2)
        with col6:
            st.subheader('Proporsi Jumlah Data {}'.format(pilihan))
            st.plotly_chart(pie1)
        with col7:
            st.subheader('Proporsi Nilai Data {}'.format(pilihan))
            st.plotly_chart(pie2)
        st.markdown('___')
        st.subheader('Detail Data')
        with st.expander('Detail Jumlah Data {}'.format(pilihan)):            
            st.table(seleksi_jumlah)
        with st.expander('Detail Nilai Data {}'.format(pilihan)):
            st.table(seleksi_nilai)