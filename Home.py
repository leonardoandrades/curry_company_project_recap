import streamlit as st

st.set_page_config(page_title='Curry Company Project',page_icon='📉')

#------Sidebar
st.sidebar.success('Selecione uma das Opções acima.')

#------Page HOME
st.header('Curry Company Project')
st.markdown("""---""")
st.markdown(
    """
    Esse dashboard foi contruido para acompanhar as metricas de crescimento dos entregadores e Restaurantes.
    #### Como utilizar esse Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Metricas gerencias de comportamento.
        - Visão Tática: KPIs semanais de Crescimento.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restautantes:
        - Acompanhamento dos indicadores semanais de crescimento.

""")
st.markdown("""---""")