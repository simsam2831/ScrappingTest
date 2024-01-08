import streamlit as st
from scraper import *
from database import create_connection, get_all_countries
from historique import show_historique


st.set_page_config(page_title="Recherche de Roadtrips", layout="wide")
st.session_state.setdefault('page', 'home')

if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

def display_title(country):
    st.markdown(f"<h1 style='text-align: center;'>Road trips {country}</h1>", unsafe_allow_html=True)

def change_to_historique():
    st.session_state['page'] = 'historique'

def change_to_oepnAi():
    st.session_state['page'] = 'openai'

with st.sidebar:
    st.header("Options")
    conn = create_connection("/Users/simondaniel/Desktop/Scraping-project/scraper/data.db")
    countries = get_all_countries(conn)
    selected_country = st.selectbox('Choisissez un pays', countries)
    number_of_roadtrips = st.slider('Combien de roadtrips voulez-vous afficher ?', 1, 10, 5)
    st.sidebar.write("")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("Historique"):
            change_to_historique()

    with col2:
        if st.button("Open AI"):
            change_to_oepnAi()

if st.session_state['page'] == 'home':

    if selected_country:
        display_title(selected_country) 
        country_url = get_country_url(selected_country)
        roadtrip_names = get_roadtrip_names(country_url)
        roadtrip_durations = get_roadtrip_duration(country_url)
        roadtrip_prices = get_roadtrip_prices(country_url)
    
        if selected_country:
            country_url = get_country_url(selected_country)
            pays_roadtrip(country_url,selected_country)

        for i in range(0, len(roadtrip_names), 3):
            cols = st.columns(2) 
            for j in range(2):
                index = i + j
                if index <= number_of_roadtrips:
                    with cols[j]:
                        st.subheader(roadtrip_names[index])
                        st.write(f"Durée : {roadtrip_durations[index]}")
                        st.write(f"Prix : à partir de {roadtrip_prices[index]}")
                        # st.image(roadtrip_img, caption='Nom du Roadtrip', use_column_width=True)
                        # st.write(f"Description : {roadtrip_descriptions[index]}")

elif st.session_state['page'] == 'historique':
    show_historique()

else : 
    change_to_oepnAi()