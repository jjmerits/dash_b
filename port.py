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
import math

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

# Define a function to generate CSS rules based on the values in column 'A'
def color_based_on_value(val):
    if val < 0:
        red_intensity = min(255, int(abs(val) * 5.1))  # Convert negative values to red (255 is the maximum intensity)
        return f'color: rgb({255 - red_intensity}, 0, 0)'
    else:
        green_intensity = min(255, int(val * 2.55))  # Convert positive values to green (255 is the maximum intensity)
        return f'color: rgb(0, {green_intensity}, 0)'
    
# Excel 파일 읽기
try:
    #df = pd.read_excel(excel_file_path, sheet_name=sheet_name).fillna('')
    #df = pd.read_excel(excel_file_path).fillna('')
    df = pd.read_csv(url)
    #print(df)
    df = df.fillna('')
    df['Value'] = df['Value'].apply(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) and not pd.isnull(x) else x)

    df_style = df.style.apply(lambda row: ['background-color: lightgreen' if row['Port'] == 1 else '' for _, row in df.iterrows()], axis=1)
    df['RETURN'] = pd.to_numeric(df['RETURN'])
    #df['RETURN'] = pd.to_numeric(df['RETURN'].str.replace('%', ''), errors='coerce')
    # Apply the function to the 'A' column in the DataFrame and render as HTML with conditional formatting
    #df = df.style.apply(lambda x: np.where(x.name == 'RETURN', x.applymap(color_based_on_value), ''), axis=None).render()
    
    sum_by_ticker = df.groupby('Ticker').agg({'RETURN': 'sum', 'NAME': 'first','CLASSIFICATION_DESCRIPTION': 'first','CLASSIFICATION_DESCRIPTION': 'first'}).reset_index()
    sorted_sum_by_value = sum_by_ticker.sort_values(by='RETURN', ascending=False)
    sorted_sum_by_value = sorted_sum_by_value.to_html(escape=False,index=False)
    
    df = df[df['IN']==1]
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
    new_column_names = ['DATES','NKY', 'NKY_Daily(%)', 'KOSPI200', 'KOSPI_Daily(%)', 'KOSDAQ150', 'KOSDAQ_Daily(%)','TWSE', 'TWSE_Daily(%)','JPN_Size','KR_Size','TW_Size','JPN_Return','KR_Return','TW_Return','Size_Sum','JPN_Return(%)','KR_Return(%)','TW_Return(%)','NKY_Daily(%)_adj','KOSPI_Daily(%)_adj','KOSDAQ_Daily(%)_adj','TWSE_Daily(%)_adj']
    
  

    # Assign the new column names to the DataFrame
    test_df.columns = new_column_names
    test_df['JPN_Cum_Return(%)'] = pd.to_numeric(test_df['JPN_Return'].str.replace(',', ''), errors='coerce') /  pd.to_numeric(test_df['JPN_Size'].str.replace(',', ''), errors='coerce').max()
    test_df['KR_Cum_Return(%)'] = pd.to_numeric(test_df['KR_Return'].str.replace(',', ''), errors='coerce') /  pd.to_numeric(test_df['KR_Size'].str.replace(',', ''), errors='coerce').max()
    test_df['TW_Cum_Return(%)'] = pd.to_numeric(test_df['TW_Return'].str.replace(',', ''), errors='coerce') /  pd.to_numeric(test_df['TW_Size'].str.replace(',', ''), errors='coerce').max()
    test_df['PORT_Cum_Return(%)'] = (pd.to_numeric(test_df['JPN_Return'].str.replace(',', ''), errors='coerce')+pd.to_numeric(test_df['KR_Return'].str.replace(',', ''), errors='coerce')+pd.to_numeric(test_df['TW_Return'].str.replace(',', ''), errors='coerce')) /  pd.to_numeric(test_df['Size_Sum'].str.replace(',', ''), errors='coerce').max()
    test_df['PORT_daily_return(%)'] = test_df['PORT_Cum_Return(%)'].pct_change()/100
    
    test_df['NKY_Cumulative_Return'] = (1 + pd.to_numeric(test_df['NKY_Daily(%)'])).cumprod() - 1
    test_df['KOSPI_Cumulative_Return'] = (1 + pd.to_numeric(test_df['KOSPI_Daily(%)'])).cumprod() - 1
    test_df['KOSDAQ_Cumulative_Return'] = (1 + pd.to_numeric(test_df['KOSDAQ_Daily(%)'])).cumprod() - 1
    test_df['TWSE_Cumulative_Return'] = (1 + pd.to_numeric(test_df['TWSE_Daily(%)'])).cumprod() - 1

    test_df['JP_LS'] = test_df['JPN_Cum_Return(%)'] - test_df['NKY_Cumulative_Return']*1
    test_df['KR_LS'] = test_df['KR_Cum_Return(%)'] - (test_df['KOSPI_Cumulative_Return'] + test_df['KOSDAQ_Cumulative_Return'])/2*1
    test_df['TW_LS'] = test_df['TW_Cum_Return(%)'] - test_df['TWSE_Cumulative_Return']*1
####################################### 전일 포지션으로 숏 포지션 유지

    test_df['NKY_Daily(%)'] =   pd.to_numeric(test_df['NKY_Daily(%)'])
    test_df['KOSPI_Daily(%)'] = pd.to_numeric(test_df['KOSPI_Daily(%)'])
    test_df['KOSDAQ_Daily(%)'] = pd.to_numeric(test_df['KOSDAQ_Daily(%)'])
    test_df['TWSE_Daily(%)'] = pd.to_numeric(test_df['TWSE_Daily(%)'])

    test_df['NKY_Daily(%)_adj'] = pd.to_numeric(test_df['NKY_Daily(%)_adj'])
    test_df['KOSPI_Daily(%)_adj'] = pd.to_numeric(test_df['KOSPI_Daily(%)_adj'])
    test_df['KOSDAQ_Daily(%)_adj']  = pd.to_numeric(test_df['KOSDAQ_Daily(%)_adj'])
    test_df['TWSE_Daily(%)_adj'] = pd.to_numeric(test_df['TWSE_Daily(%)_adj'])
    
    test_df['JPN_Size'] = pd.to_numeric(test_df['JPN_Size'].str.replace(',', ''), errors='coerce')
    test_df['KR_Size'] = pd.to_numeric(test_df['KR_Size'].str.replace(',', ''), errors='coerce')
    test_df['TW_Size'] = pd.to_numeric(test_df['TW_Size'].str.replace(',', ''), errors='coerce')

    # 포지션 1:1 대응 숏 유지시
    #test_df['NKY_Daily(%)_adj'] = test_df['NKY_Daily(%)']*(test_df['JPN_Size'].shift(1)/test_df['JPN_Size'].max())
    #test_df['KOSPI_Daily(%)_adj'] = test_df['KOSPI_Daily(%)']*(test_df['KR_Size'].shift(1)/test_df['KR_Size'].max())
    #test_df['KOSDAQ_Daily(%)_adj'] = test_df['KOSDAQ_Daily(%)']*(test_df['KR_Size'].shift(1)/test_df['KR_Size'].max())
    #test_df['TWSE_Daily(%)_adj'] = test_df['TWSE_Daily(%)']*(test_df['TW_Size'].shift(1)/test_df['TW_Size'].max())

    test_df['NKY_Cumulative_Return_adj'] = (1 + pd.to_numeric(test_df['NKY_Daily(%)_adj'])).cumprod() - 1
    test_df['KOSPI_Cumulative_Return_adj'] = (1 + pd.to_numeric(test_df['KOSPI_Daily(%)_adj'])).cumprod() - 1
    test_df['KOSDAQ_Cumulative_Return_adj'] = (1 + pd.to_numeric(test_df['KOSDAQ_Daily(%)_adj'])).cumprod() - 1
    test_df['TWSE_Cumulative_Return_adj'] = (1 + pd.to_numeric(test_df['TWSE_Daily(%)_adj'])).cumprod() - 1

    test_df['JP_LS_adj'] = test_df['JPN_Cum_Return(%)'] - test_df['NKY_Cumulative_Return_adj']
    test_df['KR_LS_adj'] = test_df['KR_Cum_Return(%)'] - (test_df['KOSPI_Cumulative_Return_adj'] + test_df['KOSDAQ_Cumulative_Return_adj'])/2
    test_df['TW_LS_adj'] = test_df['TW_Cum_Return(%)'] - test_df['TWSE_Cumulative_Return_adj']
    
    #test_df['Total_Return(%)'] = test_df['Total_Return(%)'] 
    test_df['DATES'] = pd.to_datetime(test_df['DATES'])
    


    #test_df['NKY_down_return'] = test_df['NKY_Daily(%)s'][test_df['NKY_Daily(%)'] < 0]
    #test_df['KOSPI_down_return'] = test_df['KOSPI_Daily(%)s'][test_df['KOSPI_Daily(%)'] < 0]
    #test_df['KOSDAQ_down_return'] = test_df['KOSDAQ_Daily(%)s'][test_df['KOSDAQ_Daily(%)'] < 0]
    #test_df['TWSE_down_return'] = test_df['TWSE_Daily(%)s'][test_df['TWSE_Daily(%)'] < 0]

    #test_df['JPN_down_return'] = test_df['JPN_Daily(%)s'][test_df['JPN_Daily(%)'] < 0]
    #test_df['KR_down_return'] = test_df['KR_Daily(%)s'][test_df['KR_Daily(%)'] < 0]
    #test_df['TW_down_return'] = test_df['TW_Daily(%)s'][test_df['TW_Daily(%)'] < 0]


 
        
except Exception as e:
    df = pd.DataFrame(columns=['No Excel Sheet Found'])

# 데이터 표시
#st.title('Vs benchmark chart')
st.write("9/5 수익률은 8/14일 부터의 누적 수익률")

# Create a layout with two columns


performance = [
    {
        "Name": "Nikkei225",
        "Return(%)": test_df['NKY_Cumulative_Return'].iloc[-1]*100,
        "std(%)": test_df['NKY_Daily(%)'].std()*100,
        "Sharp": (test_df['NKY_Daily(%)'].mean() / test_df['NKY_Daily(%)'].std())*math.sqrt(252),
        "Port Return(%)": test_df['JPN_Cum_Return(%)'].iloc[-1]*100,
        "Port std(%)":(pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce')).std()*100,
        "Port Sharp": (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce')).mean() / (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce')).std()*math.sqrt(252),
        "L/S Port Sharp (100%)": - (test_df['NKY_Daily(%)'] - (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / (test_df['NKY_Daily(%)'] - (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (70%)": - (test_df['NKY_Daily(%)']*0.7 - (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / (test_df['NKY_Daily(%)'] - (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (50%)": - (test_df['NKY_Daily(%)']*0.5 - (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / (test_df['NKY_Daily(%)'] - (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
         "L/S Port Sharp (30%)": - (test_df['NKY_Daily(%)']*0.3 - (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / (test_df['NKY_Daily(%)'] - (pd.to_numeric(test_df['JPN_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252)
    },
    {
        "Name": "Kospi200",
        "Return(%)": test_df['KOSPI_Cumulative_Return'].iloc[-1]*100,
        "std(%)": test_df['KOSPI_Daily(%)'].std()*100,
        "Sharp": test_df['KOSPI_Daily(%)'].mean()  / test_df['KOSPI_Daily(%)'].std()*math.sqrt(252),
        "Port Return(%)": test_df['KR_Cum_Return(%)'].iloc[-1]*100,
        "Port std(%)": (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce')).std()*100,
        "Port Sharp": (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce')).mean() / (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce')).std()*math.sqrt(252),
        "L/S Port Sharp (100%)": - ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (70%)": - ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2*0.7 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (50%)": - ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2*0.5 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (30%)": - ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2*0.3 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252)
    },
    {
        "Name": "Kosdaq150",
        "Return(%)": test_df['KOSDAQ_Cumulative_Return'].iloc[-1]*100,
        "std(%)": test_df['KOSDAQ_Daily(%)'].std()*100,
        "Sharp": test_df['KOSDAQ_Daily(%)'].mean()  / test_df['KOSDAQ_Daily(%)'].std()*math.sqrt(252),
        "Port Return(%)": test_df['KR_Cum_Return(%)'].iloc[-1]*100,
        "Port std(%)":  (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce')).std()*100,
        "Port Sharp":(pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce')).mean() /(pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce')).std()*math.sqrt(252),
        "L/S Port Sharp (100%)": - ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (70%)": - ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2*0.7 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (50%)": - ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2*0.5 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (30%)": - ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2*0.3 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / ((test_df['KOSPI_Daily(%)']+test_df['KOSDAQ_Daily(%)'])/2 - (pd.to_numeric(test_df['KR_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252)
    },
    {
        "Name": "TWSE",
        "Return(%)": test_df['TWSE_Cumulative_Return'].iloc[-1]*100,
        "std(%)": test_df['TWSE_Daily(%)'].std()*100,
        "Sharp": test_df['TWSE_Daily(%)'].mean()  / test_df['TWSE_Daily(%)'].std()*math.sqrt(252),
        "Port Return(%)": test_df['TW_Cum_Return(%)'].iloc[-1]*100,
        "Port std(%)":  (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce')).std()*100,
        "Port Sharp": (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce')).mean() / (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce')).std()*math.sqrt(252),
        "L/S Port Sharp (100%)": - (test_df['TWSE_Daily(%)'] - (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / (test_df['TWSE_Daily(%)'] - (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (70%)": - (test_df['TWSE_Daily(%)']*0.7 - (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / (test_df['TWSE_Daily(%)'] - (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (50%)": - (test_df['TWSE_Daily(%)']*0.5 - (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / (test_df['TWSE_Daily(%)'] - (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252),
        "L/S Port Sharp (30%)": - (test_df['TWSE_Daily(%)']*0.3 - (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce'))).mean() / (test_df['TWSE_Daily(%)'] - (pd.to_numeric(test_df['TW_Return(%)'].str.replace(',', ''), errors='coerce'))).std()*math.sqrt(252)
    }
    
    
]
performance_df = pd.DataFrame(performance)
performance_df = performance_df.to_html(escape=False,index=False)

st.write('Port Vs Index Performance')
st.write(performance_df, unsafe_allow_html=True)
#st.dataframe(performance_df)


width_size = 800
# Create a time series bar chart
st.title(' ')

st.write('Port_Performance_Cum_Return(%)')
fig0 = go.Figure()
fig0.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['PORT_Cum_Return(%)'] , mode='lines', name='Port_Cumulative'))
#fig0.add_trace(go.Bar(x=test_df['DATES'], y=test_df['PORT_daily_return(%)'], name='Port_Return_Daily'))

st.plotly_chart(fig0)
st.write('Japan Market')
fig1 = go.Figure()

# Add bar traces for 'NKY' and 'KOSPI200'

fig1.add_trace(go.Bar(x=test_df['DATES'], y=test_df['NKY_Daily(%)'], name='NKY225'))
fig1.add_trace(go.Bar(x=test_df['DATES'], y=test_df['JPN_Return(%)'], name='JPN_Port_Return'))
#fig1.add_trace(go.Bar(x=test_df['DATES'], y=test_df['NKY_Daily(%)_adj'], name='NKY_Daily(%)_adj'))
fig1.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['JP_LS'], mode='lines', name='JP_Port-BM'))

# Update x-axis to treat 'DATES' as a date
fig1.update_xaxes(type='category', title_text='Date')
fig1.update(
    layout=dict(
        width=950  # Set the width to 800 pixels
    )
)
st.plotly_chart(fig1)

fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['JPN_Cum_Return(%)'], mode='lines', name='JP_Port'))
fig5.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['NKY_Cumulative_Return'], mode='lines', name='Nikkei'))
fig5.update_xaxes(type='category', title_text='Date')
fig5.update_layout(width=width_size) 
fig5.update(
    layout=dict(
        width=900  # Set the width to 800 pixels
    )
)
st.plotly_chart(fig5)

fig4 = go.Figure()
fig4.add_trace(go.Bar(x=test_df['DATES'], y=test_df['JPN_Size'], name='Japan'))
fig4.update_xaxes(type='category', title_text='Date')
fig4.update(
    layout=dict(
        width=800  # Set the width to 800 pixels
    )
)
st.plotly_chart(fig4)


####################################
st.write('Korea Market')
fig2 = go.Figure()

fig2.add_trace(go.Bar(x=test_df['DATES'], y=test_df['KOSDAQ_Daily(%)'], name='KOSDAQ150'))
fig2.add_trace(go.Bar(x=test_df['DATES'], y=test_df['KOSPI_Daily(%)'], name='KOSPI200'))
fig2.add_trace(go.Bar(x=test_df['DATES'], y=test_df['KR_Return(%)'], name='KR_Port_Return'))
fig2.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['KR_LS'], mode='lines', name='KR_Port-BM'))

fig2.update_xaxes(type='category', title_text='Date')
fig2.update(
    layout=dict(
        width=950  # Set the width to 800 pixels
    )
)
st.plotly_chart(fig2)

fig7 = go.Figure()
fig7.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['KR_Cum_Return(%)'], mode='lines', name='Korea'))
fig7.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['KOSPI_Cumulative_Return'], mode='lines', name='Kospi'))
fig7.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['KOSDAQ_Cumulative_Return'], mode='lines', name='Kosdaq'))
fig7.update_xaxes(type='category', title_text='Date')
fig7.update(
    layout=dict(
        width=900  # Set the width to 800 pixels
    )
)
st.plotly_chart(fig7)

fig6 = go.Figure()
fig6.add_trace(go.Bar(x=test_df['DATES'], y=test_df['KR_Size'], name='Korea'))
fig6.update_xaxes(type='category', title_text='Date')
fig6.update(
    layout=dict(
        width=800  # Set the width to 800 pixels
    )
)
st.plotly_chart(fig6)


######################################
st.write('Taiwan Market')
fig3 = go.Figure()

fig3.add_trace(go.Bar(x=test_df['DATES'], y=test_df['TWSE_Daily(%)'], name='TWSE'))
fig3.add_trace(go.Bar(x=test_df['DATES'], y=test_df['TW_Return(%)'], name='TW_Port_Return'))
fig3.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['TW_LS'], mode='lines', name='TW_Port-BM'))

fig3.update_xaxes(type='category', title_text='Date')
fig3.update(
    layout=dict(
        width=950  # Set the width to 800 pixels
    )
)
st.plotly_chart(fig3)

fig9 = go.Figure()
fig9.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['TW_Cum_Return(%)'], mode='lines', name='Taiwan'))
fig9.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['TWSE_Cumulative_Return'], mode='lines', name='TWSE'))
fig9.update_xaxes(type='category', title_text='Date')
fig9.update(
    layout=dict(
        width=900  # Set the width to 800 pixels
    )
)
st.plotly_chart(fig9)


fig8 = go.Figure()
fig8.add_trace(go.Bar(x=test_df['DATES'], y=test_df['TW_Size'], name='Taiwan'))
fig8.update_xaxes(type='category', title_text='Date')
fig8.update(
    layout=dict(
        width=800  # Set the width to 800 pixels
    )
)
st.plotly_chart(fig8)



##################################
#st.write('Port Size by Market (Won)')

#fig4 = go.Figure()

#fig4.add_trace(go.Bar(x=test_df['DATES'], y=test_df['JPN_Size'], name='Japan'))
#fig4.add_trace(go.Bar(x=test_df['DATES'], y=test_df['KR_Size'], name='Korea'))
#fig4.add_trace(go.Bar(x=test_df['DATES'], y=test_df['TW_Size'], name='Taiwan'))

#fig4.update_xaxes(type='category', title_text='Date')


#st.plotly_chart(fig4)

#######################################
#st.write('Port Return(%)')

#fig5 = go.Figure()

#fig5.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['JPN_Cum_Return(%)'], mode='lines', name='Japan'))
#fig5.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['KR_Cum_Return(%)'], mode='lines', name='Korea'))
#fig5.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['TW_Cum_Return(%)'], mode='lines', name='Taiwan'))
#fig5.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['PORT_Cum_Return(%)'], mode='lines', name='PORT'))


#fig5.update_xaxes(type='category', title_text='Date')


#st.plotly_chart(fig5)


######################################
#st.write('Index Cumulative Return(%)')

#fig6 = go.Figure()

#fig6.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['NKY_Cumulative_Return'], mode='lines', name='Nikkei'))
#fig6.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['KOSPI_Cumulative_Return'], mode='lines', name='Kospi'))
#fig6.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['KOSDAQ_Cumulative_Return'], mode='lines', name='Kosdaq'))
#fig6.add_trace(go.Scatter(x=test_df['DATES'], y=test_df['TWSE_Cumulative_Return'], mode='lines', name='TWSE'))


#fig6.update_xaxes(type='category', title_text='Date')


#st.plotly_chart(fig6)

st.write(df, unsafe_allow_html=True)
st.write(sorted_sum_by_value, unsafe_allow_html=True)

#st.dataframe(df)

#st.dataframe(test_df)



