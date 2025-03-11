import React, { useState, useEffect } from 'react';
import { Grid, Card, CardContent, Typography } from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const Dashboard = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/job-statistics')
      .then(response => response.json())
      .then(data => setStats(data))
      .catch(error => console.error('Error:', error));
  }, []);

  if (!stats) return <Typography>Loading dashboard...</Typography>;

  return (
    <Grid container spacing={3}>
      {/* Status Distribution Chart */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Application Status Distribution</Typography>
            <PieChart width={400} height={300}>
              <Pie
                data={stats.status_distribution}
                dataKey="count"
                nameKey="status"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {stats.status_distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </CardContent>
        </Card>
      </Grid>

      {/* Location Distribution Chart */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Location Distribution</Typography>
            <BarChart
              width={400}
              height={300}
              data={stats.location_distribution}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="location" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </CardContent>
        </Card>
      </Grid>

      {/* Salary Distribution Chart */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6">Salary Range Distribution</Typography>
            <Typography variant="body1">
              Average Salary Range: ${stats.salary_statistics.average_min_salary?.toLocaleString()} - 
              ${stats.salary_statistics.average_max_salary?.toLocaleString()}
            </Typography>
            <Typography variant="body1">
              Overall Range: ${stats.salary_statistics.lowest_salary?.toLocaleString()} - 
              ${stats.salary_statistics.highest_salary?.toLocaleString()}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Application Timeline */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6">Application Timeline</Typography>
            <BarChart
              width={800}
              height={300}
              data={stats.application_timeline}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#82ca9d" />
            </BarChart>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default Dashboard;