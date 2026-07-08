/**
 * Navbar — Top navigation bar with branding.
 */
import React from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import HistoryIcon from '@mui/icons-material/History';
import SettingsIcon from '@mui/icons-material/Settings';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="logo-icon">AI</div>
        <div>
          <h1>AI-CRM HCP</h1>
          <span className="subtitle">Pharma Sales Intelligence</span>
        </div>
      </div>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Tooltip title="Interaction History">
          <IconButton size="small" sx={{ color: 'text.secondary' }}>
            <HistoryIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Notifications">
          <IconButton size="small" sx={{ color: 'text.secondary' }}>
            <NotificationsNoneIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Settings">
          <IconButton size="small" sx={{ color: 'text.secondary' }}>
            <SettingsIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Box
          sx={{
            ml: 1.5,
            width: 34,
            height: 34,
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #00D4AA, #00E4BB)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: '0.8rem',
            color: '#000',
            cursor: 'pointer',
          }}
        >
          MR
        </Box>
      </Box>
    </nav>
  );
}

export default Navbar;
