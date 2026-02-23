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
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Progression
            st.subheader("Fortschritt")
            done_count = len([t for t in data["tasks"] if t.get("done", False)])
            total_count = len(data["tasks"])
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = done_count/total_count*100 if total_count > 0 else 0,
                title = {'text': "Erledigt (%)"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#667eea"},
                    'steps': [
                        {'range': [0, 50], 'color': "#feca57"},
                        {'range': [50, 80], 'color': "#48dbfb"},
                        {'range': [80, 100], 'color': "#1dd1a1"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        # Graphique du temps par tâche
        if time_entries:
            st.subheader("⏱️ Temps passé par tâche")
            task_time = pd.DataFrame(time_entries).groupby('task_title')['duration_minutes'].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=task_time.values, 
                y=task_time.index,
                orientation='h',
                title='Top 10 Aufgaben nach Zeit',
                labels={'x': 'Minuten', 'y': ''},
                color=task_time.values,
                color_continuous_scale=['#48dbfb', '#1dd1a1', '#feca57', '#ff6b6b']
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des tâches avec performance
        st.subheader("📋 Performance-Analyse")
        tasks_df = pd.DataFrame(data["tasks"])
        tasks_df['Effizienz'] = tasks_df.apply(
            lambda x: f"{min(100, int(x.get('total_time_spent', 0)/x.get('estimated_time', 1)*100))}%" 
            if x.get('estimated_time', 0) > 0 else "0%", 
            axis=1
        )
        tasks_df['Status'] = tasks_df['done'].apply(lambda x: "✅ Erledigt" if x else "🔄 Offen")
        
        st.dataframe(
            tasks_df[['title', 'category', 'priority', 'estimated_time', 'total_time_spent', 'Effizienz', 'Status']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "title": "Aufgabe",
                "category": "Kategorie",
                "priority": "Priorität",
                "estimated_time": "Geschätzt (min)",
                "total_time_spent": "Verbraucht (min)",
                "Effizienz": "Effizienz",
                "Status": "Status"
            }
        )
    else:
        st.info("📊 Keine Daten für Analysen vorhanden.")

# TAB 5: Feedback
with tab5:
    st.header("🗣️ Feedback & Probleme")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Neues Feedback")
        with st.form("feedback_form"):
            name = st.text_input("Name (optional)")
            problem = st.text_area("💭 Dein Feedback / Problem *", 
                                  placeholder="z.B. Funktion XYZ könnte verbessert werden...")
            urgency = st.select_slider("Dringlichkeit", ["Niedrig", "Mittel", "Hoch", "Kritisch"])
            
            submitted = st.form_submit_button("📨 Absenden", use_container_width=True)
            if submitted and problem:
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
                
                st.success("✅ Danke für dein Feedback!")
                st.balloons()
    
    with col2:
        st.subheader("📢 Letzte Feedbacks")
        if os.path.exists(SURVEY_FILE):
            with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
            
            if entries:
                for entry in reversed(entries[-5:]):
                    urgency_color = {
                        "Niedrig": "🟢",
                        "Mittel": "🟡",
                        "Hoch": "🟠",
                        "Kritisch": "🔴"
                    }.get(entry['urgency'], "⚪")
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="background: #f8f9fa; border-radius: 10px; padding: 15px; margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>{entry['name']}</strong>
                                <span>{urgency_color} {entry['urgency']}</span>
                            </div>
                            <p style="margin: 10px 0;">{entry['problem']}</p>
                            <small style="color: #666;">{entry['time']}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Noch kein Feedback vorhanden.")