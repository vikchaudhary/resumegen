import React, { useState, useEffect } from 'react';
import {
  Box,
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
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import AddIcon from '@mui/icons-material/Add';
import axios from 'axios';

const ResumeList = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [title, setTitle] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

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

  const handleEdit = async (resume_id) => {
    try {
      // Implement edit functionality
      console.log('Edit resume:', resume_id);
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

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ width: '100%', p: 2 }}> {/* Add padding */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Resumes
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          sx={{ backgroundColor: '#00796b' }}
        >
          Create New Resume
        </Button>
      </Box>

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
                <TableCell>{resume.title}</TableCell>
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
                  <IconButton onClick={() => handleEdit(resume.id)} size="small">
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
    </Box>
  );
};

export default ResumeList;