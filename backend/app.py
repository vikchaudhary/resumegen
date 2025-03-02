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
# for word cloud
from wordcloud import WordCloud
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend (no GUI)
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)
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
            name TEXT NOT NULL
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
            FOREIGN KEY (owner_id) REFERENCES user (id),
            FOREIGN KEY (org_id) REFERENCES org (id)
        )
    ''')

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
@app.route('/save-job', methods=['POST'])
def save_job():
    try:
        data = request.get_json()
        title = data.get('title')
        desc = data.get('desc')
        owner_id = data.get('owner_id')
        org_id = data.get('org_id')

        print("save-job: ", title, " | ", desc[0:360], " | ", owner_id, " | ", org_id)  # debug

        # Find the owner and org objects based on their IDs
        owner = get_user(owner_id)
        org = get_org(org_id)

        if owner is None or org is None:
            return jsonify({'error': 'Invalid owner or org ID'})

        # Insert the job into the database
        insert_job(title, desc, owner_id, org_id)

        return jsonify({'message': 'Job saved successfully'})

    except Exception as e:
        print("save_job: error: ", str(e))
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Get Jobs endpoint -- Gets a list of all the jobs
# ---------------------------------------------------------
@app.route('/get-jobs/', methods=['GET'])
def get_jobs():
    try:
        # Establish a connection to the SQLite database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Execute the SQL query to fetch the jobs from the 'job' table
        cursor.execute('SELECT job.id, job.title, org.short_name FROM job INNER JOIN org ON job.org_id=org.id')
        jobs = cursor.fetchall()

        # Convert the fetched jobs to a list of dictionaries
        jobs_list = [{'id': job[0], 'title': job[1], 'org': job[2]} for job in jobs]

        # Close the database connection
        conn.close()
        
        # Return the list of jobs as a JSON response
        return jsonify(jobs_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# Get Job endpoint -- Gets the job object from it's 'id'
# ---------------------------------------------------------
@app.route('/get-job/<int:job_id>', methods=['GET'])
def get_job(job_id):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Execute the query to retrieve the job with the given job_id
        cursor.execute('SELECT job.id, job.title, job.desc, job.owner_id, job.org_id, org.short_name FROM job INNER JOIN org ON job.org_id=org.id WHERE job.id=?', (job_id,))
        job = cursor.fetchone()

        if job:
            # Create a dictionary with job data
            job_data = {
                'id': job[0],
                'title': job[1],
                'desc': job[2],
                'owner_id': job[3],
                'org_id': job[4],
                'org_name': job[5]
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
# Update Job's Company endpoint
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
def insert_job(title, desc, owner_id, company_name):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Fetch the company ID based on the company name
        cursor.execute('SELECT id FROM org WHERE short_name = ?', (company_name,))
        company = cursor.fetchone()

        if company is None:
            conn.close()
            raise ValueError("Company not found")

        org_id = company[0]  # Extract the organization ID

        # Insert the job into the job table
        cursor.execute("INSERT INTO job (title, desc, owner_id, org_id) VALUES (?, ?, ?, ?)",
                       (title, desc, owner_id, org_id))

        conn.commit()
        conn.close()

    except Exception as e:
        print("insert_job: error:", str(e))
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
#   text: the file contents
# ---------------------------------------------------------
def search_keywords(fname, keyword_arr):
    file = open(fname, "r")
    if file is not None:
        the_file_txt = file.read()    # contents of the file
        the_file = the_file_txt.lower()

        chatgpt_keyword_arr = [
            'API',
            'platform',
            'communication skills',
            'customer-centric mindset',
            'customer support',
            'data-driven processes',
            'deep technical',
            'deployment systems',
            'engineering',
            'execution focused',
            'global platform',
            'identity management',
            'product content',
            'product designers',
            'product development',
            'product management',
            'product roadmap',
            'strategic',
            'implementation',
            'customer support'
        ]
        missing_keywords_arr = []
        found_keywords_arr = []

        # Combine the lists and remove duplicates.
        # Append to the first list those elements of the second list that aren't in the first
        combined_arr = keyword_arr + list(set(chatgpt_keyword_arr) - set(keyword_arr))

        count=0
        for index, keyword in enumerate(combined_arr, start=1):
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
    return (found_keywords_arr, missing_keywords_arr, the_file_txt)


# Analyze end-point
# Searches the job description for keywords
# Returns a JSON object with these keys
#   found_keywords_arr: array of all keywords that were found
#   missing_keywords_arr: array of keywords that were not found

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
    # replace "/" separator with space
    keywords_str = keywords_str.replace("/", " ")
    # strip out the phrase at the beginning of the output
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

    # Filter out one-word keywords
    new_keyword_arr = [kw.strip() for kw in keyword_arr if len(kw.split()) > 1]
    print(keyword_arr) #debug

    # search resume for keywords
    return_arr = search_keywords(resume_fname, new_keyword_arr)
    
    return jsonify({ 'found_keywords_arr': return_arr[0], 
                     'missing_keywords_arr': return_arr[1]
                    })

#
# Generate() endpoint
# Calls the OpenAI API with the provided text from arg 'resume_fname' to add missing keywords in 'missing_keywords_arr'
#
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


if __name__ == "__main__":
    # Create the database tables
    initialize_db()
    app.run()
