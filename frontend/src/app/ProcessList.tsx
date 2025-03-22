'use client'
import React from 'react';
import { Box, Typography, Paper, Button, Grid } from '@mui/material';
import { ProcessData } from './App';

interface ProcessListProps {
  processes: ProcessData[];
  onEdit: (processData: ProcessData) => void;
  onStop: (userEmail: string) => void;
  onDelete: (userEmail: string) => void;
}

const ProcessList: React.FC<ProcessListProps> = ({ processes, onEdit, onStop, onDelete }) => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Lista de Procesos
      </Typography>
      {processes.length === 0 ? (
        <Typography>No hay procesos creados.</Typography>
      ) : (
        processes.map((proc) => (
          <Paper key={proc.USER_EMAIL} style={{ padding: 16, marginBottom: 16 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={3}>
                <Typography variant="subtitle1">
                  <strong>Correo:</strong> {proc.USER_EMAIL}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Typography variant="subtitle1">
                  <strong>Estado:</strong> {proc.status}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} container spacing={1} justifyContent="flex-end">
                {proc.status === 'active' ? (
                  <Grid item>
                    <Button variant="contained" color="secondary" onClick={() => onStop(proc.USER_EMAIL)}>
                      Detener
                    </Button>
                  </Grid>
                ) : (
                  <>
                    <Grid item>
                      <Button variant="outlined" onClick={() => onEdit(proc)}>
                        Editar
                      </Button>
                    </Grid>
                    <Grid item>
                      <Button variant="contained" color="error" onClick={() => onDelete(proc.USER_EMAIL)}>
                        Eliminar
                      </Button>
                    </Grid>
                  </>
                )}
              </Grid>
            </Grid>
          </Paper>
        ))
      )}
    </Box>
  );
};

export default ProcessList;