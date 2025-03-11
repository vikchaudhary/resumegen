import React, { useState, useEffect } from 'react';
import { 
  Card, CardContent, Typography, Grid, Box,
  Button, Dialog, DialogTitle, DialogContent
} from '@mui/material';
import StatusSelect from './StatusSelect';
import LocationSelect from './LocationSelect';
import SalaryRangeInput from './SalaryRangeInput';
import FitRatingStars from './FitRatingStars';

const JobDetailView = ({ jobId }) => {
  const [job, setJob] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (jobId) {
      fetch(`http://localhost:5000/get-job/${jobId}`)
        .then(response => response.json())
        .then(data => setJob(data))
        .catch(error => console.error('Error:', error));
    }
  }, [jobId]);

  const handleStatusChange = (event) => {
    const newStatusId = event.target.value;
    fetch('http://localhost:5000/update-job-status', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, status_id: newStatusId })
    })
    .then(() => {
      setJob({ ...job, status_id: newStatusId });
    });
  };

  const handleLocationChange = (event) => {
    const newLocationId = event.target.value;
    fetch('http://localhost:5000/update-job-location', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, location_id: newLocationId })
    })
    .then(() => {
      setJob({ ...job, location_id: newLocationId });
    });
  };

  const handleSalaryChange = (minSalary, maxSalary) => {
    fetch('http://localhost:5000/update-job-salary', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        job_id: jobId, 
        min_salary: minSalary, 
        max_salary: maxSalary 
      })
    })
    .then(() => {
      setJob({ ...job, min_salary: minSalary, max_salary: maxSalary });
    });
  };

  const handleFitRatingChange = (newRating) => {
    fetch('http://localhost:5000/update-job-fit', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, fit_rating: newRating })
    })
    .then(() => {
      setJob({ ...job, fit_rating: newRating });
    });
  };

  if (!job) return <Typography>Loading...</Typography>;

  return (
    <Card>
      <CardContent>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h5">{job.job_title}</Typography>
            <Typography color="textSecondary">{job.org_name}</Typography>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <StatusSelect 
              value={job.status_id} 
              onChange={handleStatusChange} 
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <LocationSelect 
              value={job.location_id} 
              onChange={handleLocationChange} 
            />
          </Grid>
          
          <Grid item xs={12}>
            <SalaryRangeInput 
              minSalary={job.min_salary}
              maxSalary={job.max_salary}
              onMinChange={(e) => handleSalaryChange(e.target.value, job.max_salary)}
              onMaxChange={(e) => handleSalaryChange(job.min_salary, e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12}>
            <FitRatingStars 
              value={job.fit_rating} 
              onChange={handleFitRatingChange} 
            />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="h6">Match Percentage</Typography>
            <Typography variant="h3" color="primary">
              {job.match_percentage}%
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default JobDetailView;