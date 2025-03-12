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
import FindInPageIcon from '@mui/icons-material/FindInPage';
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
/* Table */
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
/* Word Cloud */
import CardMedia from '@mui/material/CardMedia';
/* Dialog for adding a new org/compamy */
import AddCircleIcon from '@mui/icons-material/AddCircle';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
// Add these imports to implement the left navigation bar
import CssBaseline from '@mui/material/CssBaseline';
import Drawer from '@mui/material/Drawer';
import ListItemIcon from '@mui/material/ListItemIcon';
import DescriptionIcon from '@mui/icons-material/Description';
import WorkIcon from '@mui/icons-material/Work';
import AssessmentIcon from '@mui/icons-material/Assessment';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import JobDetailView from './components/JobDetailView.jsx';
import LocationSelect from './components/LocationSelect.jsx';
import SalaryRangeInput from './components/SalaryRangeInput.jsx';
import Dashboard from './components/Dashboard.jsx';
import ResumeList from './components/ResumeList.jsx';

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
const G_ANALYZE_TXT = "Analyze Resume";
const G_OPENRESUME_TXT = "Open Resume";
const G_RESUME_TXT = "Resume";
const G_GENERATERESUME_TXT = "Generate Resume";
const G_SAVEJOB_TXT = "Save this Job";
const G_JOBSHEADER_TXT = "Select a job:";
const G_JOBNAME_TXT = "Job Name";
const G_SELECT_COMPANY_TXT = "Select Company";
const G_EDIT_TXT = "Edit";
const G_ALERT_RESUMEFILENOTSET = 'Please select a resume file first';
const G_NAME_OF_ORGANIZATION_TXT = 'Name of organization';
const G_SHORT_NAME_TXT = "Short name";
const G_FULL_ORG_NAME_TXT = "Full org name";
const drawerWidth = 240;

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
  // Update the state to store both id and name
  const [selectedCompany, setSelectedCompany] = useState({ id: '', name: '' });
  /* Word cloud */
  const [wordCloudImage, setWordCloudImage] = useState('');
  /* Dialog to add a new company */
  const [openNewOrgDialog, setOpenNewOrgDialog] = useState(false);
  const [newOrgShortName, setNewOrgShortName] = useState('');
  const [newOrgLongName, setNewOrgLongName] = useState('');
  /* Added with new design */
  const [currentView, setCurrentView] = useState('resumes');
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState('');
  const [minSalary, setMinSalary] = useState('');
  const [maxSalary, setMaxSalary] = useState('');

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
       console.log('Error in fetchJobs():', error.message);
       setJobList([]); // Reset to empty array on error
    }
  };

  /* Fetches the list of companies from database */
  const fetchCompanies = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get-companies');
      /* When the response returns, update the "companies" state with the data */
      setCompanies(response.data);
    } catch (error) {
      console.error('Error in fetchCompanies():', error.message);
      setCompanies([]); // Reset to empty array on error
    }
  };

  const saveJob = async () => {
    if (!jobName || !job_desc || !selectedCompany.id) {
      console.error('Missing required fields for saving job');
      return;
    }

    const ownerID = 1; // Hardcode owner ID
    
    const jobData = {
      job_title: jobName,
      job_desc: job_desc,
      owner_id: ownerID,
      org_id: selectedCompany.id
    };

    try {
      const response = await axios.post('http://localhost:5000/save-job', jobData);
      console.log(response.data.message);
      fetchJobs();
    } catch (error) {
      console.error('Error in saveJob():', error.message);
    }
  };

  const editCompany = async () => {
    if (!jobName || !selectedCompany.id) {
      console.error('Missing job name or company information');
      return;
    }

    try {
      await axios.post('http://localhost:5000/update-job-company', {
        job_name: jobName,
        company: selectedCompany
      });
      fetchJobs();
    } catch (error) {
      console.error('Error updating company in editCompany():', error.message);
    }
  };

  /**
   * handleAddOrg–adds a new org to the org table
   */
  const handleAddOrg = async () => {
    if (!newOrgShortName || !newOrgLongName) {
      console.error('Both short name and full name are required');
      return;
    }

    try {
      const response = await axios.post('http://localhost:5000/add-org', {
        short_name: newOrgShortName,
        long_name: newOrgLongName
      });
      setNewOrgShortName('');
      setNewOrgLongName('');
      setOpenNewOrgDialog(false);
      fetchCompanies(); /* Refresh the list of orgs */
    } catch (error) {
      console.error('Error adding organization:', error.message);
    }
  };

  /**
   * Handle click event on a job item in the list.
   * Retrieve the job description from the SQLite table based on the job's ID.
   * Set the job description as the value of the "Job Description" TextField.
   *   job - The job object clicked in the list.
   */
  const handleJobClickinList = async (job) => {
    if (!job?.job_id) {
      console.error('Invalid job data');
      return;
    }

    try {
      const response = await axios.get(`http://localhost:5000/get-job/${job.job_id}`);
      const data = response.data;

      if (!data) {
        console.error('No data received for job');
        return;
      }

      if (data.job_desc) {
        handleJobDescChange({ target: { value: data.job_desc } });
      }
      if (data.org_name) {
        setSelectedCompany({ 
          id: data.org_id, 
          name: data.org_name
        });
      }
      setJobName(data.job_title);
    } catch (error) {
      console.error('Error in handleJobClickinList():', error.message);
    }
  };

  /**
   * fetchCompanyName() - Fetch org name from its id
   */
  const fetchCompanyName = async (orgID) => {
      if (!orgID) {
        console.error('Organization ID is required');
        return;
      }

      try {
        const response = await axios.get(`http://localhost:5000/get-company-name/${orgID}`);
        console.log("fetchCompanyName(): response.data:", response.data);
        setSelectedCompany({
          id: orgID,
          name: response.data.short_name
        });
      } catch (error) {
        console.error('Error fetching company name:', error.message);
        setSelectedCompany({ id: '', name: '' }); // Reset on error
      }
    };

  /**
   * Handles the Analyze button click event.
   * Calls the OpenAI API with the provided 'job_desc' to extract keywords.
   * Analyzes the file named by 'resume_fname' to find which of the keywords match or not.
   * Calls the end-point /analyze
   */
  const handleAnalyze = () => {
    if (!resume_fname) {
      alert(G_ALERT_RESUMEFILENOTSET);
      return;
    }
    
    axios.post('http://localhost:5000/analyze', { job_desc, resume_fname })
      .then(response => {
        setFoundKeywords(response.data.found_keywords_arr);
        setMissingKeywords(response.data.missing_keywords_arr);
      })
      .catch(error => {
        console.log('handleAnalyze() error:', error);
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
   * Clear the keyword list whenever the input text changes, and generate a new word cloud
   **/
  const handleJobDescChange = async (event) => {
    const newJobDesc = event.target.value;
    setJobDesc(newJobDesc);
    setEditedText('');
    setFoundKeywords([]);
    setMissingKeywords([]);

    try {
      const response = await axios.post('http://localhost:5000/generate-wordcloud', { job_desc: newJobDesc });
      setWordCloudImage(response.data.image);
    } catch (error) {
      console.error('Error generating word cloud:', error);
      setWordCloudImage(''); // Clear the image on error
    }
  };

  // handleFileSelect
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setResumeFname(file.name);
    }
  };

  /**
   * handleFileOpen() 
   * Opens a file
   **/
  const handleFileOpen = () => {
    document.getElementById('file-input').click();
  };

  // Add handlers for new components
  const handleLocationChange = (event) => {
    setSelectedLocation(event.target.value);
  };

  const handleMinSalaryChange = (event) => {
    setMinSalary(event.target.value);
  };

  const handleMaxSalaryChange = (event) => {
    setMaxSalary(event.target.value);
  };

  /**
   * ListJobsTable
   * Create a HTML table structure. The outer <TableContainer component={Paper}> 
   * is from materialUI and provides styling like shadow, rounded corners, and scrolling.
   * The <Chip> and <ListItemText> are now placed inside <td> cells, creating the two-column layout
   * Clickable Row: ee add an onClick handler to the <ListItemButton> to handle the click event 
   * for the entire row. It’s inside the table cell for styling reasons.
   **/
  function ListJobsTable({ job, handleJobClickinList }) {
    const chipColumnWidth = '60px'; 
    const titleColumnWidth = '200px'; 
    const rowHeight = '35px';

    // Enhanced logging
    useEffect(() => {
      console.log('ListJobsTable rendered with job:', {
        job_id: job.job_id,
        job_title: job.job_title,
        org_name: job.org_name
      });
    }, [job]);

    return (
      <TableContainer component={Paper} elevation={0} sx={{ width: '100%' }}>
        <Table sx={{ tableLayout: 'fixed', width: '100%' }} aria-label="Jobs table">
          <TableBody>
            <TableRow
              key={job.job_id}
              sx={{ '&:last-child td, &:last-child th': { border: 0 }, height: rowHeight, padding: "0px" }}
            >
              <TableCell component="th" scope="row" sx={{ width: chipColumnWidth, maxWidth: chipColumnWidth, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', padding: "0px" }}>
                <Chip label={job.org_name} color="primary" size="small" sx={{ mb: 1, mr: 1, ml: 1 }} />
              </TableCell>
              <TableCell align="left" sx={{ width: titleColumnWidth, padding: "0px"}}>
                <ListItemButton onClick={() => handleJobClickinList(job)}>
                  {job.job_title}
                </ListItemButton>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  // This is the web application, i.e. the output
  return (
    <div>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar variant="dense">
            <Typography variant="h6" color="inherit" component="div">
              ResumeAI
            </Typography>
          </Toolbar>
        </AppBar>

        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
            },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto' }}>
            <List>
              <ListItem disablePadding>
                <ListItemButton selected={currentView === 'resumes'} onClick={() => setCurrentView('resumes')}>
                  <ListItemIcon><DescriptionIcon /></ListItemIcon>
                  <ListItemText primary="Resumes" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton selected={currentView === 'resume'} onClick={() => setCurrentView('resume')}>
                  <ListItemIcon><DescriptionIcon /></ListItemIcon>
                  <ListItemText primary="Resume Analysis" />
                </ListItemButton>
              </ListItem>
              
              <ListItem disablePadding>
                <ListItemButton selected={currentView === 'jobs'} onClick={() => setCurrentView('jobs')}>
                  <ListItemIcon><WorkIcon /></ListItemIcon>
                  <ListItemText primary="Job Management" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton selected={currentView === 'locations'} onClick={() => setCurrentView('locations')}>
                  <ListItemIcon><LocationOnIcon /></ListItemIcon>
                  <ListItemText primary="Locations" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton selected={currentView === 'salary'} onClick={() => setCurrentView('salary')}>
                  <ListItemIcon><AttachMoneyIcon /></ListItemIcon>
                  <ListItemText primary="Salary Analysis" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton selected={currentView === 'dashboard'} onClick={() => setCurrentView('dashboard')}>
                  <ListItemIcon><AssessmentIcon /></ListItemIcon>
                  <ListItemText primary="Dashboard" />
                </ListItemButton>
              </ListItem>
            </List>
          </Box>
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          {currentView === 'resumes' && (
            <ResumeList />
          )}
          {currentView === 'resume' && (
            <Grid container spacing={2}>
              <Grid item xs={7}>
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
                <TextField label={G_RESUME_TXT}
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

                {/* Job Name and Company Selection Box */}
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                  <TextField
                    label={G_JOBNAME_TXT}
                    fullWidth
                    size="small"
                    value={jobName}
                    onChange={(e) => setJobName(e.target.value)}
                  />
                  {/* Update the Select component and MenuItems */}
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Select
                      value={selectedCompany.id}
                      onChange={(e) => {
                        const org = companies.find(c => c.id === e.target.value);
                        setSelectedCompany({ id: org.id, name: org.name });
                      }}
                      displayEmpty
                      size="small"
                      sx={{ minWidth: 200 }}
                    >
                      <MenuItem value="" disabled>{G_SELECT_COMPANY_TXT}</MenuItem>
                      {companies.map((org) => (
                        <MenuItem key={org.id} value={org.id}>
                          {org.name}
                        </MenuItem>
                      ))}
                    </Select>
                    <IconButton 
                      color="primary" 
                      onClick={() => setOpenNewOrgDialog(true)}
                      sx={{ ml: 1 }}
                    >
                      <AddCircleIcon />
                    </IconButton>
                  </Box>

                  {/* Add Organization Dialog */}
                  <Dialog open={openNewOrgDialog} onClose={() => setOpenNewOrgDialog(false)}>
                    <DialogTitle>{G_NAME_OF_ORGANIZATION_TXT}</DialogTitle>
                    <DialogContent>
                      <TextField
                        autoFocus
                        margin="dense"
                        label={G_SHORT_NAME_TXT}
                        fullWidth
                        value={newOrgShortName}
                        onChange={(e) => setNewOrgShortName(e.target.value)}
                        helperText="Brief name or acronym (e.g., IBM)"
                      />
                      <TextField
                        margin="dense"
                        label={G_FULL_ORG_NAME_TXT}
                        fullWidth
                        value={newOrgLongName}
                        onChange={(e) => setNewOrgLongName(e.target.value)}
                        helperText="Complete organization name (e.g., International Business Machines)"
                      />
                    </DialogContent>
                    <DialogActions>
                      <Button onClick={() => {
                        setOpenNewOrgDialog(false);
                        setNewOrgShortName('');
                        setNewOrgLongName('');
                      }}>Cancel</Button>
                      <Button onClick={handleAddOrg} variant="contained">Add</Button>
                    </DialogActions>
                  </Dialog>
                  <Button variant="contained" startIcon={<EditIcon />} onClick={editCompany} sx={{ pl: 2, pr: 2 }}>
                    {G_EDIT_TXT}
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

              {/* Show a list of jobs */}
              <Grid item xs={5}>
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                  <Paper sx={{ p: 2, width: 600 }}>
                    <Typography variant="subtitle1" component="h4">{G_JOBSHEADER_TXT}</Typography>
                    <List sx={{ maxHeight: 800, overflow: 'auto' }}>

                      {jobList.map((job) => (
                        // REPLACED: <ListJobsTable key={job.job_id} job={job} handleJobClickinList={handleJobClickinList}/>
                        <ListItem key={job.job_id} disablePadding>
                          <ListJobsTable job={job} handleJobClickinList={handleJobClickinList}/>
                        </ListItem>
                      ))}

                    </List>
                  </Paper>
                </Box>

                {/* Display Word Cloud */}
                {wordCloudImage && (
                  <CardMedia
                    component="img"
                    height="300"
                    image={`data:image/png;base64,${wordCloudImage}`}
                    alt="Word Cloud"
                  />
                )}
              </Grid>

              <Grid item xs={8}>

                {/* The output pane is where we display all the keywords */}
                <Button 
                  variant="contained" 
                  endIcon={<FindInPageIcon />}
                  sx={{mb:5}} 
                  onClick={handleAnalyze}
                  disabled={!resume_fname} >
                  {G_ANALYZE_TXT}
                </Button>

                <div className="keywords-pane">
                  <Box
                    sx={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      height: 150,
                      width: '95%'
                    }}>
                    <Stack direction="row" flexWrap="wrap">
                    {found_keywords.map((keyword, index) => (
                        <Chip 
                          key={index}
                          label={keyword} 
                          color="success" 
                          size="small"
                          icon={<CheckCircleIcon />} 
                          sx={{mb:1, mr:1, ml:1, py:1}} />
                    ))}
                    {missing_keywords_arr.map((keyword, index) => (
                        <Chip 
                          key={index}
                          label={keyword} 
                          color="error" 
                          size="small" 
                          icon={<ErrorIcon />} 
                          sx={{mb:1, mr:1, ml:1, py:1}} />
                    ))}
                    </Stack>
                  </Box>
                </div>
              </Grid>

              {/* Generate Resume Grid item */}
              <Grid item xs={8}>
                {/* The pane where we generate a new resume */}
                <Button variant="contained" sx={{mt:5, mb:5}} onClick={handleGenerate} endIcon={<EditNoteIcon />}>{G_GENERATERESUME_TXT}</Button>
                
                {/* Generate field containing the new resume */}
                <TextField className="output-pane" label="Edited" variant="filled" multiline rows={20} value={edited_txt} />
              
              </Grid>

            </Grid>
          )}
          
          {currentView === 'jobs' && (
            <JobDetailView jobId={selectedJobId} />
          )}
          
          {currentView === 'locations' && (
            <LocationSelect value={selectedLocation} onChange={handleLocationChange} />
          )}
          
          {currentView === 'salary' && (
            <SalaryRangeInput
              minSalary={minSalary}
              maxSalary={maxSalary}
              onMinChange={handleMinSalaryChange}
              onMaxChange={handleMaxSalaryChange}
            />
          )}
          
          {currentView === 'dashboard' && (
            <Dashboard />
          )}
        </Box>
      </Box>
    </div>
  );
}

export default App;



