# app.py - Interface Streamlit pour CampusEingang

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

st.set_page_config(page_title="CampusEingang", layout="wide", page_icon="🎓")

# Titre principal
st.title("🎓 CampusEingang - Studienstart-Assistent")
st.markdown("---")

# Configuration des fichiers de données
DATA_DIR = "campus_data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "data.json")
SURVEY_FILE = os.path.join(DATA_DIR, "survey.json")

# Données par défaut
default_data = {
    "tasks": [
        {"id": 1, "title": "Immatrikulation abschließen", "category": "Immatrikulation",
         "deadline": "2026-10-01", "link": "https://uni.example/immatrikulation", "done": False,
         "notes": "Unterlagen mitbringen"},
        {"id": 2, "title": "Chipkarte abholen", "category": "Organisatorisch",
         "deadline": "2024-01-01", "link": "", "done": False, "notes": ""}
    ],
    "next_id": 3
}

# Fonctions de gestion des données
def ensure_files():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
    if not os.path.exists(SURVEY_FILE):
        with open(SURVEY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_data():
    ensure_files()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Interface Streamlit
def main():
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Aufgaben", "➕ Neue Aufgabe", "📊 Analyse", "🗣️ Umfrage"])
    
    with tab1:
        st.header("Meine Aufgaben")
        data = load_data()
        
    # Afficher les tâches
    if data["tasks"]:
        df = pd.DataFrame(data["tasks"])
        
        # Ajouter colonne "overdue"
        def parse_deadline(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date() if s else None
            except:
                return None
        
        df["deadline_date"] = df["deadline"].apply(parse_deadline)
        today = date.today()
        df["overdue"] = df.apply(lambda r: (not r.get("done", False)) and 
                                 (r["deadline_date"] is not None) and 
                                 (r["deadline_date"] < today), axis=1)
        
        # Tri
        df = df.sort_values(by=["overdue", "deadline_date"], ascending=[False, True])
        
        # Afficher chaque tâche
        for idx, task in df.iterrows():
            with st.container():
                cols = st.columns([0.05, 0.5, 0.2, 0.1, 0.1])
                
                with cols[0]:
                    # Checkbox pour "done"
                    done = st.checkbox("", value=task.get("done", False), key=f"done_{task['id']}")
                    if done != task.get("done", False):
                        # Mettre à jour le statut
                        data = load_data()
                        for t in data["tasks"]:
                            if t["id"] == task["id"]:
                                t["done"] = done
                                break
                        save_data(data)
                        st.rerun()
                
                with cols[1]:
                    st.subheader(task["title"])
                    st.caption(f"📂 {task['category']} | 📅 {task['deadline']}")
                    if task.get("notes"):
                        st.info(task["notes"])
                    if task.get("link"):
                        st.markdown(f"[🔗 Link]({task['link']})")
                
                with cols[2]:
                    if task.get("overdue"):
                        st.error("⚠️ Überfällig")
                    elif task["deadline_date"]:
                        days_left = (task["deadline_date"] - today).days
                        if days_left < 0:
                            st.error("⚠️ Überfällig")
                        elif days_left < 7:
                            st.warning(f"🔸 {days_left} Tage")
                        else:
                            st.success(f"🟢 {days_left} Tage")
                
                with cols[3]:
                    # Bouton d'édition (à implémenter)
                    if st.button("✏️", key=f"edit_{task['id']}"):
                        st.info("Édition à implémenter")
                
                with cols[4]:
                    # BOUTON DE SUPPRESSION
                    if st.button("🗑️", key=f"delete_{task['id']}"):
                        # Demander confirmation
                        if st.checkbox(f"Sûr de supprimer '{task['title']}'?", key=f"confirm_{task['id']}"):
                            # Supprimer la tâche
                            data = load_data()
                            data["tasks"] = [t for t in data["tasks"] if t["id"] != task["id"]]
                            save_data(data)
                            st.success(f"Aufgabe '{task['title']}' gelöscht!")
                            st.rerun()
                
                st.divider()
    
    else:
        st.info("Keine Aufgaben vorhanden.")
    
    with tab2:
        st.header("Neue Aufgabe hinzufügen")
        
        with st.form("new_task"):
            title = st.text_input("Titel *", placeholder="z.B. Prüfungsanmeldung")
            category = st.selectbox("Kategorie", ["All", "Immatrikulation", "Organisatorisch", "Prüfungen", "Finanzen", "Wohnen"])
            deadline = st.date_input("Frist", min_value=date.today())
            link = st.text_input("Link (optional)", placeholder="https://...")
            notes = st.text_area("Notizen (optional)")
            
            submitted = st.form_submit_button("Aufgabe speichern")
            if submitted and title:
                data = load_data()
                new_id = data["next_id"]
                task = {
                    "id": new_id,
                    "title": title,
                    "category": category,
                    "deadline": deadline.strftime("%Y-%m-%d"),
                    "link": link,
                    "notes": notes,
                    "done": False
                }
                data["tasks"].append(task)
                data["next_id"] = new_id + 1
                save_data(data)
                st.success(f"Aufgabe '{title}' hinzugefügt!")
                st.rerun()
    
    with tab3:
        st.header("Analyse")
        data = load_data()
        df = pd.DataFrame(data["tasks"])
        
        if not df.empty:
            # Statistiques
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamtaufgaben", len(df))
            with col2:
                overdue = len(df[(df["deadline"] < datetime.now().strftime("%Y-%m-%d")) & (~df["done"])])
                st.metric("Überfällig", overdue, delta_color="inverse")
            with col3:
                done = len(df[df["done"]])
                st.metric("Erledigt", done)
            
            # Graphique par catégorie
            st.subheader("Aufgaben pro Kategorie")
            category_counts = df["category"].value_counts()
            st.bar_chart(category_counts)
            
            # Tableau détaillé
            st.subheader("Alle Aufgaben")
            st.dataframe(df[["id", "title", "category", "deadline", "done"]], use_container_width=True)
    
    with tab4:
        st.header("Umfrage: Pain Points")
        st.markdown("Teile deine Probleme und Herausforderungen mit!")
        
        with st.form("survey"):
            name = st.text_input("Name (optional)")
            problem = st.text_area("Problem / Herausforderung *", 
                                  placeholder="z.B. Unklare Prüfungsanmeldung, Schwierigkeiten bei der Wohnungssuche...")
            urgency = st.select_slider("Dringlichkeit", ["Niedrig", "Mittel", "Hoch"])
            
            submitted = st.form_submit_button("Eintrag absenden")
            if submitted and problem:
                # Charger et sauvegarder
                ensure_files()
                with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                
                entry = {
                    "name": name or "Anonym",
                    "problem": problem,
                    "urgency": urgency,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                entries.append(entry)
                
                with open(SURVEY_FILE, "w", encoding="utf-8") as f:
                    json.dump(entries, f, ensure_ascii=False, indent=2)
                
                st.success("Danke für deinen Beitrag!")
        
        # Afficher les entrées existantes
        st.subheader("Bisherige Einträge")
        if os.path.exists(SURVEY_FILE):
            with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
            
            if entries:
                for entry in reversed(entries[-10:]):  # Les 10 derniers
                    with st.container():
                        st.markdown(f"**{entry['name']}** ({entry['urgency']})")
                        st.markdown(f"> {entry['problem']}")
                        st.caption(f"📅 {entry['time']}")
                        st.divider()
            else:
                st.info("Noch keine Umfrageeinträge.")

if __name__ == "__main__":
    main()