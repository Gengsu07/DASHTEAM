from playwright.sync_api import Playwright, sync_playwright
import pyautogui as pag
from datetime import datetime
from datetime import date
import pandas as pd
import streamlit as st
from hydralit import HydraHeadApp

def getbulan():
    hari_ini = date.today()
    tahun = hari_ini.year
    bulan = hari_ini.month
    awaltahun = date(tahun,1,1)
    listbulan = pd.period_range(awaltahun,hari_ini,freq='M').month
    bulan_get = []
    for n in listbulan:
        if n<10:
            temp = '0{}'.format(n)
            bulan_get.append(temp)
        else:
            temp = '{}'.format(n)
            bulan_get.append(temp)
    return bulan_get

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to https://appportal/login/
    page.goto("https://appportal/login/")

    # Click input[name="username"]
    page.click("input[name=\"username\"]")

    # Fill input[name="username"]
    page.fill("input[name=\"username\"]", "810202558")

    # Click input[name="password"]
    page.click("input[name=\"password\"]")

    # Press NumLock
    page.press("input[name=\"password\"]", "NumLock")

    # Fill input[name="password"]
    page.fill("input[name=\"password\"]", "Gengsu08")

    # Click text=Login
    page.click("text=Login")
    # assert page.url == "https://appportal/portal/index.php"

    # Click text=DATA PENERIMAAN
    page.click('//*[@id="smoothmenu1"]/ul/li[2]/a')
    # assert page.url == "https://appportal/portal/index.php#"

    pag.moveTo(211,50)
    pag.moveTo(211,135,1)
    
    # Click text=MPN
    page.click('//*[@id="smoothmenu1"]/ul/li[2]/ul/li[3]/a')
    # assert page.url == "https://appportal/portal/index.php#"

    # Click text=MPN Harian Rekon
    page.click('//*[@id="mpnharianrekon"]')
    # assert page.url == "https://appportal/portal/index.php#"

    bulan = getbulan()
    page.select_option('select[name="tgl_akhir"]','31')
    page.select_option('select[name="dd_tahun3"]','{}'.format(date.today().year))
    for valuta in range(1,4):
        page.select_option('select[name="valuta"]','{}'.format(valuta))

        for n in bulan:
            page.select_option('select[name="bln_awal"]','{}'.format(n))
            page.click('//*[@id="btndownload"]')
            # Start waiting for the download
            with page.expect_download() as download_info:
                # Perform the action that initiates download
                page.click('//*[@id="download"]/a[1]')
            download = download_info.value
            # Wait for the download process to complete
            path = download.save_as('{}_{}.csv'.format(valuta,n))
     # ---------------------
    


    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
