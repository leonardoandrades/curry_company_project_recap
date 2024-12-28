import pandas as pd
from datetime import datetime as dt
import streamlit as st
import plotly.express as px
import folium
from haversine import haversine
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


st.set_page_config(page_title='Visão Empresa',page_icon='🏢',layout='wide')

#------SidebarStreamlit------

st.header('Marketplace - Visão Cliente')
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Selecione uma data:')
date_slider = st.sidebar.slider('Até qual data?',min_value=dt(2022,2,11),max_value=dt(2022,4,6),value=dt(2022,6,4),format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

traffic_option = st.sidebar.multiselect ('Quais são as condições de Transito',['Low','Medium','High','Jam'],default=['Low','Medium','High','Jam'])

#df1 = df1.loc[df1['Order_Date'] < date_slider,:]

df1 = df1.loc[(df1['Order_Date'] < date_slider)&(df1['Road_traffic_density'].isin(traffic_option)),:]

# df1 = df1.loc[df1['Road_traffic_density'].isin(traffic_option),:]


st.dataframe(df1)

#------LayoutStreamlit-----

tab1, tab2 = st.tabs(['Visão Gerêncial','Visão Tática'])

#----------------
with tab1:
    with st.container():
        st.header('Pedidos por dia')
        grafh1 = df1[["ID","Order_Date"]].groupby(["Order_Date"]).count().reset_index()
        fig = px.bar(grafh1, x="Order_Date", y="ID")
        st.plotly_chart(fig,use_container_width=True)

    with st.container():
        col1,col2 = st.columns(2)

        with col1:
            st.header('%Pedidos por tipo de trafego ')
            grafh3 = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            grafh3['Perc'] = grafh3['ID'] / grafh3['ID'].sum()
            fig = px.pie(grafh3, names='Road_traffic_density', values='Perc')
            st.plotly_chart(fig,use_container_width=True)

        with col2:
            st.header('Volume pedidos por cidade e trafego')
            df_aux = df1.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID')
            st.plotly_chart(fig,use_container_width=True)
#----------------
with tab2:
    with st.container():
        st.header('Pedidos por Wk')
        grafh2 = df1[['Week','ID']].groupby(['Week']).count().reset_index()
        fig = px.line(grafh2, x='Week',y='ID')
        st.plotly_chart(fig,use_container_width=True)

    with st.container():
        st.header('Qtd de entrega por Entregador')
        df1_aux = df1.loc[:,['ID','Week']].groupby(['Week']).count().reset_index().rename(columns={'ID':'Qtd Entregas'})
        df2_aux = df1.loc[:,['Delivery_person_ID','Week']].groupby('Week').nunique().reset_index().rename(columns={'Delivery_person_ID':'Qtd Delivers'})
        df = pd.merge(df1_aux,df2_aux, how='inner')
        df['Qtd Entrega'] = df['Qtd Entregas'] / df['Qtd Delivers']
        fig = px.line(df,x='Week', y='Qtd Entrega')
        st.plotly_chart(fig,use_container_width=True)
