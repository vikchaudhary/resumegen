import React from 'react';
import { Grid, TextField, InputAdornment } from '@mui/material';

const SalaryRangeInput = ({ minSalary, maxSalary, onMinChange, onMaxChange }) => {
  return (
    <Grid container spacing={2}>
      <Grid item xs={6}>
        <TextField
          fullWidth
          label="Minimum Salary"
          type="number"
          value={minSalary || ''}
          onChange={onMinChange}
          InputProps={{
            startAdornment: <InputAdornment position="start">$</InputAdornment>,
          }}
        />
      </Grid>
      <Grid item xs={6}>
        <TextField
          fullWidth
          label="Maximum Salary"
          type="number"
          value={maxSalary || ''}
          onChange={onMaxChange}
          InputProps={{
            startAdornment: <InputAdornment position="start">$</InputAdornment>,
          }}
          error={maxSalary && minSalary && maxSalary <= minSalary}
          helperText={maxSalary && minSalary && maxSalary <= minSalary ? 
            "Maximum salary must be greater than minimum" : ""}
        />
      </Grid>
    </Grid>
  );
};

export default SalaryRangeInput;