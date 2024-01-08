import streamlit as st
import sqlite3

def get_roadtrips_by_date(conn, date):
    try:
        cur = conn.cursor()
        cur.execute("SELECT name, duration, price FROM roadtrips WHERE save_date = ?", (date,))
        return cur.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def show_historique():
    conn = sqlite3.connect("/Users/simondaniel/Desktop/Scraping-project/scraper/data.db")
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT save_date FROM roadtrips ORDER BY save_date DESC")
        all_dates = cur.fetchall()
    except sqlite3.Error as e:
        st.error(f"Erreur de base de données : {e}")
        return

    st.title("Historique des Roadtrips")

    for date in all_dates:
        with st.expander(f"Roadtrips vus le {date[0]}"):
            roadtrips = get_roadtrips_by_date(conn, date[0])
            if roadtrips:
                for i in range(0, len(roadtrips), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        index = i + j
                        if index < len(roadtrips):
                            with cols[j]:
                                st.subheader(roadtrips[index][0])  # Nom du roadtrip
                                st.text(f"Durée : {roadtrips[index][1]}")
                                st.text(f"Prix : {roadtrips[index][2]}")
            else:
                st.write("Pas de roadtrips pour cette date.")
    
    conn.close()
