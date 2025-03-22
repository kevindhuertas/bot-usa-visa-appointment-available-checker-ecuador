'use client'
import React, { useState, useEffect } from 'react';
import { Container, Typography, Button, Box } from '@mui/material';
import ProcessForm from './ProcessForm';
import ProcessList from './ProcessList';
import { Constants } from '@/Constants/Contants';

export interface ProcessData {
  USER_EMAIL: string;
  USER_PASSWORD: string;
  allowed_location_to_save_appointment: string[];
  allowed_months_to_save_appointment: string[];
  stop_month: string;
  pid?: number;
  status: 'active' | 'inactive';
}

const App: React.FC = () => {
  const [showForm, setShowForm] = useState<boolean>(false);
  const [processes, setProcesses] = useState<ProcessData[]>([]);
  const [editProcess, setEditProcess] = useState<ProcessData | null>(null);

  // Función para refrescar la lista de procesos
  const fetchProcesses = async () => {
    try {
      const response = await fetch(Constants.BOT_BASE_URL + 'processes');
      if (!response.ok) {
        throw new Error('Error al obtener los procesos');
      }
      const data: ProcessData[] = await response.json();
      setProcesses(data);
    } catch (error) {
      console.error('Error fetching processes:', error);
    }
  };

  useEffect(() => {
    fetchProcesses();
    // Actualización cada 30 segundos
    const interval = setInterval(fetchProcesses, 30000);
    return () => clearInterval(interval);
  }, []);

  // Función para manejar la creación o edición de un proceso
  const handleFormSubmit = async (formData: ProcessData) => {
    try {
      let response: Response;
      if (editProcess) {
        // Editar: PUT /processes/<USER_EMAIL>
        response = await fetch(Constants.BOT_BASE_URL + `processes/${formData.USER_EMAIL}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });
      } else {
        // Crear: POST /processes
        response = await fetch(Constants.BOT_BASE_URL + 'processes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });
      }
      if (response.ok) {
        setShowForm(false);
        setEditProcess(null);
        fetchProcesses();
      } else {
        const err = await response.json();
        console.error('Error:', err);
      }
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  // Función para iniciar el proceso de edición
  const handleEdit = (processData: ProcessData) => {
    setEditProcess(processData);
    setShowForm(true);
  };

  // Funciones para detener y eliminar un proceso
  const handleStop = async (userEmail: string) => {
    try {
      const response = await fetch(Constants.BOT_BASE_URL +`processes/${userEmail}/stop`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchProcesses();
      }
    } catch (error) {
      console.error('Error stopping process:', error);
    }
  };

  const handleDelete = async (userEmail: string) => {
    try {
      const response = await fetch(Constants.BOT_BASE_URL + `processes/${userEmail}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        fetchProcesses();
      }
    } catch (error) {
      console.error('Error deleting process:', error);
    }
  };

  return (
    <Container>
      <Box mt={4} mb={2}>
        <Typography variant="h4" component="h1">
          Administrador de Búsqueda de Citas
        </Typography>
      </Box>
      <Box mb={2}>
        <Button
          variant="contained"
          color="primary"
          onClick={() => {
            setShowForm(!showForm);
            setEditProcess(null);
          }}
        >
          {showForm ? 'Cerrar Formulario' : 'Agregar nueva búsqueda'}
        </Button>
      </Box>
      {showForm && (
        <ProcessForm
          initialData={editProcess}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setShowForm(false);
            setEditProcess(null);
          }}
        />
      )}
      <Box mt={4}>
        <ProcessList
          processes={processes}
          onEdit={handleEdit}
          onStop={handleStop}
          onDelete={handleDelete}
        />
      </Box>
    </Container>
  );
};

export default App;
