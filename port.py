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
    test_df = test_df.drop(test_df.columns[1:6], axis=1)
    test_df = test_df.dropna(subset=['NKY'])
    test_df = test_df.dropna(subset=['JPN_Size'])
    test_df['DATES'] = pd.to_datetime(test_df['DATES'])
    # Filter out weekends (assuming Saturday and Sunday are weekends)
    test_df = test_df[(test_df['DATES'].dt.dayofweek != 5) & (test_df['DATES'].dt.dayofweek != 6)]
    # Define the new column names as a list
    new_column_names = ['DATES','NKY', 'NKY_Daily(%)', 'KOSPI200', 'KOSPI_Daily(%)', 'KOSDAQ150', 'KOSDAQ_Daily(%)','TWSE', 'TWSE_Daily(%)','JPN_Size','JPN_Return','KR_Size','KR_Return','TW_Size','TW_Return','Size_Sum','JPN_Return(%)','KR_Return(%)','TW_Return(%)']
    # Assign the new column names to the DataFrame
    test_df.columns = new_column_names
    test_df['DATES'] = pd.to_datetime(test_df['DATES'])

        
except Exception as e:
    df = pd.DataFrame(columns=['No Excel Sheet Found'])

# 데이터 표시
#st.title('Vs benchmark chart')
st.write("9/5 수익률은 8/14일 부터의 누적 수익률")
# Create a layout with two columns


# Create a time series bar chart
st.write('Japan Market')
fig1 = go.Figure()

# Add bar traces for 'NKY' and 'KOSPI200'

fig1.add_trace(go.Bar(x=test_df['DATES'], y=test_df['NKY_Daily(%)'], name='NKY225'))
fig1.add_trace(go.Bar(x=test_df['DATES'], y=test_df['JPN_Return(%)'], name='JPN_Port_Return'))

# Update x-axis to treat 'DATES' as a date
fig1.update_xaxes(type='category', title_text='Date')
st.plotly_chart(fig1)

st.write('Korea Market')
fig2 = go.Figure()

fig2.add_trace(go.Bar(x=test_df['DATES'], y=test_df['KOSDAQ_Daily(%)'], name='KOSDAQ150'))
fig2.add_trace(go.Bar(x=test_df['DATES'], y=test_df['KOSPI_Daily(%)'], name='KOSPI200'))
fig2.add_trace(go.Bar(x=test_df['DATES'], y=test_df['KR_Return(%)'], name='KR_Port_Return'))

fig2.update_xaxes(type='category', title_text='Date')
st.plotly_chart(fig2)

st.write('Taiwan Market')
fig3 = go.Figure()

fig3.add_trace(go.Bar(x=test_df['DATES'], y=test_df['TWSE_Daily(%)'], name='TWSE'))
fig3.add_trace(go.Bar(x=test_df['DATES'], y=test_df['TW_Return(%)'], name='TW_Port_Return'))

fig3.update_xaxes(type='category', title_text='Date')
st.plotly_chart(fig3)

st.write('Port Size by Market (Won)')
fig4 = go.Figure()

fig4.add_trace(go.Bar(x=test_df['DATES'], y=test_df['JPN_Size'], name='Japan'))
fig4.add_trace(go.Bar(x=test_df['DATES'], y=test_df['KR_Size'], name='Korea'))
fig4.add_trace(go.Bar(x=test_df['DATES'], y=test_df['TW_Size'], name='Taiwan'))

fig4.update_xaxes(type='category', title_text='Date')
st.plotly_chart(fig4)






st.write(df, unsafe_allow_html=True)
#st.dataframe(df)




