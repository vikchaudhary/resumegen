from flask import Blueprint, request, jsonify
import sqlite3
import datetime
from werkzeug.utils import secure_filename
import base64

# Create Blueprint for resume routes
resume_bp = Blueprint('resume', __name__)

DATABASE_NAME = 'keyguru.db'

@resume_bp.route('/resume', methods=['POST'])
def create_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        title = request.form.get('title')
        user_id = request.form.get('user_id')
        
        if not file or not title or not user_id:
            return jsonify({'error': 'Missing required fields'}), 400
            
        content = file.read()
        now = datetime.datetime.now()
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO resume (title, content, user_id, created_date, last_edited)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, user_id, now, now))
        
        conn.commit()
        resume_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'message': 'Resume created successfully', 'resume_id': resume_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/resumes', methods=['GET'])
def get_resumes():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.resume_id, r.title, r.created_date, r.last_edited,
                   j.id as job_id, j.title as job_title, m.score, m.match_details
            FROM resume r
            LEFT JOIN resume_job_match m ON r.resume_id = m.resume_id
            LEFT JOIN job j ON m.job_id = j.id
            ORDER BY r.last_edited DESC
        ''')
        
        resumes = {}
        for row in cursor.fetchall():
            resume_id = row[0]
            if resume_id not in resumes:
                resumes[resume_id] = {
                    'id': resume_id,
                    'title': row[1],
                    'created_date': row[2],
                    'last_edited': row[3],
                    'matches': []
                }
            if row[4]:  # if there's a job match
                resumes[resume_id]['matches'].append({
                    'job_id': row[4],
                    'job_title': row[5],
                    'score': row[6],
                    'match_details': row[7]
                })
        
        conn.close()
        return jsonify(list(resumes.values()))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/resume/<int:resume_id>/match/<int:job_id>', methods=['POST'])
def match_resume_to_job(resume_id, job_id):
    try:
        data = request.get_json()
        score = data.get('score', 0)
        match_details = data.get('match_details', '')
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO resume_job_match 
            (resume_id, job_id, score, match_details)
            VALUES (?, ?, ?, ?)
        ''', (resume_id, job_id, score, match_details))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Resume matched with job successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/resume/<int:resume_id>', methods=['GET'])
def get_resume(resume_id):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT resume_id, title, content, user_id, created_date, last_edited FROM resume WHERE resume_id = ?', (resume_id,))
        resume = cursor.fetchone()
        conn.close()
        
        if resume:
            return jsonify({
                'id': resume[0],
                'title': resume[1],
                'content': base64.b64encode(resume[2]).decode('utf-8'),
                'user_id': resume[3],
                'created_date': resume[4],
                'last_edited': resume[5]
            })
        return jsonify({'error': 'Resume not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/resume/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM resume WHERE resume_id = ?', (resume_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Resume deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/resume/<int:resume_id>/copy', methods=['POST'])
def copy_resume(resume_id):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Get the original resume
        cursor.execute('SELECT * FROM resume WHERE resume_id = ?', (resume_id,))
        original = cursor.fetchone()
        
        if not original:
            return jsonify({'error': 'Resume not found'}), 404
            
        now = datetime.datetime.now()
        
        # Insert copy with "Copy of" prefix
        cursor.execute('''
            INSERT INTO resume (title, content, user_id, created_date, last_edited)
            VALUES (?, ?, ?, ?, ?)
        ''', (f"Copy of {original[1]}", original[2], original[3], now, now))
        
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'message': 'Resume copied successfully', 'resume_id': new_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500