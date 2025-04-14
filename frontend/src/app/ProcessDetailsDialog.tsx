'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Button,
  Paper,
  styled,
  Grid,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import RefreshIcon from '@mui/icons-material/Refresh';
import { Constants } from '@/Constants/Contants';
import { ProcessData } from './dashboard/App';

interface ProcessDetailsDialogProps {
  open: boolean;
  process: ProcessData | null;
  onClose: () => void;
}

const LogDot = styled(Box)(({ theme }) => ({
  width: 10,
  height: 10,
  borderRadius: '50%',
  marginRight: theme.spacing(1),
}));

interface LogCounts {
  errors: number;
  warnings: number;
}

const ProcessDetailsDialog: React.FC<ProcessDetailsDialogProps> = ({ open, process, onClose }) => {
  const [logs, setLogs] = useState<string[]>([]);
  const [loadingLogs, setLoadingLogs] = useState<boolean>(false);

  const logCounts = useMemo<LogCounts>(() => {
    return logs.reduce((acc, log) => {
      const logType = log.split(' - ')[1]?.trim();
      if (logType === 'ERROR') acc.errors++;
      if (logType === 'WARNING') acc.warnings++;
      return acc;
    }, { errors: 0, warnings: 0 });
  }, [logs]);

  const loadLogs = async () => {
    if (!process) return;
    setLoadingLogs(true);
    try {
      const response = await fetch(
        `${Constants.BOT_BASE_URL}logs/${process.USER_EMAIL}?limit=250&offset=0`
      );
      const data = await response.ok ? await response.json() : { logs: [] };
      setLogs(data.logs || []);
    } catch {
      setLogs(['Error al cargar logs']);
    } finally {
      setLoadingLogs(false);
    }
  };

  useEffect(() => {
    if (open && process) loadLogs();
    else setLogs([]);
  }, [open, process]);

  const getLogColor = (log: string) => {
    const logType = log.split(' - ')[1]?.trim();
    switch (logType) {
      case 'ERROR': return '#ff4444';
      case 'WARNING': return '#ff9100';
      default: return 'inherit';
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>
        Detalles
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{
            position: "absolute",
            right: 8,
            top: 8,
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent dividers>
      {process && (
          <Box mb={2}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="subtitle1">
                  <strong>Usuario:</strong> {process.USER_EMAIL}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle1">
                  <strong>Estado:</strong> {process.status}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle1">
                  <strong>Ubicaciones:</strong>{" "}
                  {process.allowed_location_to_save_appointment.join(', ')}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle1">
                  <strong>Meses:</strong>{" "}
                  {process.allowed_months_to_save_appointment.join(', ')}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle1">
                  <strong>Días bloqueados:</strong>{" "}
                  {process.blocked_days.join(', ')}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle1">
                  <strong>Stop Month:</strong> {process.stop_month}
                </Typography>
              </Grid>
            </Grid>
          </Box>
        )}
        <Box>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6">Logs</Typography>
            <Box display="flex" alignItems="center" gap={3}>
              <Box display="flex" alignItems="center">
                <LogDot bgcolor="#ff4444" />
                <Typography variant="body2">{logCounts.errors}</Typography>
              </Box>
              <Box display="flex" alignItems="center">
                <LogDot bgcolor="#ff9100" />
                <Typography variant="body2">{logCounts.warnings}</Typography>
              </Box>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadLogs}
                disabled={loadingLogs}
              >
                Actualizar
              </Button>
            </Box>
          </Box>

          {loadingLogs ? (
            <Typography>Cargando logs...</Typography>
          ) : (
            <Paper variant="outlined" sx={{ maxHeight: 400, overflowY: "auto", p: 1 }}>
              {logs.map((log, index) => (
                <Typography
                  key={index}
                  variant="body2"
                  component="pre"
                  sx={{
                    fontFamily: "monospace",
                    color: getLogColor(log),
                    margin: 0,
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {log}
                </Typography>
              ))}
            </Paper>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} color="primary">Cerrar</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProcessDetailsDialog;