import React, { useState, useEffect } from 'react';
import { Box, Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Typography,
  LinearProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Snackbar
} from '@mui/material';
import { styled } from '@mui/material/styles';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import AddIcon from '@mui/icons-material/Add';
import axios from 'axios';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import MenuIcon from '@mui/icons-material/Menu';
import PreviewIcon from '@mui/icons-material/Preview';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import WorkIcon from '@mui/icons-material/Work';
import { G_COLORS } from '../config/colors.js';
import ResumeDetail from './ResumeDetail.jsx';

// Styled components using the theme colors
const StyledPaper = styled(Paper)(({ theme }) => ({
  backgroundColor: G_COLORS.BACKGROUND,
  '&:hover': {
    backgroundColor: G_COLORS.QUATERNARY,
  }
}));

const ResumeList = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [title, setTitle] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [editDialog, setEditDialog] = useState(false);
  const [editingResume, setEditingResume] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editFile, setEditFile] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [viewingResume, setViewingResume] = useState(null);
  const [resumeContent, setResumeContent] = useState(null);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    setLoading(true); // Set loading before fetch
    try {
      const response = await axios.get('http://localhost:5000/resumes');
      setResumes(response.data);
    } catch (error) {
      console.error('Error fetching resumes:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load resumes',
        severity: 'error'
      });
    } finally {
      setLoading(false); // Always set loading to false
    }
  };

  const handleCreateResume = async () => {
    if (!title || !selectedFile) {
      setSnackbar({
        open: true,
        message: 'Please provide both title and file',
        severity: 'warning'
      });
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', selectedFile);
    formData.append('user_id', 1); // Changed from owner_id to user_id
    
    try {
      await axios.post('http://localhost:5000/resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setOpenDialog(false);
      setTitle('');
      setSelectedFile(null);
      fetchResumes();
      setSnackbar({
        open: true,
        message: 'Resume created successfully',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to create resume',
        severity: 'error'
      });
    }
  };

  // Add this useEffect to fetch jobs
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await axios.get('http://localhost:5000/get-jobs');
        setJobs(response.data);
      } catch (error) {
        console.error('Error fetching jobs:', error);
      }
    };
    fetchJobs();
  }, []);

  // Update handleEdit to also fetch jobs
  const handleEdit = async (resume) => {
    try {
      // Edit the resume
      setEditingResume(resume);
      setEditTitle(resume.title);
      setSelectedJob('');
      setEditFile(null);
      setEditDialog(true);
      console.log('Edit resume:', resume.title);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to edit resume',
        severity: 'error'
      });
    }
  };

  const handleDelete = async (resume_id) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      try {
        await axios.delete(`http://localhost:5000/resume/${resume_id}`);
        fetchResumes();
        setSnackbar({
          open: true,
          message: 'Resume deleted successfully',
          severity: 'success'
        });
      } catch (error) {
        setSnackbar({
          open: true,
          message: 'Failed to delete resume',
          severity: 'error'
        });
      }
    }
  };

  const handleCopy = async (resume_id) => {
    try {
      await axios.post(`http://localhost:5000/resume/${resume_id}/copy`);
      fetchResumes();
      setSnackbar({
        open: true,
        message: 'Resume copied successfully',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to copy resume',
        severity: 'error'
      });
    }
  };

  // handle Edit 
  const handleEditSubmit = async () => {
    try {
      const formData = new FormData();
      formData.append('title', editTitle);
      formData.append('user_id', 1); // Add user_id to the form data
      if (editFile) {
        formData.append('file', editFile);
      }
      if (selectedJob) {
        formData.append('job_id', selectedJob);
      }

      await axios.put(`http://localhost:5000/resume/${editingResume.id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (selectedJob) {
        await axios.post(`http://localhost:5000/resume/${editingResume.id}/match/${selectedJob}`, {
          score: 0,
          match_details: ''
        });
      }

      setEditDialog(false);
      fetchResumes();
      setSnackbar({
        open: true,
        message: 'Resume updated successfully',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to update resume',
        severity: 'error'
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  if (loading) {
    return <LinearProgress />;
  }

  const handleView = async (resume) => {
    try {
      const response = await axios.get(`http://localhost:5000/resume/${resume.id}`);
      setResumeContent(response.data.content);
      setViewingResume(resume);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to load resume content',
        severity: 'error'
      });
    }
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {viewingResume ? (
        <ResumeDetail
          resume={viewingResume}
          content={resumeContent}
          onBack={() => setViewingResume(null)}
        />
      ) : (
        <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Resumes
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          sx={{ 
            backgroundColor: G_COLORS.PRIMARY,
            '&:hover': {
              backgroundColor: G_COLORS.SECONDARY
            }
          }}
        >
          Create New Resume
        </Button>
      </Box>

      {/* Create Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={() => setOpenDialog(false)} 
        maxWidth="sm" 
        fullWidth
        PaperProps={{ sx: { p: 2 } }} // Add padding to dialog
      >
        <DialogTitle>Create New Resume</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Resume Title"
            fullWidth
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            sx={{ mb: 2 }}
          />
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setSelectedFile(e.target.files[0])}
            style={{ width: '100%' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateResume} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog 
        open={editDialog} 
        onClose={() => setEditDialog(false)} 
        maxWidth="sm" 
        fullWidth
        PaperProps={{ sx: { p: 2 } }}
      >
        <DialogTitle>Edit Resume</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Resume Title"
            fullWidth
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            sx={{ mb: 2 }}
          />
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setEditFile(e.target.files[0])}
            style={{ width: '100%', marginBottom: '16px' }}
          />
          <Select
            fullWidth
            value={selectedJob}
            onChange={(e) => setSelectedJob(e.target.value)}
            displayEmpty
            sx={{ mb: 2 }}
          >
            <MenuItem value="" disabled>Select a job to match</MenuItem>
            {jobs.map((job) => (
              <MenuItem key={job.job_id} value={job.job_id}>
                {job.job_title} <Chip label={job.org_name} color="primary" size="small" sx={{ mb: 1, mr: 1, ml: 1 }} />
              </MenuItem>
            ))}
          </Select>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button onClick={handleEditSubmit} variant="contained">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      <TableContainer component={Paper} sx={{ mt: 2 }}>
        <Table size="medium">
          <TableHead>
            <TableRow>
              <TableCell>Resume</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Last Edited</TableCell>
              <TableCell>Job Matches</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {resumes.map((resume) => (
              <TableRow key={resume.id}>
                <TableCell>
                  <Button
                    onClick={() => handleView(resume)}
                    sx={{
                      textTransform: 'none',
                      padding: 0,
                      color: G_COLORS.PRIMARY,
                      '&:hover': {
                        textDecoration: 'underline',
                        background: 'none',
                        color: G_COLORS.SECONDARY
                      }
                    }}
                  >
                    {resume.title}
                  </Button>
                </TableCell>
                <TableCell>{new Date(resume.created_date).toLocaleDateString()}</TableCell>
                <TableCell>{new Date(resume.last_edited).toLocaleDateString()}</TableCell>
                <TableCell>
                  {resume.matches && resume.matches.length > 0 ? (
                    <Box>
                      {resume.matches.map((match, index) => (
                        <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                          {match.job_title} - Score: {match.score}%
                        </Typography>
                      ))}
                    </Box>
                  ) : (
                    'No matches'
                  )}
                </TableCell>
                <TableCell align="center">
                  <IconButton onClick={() => handleView(resume)} size="small">
                    <VisibilityIcon />
                  </IconButton>
                  <IconButton onClick={() => handleEdit(resume)} size="small">
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={() => handleCopy(resume.id)} size="small">
                    <ContentCopyIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDelete(resume.id)} size="small">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
     )}
    </Box>
  );
};

export default ResumeList;