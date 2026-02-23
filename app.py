# app.py - CampusEingang avec Time Tracking (Design Moderne)

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page (DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT)
st.set_page_config(
    page_title="CampusEingang - Time Tracker", 
    page_icon="⏱️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne et attrayant
st.markdown("""
<style>
    /* Styles généraux */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    
    /* Cartes pour les tâches */
    .task-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .task-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Badges pour les statuts */
    .badge-overdue {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-today {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-upcoming {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Métriques améliorées */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Timer actif */
    .active-timer {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #667eea;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }
    
    /* Boutons personnalisés */
    .stButton > button {
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Configuration des fichiers de données
DATA_DIR = "campus_data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "data.json")
TIME_TRACKING_FILE = os.path.join(DATA_DIR, "time_tracking.json")
SURVEY_FILE = os.path.join(DATA_DIR, "survey.json")

# Données par défaut avec Time Tracking
default_data = {
    "tasks": [
        {
            "id": 1, 
            "title": "Immatrikulation abschließen", 
            "category": "Immatrikulation",
            "deadline": "2026-10-01", 
            "link": "https://uni.example/immatrikulation", 
            "done": False,
            "notes": "Unterlagen mitbringen",
            "estimated_time": 120,  # temps estimé en minutes
            "total_time_spent": 0,   # temps total déjà passé
            "priority": "Hoch"        # Hoch, Mittel, Niedrig
        },
        {
            "id": 2, 
            "title": "Chipkarte abholen", 
            "category": "Organisatorisch",
            "deadline": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"), 
            "link": "", 
            "done": False, 
            "notes": "",
            "estimated_time": 30,
            "total_time_spent": 0,
            "priority": "Mittel"
        }
    ],
    "next_id": 3
}

# Fonctions de gestion des données
def ensure_files():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(TIME_TRACKING_FILE):
        with open(TIME_TRACKING_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
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

def load_time_entries():
    ensure_files()
    with open(TIME_TRACKING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_time_entries(entries):
    with open(TIME_TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

# Initialisation des sessions state pour le timer
if 'active_timer' not in st.session_state:
    st.session_state.active_timer = None
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None
if 'timer_task_id' not in st.session_state:
    st.session_state.timer_task_id = None

# En-tête principal avec animation
st.markdown('<h1 class="main-header">⏱️ CampusEingang Time Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Gestion intelligente de ton temps universitaire</p>', unsafe_allow_html=True)

# Sidebar avec stats et timer actif
with st.sidebar:
    st.markdown("### ⏳ Timer Actif")
    
    if st.session_state.active_timer:
        data = load_data()
        task = next((t for t in data["tasks"] if t["id"] == st.session_state.timer_task_id), None)
        if task:
            st.markdown(f"""
            <div class="active-timer">
                <h4 style="margin:0; color:#333;">▶️ En cours : {task['title']}</h4>
                <p style="font-size:2rem; font-weight:bold; margin:10px 0; color:#667eea;" id="timer">00:00:00</p>
                <p style="margin:0; color:#666;">Démarré à {st.session_state.timer_start.strftime('%H:%M:%S')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏸️ Pause", use_container_width=True):
                    # Arrêter le timer
                    elapsed = datetime.now() - st.session_state.timer_start
                    minutes = elapsed.total_seconds() / 60
                    
                    # Sauvegarder l'entrée
                    entries = load_time_entries()
                    entry = {
                        "task_id": task["id"],
                        "task_title": task["title"],
                        "start_time": st.session_state.timer_start.isoformat(),
                        "end_time": datetime.now().isoformat(),
                        "duration_minutes": round(minutes, 2),
                        "date": date.today().isoformat()
                    }
                    entries.append(entry)
                    save_time_entries(entries)
                    
                    # Mettre à jour le total de la tâche
                    data = load_data()
                    for t in data["tasks"]:
                        if t["id"] == task["id"]:
                            t["total_time_spent"] = t.get("total_time_spent", 0) + round(minutes, 2)
                            break
                    save_data(data)
                    
                    st.session_state.active_timer = False
                    st.rerun()
            
            with col2:
                if st.button("⏹️ Stop", use_container_width=True):
                    st.session_state.active_timer = False
                    st.rerun()
    else:
        st.info("💤 Kein aktiver Timer")
        st.markdown("*Starte einen Timer von einer Aufgabe aus*")
    
    st.markdown("---")
    
    # Statistiques rapides
    st.markdown("### 📊 Quick Stats")
    data = load_data()
    time_entries = load_time_entries()
    
    total_time = sum([e.get("duration_minutes", 0) for e in time_entries])
    tasks_done = len([t for t in data["tasks"] if t.get("done", False)])
    tasks_total = len(data["tasks"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Zeit total", f"{int(total_time)} min", f"{int(total_time/60)}h")
    with col2:
        st.metric("Aufgaben", f"{tasks_done}/{tasks_total}", f"{int(tasks_done/tasks_total*100) if tasks_total>0 else 0}%")
    
    st.markdown("---")
    st.markdown("### 🎯 Prioritäten")
    
    # Graphique des priorités
    if data["tasks"]:
        priorities = {"Hoch": 0, "Mittel": 0, "Niedrig": 0}
        for task in data["tasks"]:
            p = task.get("priority", "Mittel")
            priorities[p] = priorities.get(p, 0) + 1
        
        priority_df = pd.DataFrame({
            'Priorität': list(priorities.keys()),
            'Anzahl': list(priorities.values())
        })
        
        fig = px.pie(priority_df, values='Anzahl', names='Priorität', 
                     color_discrete_sequence=['#ff6b6b', '#feca57', '#48dbfb'])
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=200)
        st.plotly_chart(fig, use_container_width=True)

# Onglets principaux
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Aufgaben & Timer", 
    "➕ Neue Aufgabe", 
    "⏱️ Zeiterfassung", 
    "📊 Analysen",
    "🗣️ Feedback"
])

# TAB 1: Aufgaben & Timer
with tab1:
    st.header("📋 Meine Aufgaben mit Zeit-Tracking")
    
    data = load_data()
    
    if data["tasks"]:
        # Créer un DataFrame pour les tâches
        df = pd.DataFrame(data["tasks"])
        
        # Ajouter colonne overdue
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
        
        # Filtrer les tâches
        filter_option = st.radio(
            "Filter:",
            ["Alle", "Aktiv", "Erledigt", "Überfällig"],
            horizontal=True
        )
        
        if filter_option == "Aktiv":
            df = df[~df["done"]]
        elif filter_option == "Erledigt":
            df = df[df["done"]]
        elif filter_option == "Überfällig":
            df = df[df["overdue"]]
        
        # Afficher les tâches dans des cartes
        for idx, task in df.iterrows():
            # Déterminer le badge de deadline
            if task.get("overdue"):
                badge_class = "badge-overdue"
                badge_text = "⚠️ Überfällig"
            elif task["deadline_date"] and task["deadline_date"] <= today:
                badge_class = "badge-today"
                badge_text = "🔔 Heute"
            elif task["deadline_date"] and task["deadline_date"] <= today + timedelta(days=7):
                badge_class = "badge-upcoming"
                badge_text = f"📅 In {(task['deadline_date'] - today).days} Tagen"
            else:
                badge_class = "badge-upcoming"
                badge_text = f"📅 {task['deadline']}"
            
            # Couleur selon priorité
            priority_colors = {
                "Hoch": "#ff6b6b",
                "Mittel": "#feca57",
                "Niedrig": "#48dbfb"
            }
            priority_color = priority_colors.get(task.get("priority", "Mittel"), "#feca57")
            
            # Carte de tâche
            with st.container():
                st.markdown(f"""
                <div class="task-card" style="border-left: 5px solid {priority_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin:0;">{task['title']}</h3>
                        <span class="{badge_class}">{badge_text}</span>
                    </div>
                    <p style="color: #666; margin: 5px 0;">
                        📂 {task['category']} | 
                        🎯 Priorität: <span style="color:{priority_color}; font-weight:600;">{task.get('priority', 'Mittel')}</span>
                    </p>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**Zeit:** ⏱️ {task.get('total_time_spent', 0):.1f} min / {task.get('estimated_time', 60)} min estimé")
                    progress = min(task.get('total_time_spent', 0) / task.get('estimated_time', 60), 1.0)
                    st.progress(progress)
                
                with col2:
                    if not task.get("done", False):
                        if st.button("▶️ Start", key=f"start_{task['id']}", use_container_width=True):
                            if st.session_state.active_timer:
                                st.warning("⚠️ Stoppe zuerst den aktiven Timer!")
                            else:
                                st.session_state.active_timer = True
                                st.session_state.timer_start = datetime.now()
                                st.session_state.timer_task_id = task["id"]
                                st.rerun()
                
                with col3:
                    if st.button("✓ Done", key=f"done_{task['id']}", use_container_width=True):
                        data = load_data()
                        for t in data["tasks"]:
                            if t["id"] == task["id"]:
                                t["done"] = not t.get("done", False)
                                break
                        save_data(data)
                        st.rerun()
                
                with col4:
                    if st.button("✏️ Edit", key=f"edit_{task['id']}", use_container_width=True):
                        st.session_state[f"editing_{task['id']}"] = True
                
                with col5:
                    if st.button("🗑️", key=f"del_{task['id']}"):
                        data = load_data()
                        data["tasks"] = [t for t in data["tasks"] if t["id"] != task["id"]]
                        save_data(data)
                        st.rerun()
                
                # Notes si présentes
                if task.get("notes"):
                    st.info(f"📝 {task['notes']}")
                
                # Formulaire d'édition
                if st.session_state.get(f"editing_{task['id']}", False):
                    with st.form(key=f"edit_form_{task['id']}"):
                        new_title = st.text_input("Titel", value=task["title"])
                        new_category = st.text_input("Kategorie", value=task["category"])
                        new_deadline = st.date_input("Frist", 
                            value=datetime.strptime(task["deadline"], "%Y-%m-%d").date() if task["deadline"] else today)
                        new_priority = st.selectbox("Priorität", ["Hoch", "Mittel", "Niedrig"], 
                            index=["Hoch", "Mittel", "Niedrig"].index(task.get("priority", "Mittel")))
                        new_estimated = st.number_input("Geschätzte Zeit (min)", 
                            value=task.get("estimated_time", 60), min_value=1)
                        new_notes = st.text_area("Notizen", value=task.get("notes", ""))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Speichern"):
                                data = load_data()
                                for t in data["tasks"]:
                                    if t["id"] == task["id"]:
                                        t.update({
                                            "title": new_title,
                                            "category": new_category,
                                            "deadline": new_deadline.strftime("%Y-%m-%d"),
                                            "priority": new_priority,
                                            "estimated_time": new_estimated,
                                            "notes": new_notes
                                        })
                                        break
                                save_data(data)
                                st.session_state[f"editing_{task['id']}"] = False
                                st.rerun()
                        with col2:
                            if st.form_submit_button("❌ Abbrechen"):
                                st.session_state[f"editing_{task['id']}"] = False
                                st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("✨ Keine Aufgaben vorhanden. Erstelle deine erste Aufgabe!")

# TAB 2: Neue Aufgabe
# TAB 2: Neue Aufgabe
with tab2:
    st.header("➕ Neue Aufgabe mit Zeit-Schätzung")
    
    # DÉFINIR today ICI pour cette section
    today = date.today()
    
    with st.form("new_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("📌 Titel *", placeholder="z.B. Prüfungsanmeldung")
            category = st.selectbox("📂 Kategorie", 
                ["Immatrikulation", "Organisatorisch", "Prüfungen", "Finanzen", "Wohnen", "Sonstiges"])
            priority = st.select_slider("🎯 Priorität", 
                options=["Niedrig", "Mittel", "Hoch"], value="Mittel")
        
        with col2:
            deadline = st.date_input("📅 Frist", min_value=today)  # today est maintenant défini
            estimated_time = st.number_input("⏱️ Geschätzte Zeit (Minuten)", 
                min_value=5, max_value=480, value=60, step=5)
            link = st.text_input("🔗 Link (optional)", placeholder="https://...")
        
        notes = st.text_area("📝 Notizen", placeholder="Weitere Details...", height=100)
        
        submitted = st.form_submit_button("🚀 Aufgabe erstellen", use_container_width=True)
        
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
                "done": False,
                "estimated_time": estimated_time,
                "total_time_spent": 0,
                "priority": priority
            }
            data["tasks"].append(task)
            data["next_id"] = new_id + 1
            save_data(data)
            st.success(f"✅ Aufgabe '{title}' erfolgreich erstellt!")
            st.balloons()

# TAB 3: Zeiterfassung
with tab3:
    st.header("⏱️ Zeiterfassung & Verlauf")
    
    time_entries = load_time_entries()
    
    if time_entries:
        # Graphique du temps par jour
        entries_df = pd.DataFrame(time_entries)
        entries_df['date'] = pd.to_datetime(entries_df['date'])
        daily_time = entries_df.groupby('date')['duration_minutes'].sum().reset_index()
        
        fig = px.bar(daily_time, x='date', y='duration_minutes', 
                     title='Tägliche Arbeitszeit',
                     labels={'duration_minutes': 'Minuten', 'date': 'Datum'},
                     color_discrete_sequence=['#667eea'])
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des entrées
        st.subheader("📋 Letzte Einträge")
        
        # Formater pour affichage
        display_df = entries_df.copy()
        display_df['Datum'] = display_df['date'].dt.strftime('%d.%m.%Y')
        display_df['Aufgabe'] = display_df['task_title']
        display_df['Dauer'] = display_df['duration_minutes'].apply(lambda x: f"{int(x)} min ({x/60:.1f}h)")
        display_df['Start'] = pd.to_datetime(display_df['start_time']).dt.strftime('%H:%M')
        display_df['Ende'] = pd.to_datetime(display_df['end_time']).dt.strftime('%H:%M')
        
        st.dataframe(
            display_df[['Datum', 'Aufgabe', 'Start', 'Ende', 'Dauer']].sort_values('Datum', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Statistiques
        st.subheader("📊 Zusammenfassung")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Zeit", f"{int(entries_df['duration_minutes'].sum())} min", 
                     f"{entries_df['duration_minutes'].sum()/60:.1f}h")
        with col2:
            st.metric("Durchschnitt", f"{entries_df['duration_minutes'].mean():.0f} min", 
                     "pro Session")
        with col3:
            st.metric("Sessions", len(entries_df), "")
        with col4:
            st.metric("Produktivste Zeit", 
                     pd.to_datetime(entries_df['start_time']).dt.hour.mode().iloc[0] if len(entries_df) > 0 else "-", 
                     "Uhr")
    else:
        st.info("⏳ Noch keine Zeiteinträge vorhanden. Starte einen Timer von einer Aufgabe!")

# TAB 4: Analysen
with tab4:
    st.header("📊 Detaillierte Analysen")
    
    data = load_data()
    time_entries = load_time_entries()
    
    if data["tasks"]:
        col1, col2 = st.columns(2)
        
        with col1:
            # Répartition par catégorie
            st.subheader("Aufgaben nach Kategorie")
            category_counts = pd.DataFrame(data["tasks"])["category"].value_counts()
            fig = px.pie(values=category_counts.values, names=category_counts.index,
                        color_discrete_sequence=px.colors.sequential.RdBu)
            st.p
            
# TAB 4: Analysen (VERSION CORRIGÉE)
with tab4:
    st.header("📊 Detaillierte Analysen")
    
    data = load_data()
    today = date.today()
    
    if data["tasks"]:
        # Créer un DataFrame sécurisé
        tasks_list = []
        for task in data["tasks"]:
            # S'assurer que toutes les clés existent
            safe_task = {
                "title": task.get("title", "Sans titre"),
                "category": task.get("category", "Sonstiges"),
                "priority": task.get("priority", "Mittel"),
                "estimated_time": task.get("estimated_time", 60),
                "total_time_spent": task.get("total_time_spent", 0),
                "done": task.get("done", False),
                "deadline": task.get("deadline", ""),
                "notes": task.get("notes", "")
            }
            tasks_list.append(safe_task)
        
        tasks_df = pd.DataFrame(tasks_list)
        
        # Ajouter les colonnes calculées
        tasks_df['Effizienz'] = tasks_df.apply(
            lambda x: f"{min(100, int(x['total_time_spent'] / max(x['estimated_time'], 1) * 100))}%", 
            axis=1
        )
        tasks_df['Status'] = tasks_df['done'].apply(lambda x: "✅ Erledigt" if x else "🔄 Offen")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique catégories
            st.subheader("📊 Aufgaben nach Kategorie")
            if not tasks_df.empty:
                category_counts = tasks_df['category'].value_counts()
                fig = px.pie(
                    values=category_counts.values, 
                    names=category_counts.index,
                    title="Verteilung nach Kategorie",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Daten verfügbar")
        
        with col2:
            # Progression globale
            st.subheader("📈 Fortschritt")
            done_count = len(tasks_df[tasks_df['done']])
            total_count = len(tasks_df)
            
            if total_count > 0:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=done_count,
                    number={'prefix': "✅ "},
                    delta={'reference': total_count, 'valueformat': '.0f'},
                    title={'text': f"Erledigte Aufgaben von {total_count}"},
                    gauge={
                        'axis': {'range': [None, total_count]},
                        'bar': {'color': "#4CAF50"},
                        'steps': [
                            {'range': [0, total_count/2], 'color': "#FFB74D"},
                            {'range': [total_count/2, total_count], 'color': "#81C784"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': total_count
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Aufgaben vorhanden")
        
        # Statistiques supplémentaires
        st.subheader("📋 Statistiques détaillées")
        
        # Métriques en ligne
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            total_time_all = tasks_df['total_time_spent'].sum()
            st.metric(
                "⏱️ Temps total",
                f"{int(total_time_all)} min",
                f"{total_time_all/60:.1f}h"
            )
        
        with col_m2:
            avg_time_per_task = tasks_df['total_time_spent'].mean()
            st.metric(
                "📊 Moyenne par tâche",
                f"{int(avg_time_per_task)} min"
            )
        
        with col_m3:
            overdue_count = len([
                t for t in data["tasks"] 
                if not t.get("done", False) 
                and t.get("deadline", "9999") < today.strftime("%Y-%m-%d")
            ])
            st.metric(
                "⚠️ Überfällig",
                overdue_count,
                delta_color="inverse"
            )
        
        with col_m4:
            high_priority = len([t for t in data["tasks"] if t.get("priority") == "Hoch"])
            st.metric(
                "🔥 Hohe Priorität",
                high_priority
            )
        
        # Tableau des tâches (VERSION CORRIGÉE)
        st.subheader("📋 Liste détaillée des tâches")
        
        # Sélectionner seulement les colonnes qui existent
        display_columns = []
        column_config = {}
        
        # Définir les colonnes à afficher avec leurs configurations
        columns_to_show = [
            ("title", "Tâche"),
            ("category", "Catégorie"),
            ("priority", "Priorité"),
            ("estimated_time", "Estimé (min)"),
            ("total_time_spent", "Passé (min)"),
            ("Effizienz", "Efficacité"),
            ("Status", "Statut")
        ]
        
        for col, label in columns_to_show:
            if col in tasks_df.columns:
                display_columns.append(col)
                column_config[col] = label
        
        if display_columns:
            st.dataframe(
                tasks_df[display_columns],
                use_container_width=True,
                hide_index=True,
                column_config={col: col for col in display_columns}  # Simplifié
            )
        
        # Graphique d'efficacité
        st.subheader("📊 Analyse d'efficacité")
        
        # Préparer les données pour le graphique
        chart_df = tasks_df.copy()
        chart_df['efficacite_num'] = chart_df.apply(
            lambda x: min(100, int(x['total_time_spent'] / max(x['estimated_time'], 1) * 100)),
            axis=1
        )
        
        # Graphique en barres
        fig = px.bar(
            chart_df,
            x='title',
            y='efficacite_num',
            color='category',
            title="Efficacité par tâche (%)",
            labels={'title': 'Tâche', 'efficacite_num': 'Efficacité (%)', 'category': 'Catégorie'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Export des données
        st.subheader("📥 Export des données")
        if st.button("📥 Exporter en CSV"):
            csv = tasks_df.to_csv(index=False)
            st.download_button(
                "📥 Télécharger CSV",
                csv,
                f"campus_daten_{date.today().isoformat()}.csv",
                "text/csv",
                key='download-csv'
            )
    
    else:
        st.info("📊 Keine Daten für Analysen vorhanden. Erstelle zuerst Aufgaben!")
        
        # Afficher un exemple
        with st.expander("ℹ️ Comment ça marche ?"):
            st.markdown("""
            **Cette page d'analyse te permet de :**
            - 📊 Visualiser la répartition de tes tâches
            - ⏱️ Suivre ton temps de travail
            - 📈 Évaluer ton efficacité
            - 📥 Exporter tes données
            
            Commence par créer des tâches dans l'onglet **➕ Neue Aufgabe** !
            """)

# TAB 5: Feedback
# Imports supplémentaires en haut du fichier
import sendgrid
from sendgrid.helpers.mail import Mail
import hmac
import hashlib

# Configuration email (à mettre après les autres configurations)
# À remplacer par tes informations
SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY", "TA_CLE_API_ICI")
FROM_EMAIL = "campus@eingang.de"  # À vérifier dans SendGrid (sender verification)
TO_EMAIL = "ton-email@example.com"  # Où tu veux recevoir les feedbacks

def send_feedback_email(name, email, feedback_type, feedback, urgency):
    """
    Envoie un email avec les détails du feedback
    """
    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
        # Construction de l'email HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f5f5f5; padding: 20px; border-radius: 0 0 10px 10px; }}
                .field {{ margin: 15px 0; }}
                .label {{ font-weight: bold; color: #667eea; }}
                .value {{ background: white; padding: 10px; border-radius: 5px; margin-top: 5px; }}
                .urgency {{ display: inline-block; padding: 5px 15px; border-radius: 20px; 
                          font-weight: bold; }}
                .urgency-Hoch {{ background: #ff6b6b; color: white; }}
                .urgency-Mittel {{ background: #feca57; color: black; }}
                .urgency-Niedrig {{ background: #48dbfb; color: black; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📬 Nouveau Feedback - CampusEingang</h1>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">👤 De:</div>
                        <div class="value">{name}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">📧 Email:</div>
                        <div class="value">{email if email else 'Non renseigné'}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">📝 Type:</div>
                        <div class="value">{feedback_type}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">⚠️ Dringlichkeit:</div>
                        <div class="value">
                            <span class="urgency urgency-{urgency}">{urgency}</span>
                        </div>
                    </div>
                    
                    <div class="field">
                        <div class="label">💬 Feedback:</div>
                        <div class="value">{feedback}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">⏰ Zeitstempel:</div>
                        <div class="value">{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Créer le message
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=TO_EMAIL,
            subject=f'📬 CampusEingang - Neues Feedback von {name}',
            html_content=html_content
        )
        
        # Envoyer
        response = sg.send(message)
        
        # Optionnel: Envoyer une confirmation à l'utilisateur
        if email:
            confirmation = Mail(
                from_email=FROM_EMAIL,
                to_emails=email,
                subject='✅ Dein Feedback wurde empfangen - CampusEingang',
                html_content=f'''
                <h2>Danke für dein Feedback!</h2>
                <p>Hallo {name},</p>
                <p>wir haben dein Feedback erhalten und werden es schnellstmöglich bearbeiten.</p>
                <p><strong>Dein Feedback:</strong> {feedback}</p>
                <p>Vielen Dank für deine Hilfe, CampusEingang besser zu machen! 🎓</p>
                '''
            )
            sg.send(confirmation)
        
        return True, "Email envoyé avec succès"
    
    except Exception as e:
        return False, str(e)

# Fonction pour vérifier l'intégrité des données
def hash_feedback_id(feedback_id, timestamp):
    """Crée un hash unique pour chaque feedback"""
    secret = st.secrets.get("HASH_SECRET", "campus2026_secret")
    text = f"{feedback_id}_{timestamp}_{secret}"
    return hmac.new(secret.encode(), text.encode(), hashlib.sha256).hexdigest()[:8]

# TAB 5: Feedback (Version Email)
with tab5:
    st.header("🗣️ Feedback & Probleme")
    
    # Créer des onglets pour une meilleure organisation
    tab_send, tab_stats, tab_admin = st.tabs(["📝 Feedback senden", "📊 Statistiques", "🔐 Admin"])
    
    # TAB: Envoyer un feedback
    with tab_send:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); 
                        padding: 20px; border-radius: 15px; margin-bottom: 20px;">
                <h3 style="margin-top:0;">Deine Meinung zählt! 💭</h3>
                <p>Hilf uns, CampusEingang zu verbessern. Jedes Feedback wird ernst genommen!</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("feedback_email_form"):
                # Informations personnelles
                col_name, col_email = st.columns(2)
                with col_name:
                    name = st.text_input(
                        "👤 Dein Name", 
                        placeholder="z.B. Max Mustermann",
                        help="Wird nur für Rückfragen verwendet"
                    )
                with col_email:
                    email = st.text_input(
                        "📧 Deine E-Mail", 
                        placeholder="max@example.com",
                        help="Für Rückmeldung zu deinem Feedback"
                    )
                
                # Type de feedback avec icônes
                feedback_type = st.selectbox(
                    "📌 Art des Feedbacks",
                    [
                        "💡 Verbesserungsvorschlag",
                        "🐛 Bug/Fehler melden",
                        "❓ Frage / Hilfe",
                        "👍 Lob / Positive Rückmeldung",
                        "👎 Kritik / Negatives Erlebnis",
                        "🚀 Feature-Wunsch"
                    ]
                )
                
                # Dringlichkeit avec emojis
                urgency = st.select_slider(
                    "⚡ Dringlichkeit",
                    options=["Niedrig", "Mittel", "Hoch", "Kritisch"],
                    value="Mittel",
                    help="Wie dringend ist dein Anliegen?"
                )
                
                # Feedback texte
                feedback = st.text_area(
                    "💬 Dein Feedback *", 
                    placeholder="""Was möchtest du uns mitteilen?
                    
                    - Was gefällt dir besonders?
                    - Was könnte verbessert werden?
                    - Hast du einen Fehler gefunden?
                    - Fehlt eine Funktion?""",
                    height=150
                )
                
                # Options supplémentaires
                col_anon, col_copy = st.columns(2)
                with col_anon:
                    anonymous = st.checkbox("🕵️ Anonym bleiben", help="Dein Name wird nicht übermittelt")
                with col_copy:
                    copy_me = st.checkbox("📋 Kopie an mich", value=True, help="Erhalte eine Bestätigung per Email")
                
                # Bouton d'envoi
                submitted = st.form_submit_button(
                    "📨 Feedback senden", 
                    use_container_width=True,
                    type="primary"
                )
                
                if submitted and feedback:
                    with st.spinner("📤 Envoi en cours..."):
                        # Préparer les données
                        final_name = "Anonym" if anonymous else (name or "Anonym")
                        final_email = "" if anonymous else email
                        
                        # Sauvegarder localement (backup)
                        ensure_files()
                        with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                            entries = json.load(f)
                        
                        feedback_id = len(entries) + 1
                        timestamp = datetime.now().isoformat()
                        
                        entry = {
                            "id": feedback_id,
                            "hash": hash_feedback_id(feedback_id, timestamp),
                            "timestamp": timestamp,
                            "name": final_name,
                            "email": final_email,
                            "type": feedback_type,
                            "feedback": feedback,
                            "urgency": urgency,
                            "status": "Nouveau",
                            "responded": False
                        }
                        entries.append(entry)
                        
                        with open(SURVEY_FILE, "w", encoding="utf-8") as f:
                            json.dump(entries, f, ensure_ascii=False, indent=2)
                        
                        # Envoyer par email
                        success, message = send_feedback_email(
                            final_name, 
                            final_email if copy_me else "",
                            feedback_type, 
                            feedback, 
                            urgency
                        )
                        
                        if success:
                            st.success("✅ Feedback erfolgreich gesendet! Vielen Dank für deine Hilfe! 🎉")
                            st.balloons()
                            
                            # Afficher un résumé
                            with st.expander("📋 Zusammenfassung deines Feedbacks"):
                                st.markdown(f"""
                                **Name:** {final_name}  
                                **Typ:** {feedback_type}  
                                **Dringlichkeit:** {urgency}  
                                **Feedback:** {feedback}
                                """)
                        else:
                            st.error(f"❌ Fehler beim Senden: {message}")
                            st.info("📝 Dein Feedback wurde lokal gespeichert und wird später gesendet.")
        
        with col2:
            st.markdown("### 📊 Quick Stats")
            
            # Afficher des statistiques rapides
            if os.path.exists(SURVEY_FILE):
                with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                
                if entries:
                    # Dernier feedback
                    last = entries[-1]
                    st.markdown(f"""
                    **Dernier feedback:**  
                    {last.get('timestamp', '')[:10]}  
                    *{last.get('feedback', '')[:50]}...*
                    """)
                    
                    # Compteurs
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Total", len(entries))
                    with col_b:
                        urgent = len([e for e in entries if e.get('urgency') in ['Hoch', 'Kritisch']])
                        st.metric("Urgent", urgent)
                    
                    # Types populaires
                    from collections import Counter
                    types = Counter([e.get('type', 'Sonstiges') for e in entries[-10:]])
                    st.markdown("**Top Themen:**")
                    for t, c in types.most_common(3):
                        st.caption(f"{t}: {c}x")
            
            # Guide d'utilisation
            st.markdown("---")
            st.markdown("""
            ### 📝 Guide
            **🟢 Niedrig:** Vorschläge, Lob  
            **🟡 Mittel:** Fragen, Verbesserungen  
            **🟠 Hoch:** Wichtige Probleme  
            **🔴 Kritisch:** Dringende Fehler
            """)
    
    # TAB: Statistiques détaillées
    with tab_stats:
        st.subheader("📈 Feedback Statistiken")
        
        if os.path.exists(SURVEY_FILE):
            with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
            
            if entries:
                df = pd.DataFrame(entries)
                df['date'] = pd.to_datetime(df['timestamp']).dt.date
                
                # Graphiques
                col1, col2 = st.columns(2)
                
                with col1:
                    # Feedbacks par jour
                    daily = df.groupby('date').size().reset_index(name='count')
                    fig = px.bar(daily, x='date', y='count', title='Feedbacks par jour')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Répartition par type
                    type_counts = df['type'].value_counts()
                    fig = px.pie(values=type_counts.values, names=type_counts.index, title='Types de feedback')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Tableau des derniers
                st.subheader("📋 Derniers Feedbacks")
                display_df = df[['timestamp', 'name', 'type', 'urgency', 'status']].sort_values('timestamp', ascending=False).head(10)
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("Noch keine Feedbacks vorhanden")
    
    # TAB: Admin (protégé)
    with tab_admin:
        st.subheader("🔒 Administration")
        
        # Mot de passe simple
        password = st.text_input("Admin Passwort", type="password")
        
        if password == "campus2026":  # À changer !
            if os.path.exists(SURVEY_FILE):
                with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                
                if entries:
                    # Filtres
                    col_f1, col_f2, col_f3 = st.columns(3)
                    with col_f1:
                        status_filter = st.selectbox(
                            "Status filtern",
                            ["Alle", "Nouveau", "En cours", "Erledigt"]
                        )
                    with col_f2:
                        urgency_filter = st.selectbox(
                            "Dringlichkeit filtern",
                            ["Alle", "Niedrig", "Mittel", "Hoch", "Kritisch"]
                        )
                    with col_f3:
                        search = st.text_input("🔍 Suche", placeholder="Nom, feedback...")
                    
                    # Appliquer les filtres
                    filtered = entries
                    if status_filter != "Alle":
                        filtered = [e for e in filtered if e.get('status') == status_filter]
                    if urgency_filter != "Alle":
                        filtered = [e for e in filtered if e.get('urgency') == urgency_filter]
                    if search:
                        filtered = [e for e in filtered if 
                                  search.lower() in e.get('name', '').lower() or 
                                  search.lower() in e.get('feedback', '').lower()]
                    
                    # Afficher
                    for entry in reversed(filtered):
                        with st.expander(
                            f"[{entry.get('timestamp', '')}] {entry.get('name', 'Anonym')} - {entry.get('type', 'Feedback')} "
                            f"[{entry.get('urgency', 'Mittel')}]"
                        ):
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.markdown(f"**ID:** {entry.get('id')} | **Hash:** {entry.get('hash', 'N/A')}")
                                st.markdown(f"**Feedback:** {entry.get('feedback', '')}")
                                if entry.get('email'):
                                    st.markdown(f"**Email:** {entry['email']}")
                            
                            with col2:
                                new_status = st.selectbox(
                                    "Status",
                                    ["Nouveau", "En cours", "Erledigt"],
                                    index=["Nouveau", "En cours", "Erledigt"].index(entry.get('status', 'Nouveau')),
                                    key=f"status_{entry['id']}"
                                )
                                if new_status != entry.get('status'):
                                    entry['status'] = new_status
                                    with open(SURVEY_FILE, "w", encoding="utf-8") as f:
                                        json.dump(entries, f, ensure_ascii=False, indent=2)
                                    
                                    # Notifier par email si répondu
                                    if new_status == "Erledigt" and entry.get('email'):
                                        st.info(f"📧 Notification à {entry['email']}")
                                    st.rerun()
                            
                            with col3:
                                if st.button("🗑️ Löschen", key=f"del_{entry['id']}"):
                                    entries.remove(entry)
                                    with open(SURVEY_FILE, "w", encoding="utf-8") as f:
                                        json.dump(entries, f, ensure_ascii=False, indent=2)
                                    st.rerun()
                    
                    # Export
                    st.subheader("📥 Export")
                    if st.button("CSV exportieren"):
                        df = pd.DataFrame(entries)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "📥 Download CSV",
                            csv,
                            f"feedbacks_{date.today().isoformat()}.csv",
                            "text/csv"
                        )
                else:
                    st.info("Keine Feedbacks vorhanden")
        elif password:
            st.error("❌ Falsches Passwort")