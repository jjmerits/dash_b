import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
from datetime import datetime, timezone
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import pymongo
import json
import pytz
import time
import socket

# 지정된 IP 주소 리스트
allowed_ips = ['121.65.247.11', '10.88.116.16', '127.0.0.1']

# Streamlit 애플리케이션 시작
st.set_page_config(layout='wide',initial_sidebar_state="expanded")
st.title('Model Portfolio')

# 클라이언트 IP 주소 확인
#client_ip = socket.gethostbyname(socket.gethostname())

# IP 주소 확인 및 권한 부여

# Excel 파일 경로

url = st.secrets.db_credentials.ADDRESS
url_1 = st.secrets.db_credentials.ADDRESS_1
#excel_file_path =st.secrets.db_credentials.ADDRESS
#sheet_name = 'dash'

# Excel 파일 읽기
try:
    #df = pd.read_excel(excel_file_path, sheet_name=sheet_name).fillna('')
    #df = pd.read_excel(excel_file_path).fillna('')
    df = pd.read_csv(url)
    df = df.fillna('')
    df['Value'] = df['Value'].apply(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) and not pd.isnull(x) else x)
    df_style = df.style.apply(lambda row: ['background-color: lightgreen' if row['Port'] == 1 else '' for _, row in df.iterrows()], axis=1)
    df = df.astype(str)
    df = df.to_html(escape=False,index=False)

    test_df = pd.read_csv(url_1)
    test_df.columns = test_df.iloc[0]
    test_df = test_df.iloc[1:]
    test_df['DATES'] = pd.to_datetime(test_df['DATES'])
    # Filter out weekends (assuming Saturday and Sunday are weekends)
    test_df = test_df[(test_df['DATES'].dt.dayofweek != 5) & (test_df['DATES'].dt.dayofweek != 6)]

        
except Exception as e:
    df = pd.DataFrame(columns=['No Excel Sheet Found'])

# 데이터 표시
st.title('Time Series Chart (Excluding Weekends)')
st.write("Data loaded successfully. Here's the chart:")
fig = px.bar(test_df, x='DATES', y=[test_df.columns[0], test_df.columns[2]], title='Bar Chart')
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text='Values')

# Display the chart in the Streamlit app
st.plotly_chart(fig)

st.write(df, unsafe_allow_html=True)
#st.dataframe(df)


