import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; // Import the CSS file

/* Material UI controls */
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import { styled } from '@mui/material/styles';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import Grid from '@mui/material/Grid';
/* Icons */
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import FileOpenIcon from '@mui/icons-material/FileOpen';
import SaveAsIcon from '@mui/icons-material/SaveAs';
import EditNoteIcon from '@mui/icons-material/EditNote';
import { ThemeOptions } from '@mui/material/styles';
/* List */
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
/* AppBar */
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import EditIcon from '@mui/icons-material/Edit';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';


/* Theme 

   This is a TypeScript type annotation : ThemeOptions, which specifies that the themeOptions constant must conform to the structure defined by the ThemeOptions interface (which is imported from '@mui/material/styles').
*/
export const themeOptions: ThemeOptions = {
  palette: {
    mode: 'light',
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
  },
};

/* Constants */
const G_KEYBUTTON_TXT = "Extract Keywords";
const G_OPENRESUME_TXT = "Open Resume";
const G_GENERATERESUME_TXT = "Generate Resume";
const G_SAVEJOB_TXT = "Save this Job";
const G_JOBSHEADER_TXT = "Jobs";
const G_JOBNAME_TXT = "Job Name";
const G_SELECT_COMPANY_TXT = "Select Company";

function App() {
  /**
   * Create state variables job_desc and keywords, which will be used to store and update the 
   * current text input value and the list of extracted keywords, respectively. 
   * The setText function is used to update the value of the text state variable.
   * The setkeywords_tuple function is used to update the value of the keywords state variable.
   */
  const [job_desc, setJobDesc] = useState('');
  const [found_keywords, setFoundKeywords] = useState([]);
  const [missing_keywords_arr, setMissingKeywords] = useState([]);
  const [resume_fname, setResumeFname] = useState('');
  const [edited_txt, setEditedText] = useState('');
  /* Database */
  const [jobName, setJobName] = useState('');
  const [jobList, setJobList] = useState([]);
  /* Company name for Job */
  const [companies, setCompanies] = useState([]); /* the list of companies */
  const [selectedCompany, setSelectedCompany] = useState(''); /* the selected company */

  /* When the component first mounts, useEffect() triggers */
  useEffect(() => {
    fetchJobs();
    fetchCompanies();
  }, []);

  /* Fetches the list of jobs from database */
  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get-jobs');
      const data = response.data;
      console.log("fetchJobs(): data.jobs:", data)
      setJobList(data);
    } catch (error) {
       console.log('Error in fetchJobs():', error);
    }
  };

  /* Fetches the list of companies from database */
  const fetchCompanies = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get-companies');

      /* When the response returns, update the "companies" state with the data */
      setCompanies(response.data);
    } catch (error) {
      console.log('Error in fetchCompanies():', error);
    }
  };

  const saveJob = async () => {
    const ownerID = 1; // Hardcode owner ID
    const orgID = 1000;

    const jobData = {
      title: jobName,
      desc: job_desc,
      owner_id: ownerID,
      org_id: orgID,
      company: selectedCompany
    };

    try {
      const response = await axios.post('http://localhost:5000/save-job', jobData);
      console.log(response.data.message);
      fetchJobs();
    } catch (error) {
      console.log('Error in saveJob():', error);
    }
  };

  const editCompany = async () => {
    try {
      await axios.post('http://localhost:5000/update-job-company', {
        job_name: jobName,
        company: selectedCompany
      });
      fetchJobs();
    } catch (error) {
      console.log('Error updating company in editCompany():', error);
    }
  };

  /**
   * Handle click event on a job item in the list.
   * Retrieve the job description from the SQLite table based on the job's ID.
   * Set the job description as the value of the "Job Description" TextField.
   *   job - The job object clicked in the list.
   */
  const handleJobClickinList = async (job) => {
    try {
      // Make a GET request to the Flask API endpoint to retrieve job description
      const response = await axios.get(`http://localhost:5000/get-job/${job.id}`);
      const data = response.data;

      // Set the job description in the state to update the "Job Description" TextField
      if (data.desc) setJobDesc(data.desc);
      if (data.company) setSelectedCompany(data.company);
      setJobName(data.title);

      // Fetch the company name based on org_id
      if(data.org_id) fetchCompanyName(data.org_id);

    } catch (error) {
      console.log('Error in handleJobClickinList():', error);
    }
  };

  /**
   * Fetch company name from the backend
   * @param {int} orgID 
  */
    const fetchCompanyName = async (orgID) => {
      try {
        const response = await axios.get(`http://localhost:5000/get-company-name/${orgID}`);
        console.log("fetchCompanyName(): response.data:", response.data)
        setSelectedCompany(response.data.short_name);
      } catch (error) {
          console.log('Error fetching company name:', error);
      }
    }

  /**
   * Handles the analyze button click event.
   * Calls the OpenAI API with the provided 'job_desc' to extract keywords from the file 'resume_fname'
   */
  const handleAnalyze = () => {
    axios.post('http://localhost:5000/analyze', { job_desc, resume_fname })
      .then(response => {
        setFoundKeywords(response.data.found_keywords_arr);
        setMissingKeywords(response.data.missing_keywords_arr);
      })
      .catch(error => {
        console.log('Analyze this request error:', error);
      });
  };

  /**
   * Handles the Generate Resume button click event.
   * Calls the OpenAI API with the provided text to add missing keywords
   */
    const handleGenerate = () => {
      axios.post('http://localhost:5000/generate', { resume_fname, missing_keywords_arr })
        .then(response => {
          setEditedText(response.data.edited_txt);
        })
        .catch(error => {
          console.log('handleGenerate() error:', error);
        });
    };

  /**
   * handleJobDescChange() 
   * Clear the keyword list whenever the input text changes
  */
  const handleJobDescChange = (event) => {
    setJobDesc(event.target.value);
    setEditedText('');
    setFoundKeywords([]);
    setMissingKeywords([]);
  };

  // handleFileSelect
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setResumeFname(file.name);
    }
  };

  // handleFileOpen
  const handleFileOpen = () => {
    document.getElementById('file-input').click();
  };

  // This is the web application, i.e. the output
  return (
    <div>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar variant="dense">
            <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }}>
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" color="inherit" component="div">
              ResumeAI
            </Typography>
          </Toolbar>
        </AppBar>
      </Box>
      <br></br>
      <Box sx={{ flexGrow: 1 }}>
        <Grid container spacing={2}>
          <Grid item xs={8}>
          
            {/* Open file input */}
            <input type="file" id="file-input" onChange={handleFileSelect} style={{ display: 'none' }} />
            <Button 
              variant="contained" 
              size="large" 
              sx={{ mb: 2, mr: 2 }} 
              onClick={handleFileOpen} 
              endIcon={<FileOpenIcon />}>{G_OPENRESUME_TXT}
            </Button>

            {/* Filename text field */}
            <TextField label="Resume" 
              className="resume-filename" 
              variant="filled" 
              size="small" 
              sx={{ mb: 2 }} 
              focused value={resume_fname} 
              InputProps={{ readOnly: true }} />
          
            {/* Job Description */}
            <TextField label="Job Description" 
              className="input-pane" 
              variant="filled" 
              multiline rows={20} 
              sx={{ mb: 1 }} 
              defaultValue={job_desc} 
              onChange={handleJobDescChange} />
          
            {/* Name the job 
            <TextField label={G_JOBNAME_TXT} 
              fullWidth 
              sx={{ mb: 2 }}
              size="small"
              value={jobName}
              onChange={(e) => setJobName(e.target.value)} />
              */}

            {/* Job Name and Company Selection */}
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
              <TextField
                label={G_JOBNAME_TXT}
                fullWidth
                size="small"
                value={jobName}
                onChange={(e) => setJobName(e.target.value)}
              />
              <Select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                displayEmpty
                size="small"
                sx={{ minWidth: 200 }}
              >
                <MenuItem value="" disabled>{G_SELECT_COMPANY_TXT}</MenuItem>
                {companies.map((company) => (
                  <MenuItem key={company.id} value={company.name}>
                    {company.name}
                  </MenuItem>
                ))}
              </Select>
              <Button variant="contained" startIcon={<EditIcon />} onClick={editCompany}>
                Edit Company
              </Button>
            </Box>

            {/* Save Job button */}
            <Button 
              variant="contained" 
              endIcon={<SaveAsIcon />}
              onClick={saveJob}>
                {G_SAVEJOB_TXT}
              </Button>
          
          </Grid>

          {/* List of jobs from the database */}
          <Grid item xs={4}>
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <Paper sx={{ p: 2, width: 600 }}>
                <Typography variant="h8" component="h4">{G_JOBSHEADER_TXT}</Typography>
                <List sx={{ maxHeight: 800, overflow: 'auto' }}>
                  {jobList.map((job) => (
                    <ListItem key={job.id} disablePadding>
                      <ListItemButton onClick={() => handleJobClickinList(job)}>
                        <ListItemText primary={job.title} />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Box>
          </Grid>

          <Grid item xs={8}>
            {/* The output pane is where we display all the keywords */}
            <Button 
              variant="contained" 
              endIcon={<EditNoteIcon />}
              sx={{mb:5}} 
              onClick={handleAnalyze} >
              {G_KEYBUTTON_TXT}
            </Button>
            
            <div className="keywords-pane">
              <Box
                sx={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  width: 500,
                  height: 150
                }}>
                <Stack direction="row"  flexWrap="wrap" spacing={1}>
                {found_keywords.map((keyword, index) => (
                    <Chip label={keyword} color="success" size="small" icon={<CheckCircleIcon />} sx={{mb:1, mr:1, ml:1}} />
                ))}
                {missing_keywords_arr.map((keyword, index) => (
                    <Chip label={keyword} color="error" size="small" icon={<ErrorIcon />} sx={{mb:1, mr:1, ml:1}} />
                ))}
              </Stack>
              </Box>
            </div>
          </Grid>

          <Grid item xs={8}>
              {/* The pane where we generate a new resume */}
              <Button variant="contained" sx={{mt:5, mb:5}} onClick={handleGenerate} endIcon={<EditNoteIcon />}>{G_GENERATERESUME_TXT}</Button>
              
              {/* Generate field containing the new resume */}
              <TextField className="output-pane" label="Edited" variant="filled" multiline rows={20} value={edited_txt} />
            
          </Grid>
        </Grid>
      </Box>
    </div>
  );
}

export default App;



