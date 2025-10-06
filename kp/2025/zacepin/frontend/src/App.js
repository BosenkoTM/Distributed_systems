import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import LabelingInterface from './pages/LabelingInterface';
import FileUpload from './pages/FileUpload';
import SessionManager from './pages/SessionManager';
import Monitoring from './pages/Monitoring';
import { SessionProvider } from './contexts/SessionContext';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SessionProvider>
        <Router>
          <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <Navbar />
            <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/labeling" element={<LabelingInterface />} />
                <Route path="/upload" element={<FileUpload />} />
                <Route path="/sessions" element={<SessionManager />} />
                <Route path="/monitoring" element={<Monitoring />} />
              </Routes>
            </Box>
          </Box>
        </Router>
      </SessionProvider>
    </ThemeProvider>
  );
}

export default App;
