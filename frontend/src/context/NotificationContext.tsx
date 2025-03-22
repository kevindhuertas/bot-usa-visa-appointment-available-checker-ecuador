'use client'
// src/contexts/NotificationContext.tsx
import React, { createContext, useState, ReactNode, useContext } from 'react';
import { Snackbar, Alert } from '@mui/material';

type Severity = 'success' | 'info' | 'warning' | 'error';

interface Notification {
  open: boolean;
  message: string;
  severity: Severity;
}

interface NotificationContextProps {
  notify: (message: string, severity?: Severity) => void;
}

const NotificationContext = createContext<NotificationContextProps>({
  notify: () => {},
});

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [notification, setNotification] = useState<Notification>({
    open: false,
    message: '',
    severity: 'info',
  });

  const notify = (message: string, severity: Severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleClose = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  return (
    <NotificationContext.Provider value={{ notify }}>
      {children}
      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleClose} severity={notification.severity} sx={{ width: '100%' }}>
          {notification.message}
        </Alert>
      </Snackbar>
    </NotificationContext.Provider>
  );
};

// Hook para acceder fácilmente al context
export const useNotification = () => useContext(NotificationContext);
