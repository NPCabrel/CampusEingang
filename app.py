# app.py - CampusEingang Version Finale (Multilingue + Timer + Email)

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import time
import sendgrid
from sendgrid.helpers.mail import Mail
import hmac
import hashlib

# Configuration de la page
st.set_page_config(
    page_title="CampusEingang", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CONFIGURATION MULTILINGUE ====================
LANGUAGES = {
    'DE': 'Deutsch',
    'FR': 'Français',
    'EN': 'English',
    'ES': 'Español',
    'IT': 'Italiano'
}

# Dictionnaire de traductions
TRANSLATIONS = {
    'DE': {
        # Général
        'app_title': '🎓 CampusEingang - Studienstart-Assistent',
        'active_timer': '⏳ Aktiver Timer',
        'no_active_timer': '💤 Kein aktiver Timer',
        'quick_stats': '📊 Quick Stats',
        'total_time': '⏱️ Gesamtzeit',
        'tasks': '✅ Aufgaben',
        'filter': 'Filter:',
        'all': 'Alle',
        'active': 'Aktiv',
        'completed': 'Erledigt',
        'overdue': 'Überfällig',
        
        # Tâches
        'tasks_header': '📋 Meine Aufgaben',
        'category': 'Kategorie',
        'priority': 'Priorität',
        'estimated_time': 'Geschätzte Zeit',
        'time_spent': 'Verbrauchte Zeit',
        'deadline': 'Frist',
        'notes': 'Notizen',
        'start': '▶️ Start',
        'stop': '⏹️ Stop',
        'pause': '⏸️ Pause',
        'done': '✓ Erledigt',
        'edit': '✏️ Bearbeiten',
        'delete': '🗑️ Löschen',
        'restore': '♻️ Wiederherstellen',
        'permanent_delete': '❌ Endgültig löschen',
        
        # Nouvelle tâche
        'new_task': '➕ Neue Aufgabe',
        'title': 'Titel',
        'category_options': ['Immatrikulation', 'Organisatorisch', 'Prüfungen', 'Finanzen', 'Wohnen', 'Sonstiges'],
        'priority_options': ['Niedrig', 'Mittel', 'Hoch'],
        'create_task': '🚀 Aufgabe erstellen',
        'task_created': '✅ Aufgabe erfolgreich erstellt!',
        
        # Timer
        'timer_running': '▶️ Läuft:',
        'timer_stopped': '⏹️ Gestoppt',
        'time_recorded': '⏱️ Zeit erfasst:',
        
        # Feedback
        'feedback_header': '🗣️ Feedback & Probleme',
        'your_feedback': 'Dein Feedback',
        'name': 'Name',
        'email': 'E-Mail',
        'feedback_type': 'Art des Feedbacks',
        'feedback_types': ['💡 Verbesserungsvorschlag', '🐛 Bug melden', '❓ Frage', '👍 Lob', '👎 Kritik'],
        'urgency': 'Dringlichkeit',
        'urgency_options': ['Niedrig', 'Mittel', 'Hoch', 'Kritisch'],
        'feedback_text': 'Dein Feedback',
        'send': '📨 Senden',
        'feedback_sent': '✅ Feedback erfolgreich gesendet!',
        'feedback_received': 'Danke für dein Feedback!',
        
        # Corbeille
        'recycle_bin': '🗑️ Papierkorb',
        'empty_bin': 'Der Papierkorb ist leer',
        'deleted_tasks': 'Gelöschte Aufgaben',
        'deleted_at': 'Gelöscht am',
        'days_ago': 'Tagen',
        'today': 'Heute',
        'yesterday': 'Gestern',
        
        # Analysen
        'analysis': '📊 Analysen',
        'by_category': 'Aufgaben nach Kategorie',
        'progress': 'Fortschritt',
        'stats': 'Statistiken',
        'export': '📥 Exportieren',
        
        # Zeit
        'minutes': 'Minuten',
        'hours': 'Stunden',
        'days': 'Tage',
        'min': 'min',
        'h': 'h',
    },
    'FR': {
        'app_title': '🎓 CampusEingang - Assistant de Rentrée',
        'active_timer': '⏳ Minuteur actif',
        'no_active_timer': '💤 Aucun minuteur actif',
        'quick_stats': '📊 Stats rapides',
        'total_time': '⏱️ Temps total',
        'tasks': '✅ Tâches',
        'filter': 'Filtre:',
        'all': 'Tous',
        'active': 'Actifs',
        'completed': 'Terminés',
        'overdue': 'En retard',
        'tasks_header': '📋 Mes tâches',
        'category': 'Catégorie',
        'priority': 'Priorité',
        'estimated_time': 'Temps estimé',
        'time_spent': 'Temps passé',
        'deadline': 'Échéance',
        'notes': 'Notes',
        'start': '▶️ Démarrer',
        'stop': '⏹️ Arrêter',
        'pause': '⏸️ Pause',
        'done': '✓ Terminé',
        'edit': '✏️ Modifier',
        'delete': '🗑️ Supprimer',
        'restore': '♻️ Restaurer',
        'permanent_delete': '❌ Supprimer définitivement',
        'new_task': '➕ Nouvelle tâche',
        'title': 'Titre',
        'category_options': ['Inscription', 'Organisation', 'Examens', 'Finances', 'Logement', 'Autres'],
        'priority_options': ['Basse', 'Moyenne', 'Haute'],
        'create_task': '🚀 Créer la tâche',
        'task_created': '✅ Tâche créée avec succès!',
        'timer_running': '▶️ En cours:',
        'timer_stopped': '⏹️ Arrêté',
        'time_recorded': '⏱️ Temps enregistré:',
        'feedback_header': '🗣️ Feedback & Problèmes',
        'your_feedback': 'Votre feedback',
        'name': 'Nom',
        'email': 'E-mail',
        'feedback_type': 'Type de feedback',
        'feedback_types': ['💡 Suggestion', '🐛 Bug', '❓ Question', '👍 Éloge', '👎 Critique'],
        'urgency': 'Urgence',
        'urgency_options': ['Basse', 'Moyenne', 'Haute', 'Critique'],
        'feedback_text': 'Votre feedback',
        'send': '📨 Envoyer',
        'feedback_sent': '✅ Feedback envoyé avec succès!',
        'feedback_received': 'Merci pour votre feedback!',
        'recycle_bin': '🗑️ Corbeille',
        'empty_bin': 'La corbeille est vide',
        'deleted_tasks': 'Tâches supprimées',
        'deleted_at': 'Supprimé le',
        'days_ago': 'jours',
        'today': 'Aujourd\'hui',
        'yesterday': 'Hier',
        'analysis': '📊 Analyses',
        'by_category': 'Tâches par catégorie',
        'progress': 'Progression',
        'stats': 'Statistiques',
        'export': '📥 Exporter',
        'minutes': 'Minutes',
        'hours': 'Heures',
        'days': 'Jours',
        'min': 'min',
        'h': 'h',
    },
    'EN': {
        'app_title': '🎓 CampusEingang - Study Start Assistant',
        'active_timer': '⏳ Active Timer',
        'no_active_timer': '💤 No active timer',
        'quick_stats': '📊 Quick Stats',
        'total_time': '⏱️ Total Time',
        'tasks': '✅ Tasks',
        'filter': 'Filter:',
        'all': 'All',
        'active': 'Active',
        'completed': 'Completed',
        'overdue': 'Overdue',
        'tasks_header': '📋 My Tasks',
        'category': 'Category',
        'priority': 'Priority',
        'estimated_time': 'Estimated Time',
        'time_spent': 'Time Spent',
        'deadline': 'Deadline',
        'notes': 'Notes',
        'start': '▶️ Start',
        'stop': '⏹️ Stop',
        'pause': '⏸️ Pause',
        'done': '✓ Done',
        'edit': '✏️ Edit',
        'delete': '🗑️ Delete',
        'restore': '♻️ Restore',
        'permanent_delete': '❌ Permanently Delete',
        'new_task': '➕ New Task',
        'title': 'Title',
        'category_options': ['Enrollment', 'Organizational', 'Exams', 'Finances', 'Housing', 'Others'],
        'priority_options': ['Low', 'Medium', 'High'],
        'create_task': '🚀 Create Task',
        'task_created': '✅ Task created successfully!',
        'timer_running': '▶️ Running:',
        'timer_stopped': '⏹️ Stopped',
        'time_recorded': '⏱️ Time recorded:',
        'feedback_header': '🗣️ Feedback & Issues',
        'your_feedback': 'Your Feedback',
        'name': 'Name',
        'email': 'Email',
        'feedback_type': 'Feedback Type',
        'feedback_types': ['💡 Suggestion', '🐛 Bug Report', '❓ Question', '👍 Praise', '👎 Criticism'],
        'urgency': 'Urgency',
        'urgency_options': ['Low', 'Medium', 'High', 'Critical'],
        'feedback_text': 'Your Feedback',
        'send': '📨 Send',
        'feedback_sent': '✅ Feedback sent successfully!',
        'feedback_received': 'Thank you for your feedback!',
        'recycle_bin': '🗑️ Recycle Bin',
        'empty_bin': 'The recycle bin is empty',
        'deleted_tasks': 'Deleted Tasks',
        'deleted_at': 'Deleted on',
        'days_ago': 'days ago',
        'today': 'Today',
        'yesterday': 'Yesterday',
        'analysis': '📊 Analysis',
        'by_category': 'Tasks by Category',
        'progress': 'Progress',
        'stats': 'Statistics',
        'export': '📥 Export',
        'minutes': 'Minutes',
        'hours': 'Hours',
        'days': 'Days',
        'min': 'min',
        'h': 'h',
    },
    'ES': {
        'app_title': '🎓 CampusEingang - Asistente de Inicio',
        'active_timer': '⏳ Temporizador activo',
        'no_active_timer': '💤 Sin temporizador activo',
        'quick_stats': '📊 Estadísticas rápidas',
        'total_time': '⏱️ Tiempo total',
        'tasks': '✅ Tareas',
        'filter': 'Filtro:',
        'all': 'Todos',
        'active': 'Activos',
        'completed': 'Completados',
        'overdue': 'Vencidos',
        'tasks_header': '📋 Mis tareas',
        'category': 'Categoría',
        'priority': 'Prioridad',
        'estimated_time': 'Tiempo estimado',
        'time_spent': 'Tiempo empleado',
        'deadline': 'Fecha límite',
        'notes': 'Notas',
        'start': '▶️ Iniciar',
        'stop': '⏹️ Parar',
        'pause': '⏸️ Pausa',
        'done': '✓ Hecho',
        'edit': '✏️ Editar',
        'delete': '🗑️ Eliminar',
        'restore': '♻️ Restaurar',
        'permanent_delete': '❌ Eliminar permanentemente',
        'new_task': '➕ Nueva tarea',
        'title': 'Título',
        'category_options': ['Matrícula', 'Organización', 'Exámenes', 'Finanzas', 'Vivienda', 'Otros'],
        'priority_options': ['Baja', 'Media', 'Alta'],
        'create_task': '🚀 Crear tarea',
        'task_created': '✅ ¡Tarea creada con éxito!',
        'timer_running': '▶️ En curso:',
        'timer_stopped': '⏹️ Detenido',
        'time_recorded': '⏱️ Tiempo registrado:',
        'feedback_header': '🗣️ Feedback y Problemas',
        'your_feedback': 'Tu feedback',
        'name': 'Nombre',
        'email': 'Email',
        'feedback_type': 'Tipo de feedback',
        'feedback_types': ['💡 Sugerencia', '🐛 Reportar error', '❓ Pregunta', '👍 Elogio', '👎 Crítica'],
        'urgency': 'Urgencia',
        'urgency_options': ['Baja', 'Media', 'Alta', 'Crítica'],
        'feedback_text': 'Tu feedback',
        'send': '📨 Enviar',
        'feedback_sent': '✅ ¡Feedback enviado con éxito!',
        'feedback_received': '¡Gracias por tu feedback!',
        'recycle_bin': '🗑️ Papelera',
        'empty_bin': 'La papelera está vacía',
        'deleted_tasks': 'Tareas eliminadas',
        'deleted_at': 'Eliminado el',
        'days_ago': 'días',
        'today': 'Hoy',
        'yesterday': 'Ayer',
        'analysis': '📊 Análisis',
        'by_category': 'Tareas por categoría',
        'progress': 'Progreso',
        'stats': 'Estadísticas',
        'export': '📥 Exportar',
        'minutes': 'Minutos',
        'hours': 'Horas',
        'days': 'Días',
        'min': 'min',
        'h': 'h',
    },
    'IT': {
        'app_title': '🎓 CampusEingang - Assistente di Avvio',
        'active_timer': '⏳ Timer attivo',
        'no_active_timer': '💤 Nessun timer attivo',
        'quick_stats': '📊 Statistiche rapide',
        'total_time': '⏱️ Tempo totale',
        'tasks': '✅ Compiti',
        'filter': 'Filtro:',
        'all': 'Tutti',
        'active': 'Attivi',
        'completed': 'Completati',
        'overdue': 'In ritardo',
        'tasks_header': '📋 I miei compiti',
        'category': 'Categoria',
        'priority': 'Priorità',
        'estimated_time': 'Tempo stimato',
        'time_spent': 'Tempo impiegato',
        'deadline': 'Scadenza',
        'notes': 'Note',
        'start': '▶️ Avvia',
        'stop': '⏹️ Ferma',
        'pause': '⏸️ Pausa',
        'done': '✓ Fatto',
        'edit': '✏️ Modifica',
        'delete': '🗑️ Elimina',
        'restore': '♻️ Ripristina',
        'permanent_delete': '❌ Elimina definitivamente',
        'new_task': '➕ Nuovo compito',
        'title': 'Titolo',
        'category_options': ['Immatricolazione', 'Organizzativo', 'Esami', 'Finanze', 'Alloggio', 'Altri'],
        'priority_options': ['Bassa', 'Media', 'Alta'],
        'create_task': '🚀 Crea compito',
        'task_created': '✅ Compito creato con successo!',
        'timer_running': '▶️ In corso:',
        'timer_stopped': '⏹️ Fermato',
        'time_recorded': '⏱️ Tempo registrato:',
        'feedback_header': '🗣️ Feedback e Problemi',
        'your_feedback': 'Il tuo feedback',
        'name': 'Nome',
        'email': 'Email',
        'feedback_type': 'Tipo di feedback',
        'feedback_types': ['💡 Suggerimento', '🐛 Segnala bug', '❓ Domanda', '👍 Lode', '👎 Critica'],
        'urgency': 'Urgenza',
        'urgency_options': ['Bassa', 'Media', 'Alta', 'Critica'],
        'feedback_text': 'Il tuo feedback',
        'send': '📨 Invia',
        'feedback_sent': '✅ Feedback inviato con successo!',
        'feedback_received': 'Grazie per il tuo feedback!',
        'recycle_bin': '🗑️ Cestino',
        'empty_bin': 'Il cestino è vuoto',
        'deleted_tasks': 'Compiti eliminati',
        'deleted_at': 'Eliminato il',
        'days_ago': 'giorni fa',
        'today': 'Oggi',
        'yesterday': 'Ieri',
        'analysis': '📊 Analisi',
        'by_category': 'Compiti per categoria',
        'progress': 'Progresso',
        'stats': 'Statistiche',
        'export': '📥 Esporta',
        'minutes': 'Minuti',
        'hours': 'Ore',
        'days': 'Giorni',
        'min': 'min',
        'h': 'h',
    }
}

# Fonction pour obtenir la traduction
def t(key):
    """Retourne la traduction pour la clé donnée dans la langue sélectionnée"""
    lang = st.session_state.get('language', 'DE')
    return TRANSLATIONS[lang].get(key, key)

# Sélecteur de langue dans la sidebar
with st.sidebar:
    st.markdown("### 🌐 Sprache / Langue / Language")
    selected_lang = st.selectbox(
        "",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        key='language'
    )

# ==================== CONFIGURATION EMAIL ====================
# Configuration SendGrid (à mettre dans les secrets Streamlit)
SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY", "TA_CLE_API_ICI")
FROM_EMAIL = "campus@eingang.de"  # À vérifier dans SendGrid
TO_EMAIL = "naguepascal5@gmail.com"  # TON EMAIL POUR RECEVOIR LES FEEDBACKS

def send_feedback_email(name, email, feedback_type, feedback, urgency, lang='DE'):
    """
    Envoie un email avec les détails du feedback à naguepascal5@gmail.com
    """
    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
        # Traductions pour l'email selon la langue de l'utilisateur
        urgency_labels = {
            'DE': ['Niedrig', 'Mittel', 'Hoch', 'Kritisch'],
            'FR': ['Basse', 'Moyenne', 'Haute', 'Critique'],
            'EN': ['Low', 'Medium', 'High', 'Critical'],
            'ES': ['Baja', 'Media', 'Alta', 'Crítica'],
            'IT': ['Bassa', 'Media', 'Alta', 'Critica']
        }
        
        type_labels = {
            'DE': ['Verbesserungsvorschlag', 'Bug melden', 'Frage', 'Lob', 'Kritik'],
            'FR': ['Suggestion', 'Bug', 'Question', 'Éloge', 'Critique'],
            'EN': ['Suggestion', 'Bug Report', 'Question', 'Praise', 'Criticism'],
            'ES': ['Sugerencia', 'Reportar error', 'Pregunta', 'Elogio', 'Crítica'],
            'IT': ['Suggerimento', 'Segnala bug', 'Domanda', 'Lode', 'Critica']
        }
        
        # Construction de l'email HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 25px; border-radius: 15px 15px 0 0; }}
                .content {{ background: #f8f9fa; padding: 25px; border-radius: 0 0 15px 15px; }}
                .field {{ margin: 20px 0; }}
                .label {{ font-weight: bold; color: #667eea; font-size: 1.1em; }}
                .value {{ background: white; padding: 12px; border-radius: 8px; margin-top: 5px;
                         border-left: 4px solid #667eea; }}
                .urgency {{ display: inline-block; padding: 5px 15px; border-radius: 20px; 
                          font-weight: bold; }}
                .urgency-Hoch, .urgency-Haute, .urgency-High, .urgency-Alta {{ 
                    background: #ff6b6b; color: white; }}
                .urgency-Mittel, .urgency-Moyenne, .urgency-Medium, .urgency-Media {{ 
                    background: #feca57; color: black; }}
                .urgency-Niedrig, .urgency-Basse, .urgency-Low, .urgency-Baja {{ 
                    background: #48dbfb; color: black; }}
                .urgency-Kritisch, .urgency-Critique, .urgency-Critical, .urgency-Crítica {{ 
                    background: #ff0000; color: white; }}
                .footer {{ text-align: center; margin-top: 20px; color: #999; }}
                .badge {{ background: #667eea; color: white; padding: 3px 10px; 
                         border-radius: 15px; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin:0;">📬 Neues Feedback - CampusEingang</h1>
                    <p style="margin:5px 0 0; opacity:0.9;">Eingegangen am {datetime.now().strftime('%d.%m.%Y um %H:%M')}</p>
                </div>
                <div class="content">
                    <div style="text-align: right; margin-bottom: 15px;">
                        <span class="badge">Sprache: {LANGUAGES[lang]}</span>
                    </div>
                    
                    <div class="field">
                        <div class="label">👤 Von:</div>
                        <div class="value"><strong>{name}</strong></div>
                    </div>
                    
                    <div class="field">
                        <div class="label">📧 Kontakt:</div>
                        <div class="value">{email if email else 'Nicht angegeben'}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">📝 Art des Feedbacks:</div>
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
                        <div class="value" style="white-space: pre-line;">{feedback}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">🌐 Sprache:</div>
                        <div class="value">{LANGUAGES[lang]}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>Dieses Feedback wurde über die CampusEingang-App gesendet.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Créer le message pour toi
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=TO_EMAIL,  # Ton email : naguepascal5@gmail.com
            subject=f'📬 CampusEingang - Neues Feedback von {name}',
            html_content=html_content
        )
        
        # Envoyer
        response = sg.send(message)
        
        # Optionnel: Envoyer une confirmation à l'utilisateur si email fourni
        if email:
            user_lang = lang
            confirm_subject = {
                'DE': '✅ Dein Feedback wurde empfangen',
                'FR': '✅ Votre feedback a été reçu',
                'EN': '✅ Your feedback has been received',
                'ES': '✅ Tu feedback ha sido recibido',
                'IT': '✅ Il tuo feedback è stato ricevuto'
            }.get(user_lang, '✅ Feedback received')
            
            confirm_message = {
                'DE': f'Hallo {name},\n\ndanke für dein Feedback! Wir werden es schnellstmöglich bearbeiten.\n\nDein Feedback: {feedback}\n\nVielen Dank!\nDein CampusEingang-Team',
                'FR': f'Bonjour {name},\n\nmerci pour votre feedback ! Nous allons le traiter rapidement.\n\nVotre feedback : {feedback}\n\nMerci beaucoup !\nL\'équipe CampusEingang',
                'EN': f'Hello {name},\n\nthank you for your feedback! We will process it as soon as possible.\n\nYour feedback: {feedback}\n\nThank you very much!\nYour CampusEingang Team',
                'ES': f'Hola {name},\n\n¡gracias por tu feedback! Lo procesaremos lo antes posible.\n\nTu feedback: {feedback}\n\n¡Muchas gracias!\nEl equipo de CampusEingang',
                'IT': f'Ciao {name},\n\ngrazie per il tuo feedback! Lo elaboreremo il prima possibile.\n\nIl tuo feedback: {feedback}\n\nGrazie mille!\nIl team di CampusEingang'
            }.get(user_lang, f'Thank you for your feedback, {name}!')
            
            confirmation = Mail(
                from_email=FROM_EMAIL,
                to_emails=email,
                subject=confirm_subject,
                plain_text_content=confirm_message
            )
            sg.send(confirmation)
        
        return True, "Email envoyé avec succès"
    
    except Exception as e:
        return False, str(e)

# ==================== CONFIGURATION DES FICHIERS ====================
DATA_DIR = "campus_data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "data.json")
TIME_TRACKING_FILE = os.path.join(DATA_DIR, "time_tracking.json")
SURVEY_FILE = os.path.join(DATA_DIR, "survey.json")
RECYCLE_BIN_FILE = os.path.join(DATA_DIR, "recycle_bin.json")

# Données par défaut
default_data = {
    "tasks": [
        {
            "id": 1, 
            "title": "Immatrikulation abschließen", 
            "category": "Immatrikulation",
            "deadline": "2026-10-01", 
            "link": "", 
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

# ==================== FONCTIONS DE GESTION DES DONNÉES ====================
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
    
    if not os.path.exists(RECYCLE_BIN_FILE):
        with open(RECYCLE_BIN_FILE, "w", encoding="utf-8") as f:
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

# ==================== FONCTIONS POUR LA CORBEILLE ====================
def load_recycle_bin():
    ensure_files()
    if os.path.exists(RECYCLE_BIN_FILE):
        with open(RECYCLE_BIN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_recycle_bin(items):
    with open(RECYCLE_BIN_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def move_to_recycle_bin(task):
    recycle_bin = load_recycle_bin()
    task_with_meta = task.copy()
    task_with_meta['deleted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task_with_meta['can_be_restored'] = True
    recycle_bin.append(task_with_meta)
    save_recycle_bin(recycle_bin)

def restore_from_recycle_bin(task_id):
    recycle_bin = load_recycle_bin()
    task_to_restore = None
    
    for task in recycle_bin:
        if task['id'] == task_id:
            task_to_restore = task
            recycle_bin.remove(task)
            break
    
    if task_to_restore:
        task_to_restore.pop('deleted_at', None)
        task_to_restore.pop('can_be_restored', None)
        save_recycle_bin(recycle_bin)
        return task_to_restore
    
    return None

def permanently_delete(task_id):
    recycle_bin = load_recycle_bin()
    recycle_bin = [t for t in recycle_bin if t['id'] != task_id]
    save_recycle_bin(recycle_bin)

# ==================== SESSION STATE POUR LE TIMER ====================
if 'active_timer' not in st.session_state:
    st.session_state.active_timer = False
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None
if 'timer_task_id' not in st.session_state:
    st.session_state.timer_task_id = None
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'current_time' not in st.session_state:
    st.session_state.current_time = 0

# ==================== CSS PERSONNALISÉ ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
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
        text-align: center;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }
    .timer-display {
        font-size: 3rem;
        font-weight: bold;
        color: #667eea;
        margin: 10px 0;
    }
    .stButton > button {
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER PRINCIPAL ====================
st.markdown(f'<h1 class="main-header">{t("app_title")}</h1>', unsafe_allow_html=True)

# ==================== SIDEBAR AVEC TIMER AMÉLIORÉ ====================
with st.sidebar:
    st.markdown(f"### {t('active_timer')}")
    
    # Timer amélioré avec mise à jour automatique
    if st.session_state.active_timer and st.session_state.timer_running:
        data = load_data()
        task = next((t for t in data["tasks"] if t["id"] == st.session_state.timer_task_id), None)
        
        if task:
            # Calculer le temps écoulé
            elapsed = datetime.now() - st.session_state.timer_start
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            seconds = int(elapsed.total_seconds() % 60)
            
            # Mettre à jour le temps actuel
            st.session_state.current_time = elapsed.total_seconds()
            
            # Afficher le timer
            st.markdown(f"""
            <div class="active-timer">
                <h4 style="margin:0;">▶️ {task['title'][:30]}{'...' if len(task['title']) > 30 else ''}</h4>
                <div class="timer-display">{hours:02d}:{minutes:02d}:{seconds:02d}</div>
                <p style="margin:0;">Start: {st.session_state.timer_start.strftime('%H:%M:%S')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Boutons de contrôle
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t('stop'), use_container_width=True, type="primary"):
                    # Arrêter le timer et sauvegarder
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
                    st.session_state.timer_running = False
                    st.session_state.current_time = 0
                    st.rerun()
            
            with col2:
                if st.button(t('pause'), use_container_width=True):
                    st.session_state.timer_running = False
                    st.rerun()
            
            # Auto-refresh toutes les secondes
            time.sleep(0.1)
            st.rerun()
    
    elif st.session_state.active_timer and not st.session_state.timer_running:
        # Timer en pause
        st.markdown("""
        <div style="background: #f0f0f0; border-radius: 15px; padding: 20px; text-align: center;">
            <h4>⏸️ Timer pausiert</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶️ Fortsetzen", use_container_width=True):
            st.session_state.timer_running = True
            st.rerun()
        
        if st.button("⏹️ Beenden", use_container_width=True):
            st.session_state.active_timer = False
            st.session_state.timer_running = False
            st.session_state.current_time = 0
            st.rerun()
    
    else:
        st.info(t('no_active_timer'))
        st.markdown("*" + t('start') + " " + t('tasks') + "*")
    
    st.markdown("---")
    
    # Statistiques rapides
    st.markdown(f"### {t('quick_stats')}")
    data = load_data()
    time_entries = load_time_entries()
    
    total_time = sum([e.get("duration_minutes", 0) for e in time_entries])
    tasks_done = len([t for t in data["tasks"] if t.get("done", False)])
    tasks_total = len(data["tasks"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(t('total_time'), f"{int(total_time)} {t('min')}", f"{int(total_time/60)}{t('h')}")
    with col2:
        st.metric(t('tasks'), f"{tasks_done}/{tasks_total}")

# ==================== ONGLETS ====================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t('tasks_header'), 
    t('new_task'), 
    t('time_recorded').replace('⏱️ ', '⏱️ '), 
    t('analysis'),
    t('feedback_header'),
    t('recycle_bin')
])

# ==================== TAB 1: AUFGABEN ====================
with tab1:
    st.header(t('tasks_header'))
    
    data = load_data()
    today = date.today()
    
    if data["tasks"]:
        # Créer DataFrame
        df = pd.DataFrame(data["tasks"])
        
        # Calculer overdue
        def parse_deadline(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date() if s else None
            except:
                return None
        
        df["deadline_date"] = df["deadline"].apply(parse_deadline)
        df["overdue"] = df.apply(lambda r: (not r.get("done", False)) and 
                                 (r["deadline_date"] is not None) and 
                                 (r["deadline_date"] < today), axis=1)
        
        # Filtre
        filter_options = [t('all'), t('active'), t('completed'), t('overdue')]
        filter_option = st.radio(t('filter'), filter_options, horizontal=True)
        
        if filter_option == t('active'):
            df = df[~df["done"]]
        elif filter_option == t('completed'):
            df = df[df["done"]]
        elif filter_option == t('overdue'):
            df = df[df["overdue"]]
        
        # Afficher les tâches
        for idx, task in df.iterrows():
            # Badge
            if task.get("overdue"):
                badge = f'<span class="badge-overdue">⚠️ {t("overdue")}</span>'
            elif task["deadline_date"] and task["deadline_date"] <= today:
                badge = f'<span class="badge-today">🔔 {t("today")}</span>'
            elif task["deadline_date"]:
                days_left = (task["deadline_date"] - today).days
                badge = f'<span class="badge-upcoming">📅 {days_left} {t("days")}</span>'
            else:
                badge = f'<span class="badge-upcoming">📅 {task["deadline"]}</span>'
            
            # Couleur priorité
            priority = task.get('priority', 'Mittel')
            priority_color = {
                t('priority_options')[2]: "#ff6b6b",  # Hoch/Haute/High
                t('priority_options')[1]: "#feca57",  # Mittel/Moyenne/Medium
                t('priority_options')[0]: "#48dbfb"   # Niedrig/Basse/Low
            }.get(priority, "#feca57")
            
            st.markdown(f"""
            <div class="task-card" style="border-left: 5px solid {priority_color};">
                <div style="display: flex; justify-content: space-between;">
                    <h3 style="margin:0;">{task['title']}</h3>
                    {badge}
                </div>
                <p>📂 {task['category']} | 🎯 {priority}</p>
                <p>⏱️ {task.get('total_time_spent', 0):.0f} {t('min')} / {task.get('estimated_time', 60)} {t('min')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                progress = min(task.get('total_time_spent', 0) / max(task.get('estimated_time', 60), 1), 1.0)
                st.progress(progress)
            
            with col2:
                if not task.get("done", False) and not st.session_state.active_timer:
                    if st.button(t('start'), key=f"start_{task['id']}", use_container_width=True):
                        st.session_state.active_timer = True
                        st.session_state.timer_running = True
                        st.session_state.timer_start = datetime.now()
                        st.session_state.timer_task_id = task["id"]
                        st.rerun()
                elif st.session_state.active_timer and st.session_state.timer_task_id == task["id"]:
                    if st.button(t('stop'), key=f"stop_{task['id']}", use_container_width=True):
                        # Arrêter le timer
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
                        st.session_state.timer_running = False
                        st.rerun()
            
            with col3:
                if st.button(t('done'), key=f"done_{task['id']}", use_container_width=True):
                    data = load_data()
                    for t in data["tasks"]:
                        if t["id"] == task["id"]:
                            t["done"] = not t.get("done", False)
                            break
                    save_data(data)
                    st.rerun()
            
            with col4:
                if st.button(t('edit'), key=f"edit_{task['id']}", use_container_width=True):
                    st.session_state[f"edit_{task['id']}"] = True
            
            with col5:
                if st.button("🗑️", key=f"del_{task['id']}", use_container_width=True):
                    # Déplacer vers la corbeille
                    task_dict = dict(task)
                    move_to_recycle_bin(task_dict)
                    
                    data = load_data()
                    data["tasks"] = [t for t in data["tasks"] if t["id"] != task["id"]]
                    save_data(data)
                    
                    st.success(f"✅ Aufgabe in den Papierkorb verschoben!")
                    st.rerun()
            
            # Formulaire d'édition
            if st.session_state.get(f"edit_{task['id']}", False):
                with st.form(key=f"edit_form_{task['id']}"):
                    new_title = st.text_input(t('title'), value=task["title"])
                    new_category = st.selectbox(t('category'), t('category_options'), 
                                              index=t('category_options').index(task.get('category', t('category_options')[0])) if task.get('category') in t('category_options') else 0)
                    new_priority = st.selectbox(t('priority'), t('priority_options'),
                                              index=t('priority_options').index(task.get('priority', t('priority_options')[1])))
                    new_estimated = st.number_input(t('estimated_time'), value=task.get('estimated_time', 60), min_value=1)
                    new_notes = st.text_area(t('notes'), value=task.get('notes', ''))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 " + t('edit')):
                            data = load_data()
                            for t in data["tasks"]:
                                if t["id"] == task["id"]:
                                    t.update({
                                        "title": new_title,
                                        "category": new_category,
                                        "priority": new_priority,
                                        "estimated_time": new_estimated,
                                        "notes": new_notes
                                    })
                                    break
                            save_data(data)
                            st.session_state[f"edit_{task['id']}"] = False
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ " + t('edit') + " " + t('delete')):
                            st.session_state[f"edit_{task['id']}"] = False
                            st.rerun()
            
            st.divider()
    else:
        st.info(f"✨ {t('tasks_header')}")

# ==================== TAB 2: NEUE AUFGABE ====================
with tab2:
    st.header(t('new_task'))
    
    today = date.today()
    
    with st.form("new_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(f"📌 {t('title')} *", placeholder=t('title'))
            category = st.selectbox(f"📂 {t('category')}", t('category_options'))
            priority = st.select_slider(f"🎯 {t('priority')}", options=t('priority_options'), value=t('priority_options')[1])
        
        with col2:
            deadline = st.date_input(f"📅 {t('deadline')}", min_value=today)
            estimated_time = st.number_input(f"⏱️ {t('estimated_time')} ({t('min')})", min_value=5, max_value=480, value=60, step=5)
            link = st.text_input("🔗 Link", placeholder="https://...")
        
        notes = st.text_area(f"📝 {t('notes')}", placeholder="...", height=100)
        
        submitted = st.form_submit_button(f"🚀 {t('create_task')}", use_container_width=True)
        
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
            st.success(f"✅ {t('task_created')}")
            st.balloons()

# ==================== TAB 3: ZEITERFASSUNG ====================
with tab3:
    st.header("⏱️ " + t('time_recorded').replace('⏱️ ', ''))
    
    time_entries = load_time_entries()
    
    if time_entries:
        entries_df = pd.DataFrame(time_entries)
        entries_df['date'] = pd.to_datetime(entries_df['date'])
        
        # Graphique
        daily_time = entries_df.groupby('date')['duration_minutes'].sum().reset_index()
        fig = px.bar(daily_time, x='date', y='duration_minutes', 
                     title=t('time_recorded').replace('⏱️ ', ''),
                     labels={'duration_minutes': t('minutes'), 'date': t('deadline')})
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau
        st.subheader("📋 " + t('time_recorded'))
        display_df = entries_df.copy()
        display_df['Datum'] = display_df['date'].dt.strftime('%d.%m.%Y')
        display_df[t('tasks')] = display_df['task_title']
        display_df[t('minutes')] = display_df['duration_minutes'].apply(lambda x: f"{int(x)} {t('min')}")
        
        st.dataframe(display_df[['Datum', t('tasks'), t('minutes')]], use_container_width=True, hide_index=True)
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t('total_time'), f"{int(entries_df['duration_minutes'].sum())} {t('min')}")
        with col2:
            st.metric(t('tasks'), len(entries_df))
        with col3:
            st.metric(t('stats'), f"{int(entries_df['duration_minutes'].mean())} {t('min')}")
    else:
        st.info("⏳ " + t('time_recorded'))

# ==================== TAB 4: ANALYSEN ====================
with tab4:
    st.header(t('analysis'))
    
    data = load_data()
    today = date.today()
    
    if data["tasks"]:
        # Créer DataFrame sécurisé
        tasks_list = []
        for task in data["tasks"]:
            safe_task = {
                "title": task.get("title", "Sans titre"),
                "category": task.get("category", "Sonstiges"),
                "priority": task.get("priority", t('priority_options')[1]),
                "estimated_time": task.get("estimated_time", 60),
                "total_time_spent": task.get("total_time_spent", 0),
                "done": task.get("done", False),
                "deadline": task.get("deadline", ""),
            }
            tasks_list.append(safe_task)
        
        tasks_df = pd.DataFrame(tasks_list)
        tasks_df['Effizienz'] = tasks_df.apply(
            lambda x: f"{min(100, int(x['total_time_spent'] / max(x['estimated_time'], 1) * 100))}%", 
            axis=1
        )
        tasks_df['Status'] = tasks_df['done'].apply(lambda x: "✅ " + t('completed') if x else "🔄 " + t('active'))
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(t('by_category'))
            if not tasks_df.empty:
                category_counts = tasks_df['category'].value_counts()
                fig = px.pie(values=category_counts.values, names=category_counts.index,
                           title=t('by_category'))
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader(t('progress'))
            done_count = len(tasks_df[tasks_df['done']])
            total_count = len(tasks_df)
            
            if total_count > 0:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=done_count/total_count*100,
                    title={'text': f"{done_count}/{total_count} {t('completed')}"},
                    gauge={'axis': {'range': [None, 100]}}
                ))
                st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques
        st.subheader(t('stats'))
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            total_time_all = tasks_df['total_time_spent'].sum()
            st.metric(t('total_time'), f"{int(total_time_all)} {t('min')}")
        
        with col_m2:
            avg_time = tasks_df['total_time_spent'].mean()
            st.metric(t('stats'), f"{int(avg_time)} {t('min')}")
        
        with col_m3:
            overdue_count = len([
                t for t in data["tasks"] 
                if not t.get("done", False) 
                and t.get("deadline", "9999") < today.strftime("%Y-%m-%d")
            ])
            st.metric(t('overdue'), overdue_count)
        
        with col_m4:
            high_priority = len([t for t in data["tasks"] if t.get("priority") == t('priority_options')[2]])
            st.metric(t('priority'), high_priority)
        
        # Tableau
        st.subheader("📋 " + t('tasks'))
        display_cols = ['title', 'category', 'priority', 'estimated_time', 'total_time_spent', 'Effizienz', 'Status']
        st.dataframe(tasks_df[display_cols], use_container_width=True, hide_index=True)
        
        # Export
        if st.button(t('export')):
            csv = tasks_df.to_csv(index=False)
            st.download_button(
                f"📥 {t('export')} CSV",
                csv,
                f"campus_daten_{date.today().isoformat()}.csv",
                "text/csv"
            )
    else:
        st.info(f"📊 {t('analysis')}")

# ==================== TAB 5: FEEDBACK AVEC EMAIL ====================
with tab5:
    st.header(t('feedback_header'))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("feedback_form"):
            name = st.text_input(f"👤 {t('name')}", placeholder="Max Mustermann")
            email = st.text_input(f"📧 {t('email')}", placeholder="max@example.com", 
                                 help="Für Rückmeldung zu deinem Feedback")
            feedback_type = st.selectbox(f"📝 {t('feedback_type')}", t('feedback_types'))
            urgency = st.select_slider(f"⚠️ {t('urgency')}", options=t('urgency_options'), value=t('urgency_options')[1])
            feedback = st.text_area(f"💬 {t('feedback_text')} *", height=150)
            
            submitted = st.form_submit_button(f"📨 {t('send')}", use_container_width=True, type="primary")
            
            if submitted and feedback:
                with st.spinner("📤 Senden..."):
                    # Sauvegarde locale
                    ensure_files()
                    with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                        entries = json.load(f)
                    
                    entry = {
                        "id": len(entries) + 1,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "name": name or "Anonym",
                        "email": email,
                        "type": feedback_type,
                        "feedback": feedback,
                        "urgency": urgency,
                        "language": st.session_state.get('language', 'DE')
                    }
                    entries.append(entry)
                    
                    with open(SURVEY_FILE, "w", encoding="utf-8") as f:
                        json.dump(entries, f, ensure_ascii=False, indent=2)
                    
                    # Envoi email
                    success, message = send_feedback_email(
                        name or "Anonym",
                        email,
                        feedback_type,
                        feedback,
                        urgency,
                        st.session_state.get('language', 'DE')
                    )
                    
                    if success:
                        st.success(t('feedback_sent'))
                        st.balloons()
                    else:
                        st.error(f"❌ Fehler: {message}")
                        st.info("📝 Feedback wurde lokal gespeichert.")
    
    with col2:
        st.subheader("📊 " + t('stats'))
        if os.path.exists(SURVEY_FILE):
            with open(SURVEY_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
            
            if entries:
                st.metric(t('feedback_header'), len(entries))
                
                # Dernier feedback
                last = entries[-1]
                st.markdown(f"""
                **{t('name')}:** {last.get('name', 'Anonym')}  
                **{t('urgency')}:** {last.get('urgency', 'Mittel')}  
                **{t('feedback_text')}:** {last.get('feedback', '')[:50]}...
                """)

# ==================== TAB 6: PAPIERKORB ====================
with tab6:
    st.header(t('recycle_bin'))
    
    recycle_bin = load_recycle_bin()
    
    if recycle_bin:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t('deleted_tasks'), len(recycle_bin))
        with col2:
            if st.button("🧹 " + t('recycle_bin') + " " + t('delete'), use_container_width=True):
                with st.popover("⚠️ " + t('delete')):
                    st.warning(t('delete') + "?")
                    if st.button("Ja, " + t('delete')):
                        save_recycle_bin([])
                        st.rerun()
        
        st.markdown("---")
        
        for idx, task in enumerate(recycle_bin):
            # Info de suppression
            deleted_info = ""
            if 'deleted_at' in task:
                try:
                    deleted = datetime.strptime(task['deleted_at'], "%Y-%m-%d %H:%M:%S")
                    days = (datetime.now() - deleted).days
                    if days == 0:
                        deleted_info = f"🔸 {t('today')}"
                    elif days == 1:
                        deleted_info = f"🔸 {t('yesterday')}"
                    else:
                        deleted_info = f"🔸 {t('deleted_at')}: {days} {t('days_ago')}"
                except:
                    deleted_info = f"🔸 {task['deleted_at']}"
            
            st.markdown(f"""
            <div style="background: #2b2b2b10; border-radius: 10px; padding: 15px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <h4>{task.get('title', '')}</h4>
                    <span style="color: #666;">{deleted_info}</span>
                </div>
                <p>📂 {task.get('category', '')} | 🎯 {task.get('priority', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t('restore'), key=f"restore_{task.get('id', idx)}", use_container_width=True):
                    restored = restore_from_recycle_bin(task['id'])
                    if restored:
                        data = load_data()
                        new_id = max([t.get('id', 0) for t in data['tasks']] + [0]) + 1
                        restored['id'] = new_id
                        data['tasks'].append(restored)
                        data['next_id'] = max(data.get('next_id', 1), new_id + 1)
                        save_data(data)
                        st.rerun()
            
            with col2:
                if st.button(t('permanent_delete'), key=f"perm_{task.get('id', idx)}", use_container_width=True):
                    permanently_delete(task['id'])
                    st.rerun()
            
            st.divider()
    
    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 50px;">
            <h1 style="font-size: 4rem;">🗑️</h1>
            <h3>{t('empty_bin')}</h3>
        </div>
        """, unsafe_allow_html=True)