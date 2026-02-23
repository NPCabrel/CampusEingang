# app.py - CampusEingang avec Time Tracking (Version sans Plotly)

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta

# Configuration de la page
st.set_page_config(
    page_title="CampusEingang - Time Tracker", 
    page_icon="⏱️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        padding-bottom: 0;
    }
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
</style>
""", unsafe_allow_html=True)

# Configuration des fichiers
DATA_DIR = "campus_data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "data.json")
TIME_TRACKING_FILE = os.path.join(DATA_DIR, "time_tracking.json")
SURVEY_FILE = os.path.join(DATA_DIR, "survey.json")

# Données par défaut
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
            "estimated_time": 120,
            "total_time_spent": 0,
            "priority": "Hoch"
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

# Fonctions de gestion
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

# Session state
if 'active_timer' not in st.session_state:
    st.session_state.active_timer = None
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None
if 'timer_task_id' not in st.session_state:
    st.session_state.timer_task_id = None

# Header
st.markdown('<h1 class="main-header">⏱️ CampusEingang Time Tracker</h1>', unsafe_allow_html=True)
st.markdown("Gestion intelligente de ton temps universitaire")

# Sidebar
with st.sidebar:
    st.markdown("### ⏳ Timer Actif")
    
    if st.session_state.active_timer:
        data = load_data()
        task = next((t for t in data["tasks"] if t["id"] == st.session_state.timer_task_id), None)
        if task:
            elapsed = datetime.now() - st.session_state.timer_start
            minutes = int(elapsed.total_seconds() / 60)
            seconds = int(elapsed.total_seconds() % 60)
            
            st.markdown(f"""
            <div class="active-timer">
                <h4 style="margin:0;">▶️ {task['title']}</h4>
                <p style="font-size:2rem; font-weight:bold; margin:10px 0;">{minutes:02d}:{seconds:02d}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏸️ Stopp", use_container_width=True):
                    elapsed = datetime.now() - st.session_state.timer_start
                    minutes = elapsed.total_seconds() / 60
                    
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
                    
                    data = load_data()
                    for t in data["tasks"]:
                        if t["id"] == task["id"]:
                            t["total_time_spent"] = t.get("total_time_spent", 0) + round(minutes, 2)
                            break
                    save_data(data)
                    
                    st.session_state.active_timer = False
                    st.rerun()
            
            with col2:
                if st.button("❌ Abbrechen", use_container_width=True):
                    st.session_state.active_timer = False
                    st.rerun()
    else:
        st.info("💤 Kein aktiver Timer")
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📊 Quick Stats")
    data = load_data()
    time_entries = load_time_entries()
    
    total_time = sum([e.get("duration_minutes", 0) for e in time_entries])
    tasks_done = len([t for t in data["tasks"] if t.get("done", False)])
    tasks_total = len(data["tasks"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⏱️ Total", f"{int(total_time)} min")
    with col2:
        st.metric("✅ Aufgaben", f"{tasks_done}/{tasks_total}")

# Onglets
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Aufgaben", "➕ Neue Aufgabe", "⏱️ Zeiterfassung", "📊 Analysen", "🗣️ Feedback"
])

# TAB 1: Aufgaben
with tab1:
    st.header("📋 Meine Aufgaben")
    
    data = load_data()
    
    if data["tasks"]:
        df = pd.DataFrame(data["tasks"])
        
        # Overdue
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
        
        # Filtre
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
        
        for _, task in df.iterrows():
            # Badge
            if task.get("overdue"):
                badge = '<span class="badge-overdue">⚠️ Überfällig</span>'
            elif task["deadline_date"] and task["deadline_date"] <= today:
                badge = '<span class="badge-today">🔔 Heute</span>'
            else:
                badge = f'<span class="badge-upcoming">📅 {task["deadline"]}</span>'
            
            # Priorité
            priority_colors = {"Hoch": "#ff6b6b", "Mittel": "#feca57", "Niedrig": "#48dbfb"}
            priority_color = priority_colors.get(task.get("priority", "Mittel"), "#feca57")
            
            st.markdown(f"""
            <div class="task-card" style="border-left: 5px solid {priority_color};">
                <div style="display: flex; justify-content: space-between;">
                    <h3 style="margin:0;">{task['title']}</h3>
                    {badge}
                </div>
                <p>📂 {task['category']} | 🎯 {task.get('priority', 'Mittel')}</p>
                <p>⏱️ {task.get('total_time_spent', 0):.0f} min / {task.get('estimated_time', 60)} min</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                st.progress(min(task.get('total_time_spent', 0) / task.get('estimated_time', 60), 1.0))
            
            with col2:
                if not task.get("done", False) and not st.session_state.active_timer:
                    if st.button("▶️ Start", key=f"start_{task['id']}"):
                        st.session_state.active_timer = True
                        st.session_state.timer_start = datetime.now()
                        st.session_state.timer_task_id = task["id"]
                        st.rerun()
            
            with col3:
                if st.button("✓ Done", key=f"done_{task['id']}"):
                    data = load_data()
                    for t in data["tasks"]:
                        if t["id"] == task["id"]:
                            t["done"] = not t.get("done", False)
                            break
                    save_data(data)
                    st.rerun()
            
            with col4:
                if st.button("✏️", key=f"edit_{task['id']}"):
                    st.session_state[f"edit_{task['id']}"] = True
            
            with col5:
                if st.button("🗑️", key=f"del_{task['id']}"):
                    data = load_data()
                    data["tasks"] = [t for t in data["tasks"] if t["id"] != task["id"]]
                    save_data(data)
                    st.rerun()
            
            if st.session_state.get(f"edit_{task['id']}", False):
                with st.form(key=f"form_{task['id']}"):
                    new_title = st.text_input("Titel", value=task["title"])
                    if st.form_submit_button("Speichern"):
                        data = load_data()
                        for t in data["tasks"]:
                            if t["id"] == task["id"]:
                                t["title"] = new_title
                                break
                        save_data(data)
                        st.session_state[f"edit_{task['id']}"] = False
                        st.rerun()
            
            st.divider()
    else:
        st.info("✨ Keine Aufgaben vorhanden.")

# TAB 2: Neue Aufgabe
with tab2:
    st.header("➕ Neue Aufgabe")
    
    with st.form("new_task"):
        title = st.text_input("Titel *")
        category = st.selectbox("Kategorie", ["Immatrikulation", "Organisatorisch", "Prüfungen", "Sonstiges"])
        deadline = st.date_input("Frist", min_value=today)
        estimated_time = st.number_input("Geschätzte Zeit (min)", min_value=5, value=60)
        priority = st.select_slider("Priorität", ["Niedrig", "Mittel", "Hoch"])
        notes = st.text_area("Notizen")
        
        if st.form_submit_button("Erstellen") and title:
            data = load_data()
            task = {
                "id": data["next_id"],
                "title": title,
                "category": category,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "notes": notes,
                "done": False,
                "estimated_time": estimated_time,
                "total_time_spent": 0,
                "priority": priority
            }
            data["tasks"].append(task)
            data["next_id"] += 1
            save_data(data)
            st.success("✅ Aufgabe erstellt!")
            st.rerun()

# TAB 3: Zeiterfassung
with tab3:
    st.header("⏱️ Zeiterfassung")
    
    entries = load_time_entries()
    
    if entries:
        df = pd.DataFrame(entries)
        
        # Graphique simple avec st.line_chart
        daily = df.groupby('date')['duration_minutes'].sum().reset_index()
        st.subheader("Tägliche Arbeitszeit")
        st.line_chart(daily.set_index('date'))
        
        # Tableau
        st.subheader("Letzte Einträge")
        display_df = df.copy()
        display_df['Datum'] = pd.to_datetime(display_df['date']).dt.strftime('%d.%m.%Y')
        display_df['Dauer'] = display_df['duration_minutes'].apply(lambda x: f"{int(x)} min")
        st.dataframe(display_df[['Datum', 'task_title', 'Dauer']], use_container_width=True, hide_index=True)
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Zeit", f"{int(df['duration_minutes'].sum())} min")
        with col2:
            st.metric("Einträge", len(df))
        with col3:
            st.metric("Ø pro Tag", f"{int(df['duration_minutes'].mean())} min")
    else:
        st.info("Noch keine Zeiteinträge.")

# TAB 4: Analysen
with tab4:
    st.header("📊 Analysen")
    
    data = load_data()
    
    if data["tasks"]:
        # Stats simples
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(data["tasks"])
        done = len([t for t in data["tasks"] if t.get("done", False)])
        overdue = len([t for t in data["tasks"] if 
                      not t.get("done", False) and 
                      t.get("deadline", "9999") < date.today().strftime("%Y-%m-%d")])
        total_time = sum([t.get("total_time_spent", 0) for t in data["tasks"]])
        
        with col1:
            st.metric("Total", total)
        with col2:
            st.metric("Erledigt", done, f"{int(done/total*100)}%" if total > 0 else "0%")
        with col3:
            st.metric("Überfällig", overdue)
        with col4:
            st.metric("Zeit total", f"{int(total_time)} min")
        
        # Tableau
        st.subheader("Alle Aufgaben")
        df = pd.DataFrame(data["tasks"])
        df['Fortschritt'] = df.apply(
            lambda x: f"{min(100, int(x.get('total_time_spent', 0)/x.get('estimated_time', 1)*100))}%", 
            axis=1
        )
        st.dataframe(df[['title', 'category', 'priority', 'estimated_time', 'total_time_spent', 'Fortschritt', 'done']],
                    use_container_width=True, hide_index=True)
    else:
        st.info("Keine Daten für Analysen.")

# TAB 5: Feedback
with tab5:
    st.header("🗣️ Feedback")
    
    with st.form("feedback"):
        name = st.text_input("Name (optional)")
        feedback = st.text_area("Dein Feedback *")
        
        if st.form_submit_button("Absenden") and feedback:
            with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
            
            entries.append({
                "name": name or "Anonym",
                "feedback": feedback,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
            with open(SURVEY_FILE, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
            
            st.success("Danke!")
    
    # Afficher les feedbacks
    if os.path.exists(SURVEY_FILE):
        with open(SURVEY_FILE, "r", encoding="utf-8") as f:
            entries = json.load(f)
        
        if entries:
            st.subheader("Letzte Feedbacks")
            for e in reversed(entries[-5:]):
                with st.container():
                    st.markdown(f"**{e['name']}** - {e['time']}")
                    st.markdown(f"> {e['feedback']}")
                    st.divider()