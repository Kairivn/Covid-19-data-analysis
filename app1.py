import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.preprocessing import LabelEncoder # type: ignore


st.title('COVID-19 India cases')
st.write('It shoes **coronavirus cases** in India')
st.sidebar.title('selector')
st.markdown('<style>body{backgroundcolor : lightblue;}</style>',unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('covid_india_cases.csv')
    df=df.dropna()
    a = df.loc[: , "Date"]
    a = list(a)
    a =[int(a[i][6:]) for i in range(len(a))]
    b= [a[i] if a[i]>=2020 else 0 for i in range(0,len(a))]
    df['new_dates'] = b
    c=list()
    for i in range (0,len(b)):
        if b[i]==0 :
            c.append(1)
            df.drop(df.index[i],inplace=True)
    df.drop(df.index[0],inplace=True)
    return df
df = load_data()



visualistaion = st.sidebar.selectbox('select chart type',('bar chart','pie chart','line chart'))
state_select  = st.sidebar.selectbox('select a region',df['Region'].unique())
status_select = st.sidebar.radio('covid-19 patent status',('confirmed cases','active cases','recovered cases','death cases'))
selected_state = df[df['Region']==state_select]
st.markdown('##  **state level analysis as per 12 December 2021**')

def get_total_dataframe(df):
    total_dataframe = pd.DataFrame({
        'Status':['Confirmed','Active','Recovered','Deaths'],
        'Number of Cases':(df.iloc[0]['Confirmed Cases'],
                           df.iloc[0]['Active Cases'],
                           df.iloc[0]['Cured/Discharged'],
                           df.iloc[0]['Death'])
        
    })
    return total_dataframe
state_total = get_total_dataframe(selected_state)


if visualistaion == 'bar chart':
    state_total_graph = px.bar(state_total, x = 'Status',y = 'Number of Cases',
                               labels = {'Number of Cases':'Number of Cases in %s'%(state_select)}, color = 'Status')
    st.plotly_chart(state_total_graph)
elif visualistaion == 'pie chart':
    if status_select == 'confirmed cases':
        st.title("Total Confirmed Cases")
        
        state_total_graph = px.pie(df, values = df['Confirmed Cases'],names = df['Region'])
        st.plotly_chart(state_total_graph)
    elif status_select == 'active cases':
        st.title("Total Active Cases")
        state_total_graph = px.pie(df, values = df['Active Cases'],names = df['Region'])
        st.plotly_chart(state_total_graph)
    elif status_select == 'death cases':
        st.title("Total Death Cases")
        state_total_graph = px.pie(df, values = df['Death'],names = df['Region'])
        st.plotly_chart(state_total_graph)
    else:
        st.title("Total recovered cases")
        state_total_graph = px.pie(df, values = df['Cured/Discharged'],names = df['Region'])
        st.plotly_chart(state_total_graph)
elif visualistaion == 'line chart':
    if status_select == 'death cases':
        st.title("Total death Cases among states")
        state_total_graph = px.line(df, x='Region',y = 'Death')
        st.plotly_chart(state_total_graph)
    elif status_select == 'confirmed cases':
        st.title("Total confirmed Cases among states")
        state_total_graph = px.line(df, x = 'Region',y = 'Confirmed Cases')
        st.plotly_chart(state_total_graph)
    elif status_select == 'active cases':
        st.title("Total active Cases among states")
        state_total_graph = px.line(df, x = 'Region',y = 'Active Cases')
        st.plotly_chart(state_total_graph)
    else:
        st.title("Total recovered Cases among states")
        state_total_graph = px.line(df, x = 'Region',y = 'Cured/Discharged')
        st.plotly_chart(state_total_graph)

def get_data_table():
    datatable = df[['Region','Confirmed Cases','Active Cases','Cured/Discharged','Death']].sort_values(by='Confirmed Cases',ascending=False)
    return datatable
datatable = get_data_table()
st.dataframe(datatable)

per_state = df[df['Region']==state_select]


st.markdown('##  **per state analysis**')

def get_total_dataframe(df):
    total_dataframe = pd.DataFrame({
        'Status':['Confirmed','Active','Recovered','Deaths'],
        'Number of Cases':(df.iloc[0]['Confirmed Cases'],
                           df.iloc[0]['Active Cases'],
                           df.iloc[0]['Cured/Discharged'],
                           df.iloc[0]['Death'])
        
    })
    return total_dataframe
state_total = get_total_dataframe(per_state)



per_state = df.groupby('Region')[['Confirmed Cases','Active Cases','Cured/Discharged','Death']].sum().reset_index()
fig = make_subplots(rows=2,cols=2,subplot_titles=('confirmed cases','active cases','recovered cases','death cases'),shared_xaxes=False)
fig.add_trace(go.Bar(x=per_state['Region'],y=per_state['Confirmed Cases']),row=1,col=1)
fig.add_trace(go.Bar(x=per_state['Region'],y=per_state['Active Cases']),row=1,col=2)
fig.add_trace(go.Bar(x=per_state['Region'],y=per_state['Cured/Discharged']),row=2,col=1)
fig.add_trace(go.Bar(x=per_state['Region'],y=per_state['Death']),row=2,col=2)
fig.update_layout(height=1000,width=None)
st.plotly_chart(fig)





per_state = df.groupby('Region')[['Confirmed Cases','Active Cases','Cured/Discharged','Death']].sum().reset_index()
fig = make_subplots(rows=2,cols=2,subplot_titles=('confirmed cases','active cases','recovered cases','death cases'),shared_xaxes=False)
fig.add_trace(go.Line(x=per_state['Region'],y=per_state['Confirmed Cases']),row=1,col=1)
fig.add_trace(go.Line(x=per_state['Region'],y=per_state['Active Cases']),row=1,col=2)
fig.add_trace(go.Line(x=per_state['Region'],y=per_state['Cured/Discharged']),row=2,col=1)
fig.add_trace(go.Line(x=per_state['Region'],y=per_state['Death']),row=2,col=2)
fig.update_layout(height=1000,width=1000)
st.plotly_chart(fig)



from datetime import date

df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
df = df[df['Date'] >= '2020-01-01'].dropna(subset=['Date'])
df = df.sort_values('Date')

# Sidebar: Select state
state_option = st.sidebar.selectbox(
    "Select State for Trend Analysis",
    sorted(df['Region'].unique()),
    key = 'state selector'
)
min_date = date(2020,4,3)
max_date = date(2022,6,30)

valid_dates = df.dropna(subset=["Date"])
min_date = valid_dates['Date'].min().date()
max_date = valid_dates['Date'].max().date()


start_date, end_date = st.sidebar.slider(
    label="Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="DD/MM/YYYY",
    key="date_range_slider"
)
st.sidebar.write(f"Showing data from {start_date} to {end_date}")

region_df = df[
    (df['Region'] == state_option) &
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date))
]



fig = go.Figure()

fig.add_trace(go.Scatter(
    x=region_df['Date'], y=region_df['Confirmed Cases'],
    mode='lines', name='Confirmed',
    line=dict(color='blue', width=1)
))

fig.add_trace(go.Scatter(
    x=region_df['Date'], y=region_df['Active Cases'],
    mode='lines', name='Active',
    line=dict(color='orange', width=1)
))

fig.add_trace(go.Scatter(
    x=region_df['Date'], y=region_df['Cured/Discharged'],
    mode='lines', name='Cured/Discharged',
    line=dict(color='green', width=1)
))

fig.add_trace(go.Scatter(
    x=region_df['Date'], y=region_df['Death'],
    mode='lines', name='Death',
    line=dict(color='red', width=1)
))


fig.update_layout(
    title=f"Day Wise COVID-19 Cases: {state_option}",
    xaxis_title="Date",
    yaxis_title="Number of Cases",
    hovermode='x unified',
    height=600,
    margin=dict(l=40, r=40, t=60, b=100)
)
fig.update_xaxes(
    tickangle=45,
    dtick="M1",  # monthly ticks
    tickformat="%b %Y"  # format like Jan 2021
)

st.plotly_chart(fig, use_container_width=True)
