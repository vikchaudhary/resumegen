# ResumeGen

ResumeGen is a tool designed to scan resumes and check for specific keywords, helping users optimize their resumes for applicant tracking systems (ATS) and improve their chances of getting noticed by recruiters.

## Features

- **Keyword Analysis**: Scans resumes to identify the presence of specified keywords.
- **ATS Optimization**: Assists in tailoring resumes to be more ATS-friendly by highlighting missing or underused keywords.

## Installation

To set up ResumeGen locally, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/vikchaudhary/resumegen.git
   cd resumegen
   ```

2. **Set Up the Backend:**

   - Navigate to the backend directory:

     ```bash
     cd backend
     ```

   - Create a virtual environment:

     ```bash
     python3 -m venv venv
     source venv/bin/activate  # On Windows, use venv\Scripts\activate
     ```

   - Install the required Python packages:

     ```bash
     pip install -r requirements.txt
     ```

   - Start the backend server:

     ```bash
     python app.py
     ```

3. **Set Up the Frontend:**

   - Navigate to the frontend directory:

     ```bash
     cd ../frontend
     ```

   - Install the required Node.js packages:

     ```bash
     npm install
     ```

   - Start the frontend application:

     ```bash
     npm start
     ```

The application should now be running locally. Access the frontend interface through your web browser to upload and analyze your resume.

## Usage

1. **Upload Your Resume:** Use the frontend interface to upload your resume in a supported format (e.g., PDF or DOCX).

2. **Keyword Analysis:** The application will scan your resume and provide feedback on the presence of specified keywords.

3. **Optimize Your Resume:** Based on the analysis, adjust your resume to include relevant keywords to improve its ATS compatibility.

## Contributing

Contributions are welcome! If you'd like to contribute to ResumeGen, please follow these steps:

1. Fork the repository.

2. Create a new branch:

   ```bash
   git checkout -b feature-branch
   ```

3. Make your changes and commit them:

   ```bash
   git commit -m "Description of changes"
   ```

4. Push to the branch:

   ```bash
   git push origin feature-branch
   ```

5. Open a pull request detailing your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

Special thanks to all contributors and the open-source community for their support and contributions.

---

