import React, { useState, useEffect } from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

const LocationSelect = ({ value, onChange }) => {
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/get-locations')
      .then(response => response.json())
      .then(data => setLocations(data))
      .catch(error => console.error('Error fetching locations:', error));
  }, []);

  return (
    <FormControl fullWidth>
      <InputLabel>Location</InputLabel>
      <Select
        value={value || ''}
        onChange={onChange}
        label="Location"
      >
        {locations.map(location => (
          <MenuItem key={location.id} value={location.id}>
            {location.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default LocationSelect;