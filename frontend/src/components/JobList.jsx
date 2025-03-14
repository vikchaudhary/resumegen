import React, { useState, useEffect } from 'react';
import {
  Box, Button, IconButton, Menu, MenuItem, Checkbox,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Typography, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Rating, Chip, Toolbar, AppBar, Tab, Tabs
} from '@mui/material';
import {
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Archive as ArchiveIcon,
  Delete as DeleteIcon,
  ViewColumn as ViewColumnIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { G_COLORS } from '../config/colors.js';


// JobsNavBar Component
const JobsNavBar = ({ activeView, onViewChange }) => (
  <AppBar position="static" color="default">
    <Tabs value={activeView} onChange={onViewChange}
          sx={{
            '& .MuiTab-root': { color: G_COLORS.BACKGROUND },
            '& .Mui-selected': { color: G_COLORS.QUATERNARY }
          }}>
      <Tab label="Jobs" value="jobs" />
      <Tab label="People" value="people" />
      <Tab label="Companies" value="companies" />
    </Tabs>
  </AppBar>
);

// JobsActionBar Component
const JobsActionBar = ({ 
  selectedCount, 
  onArchive, 
  onDelete, 
  onAddNew, 
  onGroupByChange,
  onColumnVisibilityChange,
  columns 
}) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [columnMenuAnchor, setColumnMenuAnchor] = useState(null);

  return (
    <Toolbar>
      <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onAddNew}
          sx={{ 
            backgroundColor: G_COLORS.PRIMARY,
            '&:hover': {
              backgroundColor: G_COLORS.SECONDARY,
            }
          }}
        >
          Add a New Job
        </Button>

        <TextField
          select
          size="small"
          label="Group By"
          defaultValue="status"
          sx={{ 
            minWidth: 120,
            '& .MuiInputBase-input': {
              fontSize: '0.9rem',
            },
            '& .MuiInputLabel-root': {
              fontSize: '0.9rem',
            }
          }}
          onChange={onGroupByChange}
        >
          <MenuItem value="status" sx={{ typography: 'body2' }}>Status</MenuItem>
          <MenuItem value="company" sx={{ typography: 'body2' }}>Company</MenuItem>
          <MenuItem value="location" sx={{ typography: 'body2' }}>Location</MenuItem>
        </TextField>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2">Show columns</Typography>
          <IconButton onClick={(e) => setColumnMenuAnchor(e.currentTarget)}>
            <VisibilityIcon />
          </IconButton>
        </Box>

        {selectedCount > 0 && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2">
              {selectedCount} selected
            </Typography>
            <IconButton onClick={onArchive}>
              <ArchiveIcon />
            </IconButton>
            <IconButton onClick={onDelete}>
              <DeleteIcon />
            </IconButton>
          </Box>
        )}
      </Box>

      <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
        <MoreVertIcon />
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem>Export Selected</MenuItem>
        <MenuItem>Import Jobs</MenuItem>
      </Menu>

      <Menu
        anchorEl={columnMenuAnchor}
        open={Boolean(columnMenuAnchor)}
        onClose={() => setColumnMenuAnchor(null)}
      >
        {columns.map(column => (
          <MenuItem key={column.id}>
            <Checkbox
              checked={column.visible}
              onChange={() => onColumnVisibilityChange(column.id)}
            />
            {column.label}
          </MenuItem>
        ))}
      </Menu>
    </Toolbar>
  );
};

// JobsTable Component
const JobsTable = ({ jobs, columns, selectedRows, onSelectionChange, onSort, sortConfig, onJobUpdate }) => {
  const getJobProperty = (job, columnId) => {
    if (columnId === 'fit') {
      return parseInt(job.fit_rating) || 0;
    }
    
    const propertyMap = {
      'position': job.job_title,
      'company': job.org_name,
      'salary': job.max_salary,
      'location': job.location_name,
      'status': job.status_name,
      'date_saved': job.created_at,
      'deadline': '',  // Add if available in your job data
      'date_applied': '',  // Add if available in your job data
      'follow_up': '',  // Add if available in your job data
      'fit': Number(job.fit_rating) || 0  // Convert to number and provide default value
    };
    return propertyMap[columnId] || '';
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                indeterminate={selectedRows.length > 0 && selectedRows.length < jobs.length}
                checked={selectedRows.length === jobs.length}
                onChange={(e) => onSelectionChange(e.target.checked ? jobs.map(j => j.job_id) : [])}
              />
            </TableCell>
            {columns.filter(col => col.visible).map(column => (
              <TableCell
                key={column.id}
                sortDirection={sortConfig.field === column.id ? sortConfig.direction : false}
                onClick={() => onSort(column.id)}
              >
                {column.label}
              </TableCell>
            ))}
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {jobs.map(job => (
            <TableRow key={job.job_id}>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedRows.includes(job.job_id)}
                  onChange={(e) => {
                    const newSelected = e.target.checked
                      ? [...selectedRows, job.job_id]
                      : selectedRows.filter(id => id !== job.job_id);
                    onSelectionChange(newSelected);
                  }}
                />
              </TableCell>
              {columns.filter(col => col.visible).map(column => (
                <TableCell key={`${job.job_id}-${column.id}`}>
                  {column.id === 'status' ? (
                    <Chip label={getJobProperty(job, column.id)} 
                          sx={{ 
                            backgroundColor: G_COLORS.PRIMARY,
                            color: G_COLORS.BACKGROUND,
                          }} 
                          size="small" />
                  ) : column.id === 'fit' ? (
                    <Rating value={getJobProperty(job, column.id)} readOnly size="small" />
                  ) : (
                    getJobProperty(job, column.id)
                  )}
                </TableCell>
              ))}
              <TableCell>
                <IconButton 
                  size="small"
                  onClick={() => onJobUpdate(job)}
                  sx={{ color: G_COLORS.PRIMARY }}
                >
                  <EditIcon />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

// NewJobDialog Component
const NewJobDialog = ({ open, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    position: '',
    company: '',
    location: '',
    salary: '',
    deadline: '',
    fit: 3
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add a New Job</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
          <TextField
            label="Job"
            value={formData.position}
            onChange={(e) => setFormData({ ...formData, position: e.target.value })}
          />
          <TextField
            label="Company"
            value={formData.company}
            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
          />
          <TextField
            label="Location"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          />
          <TextField
            label="Max Salary"
            value={formData.salary}
            onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
          />
          <TextField
            label="Application Deadline"
            type="date"
            value={formData.deadline}
            onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
          <Box>
            <Typography component="legend">Fit</Typography>
            <Rating
              value={formData.fit}
              onChange={(e, newValue) => setFormData({ ...formData, fit: newValue })}
            />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={() => onSubmit(formData)}>
          Add Job
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Main JobList Component
const JobList = ({ jobs, onJobUpdate, companies }) => {

  const [referenceData, setReferenceData] = useState({
    organizations: [],
    locations: [],
    statuses: []
  });
  const [selectedJob, setSelectedJob] = useState(null);
  
  // Fetch reference data on component mount
  useEffect(() => {
    fetch('/reference-data')
      .then(response => response.json())
      .then(data => {
        console.log('useEffect() - Fetched reference data:', data);
        setReferenceData(data);
      })
      .catch(error => console.error('useEffect() - Error fetching reference data:', error));
  }, []);

  const [isEditDialogOpen, setEditDialogOpen] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const [activeView, setActiveView] = useState('jobs');
  const [selectedRows, setSelectedRows] = useState([]);
  const [isNewJobDialogOpen, setNewJobDialogOpen] = useState(false);
  const [sortConfig, setSortConfig] = useState({ field: 'date_saved', direction: 'desc' });
  const [columns, setColumns] = useState([
    { id: 'position', label: 'Job Position', visible: true },
    { id: 'company', label: 'Company', visible: true },
    { id: 'salary', label: 'Max Salary', visible: true },
    { id: 'location', label: 'Location', visible: true },
    { id: 'status', label: 'Status', visible: true },
    { id: 'date_saved', label: 'Date Saved', visible: true },
    { id: 'deadline', label: 'Deadline', visible: true },
    { id: 'date_applied', label: 'Date Applied', visible: true },
    { id: 'follow_up', label: 'Follow Up', visible: true },
    { id: 'fit', label: 'Fit', visible: true }
  ]);

  const handleEditJob = async (job) => {
    try {
      console.log('handleEditJob() - job:', { job_id: job.job_id, job_title: job.job_title });
      const response = await fetch(`/get-job-details/${job.job_id}`);

      // Check if response is JSON by looking at Content-Type header
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const contentType = response.headers.get('content-type');   
      if (!contentType || !contentType.includes('application/json')) {
        console.log("handleEditJob() - Response was not JSON");
        throw new TypeError("handleEditJob() - throw: Response was not JSON");
      }
      
      const data = await response.json();
      if (data.error) {
        console.error('handleEditJob() - Error fetching job details 1:', data.error);
        return;
      }

      const formattedJob = {
        job_id: data.job[0],
        job_title: data.job[1],
        org_id: data.job[2],
        org_name: data.job[3],
        status_id: data.job[4],
        status_name: data.job[5],
        location_id: data.job[6],
        location_name: data.job[7],
        min_salary: data.job[8],
        max_salary: data.job[9],
        fit_rating: data.job[10],
        match_percentage: data.job[11],
        created_at: data.job[12],
        updated_at: data.job[13]
      };
      
      setEditingJob(formattedJob);
      setEditDialogOpen(true);
    } catch (error) {
      console.error('handleEditJob() - Error fetching job details 2:', error);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <JobsNavBar
        activeView={activeView}
        onViewChange={(e, newValue) => setActiveView(newValue)}
      />
      <JobsActionBar
        selectedCount={selectedRows.length}
        onArchive={() => {/* Implement archive */}}
        onDelete={() => {/* Implement delete */}}
        onAddNew={() => setNewJobDialogOpen(true)}
        onGroupByChange={() => {/* Implement group by */}}
        onColumnVisibilityChange={(columnId) => {
          setColumns(columns.map(col =>
            col.id === columnId ? { ...col, visible: !col.visible } : col
          ));
        }}
        columns={columns}
      />
      <JobsTable
        jobs={jobs}
        columns={columns}
        selectedRows={selectedRows}
        onSelectionChange={setSelectedRows}
        onSort={(field) => {
          setSortConfig({
            field,
            direction: sortConfig.field === field && sortConfig.direction === 'asc' ? 'desc' : 'asc'
          });
        }}
        sortConfig={sortConfig}
        onJobUpdate={handleEditJob}
      />
      <NewJobDialog
        open={isNewJobDialogOpen}
        onClose={() => setNewJobDialogOpen(false)}
        onSubmit={(data) => {
          setNewJobDialogOpen(false);
        }}
      />
      <Dialog open={isEditDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Job</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField
              label="Job"
              value={editingJob?.job_title || ''}
              onChange={(e) => setEditingJob({...editingJob, job_title: e.target.value})}
            />
            <TextField
              select
              label="Company"
              value={editingJob?.org_id?.toString() || ''}  
              onChange={(e) => setEditingJob({
                ...editingJob, 
                org_id: parseInt(e.target.value),  // Convert back to number
                org_name: referenceData.organizations.find(org => org.org_id === parseInt(e.target.value))?.org_name
              })}
            >
              {referenceData.organizations.map(org => (
              <MenuItem 
                key={org.org_id} 
                value={org.org_id.toString()}
                selected={org.org_name === editingJob?.org_name}>  
                  {org.org_name}
              </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Location"
              value={editingJob?.location_id?.toString() || ''}  // Convert to string
              onChange={(e) => setEditingJob({
                ...editingJob, 
                location_id: parseInt(e.target.value),  // Convert back to number
                location_name: referenceData.locations.find(loc => loc.location_id === parseInt(e.target.value))?.location_name
              })}
            >
              {referenceData.locations.map(location => (
                <MenuItem key={location.location_id} value={location.location_id.toString()}>
                  {location.location_name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Status"
              value={editingJob?.status_id?.toString() || ''}  // Convert to string
              onChange={(e) => setEditingJob({
                ...editingJob, 
                status_id: parseInt(e.target.value),  // Convert back to number
                status_name: referenceData.statuses.find(status => status.status_id === parseInt(e.target.value))?.status_name
              })}
            >
              {referenceData.statuses.map(status => (
                <MenuItem key={status.status_id} value={status.status_id.toString()}>
                  {status.status_name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Max Salary"
              value={editingJob?.max_salary || ''}
              onChange={(e) => setEditingJob({...editingJob, max_salary: e.target.value})}
            />
            <Box>
              <Typography component="legend">Fit</Typography>
              <Rating
                value={Number(editingJob?.fit_rating) || 0}
                onChange={(e, newValue) => setEditingJob({...editingJob, fit_rating: newValue})}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              onJobUpdate(editingJob);
              setEditDialogOpen(false);
            }}
          >
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default JobList;


  