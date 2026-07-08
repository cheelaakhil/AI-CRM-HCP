/**
 * MUI Theme — Premium pharma-themed design with dark mode.
 */
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6C63FF',
      light: '#8B83FF',
      dark: '#4A42CC',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#00D4AA',
      light: '#33DDBB',
      dark: '#00A888',
      contrastText: '#000000',
    },
    background: {
      default: '#0A0E1A',
      paper: '#111827',
    },
    surface: {
      main: '#1A1F2E',
      light: '#242B3D',
    },
    success: {
      main: '#10B981',
    },
    warning: {
      main: '#F59E0B',
    },
    error: {
      main: '#EF4444',
    },
    text: {
      primary: '#F1F5F9',
      secondary: '#94A3B8',
      disabled: '#64748B',
    },
    divider: 'rgba(148, 163, 184, 0.12)',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h5: {
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h6: {
      fontWeight: 600,
    },
    subtitle1: {
      fontWeight: 500,
      color: '#94A3B8',
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          padding: '10px 24px',
          fontSize: '0.875rem',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(108, 99, 255, 0.3)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #6C63FF 0%, #8B83FF 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #5A52E0 0%, #7A73FF 100%)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(148, 163, 184, 0.08)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
            '& fieldset': {
              borderColor: 'rgba(148, 163, 184, 0.15)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(108, 99, 255, 0.4)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#6C63FF',
            },
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          borderRadius: 10,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          border: '1px solid rgba(148, 163, 184, 0.08)',
        },
      },
    },
  },
});

export default theme;
