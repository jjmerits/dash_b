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
    #print(df)
    df = df.fillna('')
    df['Value'] = df['Value'].apply(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) and not pd.isnull(x) else x)

    df_style = df.style.apply(lambda row: ['background-color: lightgreen' if row['Port'] == 1 else '' for _, row in df.iterrows()], axis=1)
    df = df.astype(str)
    df = df.to_html(escape=False,index=False)

    test_df = pd.read_csv(url_1)
    print(test_df)
    test_df.columns = test_df.iloc[0]
    test_df = test_df.iloc[1:]
    test_df = test_df.drop(test_df.columns[1:6], axis=1)
    test_df = test_df.dropna(subset=['NKY'])
    test_df = test_df.dropna(subset=['JPN_Size'])
    test_df['DATES'] = pd.to_datetime(test_df['DATES'])
    # Filter out weekends (assuming Saturday and Sunday are weekends)
    test_df = test_df[(test_df['DATES'].dt.dayofweek != 5) & (test_df['DATES'].dt.dayofweek != 6)]
    # Define the new column names as a list
    new_column_names = ['DATES','NKY', 'NKY_Daily(%)', 'KOSPI200', 'KOSPI_Daily(%)', 'KOSDAQ150', 'KOSDAQ_Daily(%)','TWSE', 'TWSE_Daily(%)','JPN_Size','KR_Size','TW_Size','JPN_Return','KR_Return','TW_Return','Size_Sum','JPN_Return(%)','KR_Return(%)','TW_Return(%)']
    
  

    # Assign the new column names to the DataFrame
    test_df.columns = new_column_names
    test_df['JPN_Cum_Return(%)'] = pd.to_numeric(test_df['JPN_Return'].str.replace(',', ''), errors='coerce') /  pd.to_numeric(test_df['JPN_Size'].str.replace(',', ''), errors='coerce').max()
    test_df['KR_Cum_Return(%)'] = pd.to_numeric(test_df['KR_Return'].str.replace(',', ''), errors='coerce') /  pd.to_numeric(test_df['KR_Size'].str.replace(',', ''), errors='coerce').max()
    test_df['TW_Cum_Return(%)'] = pd.to_numeric(test_df['TW_Return'].str.replace(',', ''), errors='coerce') /  pd.to_numeric(test_df['TW_Size'].str.replace(',', ''), errors='coerce').max()
    test_df['PORT_Cum_Return(%)'] = (pd.to_numeric(test_df['JPN_Return'].str.replace(',', ''), errors='coerce')+pd.to_numeric(test_df['KR_Return'].str.replace(',', ''), errors='coerce')+pd.to_numeric(test_df['TW_Return'].str.replace(',', ''), errors='coerce')) /  pd.to_numeric(test_df['Size_Sum'].str.replace(',', ''), errors='coerce').max()

    test_df['NKY_Cumulative_Return'] = (1 + pd.to_numeric(test_df['NKY_Daily(%)'])).cumprod() - 1
    test_df['KOSPI_Cumulative_Return'] = (1 + pd.to_numeric(test_df['KOSPI_Daily(%)'])).cumprod() - 1
    test_df['KOSDAQ_Cumulative_Return'] = (1 + pd.to_numeric(test_df['KOSDAQ_Daily(%)'])).cumprod() - 1
    test_df['TWSE_Cumulative_Return'] = (1 + pd.to_numeric(test_df['TWSE_Daily(%)'])).cumprod() - 1

    test_df['JP_LS'] = test_df['JPN_Cum_Return(%)'] - test_df['NKY_Cumulative_Return']
    test_df['KR_LS'] = test_df['KR_Cum_Return(%)'] - (test_df['KOSPI_Cumulative_Return'] + test_df['KOSDAQ_Cumulative_Return'])/2
    test_df['TW_LS'] = test_df['TW_Cum_Return(%)'] - test_df['TWSE_Cumulative_Return']
#######################################

    test_df['NKY_Daily(%)'] =   pd.to_numeric(test_df['NKY_Daily(%)'])
    test_df['KOSPI_Daily(%)'] = pd.to_numeric(test_df['KOSPI_Daily(%)'])
    test_df['KOSDAQ_Daily(%)'] = pd.to_numeric(test_df['KOSDAQ_Daily(%)'])
    test_df['TWSE_Daily(%)'] = pd.to_numeric(test_df['TWSE_Daily(%)'])

    test_df['JPN_Size'] = pd.to_numeric(test_df['JPN_Size'].str.replace(',', ''), errors='coerce')
    test_df['KR_Size'] = pd.to_numeric(test_df['KR_Size'].str.replace(',', ''), errors='coerce')
    test_df['TW_Size'] = pd.to_numeric(test_df['TW_Size'].str.replace(',', ''), errors='coerce')
    
    test_df['NKY_Daily(%)_adj'] = test_df['NKY_Daily(%)']*(test_df['JPN_Size']/test_df['JPN_Size'].max())
    test_df['KOSPI_Daily(%)_adj'] = test_df['KOSPI_Daily(%)']*(test_df['KR_Size']/test_df['KR_Size'].max())
    test_df['KOSDAQ_Daily(%)_adj'] = test_df['KOSDAQ_Daily(%)']*(test_df['KR_Size']/test_df['KR_Size'].max())
    test_df['TWSE_Daily(%)_adj'] = test_df['TWSE_Daily(%)']*(test_df['TW_Size']/test_df['TWSize'].max())

    test_df['NKY_Cumulative_Return_adj'] = (1 + pd.to_numeric(test_df['NKY_Daily(%)_adj'])).cumprod() - 1
    test_df['KOSPI_Cumulative_Return_adj'] = (1 + pd.to_numeric(test_df['KOSPI_Daily(%)_adj'])).cumprod() - 1
    test_df['KOSDAQ_Cumulative_Return_adj'] = (1 + pd.to_numeric(test_df['KOSDAQ_Daily(%)_adj'])).cumprod() - 1
    test_df['TWSE_Cumulative_Return_adj'] = (1 + pd.to_numeric(test_df['TWSE_Daily(%)_adj'])).cumprod() - 1

    test_df['JP_LS_adj'] = test_df['JPN_Cum_Return(%)'] - test_df['NKY_Cumulative_Return_adj']
    test_df['KR_LS_adj'] = test_df['KR_Cum_Return(%)'] - (test_df['KOSPI_Cumulative_Return_adj'] + test_df['KOSDAQ_Cumulative_Return_adj'])/2
    test_df['TW_LS_adj'] = test_df['TW_Cum_Return(%)'] - test_df['TWSE_Cumulative_Return_adj']
    
    #test_df['Total_Return(%)'] = test_df['Total_Return(%)'] 
    test_df['DATES'] = pd.to_datetime(test_df['DATES'])


 
        
except Exception as e:
    df = pd.DataFrame(columns=['No Excel Sheet Found'])

# 데이터 표시
#st.title('Vs benchmark chart')
st.write("9/5 수익률은 8/14일 부터의 누적 수익률")
# Create a layout with two columns

width_size = 800
# Create a time series bar chart
st.write('Japan Market')
fig1 = go.Figure()

# Add bar traces for 'NKY' and 'KOSPI200'

fig1.add_trace(go.Bar(x=test_df['DATES'], y=test_df['NKY_Daily(%)'], name='NKY225'))
fig1.add_trace(go.Bar(x=test_df['DATES'], y=test_df['JPN_Return(%)'], name='JPN_Port_Return'))
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
#st.dataframe(df)




