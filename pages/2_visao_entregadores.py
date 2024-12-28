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


st.set_page_config(page_title='Visão Entregadores',page_icon='🚚',layout='wide')

#------SidebarStreamlit------

st.header('Marketplace - Visão Entregadores')
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Selecione uma data:')
date_slider = st.sidebar.slider('Até qual data?',min_value=dt(2022,2,11),max_value=dt(2022,4,6),value=dt(2022,4,6),format='DD-MM-YYYY')
st.sidebar.markdown("""---""")
traffic_option = st.sidebar.multiselect ('Quais são as condições de Transito',['Low','Medium','High','Jam'],default=['Low','Medium','High','Jam'])

df1 = df1.loc[(df1['Order_Date'] < date_slider)&(df1['Road_traffic_density'].isin(traffic_option)),:]

#------LayoutStreamlit-----13min

#---------------------------------------------------------------------------------------------------
tab1, tab2 = st.tabs(['Visão Gerêncial',' '])

with tab1:
    with st.container():
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            st.metric(label='Maior Idade:', value=df1.loc[:,'Delivery_person_Age'].max())
        
        with col2:
            st.metric(label='Menor Idade:', value=df1.loc[:,'Delivery_person_Age'].min())

        with col3:
            st.metric(label='Melhor condição Veiculo:', value=df1.loc[:,'Vehicle_condition'].max())

        with col4:
            st.metric(label='Pior condição Veiculo:', value=df1.loc[:,'Vehicle_condition'].min())
    
    st.markdown("""---""")
    
#---------------------------------------------------------------------------------------------------
    with st.container():
        st.title('Avaliações:')
        col1,col2 = st.columns(2)

        with col1:
            st.markdown('Avaliações média por Entregador')
            df_aux = (df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
                         .rename(columns={'Delivery_person_ID':'ID','Delivery_person_Ratings': 'Ratings' }))
            st.dataframe(df_aux,use_container_width=True)

        with col2:
            st.markdown('Avaliações média por tipo trafego')
            df_aux = df1.loc[:,['Road_traffic_density','Delivery_person_Ratings']].groupby('Road_traffic_density').agg(['mean','std'])
            df_aux.columns = ['mean','std']
            df_aux.reset_index()
            st.dataframe(df_aux,use_container_width=True)

            st.markdown('Avaliações média por Condições Climáticas')
            df_aux = df1.loc[:,['Weatherconditions','Delivery_person_Ratings']].groupby('Weatherconditions').agg(['mean','std'])
            df_aux.columns = ['mean','std']
            df_aux.reset_index()
            st.dataframe(df_aux,use_container_width=True)
    st.markdown("""---""")

#---------------------------------------------------------------------------------------------------
    with st.container():
        st.title('Velocidade na Entrega:')
        col1,col2 = st.columns(2)

        with col1:
            st.markdown('Top10 entregadores mais rápidos por cidade')
            
            df_urban = (df1.loc[df1['City']=='Urban',['Delivery_person_ID','City','Time_taken(min)']]
                          .groupby(['Delivery_person_ID','City']).mean().sort_values(['City','Time_taken(min)'], ascending=True).reset_index().head(10))
            
            df_metro = (df1.loc[df1['City']=='Metropolitian',['Delivery_person_ID','City','Time_taken(min)']]
                          .groupby(['Delivery_person_ID','City']).mean().sort_values(['City','Time_taken(min)'], ascending=True).reset_index().head(10))
            
            df_semi = (df1.loc[df1['City']=='Semi-Urban',['Delivery_person_ID','City','Time_taken(min)']]
                         .groupby(['Delivery_person_ID','City']).mean().sort_values(['City','Time_taken(min)'], ascending=True).reset_index().head(10))
            
            df_all = pd.concat([df_urban,df_metro,df_semi]).reset_index(drop=True).rename(columns={'Time_taken(min)':'Time'})
            st.dataframe(df_all,use_container_width=True)

        with col2:
            st.markdown('Top10 entregadores mais lentos por cidade')
            df_urban = (df1.loc[df1['City']=='Urban',['Delivery_person_ID','City','Time_taken(min)']]
                           .groupby(['Delivery_person_ID','City']).mean().sort_values(['City','Time_taken(min)'], ascending=False).reset_index().head(10))

            df_metro = (df1.loc[df1['City']=='Metropolitian',['Delivery_person_ID','City','Time_taken(min)']]
                           .groupby(['Delivery_person_ID','City']).mean().sort_values(['City','Time_taken(min)'], ascending=False).reset_index().head(10))

            df_semi = (df1.loc[df1['City']=='Semi-Urban',['Delivery_person_ID','City','Time_taken(min)']]
                          .groupby(['Delivery_person_ID','City']).mean().sort_values(['City','Time_taken(min)'], ascending=False).reset_index().head(10))

            df_all = pd.concat([df_urban,df_metro,df_semi]).reset_index(drop=True).rename(columns={'Time_taken(min)':'Time'})
            st.dataframe(df_all,use_container_width=True)

