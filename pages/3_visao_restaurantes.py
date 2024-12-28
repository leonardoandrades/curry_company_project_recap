import pandas as pd
from datetime import datetime as dt
import streamlit as st
import plotly.express as px
import folium
from haversine import haversine
import plotly.graph_objects as go
# from streamlit_folium import folium_static

#limpeza
df = pd.read_csv('dataset/train.csv')
df1 = df.copy()

#0. Remove NaN
df1 = df1.loc[df1["Delivery_person_Age"] != "NaN "]
df1 = df1.loc[df1["multiple_deliveries"] != "NaN "]
df1 = df1.loc[df1["Weatherconditions"] != "conditions NaN"]
df1 = df1.loc[df1["City"] != "NaN "]
df1 = df1.loc[df1["Festival"] != "NaN "]

#1. Changing Types Columns
df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype(int)
df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype(float)
df1["Order_Date"] = pd.to_datetime(df1["Order_Date"],format="%d-%m-%Y")
df1["multiple_deliveries"] = df1["multiple_deliveries"].astype(int)
df1 = df1.reset_index(drop=True)

#3. Remove spaces V2
df1.loc[:,"ID"] = df1.loc[:,"ID"].str.strip()
df1.loc[:,"Delivery_person_ID"] = df1.loc[:,"Delivery_person_ID"].str.strip()
df1.loc[:,"Road_traffic_density"] = df1.loc[:,"Road_traffic_density"].str.strip()
df1.loc[:,"Type_of_order"] = df1.loc[:,"Type_of_order"].str.strip()
df1.loc[:,"Type_of_vehicle"] = df1.loc[:,"Type_of_vehicle"].str.strip()
df1.loc[:,"Festival"] = df1.loc[:,"Festival"].str.strip()
df1.loc[:,"City"] = df1.loc[:,"City"].str.strip()

#4 Edit Weatherconditions
df1["Weatherconditions"] = df1["Weatherconditions"].str.split().str.get(-1)
df1['Week'] = df1['Order_Date'].dt.strftime('%U')

#Limpeza Coluna time_taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

#Add Distance Col
cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
df1['Distance'] = df1.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)


st.set_page_config(page_title='Visão Restaurantes',page_icon='🍽️',layout='wide')

#------SidebarStreamlit------

st.header('Marketplace - Visão Restaurantes')
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Selecione uma data:')
date_slider = st.sidebar.slider('Até qual data?',min_value=dt(2022,2,11),max_value=dt(2022,4,6),value=dt(2022,4,6),format='DD-MM-YYYY')
st.sidebar.markdown("""---""")
traffic_option = st.sidebar.multiselect ('Quais são as condições de Transito',['Low','Medium','High','Jam'],default=['Low','Medium','High','Jam'])

df1 = df1.loc[(df1['Order_Date'] < date_slider)&(df1['Road_traffic_density'].isin(traffic_option)),:]

#------LayoutStreamlit-----15min

#---------------------------------------------------------------------------------------------------
tab1, tab2 = st.tabs(['Visão Gerêncial',' '])

with tab1:
    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            st.metric(label='Qtd Delivers:', value=len(df1[['Delivery_person_ID']].drop_duplicates()))
        
        with col2:
            st.metric(label='Distancia Média:', value=round(df1['Distance'].mean(),1))

        with col3:
            st.metric(label='Avg C/Festival:', value=round(df1.loc[df1['Festival']=='Yes',['Time_taken(min)']].mean(),1))

        with col4:
            st.metric(label='DesvP C/Festival:', value=round(df1.loc[df1['Festival']=='Yes',['Time_taken(min)']].std(),1))
        
        with col5:
            st.metric(label='Avg S/Festival:', value=round(df1.loc[df1['Festival']=='No',['Time_taken(min)']].mean(),1))

        with col6:
            st.metric(label='DesvP S/Festival:', value=round(df1.loc[df1['Festival']=='No',['Time_taken(min)']].std(),1))
            
    
    st.markdown("""---""")
    
#---------------------------------------------------------------------------------------------------
    with st.container():
        col1,col2 = st.columns(2)

        with col1:
            st.markdown('A distancia média por Cidade')
            cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            df1['Distance'] = df1.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
            df_aux = df1.loc[:,['City','Distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=df_aux['City'],values=df_aux['Distance'],pull=[0,0.1,0])])
            st.plotly_chart(fig,use_container_width=True)

        with col2:      
            st.markdown('Tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego')
            df_aux = df1.loc[:,['City','Road_traffic_density','Time_taken(min)']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']}).reset_index()
            df_aux.columns = ['City','Road_traffic_density','mean', 'std']
            fig = px.sunburst(df_aux,path=['City','Road_traffic_density'],values='mean',color='std',color_continuous_scale='balance',color_continuous_midpoint=(df_aux['std'].mean()))
            st.plotly_chart(fig,use_container_width=True)

    st.markdown("""---""")

#---------------------------------------------------------------------------------------------------
    with st.container():
        col1,col2 = st.columns(2)

        with col1:
            st.markdown('Tempo médio e o desvio padrão de entrega por cidade')
            df_aux = df1.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']}).reset_index()
            df_aux.columns = ['City','mean', 'std']
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['mean'],error_y=dict(type='data',array=df_aux['std'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, use_container_width=True)


        with col2:
            st.markdown('Tempo médio e o desvio padrão de entrega por cidade e tipo de pedid')
            df_aux = df1.loc[:,['City','Type_of_order','Time_taken(min)']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']}).reset_index()
            df_aux.columns = ['City','Type_of_order','mean', 'std']
            st.dataframe(df_aux,use_container_width=True)

    st.markdown("""---""")