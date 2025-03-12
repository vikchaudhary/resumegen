# This Python app is a backend application. It serves as an API server and does not include a frontend.
# It uses Flask to define REST API endpoints that handle requests and return JSON responses:
#   /save-job
#   /get-jobs
#   /get-job/<job_id>
#   /analyze
#   /generate
# 
# Functionality:
#   Manages data in a SQLite database.
#   Performs keyword extraction and resume enhancement using OpenAI's API.
#   Interacts with clients via JSON over HTTP.
#   The app is designed to be consumed by external clients such as web or mobile frontends.

# Import all libs
from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
from openai import OpenAI
import re
from pathlib import Path
import os
import logging
import re
# for word cloud
from wordcloud import WordCloud
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend (no GUI)
import matplotlib.pyplot as plt
from resume import resume_bp  # import resume.py

app = Flask(__name__)
CORS(app)
app.register_blueprint(resume_bp)  # Register the resume blueprint
app.debug = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['LOGGING_FORMAT'] = '%(asctime)s %(levelname)s: %(message)s'
app.config['LOGGING_LEVEL'] = logging.INFO
logging.basicConfig(format=app.config['LOGGING_FORMAT'], level=app.config['LOGGING_LEVEL'], filename='backend.log')

# Create a logger
logger = logging.getLogger(__name__)

# Global variables
# WARNING! Do not publish this code with your secret OpenAI key!
# openai.api_key = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

# Configure SQLite database
DATABASE_NAME = 'keyguru.db'

def initialize_db():
    # This function connects to the SQLite database and creates the required tables 
    # It ensures that the database is set up before the application runs.
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create the "user" table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    # Create the "org" table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS org (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_name TEXT NOT NULL,
            long_name TEXT
        )
    ''')

    # Create job_status table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            display_order INTEGER NOT NULL UNIQUE
        )
    ''')

    # Create location table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS location (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create the "job" table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            desc TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            org_id INTEGER NOT NULL,
            status_id INTEGER,
            location_id INTEGER,
            min_salary INTEGER,
            max_salary INTEGER,
            fit_rating INTEGER CHECK (fit_rating BETWEEN 1 AND 5),
            match_percentage INTEGER CHECK (match_percentage BETWEEN 0 AND 100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES user (id),
            FOREIGN KEY (org_id) REFERENCES org (id),
            FOREIGN KEY (status_id) REFERENCES job_status (id),
            FOREIGN KEY (location_id) REFERENCES location (id),
            CHECK (max_salary IS NULL OR min_salary IS NULL OR max_salary > min_salary)
        )
    ''')

    # Create the resume table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume (
            resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content BLOB NOT NULL,
            user_id INTEGER NOT NULL,
            created_date DATETIME NOT NULL,
            last_edited DATETIME NOT NULL,
            score INTEGER DEFAULT 0,
            matched_job TEXT,
            match TEXT,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')

    # Populate job_status table with initial values
    # cursor.execute('DELETE FROM job_status')
    # statuses = [
    #     (1, 'Exploring'),
    #     (2, 'Referral Hunt'),
    #     (3, 'Open'),
    #     (4, 'Applied'),
    #     (5, 'Engaged'),
    #     (6, 'Recruiter Screen'),
    #     (7, 'HM Interview'),
    #     (8, 'Panel Interviews'),
    #     (9, 'Declined'),
    #     (10, 'Accepted'),
    #     (11, 'Ghosted'),
    #     (12, 'Rejected'),
    #     (13, 'Unqualified'),
    #     (14, 'Uninterested'),
    #     (15, 'Unavailable'),
    #     (16, 'Late')
    # ]
    # cursor.executemany('INSERT INTO job_status (display_order, name) VALUES (?, ?)', statuses)

    # # Populate location table with initial values
    # cursor.execute('DELETE FROM location')
    # locations = [
    #     ('SF',), ('Menlo Park',), ('Mountain View',), ('Sunnyvale',),
    #     ('San Mateo',), ('Redwood City',), ('Santa Clara',), ('San Jose',),
    #     ('Cupertino',), ('Barcelona',), ('Boise',), ('Los Gatos',),
    #     ('New York',), ('Oakland',), ('Palo Alto',), ('Remote',),
    #     ('Berlin',), ('London',), ('Tel Aviv',), ('Seattle',)
    # ]
    # cursor.executemany('INSERT INTO location (name) VALUES (?)', locations)

    conn.commit()
    conn.close()
    logger.info("--------------------------------------")
    logger.info("initialize_db(): done.")
    logger.info("--------------------------------------")

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Resumegen API! Available endpoints: /save-job, /get-jobs, /get-job/<job_id>, /analyze, /generate"})

# ---------------------------------------------------------
# Save Job endpoint
# ---------------------------------------------------------
# Update save_job endpoint to handle new fields
@app.route('/save-job', methods=['POST'])
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

        # Validate required fields
        if not all([job_title, job_desc, owner_id, org_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Find the owner and org objects
        owner = get_user(owner_id)
        org = get_org(org_id)

        if owner is None or org is None:
            return jsonify({'save_job() error': 'Invalid owner or org ID'})

        # Insert the job with all fields
        insert_job(job_title, job_desc, owner_id, org_id, status_id, 
                  location_id, min_salary, max_salary, fit_rating)

        return jsonify({'save_job() message': 'Job saved successfully'})

    except Exception as e:
        print("save_job: error: ", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Get Jobs endpoint -- Gets a list of all the jobs
# ---------------------------------------------------------
# Update get_jobs endpoint to include new fields
@app.route('/get-jobs/', methods=['GET'])
def get_jobs():
    try:
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
# Get Job endpoint -- Gets the job object from it's 'id'
# ---------------------------------------------------------
@app.route('/get-job/<int:job_id>', methods=['GET'])
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
        print("get_job: error: ", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Get Companies endpoint
# ---------------------------------------------------------
@app.route('/get-companies', methods=['GET'])
def get_companies():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Fetch all companies from the company table
        cursor.execute('SELECT id, short_name FROM org ORDER BY short_name ASC')
        companies = cursor.fetchall()

        conn.close()

        # Convert to list of dictionaries
        company_list = [{'id': company[0], 'name': company[1]} for company in companies]
        # logger.info("company_list:", company_list)

        return jsonify(company_list)

    except Exception as e:
        print("get_companies: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Get Company Name endpoint
# Retrieves the short_name (company name) based on the org_id
# ---------------------------------------------------------
@app.route('/get-company-name/<int:org_id>', methods=['GET'])
def get_company_name(org_id):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Fetch the company name based on the org_id
        cursor.execute('SELECT short_name FROM org WHERE id = ?', (org_id,))
        company = cursor.fetchone()

        conn.close()

        if company:
            return jsonify({'short_name': company[0]})
        else:
            return jsonify({'error': 'Company not found'}), 404

    except Exception as e:
        print("get_company_name: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Update Job's Org endpoint
# ---------------------------------------------------------
@app.route('/update-job-company', methods=['POST'])
def update_job_company():
    try:
        data = request.get_json()
        job_name = data.get('job_name')
        company_name = data.get('company')

        if not job_name or not company_name:
            return jsonify({'error': 'Job name and company name are required'}), 400

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Fetch the company ID based on the company name
        cursor.execute('SELECT id FROM org WHERE short_name = ?', (company_name,))
        company = cursor.fetchone()

        if company is None:
            conn.close()
            return jsonify({'error': 'Company not found'}), 404

        company_id = company[0]

        # Update the job's org_id based on the job title
        cursor.execute('UPDATE job SET org_id = ? WHERE title = ?', (company_id, job_name))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Job company updated successfully'})

    except Exception as e:
        print("update_job_company: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# /add-org endpoint
# ---------------------------------------------------------
@app.route('/add-org', methods=['POST'])
def add_org():
    try:
        data = request.json
        short_name = data.get('short_name')
        long_name = data.get('long_name')
        
        if not short_name:
            return jsonify({'add-org() error': 'Organization short name is required'}), 400

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Insert new organization
        cursor.execute('INSERT INTO org (short_name, long_name) VALUES (?, ?)', 
                      (short_name, long_name))
        conn.commit()
        
        # Get the id of the newly inserted org
        new_org_id = cursor.lastrowid
        
        conn.close()
        
        return jsonify({
            'message': 'Organization added successfully',
            'org': {
                'org_id': new_org_id,
                'short_name': short_name,
                'long_name': long_name
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------
# /generate-wordcloud endpoint
# ---------------------------------------------------------
@app.route('/generate-wordcloud', methods=['POST'])
def generate_wordcloud():
    """Generates a word cloud image from job description and returns it as a Base64 encoded string."""
    try:
        data = request.get_json()
        job_desc = data.get('job_desc')

        if not job_desc:
            return jsonify({'error': 'Job description is required'}), 400

        img_base64 = generate_wordcloud_base64(job_desc)

        if img_base64:
            return jsonify({'image': img_base64})
        else:
            return jsonify({'error': 'Failed to generate word cloud'}), 500

    except Exception as e:
        print("generate_wordcloud: error:", str(e))
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------
# get_user
# ---------------------------------------------------------
def get_user(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# ---------------------------------------------------------
# get_org
# ---------------------------------------------------------
def get_org(org_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM org WHERE id = ?", (org_id,))
    org = cursor.fetchone()
    conn.close()
    return org

# ---------------------------------------------------------
# insert_job
# ---------------------------------------------------------
def insert_job(title, desc, owner_id, org_id):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Check that the org exists
        cursor.execute('SELECT short_name FROM org WHERE id = ?', (org_id,))
        org = cursor.fetchone()
        if org is None:
            conn.close()
            raise ValueError("insert_job(): Company not found")

        # Insert the job into the job table
        cursor.execute("INSERT INTO job (title, desc, owner_id, org_id) VALUES (?, ?, ?, ?)",
                       (title, desc, owner_id, org_id))

        conn.commit()
        conn.close()

    except Exception as e:
        print("insert_job() error:", str(e))
        return {'error': str(e)}

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
# generate_wordcloud_base64
# Generates a word cloud from the given text and returns it as a base64 encoded string.
# ---------------------------------------------------------
def generate_wordcloud_base64(text):
  try:
    # generate the wordcloud
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100).generate(text)

    # Create a BytesIO object to hold the image data. This is an in-memory file-like object 
    # from the io module. We use it to store the image data without writing it to a file on disk.
    img_buffer = BytesIO()

    # Save the wordcloud to the BytesIO object as a PNG. Use plt.savefig() to save the Matplotlib 
    # figure to the BytesIO buffer in PNG format. Crucially, we're saving the figure to the buffer. 
    plt.figure(figsize=(12, 6))  # Create a figure so that we can save it to the buffer
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")  # Hide axes
    plt.savefig(img_buffer, format="png")  # Save the figure to the buffer
    plt.close()  # Close the figure to free memory.

    # Encode the image data to base64. Encodes the raw image bytes into a Base64 string, which 
    # is a text-based representation of the image. The .decode('utf-8') converts the resulting 
    # bytes object to a regular string.
    img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    return img_str

  except Exception as e:
        print(f"Error generating word cloud: {e}")
        return None

# ---------------------------------------------------------
# search_keywords() –– internal function
#   fname: search file with this fully-qualified name...
#   keyword_arr: ...for the list of keywords in this string array
# return an array with these contents:
#   arr: found keyword array
#   arr: the missing keyword array
# identifies which job-related keywords are present in the user's resume and which ones are missing, helping 
# understand how well a resume matches the job requirements.
# ---------------------------------------------------------
def search_keywords(fname, keyword_arr):
    file = open(fname, "r")
    if file is not None:
        the_file_txt = file.read()    # contents of the file
        the_file = the_file_txt.lower()
        missing_keywords_arr = []
        found_keywords_arr = []

        count=0
        for index, keyword in enumerate(keyword_arr, start=1):
            if keyword:
                if keyword.lower() in the_file:
                    # keyword found
                    found_keywords_arr.append(keyword)
                    print(f'{index}. {keyword}')
                    count=count+1
                else:
                    # keyword not found
                    missing_keywords_arr.append(keyword)
                    print("[x] " + f'{index}. {keyword}')
                    count=count+1
    
    # return an array containing the found keyword array, the missing keyword array, and the file contents
    return (found_keywords_arr, missing_keywords_arr)

#----------------------------------------------------------------
# Analyze end-point
# Searches the job description for keywords
# Returns a JSON object with these keys
#   found_keywords_arr: array of all keywords that were found
#   missing_keywords_arr: array of keywords that were not found
#----------------------------------------------------------------
@app.route('/analyze', methods=['POST'])
def analyze_text():
    print("Analyzing job listing...")
    data = request.get_json()
    text = data.get('job_desc')
    resume_fname = os.path.expanduser('~') + "/Downloads/" + data.get('resume_fname')
    print("resume_fname= ", resume_fname)
    
    response = client.completions.create(
        model='gpt-3.5-turbo-instruct',
        # prompt=f'Your task is to do keyword extraction from unstructured text. Generate a list of two-word keywords from the text. Remove all proper nouns from the list. Sort keywords alphabetically. \n\nText:\n{text}\n',
        prompt=f'List the important two-word keywords in the job description, below.  Remove all keywords that start or end with pronouns. Sort the list alphabetically. \n\nText:\n{text}\n',
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # clean up the keywords so unnecessary information is removed
    keywords_str = response.choices[0].text.strip()
    keywords_str = keywords_str.replace("/", " ") # replace "/" separator with space
    
    # strip out the phrase "Two-word keywords:" and all variations at the beginning of the output
    substring = "Two-Word Keywords:\n"
    str_list = keywords_str.split(substring)
    keywords_str = "".join(str_list)
    # do this again with another variation of the phrase
    substring = "Two Word Keywords:\n"
    str_list = keywords_str.split(substring)
    keywords_str = "".join(str_list)
    # do this again with another variation of the phrase
    substring = "Two-word keywords:\n"
    str_list = keywords_str.split(substring)
    keywords_str = "".join(str_list)
    # do this again with another variation of the phrase
    substring = "Two word keywords:\n"
    str_list = keywords_str.split(substring)
    keywords_str = "".join(str_list)
    # do this again with another variation of the phrase
    substring = "Two-word keywords:\n"
    str_list = keywords_str.split(substring)
    keywords_str = "".join(str_list)
    # do this again with another variation of the phrase
    substring = "two-word keywords:\n"
    str_list = keywords_str.split(substring)
    keywords_str = "".join(str_list)
    # do this again with another variation of the phrase
    substring = "Keywords:\n"
    str_list = keywords_str.split(substring)
    keywords_str = "".join(str_list)
    # do this again with another variation of the phrase
    substring = "Answer:\n"
    str_list = keywords_str.split(substring)
    keywords_str = "".join(str_list)

    # remove all commas and newlines from the keywords
    keyword_arr=re.split(',|\n', keywords_str)

    # print(f"analyze_txt() keywords_str: {keywords_str}") 
    keyword_arr = [strip_leading_chars(item) for item in keyword_arr]

    # Remove all one-word keywords
    new_keyword_arr = [item.strip() for item in keyword_arr if len(item.split()) > 1]
    # print(f"analyze_txt() new_keyword_arr: {new_keyword_arr}") # print the keywords

    # search resume for keywords
    return_arr = search_keywords(resume_fname, new_keyword_arr)
    
    return jsonify({ 'found_keywords_arr': return_arr[0], 
                     'missing_keywords_arr': return_arr[1]
                    })

#----------------------------------------------------------------
# strip_leading_chars() removes all leading spaces, dashes, asterisks
#----------------------------------------------------------------
def strip_leading_chars(str):
    # print(f"strip_leading_chars(): {str}")
    while str and str[0] in " -*":
        str = str[1:]  # Remove leading characters if they are in the set
    return str

#----------------------------------------------------------------
# Generate() endpoint
# Calls the OpenAI API with the provided text from arg 'resume_fname' to add missing keywords in 'missing_keywords_arr'
#----------------------------------------------------------------
@app.route('/generate', methods=['POST'])
def generate_resume():
    data = request.get_json()
    resume_fname = os.path.expanduser('~') + "/Downloads/" + data.get('resume_fname')
    print("Generating new resume from: ", resume_fname)
    missing_keywords_arr = data.get('missing_keywords_arr')

    # get the contents of 'resume_fname'
    resume_file = open(resume_fname, "r")
    if resume_file is not None:
        # read the contents of the resume
        resume_contents_txt = resume_file.read()    

        # Now generate a new resume to add the missing keywords
        missing_keywords_str = ",".join(missing_keywords_arr)
        print("missing keywords: ", missing_keywords_str)

        response = client.completions.create(
            model='gpt-3.5-turbo-instruct',
            prompt=f'Your task is to rewrite the Resume by inserting each of the Keywords into the Resume. Return the edited Resume. \n\nKeywords:\n{missing_keywords_str} \n\nResume:\n{resume_contents_txt}\n',
            temperature=1,
            max_tokens=2100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        print("finish_reason: ", response.choices[0].finish_reason)
        print("edited_txt:\n", response.choices[0].text)
        print("Done!")
    
        return jsonify({ 'edited_txt': response.choices[0].text })


# ---------------------------------------------------------
# Get Job Statuses endpoint
# ---------------------------------------------------------
@app.route('/get-job-statuses', methods=['GET'])
def get_job_statuses():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('SELECT id, name, display_order FROM job_status ORDER BY display_order ASC')
        statuses = cursor.fetchall()
        conn.close()

        status_list = [{'id': status[0], 'name': status[1], 'display_order': status[2]} for status in statuses]
        return jsonify(status_list)

    except Exception as e:
        print("get_job_statuses: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Get Locations endpoint
# ---------------------------------------------------------
@app.route('/get-locations', methods=['GET'])
def get_locations():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('SELECT id, name FROM location ORDER BY name ASC')
        locations = cursor.fetchall()
        conn.close()

        location_list = [{'id': loc[0], 'name': loc[1]} for loc in locations]
        return jsonify(location_list)

    except Exception as e:
        print("get_locations: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Update Job Status endpoint
# ---------------------------------------------------------
@app.route('/update-job-status', methods=['PUT'])
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
        print("update_job_status: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Update Job Location endpoint
# ---------------------------------------------------------
@app.route('/update-job-location', methods=['PUT'])
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
        print("update_job_location: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Update Job Fit Rating endpoint
# ---------------------------------------------------------
@app.route('/update-job-fit', methods=['PUT'])
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
        print("update_job_fit: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ... existing code ...

# ---------------------------------------------------------
# Update Job Salary endpoint
# ---------------------------------------------------------
@app.route('/update-job-salary', methods=['PUT'])
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
        print("update_job_salary: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Update Job Match Percentage endpoint
# ---------------------------------------------------------
@app.route('/update-job-match', methods=['PUT'])
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
        print("update_job_match: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Search and Filter Jobs endpoint
# ---------------------------------------------------------
@app.route('/search-jobs', methods=['GET'])
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
# Job Statistics endpoint
# ---------------------------------------------------------
@app.route('/job-statistics', methods=['GET'])
def get_job_statistics():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Status distribution
        cursor.execute('''
            SELECT s.name, COUNT(j.id) as count
            FROM job_status s
            LEFT JOIN job j ON s.id = j.status_id
            GROUP BY s.id, s.name
            ORDER BY s.display_order
        ''')
        status_stats = [{'status': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # Location distribution
        cursor.execute('''
            SELECT l.name, COUNT(j.id) as count
            FROM location l
            LEFT JOIN job j ON l.id = j.location_id
            GROUP BY l.id, l.name
            ORDER BY count DESC
        ''')
        location_stats = [{'location': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # Salary statistics
        cursor.execute('''
            SELECT 
                AVG(min_salary) as avg_min_salary,
                AVG(max_salary) as avg_max_salary,
                MIN(min_salary) as lowest_salary,
                MAX(max_salary) as highest_salary
            FROM job
            WHERE min_salary IS NOT NULL OR max_salary IS NOT NULL
        ''')
        salary_stats = cursor.fetchone()

        # Application timeline
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM job
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 30
        ''')
        timeline_stats = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'status_distribution': status_stats,
            'location_distribution': location_stats,
            'salary_statistics': {
                'average_min_salary': salary_stats[0],
                'average_max_salary': salary_stats[1],
                'lowest_salary': salary_stats[2],
                'highest_salary': salary_stats[3]
            },
            'application_timeline': timeline_stats
        })

    except Exception as e:
        print("get_job_statistics: error:", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    # Create the database tables
    initialize_db()
    
    app.run()
