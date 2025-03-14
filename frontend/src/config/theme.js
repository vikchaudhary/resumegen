import { createTheme } from '@mui/material/styles';
import { G_COLORS } from './colors';

export const theme = createTheme({
  palette: {
    primary: {
      main: G_COLORS.PRIMARY,
    },
    secondary: {
      main: G_COLORS.SECONDARY,
    },
    background: {
      default: G_COLORS.BACKGROUND,
      paper: G_COLORS.BACKGROUND,
    },
    action: {
      hover: G_COLORS.QUATERNARY,
    }
  },
  components: {
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: G_COLORS.PRIMARY,
          color: G_COLORS.BACKGROUND,
          '& .MuiListItemIcon-root': {
            color: G_COLORS.BACKGROUND,
          },
          '& .MuiListItemText-root': {
            color: G_COLORS.BACKGROUND,
          },
          '& .MuiListItemButton-root:hover': {
            backgroundColor: G_COLORS.SECONDARY,
          }
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        contained: {
          backgroundColor: G_COLORS.PRIMARY,
          '&:hover': {
            backgroundColor: G_COLORS.SECONDARY,
          }
        }
      }
    }
  }
});