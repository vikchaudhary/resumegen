import React, { useState } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Button,
  Paper
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import MenuIcon from '@mui/icons-material/Menu';
import PreviewIcon from '@mui/icons-material/Preview';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import WorkIcon from '@mui/icons-material/Work';

const ResumeDetail = ({ resume, content, onBack }) => {
  const [activeTab, setActiveTab] = useState('preview');

  return (
    <Box sx={{ width: '100%' }}>
      <AppBar position="static" sx={{ backgroundColor: 'white', color: 'black' }}>
        <Toolbar>
          <IconButton edge="start" onClick={onBack}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" sx={{ ml: 2, flex: 1 }}>
            {resume.title}
          </Typography>
          <IconButton>
            <PictureAsPdfIcon />
          </IconButton>
          <IconButton edge="end">
            <MenuIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      
      <Paper sx={{ mt: 1, p: 1 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            startIcon={<PreviewIcon />}
            variant={activeTab === 'preview' ? 'contained' : 'text'}
            onClick={() => setActiveTab('preview')}
          >
            Preview
          </Button>
          <Button
            startIcon={<AnalyticsIcon />}
            variant={activeTab === 'analysis' ? 'contained' : 'text'}
            onClick={() => setActiveTab('analysis')}
          >
            Analysis
          </Button>
          <Button
            startIcon={<WorkIcon />}
            variant={activeTab === 'matching' ? 'contained' : 'text'}
            onClick={() => setActiveTab('matching')}
          >
            Job Matching
          </Button>
        </Box>
      </Paper>

      <Box sx={{ mt: 2, p: 2 }}>
        {activeTab === 'preview' && (
          <iframe
            src={`data:application/pdf;base64,${content}`}
            style={{ width: '100%', height: 'calc(100vh - 200px)' }}
            title="Resume Preview"
          />
        )}
      </Box>
    </Box>
  );
};

export default ResumeDetail;