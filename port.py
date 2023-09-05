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

#url = 'https://raw.githubusercontent.com/jjmerits/Dashboard/main/test_df_all.csv'
#test_df = pd.read_csv(url)

#name_list = test_df['Name'].unique().tolist()
#df = test_df[test_df['Name'] == name_list[4]]


#df['date'] = df['date'].apply(lambda x: datetime.strptime(x,'%Y-%m-%d %H:%M:%S').strftime('%Y/%m/%d'))
#df.set_index("date", inplace = True)


st.set_page_config(layout='wide')
#fig = go.Figure()
#fig.add_trace(go.Bar(x=df[['actual']].index,y=df['actual'].to_list(),name='actual'))
#fig.add_trace(go.Bar(x=df[['actual']].index,y=df['forecast'].to_list(),name='forecast'))
#fig.update_layout(barmode='group',title=name_list[4], yaxis=dict(title = 'y/y %'))

#st.plotly_chart(fig,use_container_width=True)

# Initialize connection.
conn = pymongo.MongoClient(st.secrets.db_credentials.HOST,st.secrets.db_credentials.PORT, username=st.secrets.db_credentials.DB_USER,password=st.secrets.db_credentials.DB_TOKEN, tls=True, tlsAllowInvalidCertificates=True)

# Pull data from the collection.
# Uses st.cache to only rerun when the query changes or after 10 min.
event_list = conn.econdata.glob.find({}).distinct('event')
cursor = conn.econdata.glob.find({'event':{"$in":event_list}},{'_id':False})
df_all=pd.DataFrame(cursor)

df_all = df_all.loc[df_all['date'].between('2017-01-01','2100-12-31', inclusive=False)]

df_all['date'] = df_all['date'].apply(lambda x: datetime.strftime(x,'%Y/%m/%d'))
#df.set_index("date", inplace = True)


#plot graph
def plot_graph(x,y=""):
  df_x = df[(df['event'] == x) | (df['event'] == y)]
  df_x = df_x.loc[df_x[['date','actual','forecast']].drop_duplicates().index]
  df_x.sort_values('date', inplace = True)
  df_x.set_index("date", inplace = True)
  fig = go.Figure()
  fig.add_trace(go.Bar(x=df_x[['actual']].index,y=df_x['actual'].to_list(),name='actual'))
  fig.add_trace(go.Bar(x=df_x[['actual']].index,y=df_x['forecast'].to_list(),name='forecast'))
  fig.update_layout(barmode='group',title=x, yaxis=dict(title = '')) #title=x+" "+df_x['currency'].values[1]
  #fig.show()
  st.plotly_chart(fig,use_container_width=True)

st.header("PMI")
st.write("US")
df = df_all[df_all['currency'] == 'USD']

col1, col2 = st.columns(2)

with col1:
  plot_graph("ISM Manufacturing PMI")

with col2:
  plot_graph("ISM Non-Manufacturing PMI","ISM Services PMI")
##########################    

st.write("EU")
df = df_all[df_all['currency'] == 'EUR']
col1, col2 = st.columns(2)

with col1:
  plot_graph("Flash Manufacturing PMI")

with col2:
  plot_graph("Flash Services PMI")
  
##########################  

st.write("UK")
df = df_all[df_all['currency'] == 'GBP']
col1, col2 = st.columns(2)

with col1:
  plot_graph("Flash Manufacturing PMI")

with col2:
  plot_graph("Flash Services PMI")
  
##########################  
st.write("China")
df = df_all[df_all['currency'] == 'CNY']

col1, col2 = st.columns(2)

with col1:
  plot_graph("Fixed Asset Investment ytd/y")

with col2:
  plot_graph("Industrial Production y/y")

  ##########################  
st.write("Aus")
df = df_all[df_all['currency'] == 'AUD']
col1, col2 = st.columns(2)

with col1:
  plot_graph("Flash Manufacturing PMI")

with col2:
  plot_graph("Flash Services PMI")
########################################################################################

st.header("CPI/PPI")
st.write("US")
df = df_all[df_all['currency'] == 'USD']
col1, col2 = st.columns(2)

with col1:
  plot_graph("Core CPI m/m")

with col2:
  plot_graph("Core PPI m/m")
##########################  
st.write("EU")
df = df_all[df_all['currency'] == 'EUR']
col1, col2 = st.columns(2)

with col1:
  plot_graph("Final Core CPI y/y")

with col2:
  plot_graph("PPI m/m")
  
##########################    
st.write("UK")
df = df_all[df_all['currency'] == 'GBP']
col1, col2 = st.columns(2)

with col1:
  plot_graph("Core CPI y/y")

with col2:
  plot_graph("Consumer Inflation Expectations")
  
col1, col2 = st.columns(2)

with col1:
  plot_graph("PPI Input m/m")

with col2:
  plot_graph("PPI Output m/m")
    

##########################  
st.write("China")
df = df_all[df_all['currency'] == 'CNY']

col1, col2 = st.columns(2)

with col1:
  plot_graph("PPI y/y")

with col2:
  plot_graph("CPI y/y") 
##########################  

st.write("Aus")
df = df_all[df_all['currency'] == 'AUD']
col1, col2 = st.columns(2)

with col1:
  plot_graph("PPI q/q")

with col2:
  plot_graph("CPI q/q")
  
col1, col2 = st.columns(2)

with col1:
  plot_graph("Commodity Prices y/y")

with col2:
  plot_graph("Company Operating Profits q/q")
###############################################################################################  
st.header("Retail/Consumer")

st.write("US")
df =df_all[df_all['currency'] == 'USD']

col1, col2 = st.columns(2)

with col1:
  plot_graph("Core Retail Sales m/m")

with col2:
  plot_graph("Non-Farm Employment Change")
##########################  
col1, col2 = st.columns(2)

with col1:
  plot_graph("Wards Total Vehicle Sales")

with col2:
  plot_graph("CB Consumer Confidence")
##########################  
st.write("EU")
df =df_all[df_all['currency'] == 'EUR']

col1, col2 = st.columns(2)

with col1:
  plot_graph("Retail Sales m/m")

with col2:
  plot_graph("Consumer Confidence")
########################## #############################################################

def tz_diff(date, tz1, tz2):
    '''
    Returns the difference in hours between timezone1 and timezone2
    for a given date.
    '''
    date = pd.to_datetime(date)
    return (tz1.localize(date) -
            tz2.localize(date).astimezone(tz1)) \
               .seconds/3600
est = pytz.timezone('US/Eastern')
seo = pytz.timezone('Asia/Seoul')
time_diff = tz_diff(datetime.today().strftime('%Y-%m-%d'), est, seo)
est_time = datetime.today().astimezone(seo).astimezone(est).strftime('%d/%m/%y %H:%M:%S')
seo_time = datetime.today().astimezone(seo).strftime('%d/%m/%y %H:%M:%S')
st.header('News Flow (TimeZone = US/Eastern)')
st.write(f'Last updated time (US/EST): {est_time} / (Asia/Seoul):{seo_time}')

def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = link.split('=')
    return f'<a target="_blank" href="{link}">{"link"}</a>'

def tz_diff(date, tz1, tz2):
    '''
    Returns the difference in hours between timezone1 and timezone2
    for a given date.
    '''
    date = pd.to_datetime(date)
    return (tz1.localize(date) -
            tz2.localize(date).astimezone(tz1)) \
               .seconds/3600
  
def gnews_html(q_str, cn='US', la='english'):
  st.write(q_str)
  google_news = gnews.GNews()
  google_news.country = cn
  google_news.language = la
  google_news.period = '12h'
  google_news.results = 30
  df = google_news.get_news(q_str)
  df = pd.DataFrame.from_records(df)
  df = df.reset_index().rename({'index':'importance'}, axis = 'columns')
  df['published date'] = df['published date'].apply(lambda x: datetime.strptime(x, '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc))
  df['published date'] = df['published date'].dt.tz_convert('US/Eastern')
  #df['published date'] = df['published date'].apply(lambda x: x.strftime('%d/%m/%y %H:%M:%S'))
  df['published date'] = datetime.today().astimezone(seo).astimezone(est) - df['published date']
  df['published date'] = df['published date'].apply(lambda x: int(x.total_seconds()//3600))
  df.rename(columns={'published date': 'hour ago'}, inplace = True)
  df = df.iloc[0:50,]
    
  df.sort_values('hour ago', inplace = True, ascending = True)
  df.drop(['description','publisher'], axis=1, inplace = True)
  # link is the column with hyperlinks
  df['url'] = df['url'].apply(make_clickable)
  #df.reset_index(drop=True, inplace=True)
  df = df.iloc[0:30,].to_html(escape=False,index=False)
  st.write(df, unsafe_allow_html=True)
##########################  
col1, col2 = st.columns(2)
with col1:
  gnews_html("Dollar Index ~market","US")
  
with col2:
  gnews_html("FOMC ~market")
##########################
col1, col2 = st.columns(2)
with col1:
  gnews_html("Chinese Yuan ~market","HK")
  
with col2:
  gnews_html("AUD currency ~market","AU")
##########################

st.header(" ")
ts = time.time()
numofweek = str(datetime.fromtimestamp(ts).isocalendar()[1])
numofyear = str(datetime.fromtimestamp(ts).isocalendar()[0])
url = f'https://raw.githubusercontent.com/jjmerits/Dashboard/main/01010{numofweek}{numofyear}final.HTML'
#with open(url) as f:
t = requests.get(url,verify=False)
st.markdown(t.text, unsafe_allow_html=True)
  
##########################


#########################



#st.set_page_config(layout='centered')
#st.write(df.head(5))

conn.close()
