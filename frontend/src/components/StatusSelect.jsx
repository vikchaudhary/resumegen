import React, { useState, useEffect } from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

const StatusSelect = ({ value, onChange }) => {
  const [statuses, setStatuses] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/get-job-statuses')
      .then(response => response.json())
      .then(data => setStatuses(data))
      .catch(error => console.error('Error fetching statuses:', error));
  }, []);

  return (
    <FormControl fullWidth>
      <InputLabel>Status</InputLabel>
      <Select
        value={value || ''}
        onChange={onChange}
        label="Status"
      >
        {statuses.map(status => (
          <MenuItem key={status.id} value={status.id}>
            {status.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default StatusSelect;