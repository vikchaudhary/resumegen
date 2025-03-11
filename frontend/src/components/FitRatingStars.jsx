import React from 'react';
import { Rating, Typography, Box } from '@mui/material';

const FitRatingStars = ({ value, onChange }) => {
  return (
    <Box>
      <Typography component="legend">Fit Rating</Typography>
      <Rating
        name="fit-rating"
        value={value || 0}
        onChange={(event, newValue) => {
          onChange(newValue);
        }}
        max={5}
        size="large"
      />
    </Box>
  );
};

export default FitRatingStars;