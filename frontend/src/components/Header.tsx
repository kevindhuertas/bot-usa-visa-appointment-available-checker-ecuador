// src/components/Header.tsx
import React, { useState } from 'react';
import { AppBar, Toolbar, IconButton, Menu, MenuItem, Box } from '@mui/material';
import { AccountCircle, Brightness4, Brightness7 } from '@mui/icons-material';
import Image from 'next/image';
import { useAuth } from '../context/AuthContext';
import { Constants } from '@/Constants/Contants';
import { useThemeContext } from '@/context/MuiThemeProvider';

interface HeaderProps {
  toggleDarkMode?: () => void;
  darkMode?: boolean;
}

const Header: React.FC<HeaderProps> = () => {
  const { user, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useThemeContext();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    handleMenuClose();
  };

  return (
    <AppBar position="static">
      <Toolbar>
        {/* Logo a la izquierda */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <Image src={Constants.APP_LOGO} alt="App Logo" width={40} height={40} />
          {/* <Typography variant="h6" sx={{ ml: 1 }}>
            Mi App
          </Typography> */}
        </Box>
        {/* Botón para alternar dark mode */}
        <IconButton color="default" onClick={toggleDarkMode}>
          {darkMode ? <Brightness7 /> : <Brightness4 />}
        </IconButton>
        {/* Botón de usuario que despliega el menú */}
        <IconButton color="default" onClick={handleMenuOpen}>
          <AccountCircle />
        </IconButton>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          sx={{ minWidth: "400px" }}
        >
          <MenuItem disabled>{user?.email || 'Usuario'}</MenuItem>
          <MenuItem onClick={handleLogout}>Salir </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
