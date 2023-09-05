import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
from datetime import datetime, timezone
import seaborn as sns
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"

import plotly.graph_objects as go
import pymongo
import json
import requests

import gnews

import pytz
import time
import streamlit as st
import pandas as pd
import socket

# 지정된 IP 주소 리스트
allowed_ips = ['121.65.247.11', '10.88.116.16', '127.0.0.1']

# Streamlit 애플리케이션 시작
st.set_page_config(layout='wide',initial_sidebar_state="expanded")
st.title('Model Portfolio')

# 클라이언트 IP 주소 확인
client_ip = socket.gethostbyname(socket.gethostname())

# IP 주소 확인 및 권한 부여
if client_ip in allowed_ips:
    st.success('Access granted from IP: ' + client_ip)

    # Excel 파일 경로
    url = 'https://raw.githubusercontent.com/jjmerits/Dashboard/main/dash.csv'
 
    #excel_file_path = r'https://raw.githubusercontent.com/jjmerits/Dashboard/main/dash.csv'
    #sheet_name = 'dash'

    # Excel 파일 읽기
    try:
        #df = pd.read_excel(excel_file_path, sheet_name=sheet_name).fillna('')
        #df = pd.read_excel(excel_file_path).fillna('')
        df = pd.read_csv(url)
        df = df.astype(str)
    except Exception as e:
        df = pd.DataFrame(columns=['No Excel Sheet Found'])

    # 데이터 표시
    st.dataframe(df)

else:
    st.error('Access denied. Your IP is not allowed.')
