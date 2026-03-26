import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "financial_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Eventos do calendário econômico
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS economic_events (
            id TEXT PRIMARY KEY,
            time TEXT,
            currency TEXT,
            importance INTEGER,
            event TEXT,
            actual TEXT,
            forecast TEXT,
            previous TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Gerenciador de links
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitored_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            description TEXT,
            last_scraped DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def save_events(events):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for event in events:
        # Generate a unique ID for the event based on time + currency + event name
        event_id = f"{event['time']}_{event['currency']}_{event['event']}".replace(" ", "_")
        cursor.execute('''
            INSERT OR REPLACE INTO economic_events 
            (id, time, currency, importance, event, actual, forecast, previous, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_id, 
            event.get('time', ''), 
            event.get('currency', ''), 
            event.get('importance', 0), 
            event.get('event', ''), 
            event.get('actual', ''), 
            event.get('forecast', ''), 
            event.get('previous', ''), 
            datetime.now()
        ))
    conn.commit()
    conn.close()

def get_today_events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM economic_events ORDER BY time ASC')
    rows = cursor.fetchall()
    
    # Convert rows to list of dicts
    columns = [description[0] for description in cursor.description]
    events = []
    for row in rows:
        events.append(dict(zip(columns, row)))
        
    conn.close()
    return events
