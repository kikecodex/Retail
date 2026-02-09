"""
Database Module for GEOCENTER LAB
SQLite-based storage for test results and historical data

Tables:
- projects: Project information
- calicatas: Borehole/pit data
- tests: Individual test results
"""
import sqlite3
import json
from datetime import datetime
import os

# Use /tmp on Vercel (read-only filesystem), local path otherwise
if os.environ.get('VERCEL'):
    DB_PATH = '/tmp/geocenter.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'geocenter.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client TEXT,
            location TEXT,
            date_created TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    ''')
    
    # Calicatas (boreholes/pits) table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calicatas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            name TEXT NOT NULL,
            depth_m REAL,
            date_sampled TEXT,
            location_x REAL,
            location_y REAL,
            notes TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')
    
    # Tests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calicata_id INTEGER,
            test_type TEXT NOT NULL,
            date_performed TEXT DEFAULT CURRENT_TIMESTAMP,
            results_json TEXT,
            sucs_classification TEXT,
            validation_status TEXT,
            anomalies_json TEXT,
            notes TEXT,
            FOREIGN KEY (calicata_id) REFERENCES calicatas(id)
        )
    ''')
    
    # Statistics cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sucs_type TEXT NOT NULL,
            param_name TEXT NOT NULL,
            count INTEGER DEFAULT 0,
            mean_value REAL,
            min_value REAL,
            max_value REAL,
            std_dev REAL,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sucs_type, param_name)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_project(name, client=None, location=None, notes=None):
    """Save a new project"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO projects (name, client, location, notes)
        VALUES (?, ?, ?, ?)
    ''', (name, client, location, notes))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def save_calicata(project_id, name, depth_m=None, date_sampled=None, notes=None):
    """Save a new calicata/borehole"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO calicatas (project_id, name, depth_m, date_sampled, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (project_id, name, depth_m, date_sampled, notes))
    calicata_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return calicata_id

def save_test(calicata_id, test_type, results, sucs=None, validation=None, anomalies=None, notes=None):
    """Save test results"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tests (calicata_id, test_type, results_json, sucs_classification, 
                          validation_status, anomalies_json, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (calicata_id, test_type, json.dumps(results), sucs, 
          validation, json.dumps(anomalies) if anomalies else None, notes))
    test_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return test_id

def get_project_history(project_id):
    """Get all calicatas and tests for a project"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.*, t.test_type, t.results_json, t.sucs_classification, t.date_performed
        FROM calicatas c
        LEFT JOIN tests t ON c.id = t.calicata_id
        WHERE c.project_id = ?
        ORDER BY c.id, t.date_performed
    ''', (project_id,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_statistics_by_sucs(sucs_type):
    """Get statistics for a specific SUCS type"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT param_name, count, mean_value, min_value, max_value, std_dev
        FROM statistics
        WHERE sucs_type = ?
    ''', (sucs_type,))
    
    rows = cursor.fetchall()
    conn.close()
    return {row['param_name']: dict(row) for row in rows}

def update_statistics(sucs_type, param_name, value):
    """Update running statistics for a parameter"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get current stats
    cursor.execute('''
        SELECT count, mean_value, min_value, max_value
        FROM statistics
        WHERE sucs_type = ? AND param_name = ?
    ''', (sucs_type, param_name))
    
    row = cursor.fetchone()
    
    if row:
        # Update existing
        n = row['count'] + 1
        old_mean = row['mean_value'] or 0
        new_mean = old_mean + (value - old_mean) / n
        new_min = min(row['min_value'] or value, value)
        new_max = max(row['max_value'] or value, value)
        
        cursor.execute('''
            UPDATE statistics
            SET count = ?, mean_value = ?, min_value = ?, max_value = ?, last_updated = ?
            WHERE sucs_type = ? AND param_name = ?
        ''', (n, new_mean, new_min, new_max, datetime.now().isoformat(), sucs_type, param_name))
    else:
        # Insert new
        cursor.execute('''
            INSERT INTO statistics (sucs_type, param_name, count, mean_value, min_value, max_value)
            VALUES (?, ?, 1, ?, ?, ?)
        ''', (sucs_type, param_name, value, value, value))
    
    conn.commit()
    conn.close()

def get_all_projects():
    """Get list of all projects"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY date_created DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_recent_tests(limit=20):
    """Get most recent test results"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, c.name as calicata_name, p.name as project_name
        FROM tests t
        JOIN calicatas c ON t.calicata_id = c.id
        JOIN projects p ON c.project_id = p.id
        ORDER BY t.date_performed DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Initialize database on import
init_db()
