'use client'
import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  SelectChangeEvent,
} from '@mui/material';
import { ProcessData } from './App';

interface ProcessFormProps {
  initialData: ProcessData | null;
  onSubmit: (formData: ProcessData) => void;
  onCancel: () => void;
}

const allowedLocations = ['Quito', 'Guayaquil'];
const allowedMonths = ['February', 'March', 'Febrero', 'Marzo'];
const stopMonthOptions = ['May', 'Mayo'];

const ProcessForm: React.FC<ProcessFormProps> = ({ initialData, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<ProcessData>({
    USER_EMAIL: initialData?.USER_EMAIL || '',
    USER_PASSWORD: initialData?.USER_PASSWORD || '',
    allowed_location_to_save_appointment: initialData?.allowed_location_to_save_appointment || [],
    allowed_months_to_save_appointment: initialData?.allowed_months_to_save_appointment || [],
    stop_month: initialData?.stop_month || '',
    status: initialData?.status || 'inactive',
  });

  // Actualizar el estado si initialData cambia (en edición)
  useEffect(() => {
    if (initialData) {
      setFormData({
        USER_EMAIL: initialData.USER_EMAIL,
        USER_PASSWORD: initialData.USER_PASSWORD,
        allowed_location_to_save_appointment: initialData.allowed_location_to_save_appointment,
        allowed_months_to_save_appointment: initialData.allowed_months_to_save_appointment,
        stop_month: initialData.stop_month,
        status: initialData.status,
        pid: initialData.pid,
      });
    }
  }, [initialData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | React.ChangeEvent<{ name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name as string]: value }));
  };

  const selectChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name as string]: value }));
  };

  const handleChipToggle = (field: 'allowed_location_to_save_appointment' | 'allowed_months_to_save_appointment', option: string) => {
    setFormData((prev) => {
      const current = prev[field];
      const updated = current.includes(option)
        ? current.filter((item: string) => item !== option)
        : [...current, option];
      return { ...prev, [field]: updated };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Llama a la función onSubmit con los datos del formulario
    onSubmit(formData);
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      mb={4}
      p={2}
      border={1}
      borderRadius={2}
      borderColor="grey.300"
    >
      <TextField
        fullWidth
        margin="normal"
        label="USER_EMAIL"
        name="USER_EMAIL"
        value={formData.USER_EMAIL}
        onChange={handleChange}
        required
      />
      <TextField
        fullWidth
        margin="normal"
        label="USER_PASSWORD"
        name="USER_PASSWORD"
        type="password"
        value={formData.USER_PASSWORD}
        onChange={handleChange}
        required
      />
      <Box mt={2} mb={2}>
        <InputLabel>Allowed Location to Save Appointment</InputLabel>
        {allowedLocations.map((loc) => (
          <Chip
            key={loc}
            label={loc}
            color={formData.allowed_location_to_save_appointment.includes(loc) ? 'primary' : 'default'}
            onClick={() => handleChipToggle('allowed_location_to_save_appointment', loc)}
            style={{ marginRight: 8, marginTop: 8 }}
          />
        ))}
        {formData.allowed_location_to_save_appointment.length === 0 && (
          <FormHelperText error>Selecciona al menos una ubicación</FormHelperText>
        )}
      </Box>
      <Box mt={2} mb={2}>
        <InputLabel>Allowed Months to Save Appointment</InputLabel>
        {allowedMonths.map((month) => (
          <Chip
            key={month}
            label={month}
            color={formData.allowed_months_to_save_appointment.includes(month) ? 'primary' : 'default'}
            onClick={() => handleChipToggle('allowed_months_to_save_appointment', month)}
            style={{ marginRight: 8, marginTop: 8 }}
          />
        ))}
        {formData.allowed_months_to_save_appointment.length === 0 && (
          <FormHelperText error>Selecciona al menos un mes</FormHelperText>
        )}
      </Box>
      <FormControl fullWidth margin="normal" required>
        <InputLabel>Stop Month</InputLabel>
        <Select
          name="stop_month"
          value={formData.stop_month}
          onChange={selectChange}
        >
          {stopMonthOptions.map((option) => (
            <MenuItem key={option} value={option}>
              {option}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Box mt={2} display="flex" justifyContent="flex-end">
        <Button variant="outlined" onClick={onCancel} style={{ marginRight: 16 }}>
          Cancelar
        </Button>
        <Button variant="contained" color="primary" type="submit">
          {initialData ? 'Actualizar Proceso' : 'Crear Proceso'}
        </Button>
      </Box>
    </Box>
  );
};

export default ProcessForm;
