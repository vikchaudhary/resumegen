# Import all libs
from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import openai
import re
from pathlib import Path
import os
import logging

app = Flask(__name__)
CORS(app)
app.debug = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['LOGGING_FORMAT'] = '%(asctime)s %(levelname)s: %(message)s'
app.config['LOGGING_LEVEL'] = logging.INFO
logging.basicConfig(format=app.config['LOGGING_FORMAT'], level=app.config['LOGGING_LEVEL'])

# Global variables
# WARNING! Do not publish this code with your secret OpenAI key!
openai.api_key = ''

# Configure SQLite database
db_file = 'keyguru.db'

# Save Job endpoint
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

# Get Jobs endpoint -- Gets a list of all the jobs
@app.route('/get-jobs/', methods=['GET'])
def get_jobs():
    try:
        # Establish a connection to the SQLite database
        conn = sqlite3.connect('keyguru.db')
        cursor = conn.cursor()

        # Execute the SQL query to fetch the jobs from the 'job' table
        cursor.execute('SELECT id, title FROM job')
        jobs = cursor.fetchall()

        # Convert the fetched jobs to a list of dictionaries
        jobs_list = [{'id': job[0], 'title': job[1]} for job in jobs]

        # Close the database connection
        conn.close()

        print("jobs_list: ", jobs_list)  #debug
        
        # Return the list of jobs as a JSON response
        return jsonify(jobs_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Job endpoint -- Gets the job object from it's 'id'
@app.route('/get-job/<int:job_id>', methods=['GET'])
def get_job(job_id):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('keyguru.db')
        cursor = conn.cursor()

        # Execute the query to retrieve the job with the given job_id
        cursor.execute('SELECT * FROM job WHERE id=?', (job_id,))
        job = cursor.fetchone()

        if job:
            # Create a dictionary with job data
            job_data = {
                'id': job[0],
                'title': job[1],
                'desc': job[2],
                'owner_id': job[3],
                'org_id': job[4]
            }
            return jsonify(job_data)
        else:
            return jsonify({'error': 'Job not found'})

    except Exception as e:
        print("get_job: error: ", str(e))
        return jsonify({'error': str(e)}), 500



def get_user(user_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_org(org_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM org WHERE id = ?", (org_id,))
    org = cursor.fetchone()
    conn.close()
    return org


def insert_job(title, desc, owner_id, org_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO job (title, desc, owner_id, org_id) VALUES (?, ?, ?, ?)",
                   (title, desc, owner_id, org_id))
    conn.commit()
    conn.close()


def get_job_by_id(job_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    return job

# search_keywords() –– internal function
#   fname: search file with this fully-qualified name...
#   keyword_arr: ...for the list of keywords in this string array
# return an array with these contents:
#   arr: found keyword array
#   arr: the missing keyword array
#   text: the file contents
#
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
    
    response = openai.Completion.create(
        engine='text-davinci-003',
        # prompt=f'Your task is to do keyword extraction from unstructured text. Generate a list of two-word keywords from the text. Remove all proper nouns from the list. Sort keywords alphabetically. \n\nText:\n{text}\n',
        prompt=f'List the important two-word keywords in the job description, below.  Remove all keywords that start or end with pronouns. Sort the list alphabetically. \n\nText:\n{text}\n',
        temperature=1,
        max_tokens=256,
        top_p=1,
        best_of=3,
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
    print(keyword_arr) #debug

    # search resume for keywords
    return_arr = search_keywords(resume_fname, keyword_arr)
    
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

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f'Your task is to rewrite the Resume by inserting each of the Keywords into the Resume. Return the edited Resume. \n\nKeywords:\n{missing_keywords_str} \n\nResume:\n{resume_contents_txt}\n',
            temperature=1,
            max_tokens=2100,
            top_p=1,
            best_of=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        print("finish_reason: ", response.choices[0].finish_reason)
        print("edited_txt:\n", response.choices[0].text)
        print("Done!")
    
        return jsonify({ 'edited_txt': response.choices[0].text })


if __name__ == "__main__":
    # Create the database tables
    db.create_all()
    app.run()
