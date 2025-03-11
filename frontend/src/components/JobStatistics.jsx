import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid } from '@mui/material';

const JobStatistics = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/job-statistics')
      .then(response => response.json())
      .then(data => setStats(data))
      .catch(error => console.error('Error fetching statistics:', error));
  }, []);

  if (!stats) return <Typography>Loading statistics...</Typography>;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Status Distribution</Typography>
            {stats.status_distribution.map(item => (
              <Typography key={item.status}>
                {item.status}: {item.count}
              </Typography>
            ))}
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Location Distribution</Typography>
            {stats.location_distribution.map(item => (
              <Typography key={item.location}>
                {item.location}: {item.count}
              </Typography>
            ))}
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6">Salary Statistics</Typography>
            <Typography>
              Average Range: ${stats.salary_statistics.average_min_salary?.toLocaleString()} - 
              ${stats.salary_statistics.average_max_salary?.toLocaleString()}
            </Typography>
            <Typography>
              Overall Range: ${stats.salary_statistics.lowest_salary?.toLocaleString()} - 
              ${stats.salary_statistics.highest_salary?.toLocaleString()}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default JobStatistics;