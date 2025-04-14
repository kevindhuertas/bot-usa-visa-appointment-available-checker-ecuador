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
  ListItemSecondaryAction,
  IconButton,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { ProcessData } from './dashboard/App';
import ProcessDetailsDialog from './ProcessDetailsDialog';

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
  // Estados para filtros
  const [emailFilter, setEmailFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  // Estados para el dialogo de detalles
  const [openModal, setOpenModal] = useState(false);
  const [selectedProcess, setSelectedProcess] = useState<ProcessData | null>(null);

  // Manejador de filtro por email
  const handleEmailFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmailFilter(e.target.value);
  };

  // Manejador de filtro por estado
  const handleStatusFilter = (status: 'all' | 'active' | 'inactive') => {
    setStatusFilter(status);
  };

  // Filtrado de procesos
  const filteredProcesses = processes.filter((proc) => {
    const matchesEmail = proc.USER_EMAIL.toLowerCase().includes(emailFilter.toLowerCase());
    const matchesStatus = statusFilter === 'all' || proc.status === statusFilter;
    return matchesEmail && matchesStatus;
  });

  // Abre el dialogo de detalles
  const handleOpenModal = (proc: ProcessData) => {
    setSelectedProcess(proc);
    setOpenModal(true);
  };

  // Cierra el dialogo de detalles
  const handleCloseModal = () => {
    setOpenModal(false);
    setSelectedProcess(null);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Lista de Procesos
      </Typography>

      {/* Filtros */}
      <Box mb={2} display="flex" justifyContent="center" alignItems="center">
        <Box display="flex" justifyContent="space-between" alignItems="center" width="100%">
          <TextField
            label="Filtrar por email"
            variant="outlined"
            size="small"
            value={emailFilter}
            onChange={handleEmailFilterChange}
          />
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
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  // backgroundColor: proc.pid ? 'green' : proc.status == 'active' ? 'gray': 'red',
                  backgroundColor: proc.pid ? 'green' : 'gray',
                  marginRight: 2,
                }}
              />
              <ListItemText
                primary={proc.USER_EMAIL}
                secondary={`Estado: ${proc.status}`}
              />
              <ListItemSecondaryAction>
                {/* Botón para ver detalles (ícono de ojo) */}
                <IconButton onClick={() => handleOpenModal(proc)} color="primary">
                  <VisibilityIcon />
                </IconButton>
                {proc.status === 'active' ? (
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => onStop(proc.USER_EMAIL)}
                    style={{ marginLeft: 8 }}
                  >
                    Detener
                  </Button>
                ) : (
                  <>
                    <Button
                      variant="outlined"
                      onClick={() => onEdit(proc)}
                      style={{ marginLeft: 8, marginRight: 8 }}
                    >
                      Editar
                    </Button>
                    <Button
                      variant="contained"
                      color="error"
                      onClick={() => onDelete(proc.USER_EMAIL)}
                      style={{ marginLeft: 8 }}
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

      {/* Componente de dialogo para ver detalles */}
      <ProcessDetailsDialog
        open={openModal}
        process={selectedProcess}
        onClose={handleCloseModal}
      />
    </Box>
  );
};

export default ProcessList;
