'use client';

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import { ProcessData } from './App';

interface ProcessListProps {
  processes: ProcessData[];
  onEdit: (processData: ProcessData) => void;
  onStop: (userEmail: string) => void;
  onDelete: (userEmail: string) => void;
}

const ProcessList: React.FC<ProcessListProps> = ({
  processes,
  onEdit,
  onStop,
  onDelete
}) => {
  // Estado para filtrar por email
  const [emailFilter, setEmailFilter] = useState('');
  // Estado para filtrar por status: todos, activos o inactivos
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');

  // Maneja el cambio en el filtro de email
  const handleEmailFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmailFilter(e.target.value);
  };

  // Maneja el filtro de estado
  const handleStatusFilter = (status: 'all' | 'active' | 'inactive') => {
    setStatusFilter(status);
  };

  // Filtramos la lista según el email y el status
  const filteredProcesses = processes.filter((proc) => {
    const matchesEmail = proc.USER_EMAIL.toLowerCase().includes(emailFilter.toLowerCase());
    const matchesStatus = (statusFilter === 'all') || (proc.status === statusFilter);
    return matchesEmail && matchesStatus;
  });

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Lista de Procesos
      </Typography>

      {/* Filtro por email */}
      <Box mb={2} display="flex" justifyContent="center" alignItems="center">
  {/* Contenedor para centrar el contenido */}
  <Box display="flex" justifyContent="space-between" alignItems="center" width="100%" >
    {/* TextField a la izquierda */}
    <TextField
      label="Filtrar por email"
      variant="outlined"
      size="small"
      value={emailFilter}
      onChange={handleEmailFilterChange}
    />

    {/* Chips a la derecha */}
    <Box>
      <Chip
        label="Todos"
        color={statusFilter === 'all' ? 'primary' : 'default'}
        onClick={() => handleStatusFilter('all')}
        style={{ marginLeft: 8 }}
      />
      <Chip
        label="Activos"
        color={statusFilter === 'active' ? 'primary' : 'default'}
        onClick={() => handleStatusFilter('active')}
        style={{ marginLeft: 8 }}
      />
      <Chip
        label="Inactivos"
        color={statusFilter === 'inactive' ? 'primary' : 'default'}
        onClick={() => handleStatusFilter('inactive')}
        style={{ marginLeft: 8 }}
      />
    </Box>
  </Box>
</Box>


 
      {/* Lista de procesos */}
      {filteredProcesses.length === 0 ? (
        <Typography>No hay procesos que coincidan con el filtro.</Typography>
      ) : (
        <List>
          {filteredProcesses.map((proc) => (
            <ListItem key={proc.USER_EMAIL} divider>
              {/* Círculo verde o gris según el pid */}
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: proc.pid ? 'green' : 'gray',
                  marginRight: 2,
                }}
              />

              <ListItemText
                primary={proc.USER_EMAIL}
                secondary={`Estado: ${proc.status}`}
              />

              <ListItemSecondaryAction>
                {proc.status === 'active' ? (
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => onStop(proc.USER_EMAIL)}
                  >
                    Detener
                  </Button>
                ) : (
                  <>
                    <Button
                      variant="outlined"
                      onClick={() => onEdit(proc)}
                      style={{ marginRight: 8 }}
                    >
                      Editar
                    </Button>
                    <Button
                      variant="contained"
                      color="error"
                      onClick={() => onDelete(proc.USER_EMAIL)}
                    >
                      Eliminar
                    </Button>
                  </>
                )}
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
};

export default ProcessList;