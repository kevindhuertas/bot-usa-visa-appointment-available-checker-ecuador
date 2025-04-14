'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  IconButton,
  InputAdornment,
  TextField,
  Typography,
  Paper
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { useAuth } from '../../context/AuthContext';
import { Constants } from '@/Constants/Contants';

const LoginPage: React.FC = () => {
  const router = useRouter();
  const { login } = useAuth();

  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [remember, setRemember] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [showReset, setShowReset] = useState<boolean>(false);
  const [resetEmail, setResetEmail] = useState<string>('');
  const [resetMessage, setResetMessage] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      await login(email, password);
      router.push('/dashboard'); // Redirige al dashboard tras el login exitoso
       // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message);
    }
    setLoading(false);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    handleLogin();
  };

  // Funcionalidad simulada para resetear contraseña
  const handleResetPassword = async () => {
    setResetMessage(
      'Se ha enviado la solicitud. El administrador se contactará lo antes posible para resetear la contraseña.'
    );
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box
    sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, rgba(152, 157, 255, 0.8), rgba(68, 162, 255, 0.8))',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      p: 2,
      position: 'relative',
      overflow: 'hidden',

    }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 400,
          width: '100%',
          borderRadius: 2,
          textAlign: 'center',
        
        }}
      >
        <Box sx={{ mb: 2 }}>
          <img src={Constants.APP_LOGO} alt="App Logo" style={{ maxWidth: '100%', maxHeight: '40px' }} />
        </Box>
        {!showReset ? (
          <form onSubmit={handleSubmit}>
            <Typography variant="h5" sx={{ mb: 2 }}>
              Iniciar Sesión
            </Typography>
            <TextField
              label="Correo"
              variant="outlined"
              fullWidth
              sx={{ mb: 2 }}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              label="Contraseña"
              variant="outlined"
              fullWidth
              type={showPassword ? 'text' : 'password'}
              sx={{ mb: 2 }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleTogglePasswordVisibility} edge="end">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  color="primary"
                />
              }
              label="Recordar usuario"
              labelPlacement="start" // Ubica el label a la izquierda del checkbox
              sx={{ mb: 2, justifyContent: 'flex-start' }}
            />
            {error && (
              <Typography color="error" sx={{ mb: 2 }}>
                {error}
              </Typography>
            )}
            <Button variant="contained" fullWidth type="submit" disabled={loading}>
              {loading ? 'Iniciando...' : 'Iniciar Sesión'}
            </Button>
            <Button
              variant="text"
              fullWidth
              onClick={() => setShowReset(true)}
              sx={{ mt: 1 }}
            >
              ¿Olvidaste tu contraseña?
            </Button>
          </form>
        ) : (
          <>
            <Box display="flex" alignItems="center" sx={{ mb: 2 }}>
              <IconButton onClick={() => setShowReset(false)}>
                <ArrowBackIcon />
              </IconButton>
              <Typography variant="h6">Resetear Contraseña</Typography>
            </Box>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Para resetear la contraseña, contacta con el administrador vía SMS o WhatsApp al número{" "}
              <strong>+593 987232113</strong> o escribe al correo <strong>adelantar.info@gmail.com</strong>.
            </Typography>
            <TextField
              label="Tu correo"
              variant="outlined"
              fullWidth
              sx={{ mb: 2 }}
              value={resetEmail}
              onChange={(e) => setResetEmail(e.target.value)}
            />
            <Button variant="contained" fullWidth onClick={handleResetPassword}>
              Enviar solicitud
            </Button>
            {resetMessage && (
              <Typography variant="body2" color="primary" sx={{ mt: 2 }}>
                {resetMessage}
              </Typography>
            )}
          </>
        )}
      </Paper>
    </Box>
  );
};

export default LoginPage;
