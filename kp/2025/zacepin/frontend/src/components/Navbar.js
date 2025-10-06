import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Chip,
  Menu,
  MenuItem,
  IconButton
} from '@mui/material';
import {
  Dashboard,
  Label,
  CloudUpload,
  Settings,
  Monitor,
  AccountCircle,
  ExitToApp
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSession } from '../contexts/SessionContext';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentSession, endSession } = useSession();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    try {
      await endSession();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
    handleClose();
  };

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: <Dashboard /> },
    { path: '/labeling', label: 'Разметка', icon: <Label /> },
    { path: '/upload', label: 'Загрузка', icon: <CloudUpload /> },
    { path: '/sessions', label: 'Сессии', icon: <Settings /> },
    { path: '/monitoring', label: 'Мониторинг', icon: <Monitor /> },
  ];

  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Labeling System
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {menuItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              startIcon={item.icon}
              onClick={() => navigate(item.path)}
              sx={{
                backgroundColor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              {item.label}
            </Button>
          ))}

          {currentSession && (
            <>
              <Chip
                label={`Сессия: ${currentSession.session_id.slice(0, 8)}...`}
                color="secondary"
                size="small"
                sx={{ color: 'white', backgroundColor: 'rgba(255,255,255,0.2)' }}
              />
              <Chip
                label={`Реплика: ${currentSession.current_replica}`}
                color="info"
                size="small"
                sx={{ color: 'white', backgroundColor: 'rgba(255,255,255,0.2)' }}
              />
            </>
          )}

          <IconButton
            size="large"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
          >
            <AccountCircle />
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            {currentSession && (
              <MenuItem onClick={handleClose}>
                <Typography variant="body2">
                  Разметчик: {currentSession.annotator_id}
                </Typography>
              </MenuItem>
            )}
            <MenuItem onClick={handleLogout}>
              <ExitToApp sx={{ mr: 1 }} />
              Выйти
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
