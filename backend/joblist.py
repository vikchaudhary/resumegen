from flask import Blueprint, request, jsonify
import sqlite3
from pathlib import Path
import os
import logging
import sys

# Create a Blueprint for jobs
joblist_bp = Blueprint('joblist', __name__)

# Database configuration
DATABASE_NAME = 'keyguru.db'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add a test log message
logger.info("joblist.py: logging started")

# ---------------------------------------------------------
# Get Jobs endpoint -- Gets a list of all the jobs
# ---------------------------------------------------------
@joblist_bp.route('/get-jobs/', methods=['GET'])
def get_jobs():
    try:
        logger.info("get_jobs() - Fetching organizations...")
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT j.id, j.title, j.org_id, o.short_name, 
                   j.status_id, s.name as status_name,
                   j.location_id, l.name as location_name,
                   j.min_salary, j.max_salary, j.fit_rating,
                   j.created_at, j.updated_at
            FROM job j
            INNER JOIN org o ON j.org_id = o.id
            LEFT JOIN job_status s ON j.status_id = s.id
            LEFT JOIN location l ON j.location_id = l.id
            ORDER BY j.title ASC
        ''')
        jobs = cursor.fetchall()

        jobs_list = [{
            'job_id': job[0],
            'job_title': job[1],
            'org_id': job[2],
            'org_name': job[3],
            'status_id': job[4],
            'status_name': job[5],
            'location_id': job[6],
            'location_name': job[7],
            'min_salary': job[8],
            'max_salary': job[9],
            'fit_rating': job[10],
            'created_at': job[11],
            'updated_at': job[12]
        } for job in jobs]

        conn.close()
        return jsonify(jobs_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Get Job endpoint -- Gets the job object from it's 'id'
# ---------------------------------------------------------
@joblist_bp.route('/get-job/<int:job_id>', methods=['GET'])
def get_job(job_id):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT j.id, j.title, j.desc, j.owner_id, j.org_id, 
                   o.short_name, j.status_id, s.name as status_name,
                   j.location_id, l.name as location_name,
                   j.min_salary, j.max_salary, j.fit_rating,
                   j.match_percentage, j.created_at, j.updated_at
            FROM job j
            INNER JOIN org o ON j.org_id = o.id
            LEFT JOIN job_status s ON j.status_id = s.id
            LEFT JOIN location l ON j.location_id = l.id
            WHERE j.id = ?
        ''', (job_id,))
        job = cursor.fetchone()

        if job:
            job_data = {
                'job_id': job[0],
                'job_title': job[1],
                'job_desc': job[2],
                'job_owner_id': job[3],
                'org_id': job[4],
                'org_name': job[5],
                'status_id': job[6],
                'status_name': job[7],
                'location_id': job[8],
                'location_name': job[9],
                'min_salary': job[10],
                'max_salary': job[11],
                'fit_rating': job[12],
                'match_percentage': job[13],
                'created_at': job[14],
                'updated_at': job[15]
            }
            return jsonify(job_data)
        else:
            return jsonify({'error': 'Job not found'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Save Job endpoint
# ---------------------------------------------------------
@joblist_bp.route('/save-job', methods=['POST'])
def save_job():
    try:
        data = request.get_json()
        job_title = data.get('job_title')
        job_desc = data.get('job_desc')
        owner_id = data.get('owner_id')
        org_id = data.get('org_id')
        status_id = data.get('status_id')
        location_id = data.get('location_id')
        min_salary = data.get('min_salary')
        max_salary = data.get('max_salary')
        fit_rating = data.get('fit_rating')

        if not all([job_title, job_desc, owner_id, org_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO job (
                title, desc, owner_id, org_id, status_id, 
                location_id, min_salary, max_salary, fit_rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (job_title, job_desc, owner_id, org_id, status_id, 
              location_id, min_salary, max_salary, fit_rating))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Job saved successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def insert_job(title, desc, owner_id, org_id, status_id=None, 
               location_id=None, min_salary=None, max_salary=None, 
               fit_rating=None):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO job (
                title, desc, owner_id, org_id, status_id, 
                location_id, min_salary, max_salary, fit_rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, desc, owner_id, org_id, status_id, 
              location_id, min_salary, max_salary, fit_rating))

        conn.commit()
        conn.close()

    except Exception as e:
        print("insert_job() error:", str(e))
        return {'error': str(e)}

# ---------------------------------------------------------
# Update Job Status endpoint
# ---------------------------------------------------------
@joblist_bp.route('/update-job-status', methods=['PUT'])
def update_job_status():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        status_id = data.get('status_id')

        if not job_id or not status_id:
            return jsonify({'error': 'Job ID and status ID are required'}), 400

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('UPDATE job SET status_id = ? WHERE id = ?', (status_id, job_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Job status updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Update Job Location endpoint
# ---------------------------------------------------------
@joblist_bp.route('/update-job-location', methods=['PUT'])
def update_job_location():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        location_id = data.get('location_id')

        if not job_id or not location_id:
            return jsonify({'error': 'Job ID and location ID are required'}), 400

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('UPDATE job SET location_id = ? WHERE id = ?', (location_id, job_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Job location updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Update Job Fit Rating endpoint
# ---------------------------------------------------------
@joblist_bp.route('/update-job-fit', methods=['PUT'])
def update_job_fit():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        fit_rating = data.get('fit_rating')

        if not job_id or not fit_rating or not (1 <= fit_rating <= 5):
            return jsonify({'error': 'Job ID and valid fit rating (1-5) are required'}), 400

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('UPDATE job SET fit_rating = ? WHERE id = ?', (fit_rating, job_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Job fit rating updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Update Job Salary endpoint
# ---------------------------------------------------------
@joblist_bp.route('/update-job-salary', methods=['PUT'])
def update_job_salary():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        min_salary = data.get('min_salary')
        max_salary = data.get('max_salary')

        if not job_id:
            return jsonify({'error': 'Job ID is required'}), 400
        if max_salary and min_salary and max_salary <= min_salary:
            return jsonify({'error': 'Maximum salary must be greater than minimum salary'}), 400

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('UPDATE job SET min_salary = ?, max_salary = ? WHERE id = ?', 
                      (min_salary, max_salary, job_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Job salary updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Update Job Match Percentage endpoint
# ---------------------------------------------------------
@joblist_bp.route('/update-job-match', methods=['PUT'])
def update_job_match():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        match_percentage = data.get('match_percentage')

        if not job_id or not isinstance(match_percentage, int) or not (0 <= match_percentage <= 100):
            return jsonify({'error': 'Job ID and valid match percentage (0-100) are required'}), 400

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('UPDATE job SET match_percentage = ? WHERE id = ?', 
                      (match_percentage, job_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Job match percentage updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Search and Filter Jobs endpoint
# ---------------------------------------------------------
@joblist_bp.route('/search-jobs', methods=['GET'])
def search_jobs():
    try:
        status_id = request.args.get('status_id')
        location_id = request.args.get('location_id')
        min_salary = request.args.get('min_salary')
        max_salary = request.args.get('max_salary')
        keyword = request.args.get('keyword')

        query = '''
            SELECT j.id, j.title, j.org_id, o.short_name, 
                   j.status_id, s.name as status_name,
                   j.location_id, l.name as location_name,
                   j.min_salary, j.max_salary, j.fit_rating,
                   j.match_percentage, j.created_at, j.updated_at
            FROM job j
            INNER JOIN org o ON j.org_id = o.id
            LEFT JOIN job_status s ON j.status_id = s.id
            LEFT JOIN location l ON j.location_id = l.id
            WHERE 1=1
        '''
        params = []

        if status_id:
            query += ' AND j.status_id = ?'
            params.append(status_id)
        if location_id:
            query += ' AND j.location_id = ?'
            params.append(location_id)
        if min_salary:
            query += ' AND j.min_salary >= ?'
            params.append(min_salary)
        if max_salary:
            query += ' AND j.max_salary <= ?'
            params.append(max_salary)
        if keyword:
            query += ' AND (j.title LIKE ? OR j.desc LIKE ?)'
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param])

        query += ' ORDER BY j.updated_at DESC'

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        jobs = cursor.fetchall()

        jobs_list = [{
            'job_id': job[0],
            'job_title': job[1],
            'org_id': job[2],
            'org_name': job[3],
            'status_id': job[4],
            'status_name': job[5],
            'location_id': job[6],
            'location_name': job[7],
            'min_salary': job[8],
            'max_salary': job[9],
            'fit_rating': job[10],
            'match_percentage': job[11],
            'created_at': job[12],
            'updated_at': job[13]
        } for job in jobs]

        conn.close()
        return jsonify(jobs_list)

    except Exception as e:
        print("search_jobs: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# get_job_by_id
# ---------------------------------------------------------
def get_job_by_id(job_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    return job

# ---------------------------------------------------------
# get-job-details -- When a Job is edited, we lookup all the data related to that jon
# ---------------------------------------------------------
@joblist_bp.route('/get-job-details/<int:job_id>', methods=['GET'])
def get_job_details(job_id):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        logger.info(f"get_job_details() - job_id: {job_id}")

        # Get the specific job details
        cursor.execute('''
            SELECT j.*, o.short_name as org_name, s.name as status_name, l.name as location_name
            FROM job j
            LEFT JOIN org o ON j.org_id = o.id
            LEFT JOIN job_status s ON j.status_id = s.id
            LEFT JOIN location l ON j.location_id = l.id
            WHERE j.id = ?
        ''', (job_id,))
        job = cursor.fetchone()
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        return jsonify({'job': job})

    except Exception as e:
        logger.error(f"Error in get_job_details: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@joblist_bp.route('/reference-data', methods=['GET'])
def get_reference_data():
    try:
        logger.info("get_reference_data() called")

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Get organizations
        logger.info("get_reference_data() - Fetching organizations...")
        cursor.execute("SELECT id as org_id, short_name as org_name FROM org")
        organizations = [{'org_id': row[0], 'org_name': row[1]} for row in cursor.fetchall()]

        # Get locations
        logger.info("get_reference_data() - Fetching locations...")
        cursor.execute("SELECT id as location_id, name as location_name FROM location")
        locations = [{'location_id': row[0], 'location_name': row[1]} for row in cursor.fetchall()]

        # Get statuses
        logger.info("get_reference_data() - Fetching job statuses...")
        cursor.execute("SELECT id as status_id, name as status_name FROM job_status")
        statuses = [{'status_id': row[0], 'status_name': row[1]} for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'organizations': organizations,
            'locations': locations,
            'statuses': statuses
        })

    except Exception as e:
        logger.error(f"Error in get_reference_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

