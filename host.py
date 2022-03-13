from operator import add
from hydralit import HydraHeadApp
from hydralit.hydra_app import HydraApp
from sqlalchemy.sql.functions import user
import streamlit as st 
from MPN import mpn_app
from PPMPKM import ppmpkm_app
from APPROWEB import approweb_app
from DATA_APPROWEB import Pemanfaatan_App
from EKSPLOR import eda_app
from login_app import LoginApp
from dashboard_app import dashboard
from update_netto2021 import update_db#
from visualisasi import report2021_app
from dash_powerbi import penerimaan2022_app

if __name__ == '__main__':
    over_theme = {'txc_inactive': '#C99E10','menu_background':'#02275d','option_active':'#ffc91b','txc_active: Active':'#102754'}
    app = HydraApp(title='Dashboard KPP Madya Jaktim',favicon="resources\djp_kotak.png",
    hide_streamlit_markers=True, 
    banner_spacing=[5,30,60,30,5],
    navbar_animation = True,
    use_navbar=True,
    navbar_sticky=True,
    navbar_theme=over_theme)    

    app.add_app('Login',app=LoginApp(title='Login'),is_login=True)
    app.add_app('Dashboard',app=penerimaan2022_app(title='Dashboard'),is_home=True)
    #app.add_app('Dashboard', app=dashboard(title='Dashboard'),is_home=True)
    app.add_app('MPN',icon='📊',app=mpn_app(title = 'MPN'))
    app.add_app('PPM_PKM',icon='📈', app=ppmpkm_app(title='PPM_PKM') )
    app.add_app('Aktivitas_Approweb', app=approweb_app(title='Aktivitas_Approweb'))
    app.add_app('Data_Approweb',app=Pemanfaatan_App(title='Data_Approweb'))
    app.add_app('Eksplorasi Data', app = eda_app(title='Eksplorasi Data'))
    app.add_app('Update Database',app=update_db(title = 'Update Database'))
    app.add_app('Laporan Penerimaan 2021',app=report2021_app(title='Laporan Penerimaan 2021'))

   
    user_access_level, username = app.check_access()
    if user_access_level == 1:
        complex_nav = {
            'Dashboard': ['Dashboard'],
            'Visualisasi 🔥':['Laporan Penerimaan 2021','MPN'],
            '🔥 Kinerja Penerimaan': ['MPN','PPM_PKM'],
            'Approweb': ['Aktivitas_Approweb',"Data_Approweb"],
            'Tools': ["Eksplorasi Data"],
            'Admin':['Update Database']
        }
    elif user_access_level == 2:
        complex_nav = {
            'Dashboard': ['Dashboard'],
            'Visualisasi 🔥':['Laporan Penerimaan 2021'],
            '🔥 Kinerja Penerimaan': ['MPN','PPM_PKM']
        }
    else:
        complex_nav = {
            'Dashboard': ['Dashboard']
        }

    app.run(complex_nav)