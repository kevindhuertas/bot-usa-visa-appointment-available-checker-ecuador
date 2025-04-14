"use client";
import React, { useState, useEffect } from "react";
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
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import { ProcessData } from "./dashboard/App";
import { LocalizationProvider, DatePicker } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { format } from "date-fns";

// Utilidad para obtener los nombres de los meses en español
const getMonthName = (date: Date) =>
  date.toLocaleString("es-ES", { month: "long" });

interface ProcessFormProps {
  initialData: ProcessData | null;
  onSubmit: (formData: ProcessData) => void;
  onCancel: () => void;
}

const allowedLocations = ["Quito", "Guayaquil"];

const ProcessForm: React.FC<ProcessFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
}) => {
  // Calcular los 5 meses siguientes (incluyendo el actual)
  const [dynamicAllowedMonths, setDynamicAllowedMonths] = useState<string[]>(
    []
  );
  // Calcular la fecha máxima permitida para el date picker (último día del 5to mes)
  const [maxDate, setMaxDate] = useState<string>("");
  // Control para el DatePicker de días bloqueados
  const [openBlockedDayPicker, setOpenBlockedDayPicker] = useState(false);
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

  useEffect(() => {
    const months: string[] = [];
    const now = new Date();
    for (let i = 0; i < 5; i++) {
      const date = new Date(now.getFullYear(), now.getMonth() + i, 1);
      months.push(getMonthName(date));
    }
    setDynamicAllowedMonths(months);

    // Calcular el último día del 5to mes (índice 4)
    const fifthMonth = new Date(now.getFullYear(), now.getMonth() + 5, 0);
    // Formatear a yyyy-mm-dd
    const yyyy = fifthMonth.getFullYear();
    const mm = String(fifthMonth.getMonth() + 1).padStart(2, "0");
    const dd = String(fifthMonth.getDate()).padStart(2, "0");
    setMaxDate(`${yyyy}-${mm}-${dd}`);
  }, []);

  const [formData, setFormData] = useState<ProcessData>({
    USER_EMAIL: initialData?.USER_EMAIL || "",
    USER_PASSWORD: initialData?.USER_PASSWORD || "",
    allowed_location_to_save_appointment:
      initialData?.allowed_location_to_save_appointment || [],
    allowed_months_to_save_appointment:
      initialData?.allowed_months_to_save_appointment || [],
    stop_month: initialData?.stop_month || "",
    blocked_days: initialData?.blocked_days || [],
    status: initialData?.status || "inactive",
  });

  // Actualizar el estado si initialData cambia (en edición)
  useEffect(() => {
    if (initialData) {
      setFormData({
        USER_EMAIL: initialData.USER_EMAIL,
        USER_PASSWORD: initialData.USER_PASSWORD,
        allowed_location_to_save_appointment:
          initialData.allowed_location_to_save_appointment,
        allowed_months_to_save_appointment:
          initialData.allowed_months_to_save_appointment,
        stop_month: initialData.stop_month,
        blocked_days: initialData.blocked_days || [],
        status: initialData.status,
        pid: initialData.pid,
      });
    }
  }, [initialData]);

  // Al iniciar, si no hay stop_month definido, se pone el 5to mes (último de dynamicAllowedMonths)
  useEffect(() => {
    if (!formData.stop_month && dynamicAllowedMonths.length === 5) {
      setFormData((prev) => ({ ...prev, stop_month: dynamicAllowedMonths[4] }));
    }
  }, [dynamicAllowedMonths, formData.stop_month]);

  const handleChange = (
    e:
      | React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
      | React.ChangeEvent<{ name?: string; value: unknown }>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name as string]: value }));
  };

  const selectChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name as string]: value }));
  };

  const handleChipToggle = (
    field:
      | "allowed_location_to_save_appointment"
      | "allowed_months_to_save_appointment",
    option: string
  ) => {
    setFormData((prev) => {
      const current = prev[field] as string[];
      const updated = current.includes(option)
        ? current.filter((item: string) => item !== option)
        : [...current, option];
      return { ...prev, [field]: updated };
    });
  };

  const handleRemoveDate = (date: string) => {
    setFormData((prev) => ({
      ...prev,
      blocked_days: (prev.blocked_days || []).filter((d) => d !== date),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleOpenDatePicker = (e: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(e.currentTarget);
    setOpenBlockedDayPicker(true);
  };

  // Calcular fecha mínima para el date picker (hoy)
  const today = new Date();
  const yyyyToday = today.getFullYear();
  const mmToday = String(today.getMonth() + 1).padStart(2, "0");
  const ddToday = String(today.getDate()).padStart(2, "0");
  const minDate = `${yyyyToday}-${mmToday}-${ddToday}`;

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
        label="Correo Electrónico"
        name="USER_EMAIL"
        value={formData.USER_EMAIL}
        onChange={handleChange}
        required
      />
      <TextField
        fullWidth
        margin="normal"
        label="Contraseña"
        name="USER_PASSWORD"
        type="password"
        value={formData.USER_PASSWORD}
        onChange={handleChange}
        required
      />
      <Box mt={2} mb={2}>
        <InputLabel shrink>Ubicaciones Permitidas para Agendar Cita</InputLabel>
        {allowedLocations.map((loc) => (
          <Chip
            key={loc}
            label={loc}
            color={
              formData.allowed_location_to_save_appointment.includes(loc)
                ? "primary"
                : "default"
            }
            onClick={() =>
              handleChipToggle("allowed_location_to_save_appointment", loc)
            }
            style={{ marginRight: 8, marginTop: 8 }}
          />
        ))}
        {formData.allowed_location_to_save_appointment.length === 0 && (
          <FormHelperText error>
            Selecciona al menos una ubicación
          </FormHelperText>
        )}
      </Box>
      <Box mt={2} mb={2}>
        <InputLabel shrink>Meses Permitidos para Agendar Cita</InputLabel>
        {dynamicAllowedMonths.map((month) => (
          <Chip
            key={month}
            label={month}
            color={
              formData.allowed_months_to_save_appointment.includes(month)
                ? "primary"
                : "default"
            }
            onClick={() =>
              handleChipToggle("allowed_months_to_save_appointment", month)
            }
            style={{ marginRight: 8, marginTop: 8 }}
          />
        ))}
        {formData.allowed_months_to_save_appointment.length === 0 && (
          <FormHelperText error>Selecciona al menos un mes</FormHelperText>
        )}
      </Box>
      <FormControl fullWidth margin="normal" required>
        <InputLabel shrink>Mes de Corte</InputLabel>
        <Select
          name="stop_month"
          value={formData.stop_month}
          onChange={selectChange}
          disabled
        >
          {dynamicAllowedMonths.map((option) => (
            <MenuItem key={option} value={option}>
              {option}
            </MenuItem>
          ))}
        </Select>
        <FormHelperText>
          Se asigna automáticamente el último mes permitido
        </FormHelperText>
      </FormControl>
      <Box mt={2} mb={2}>
        <InputLabel shrink>Días Bloqueados</InputLabel>
        <Box display="flex" alignItems="center" flexWrap="wrap">
          <Button
            variant="contained"
            color="primary"
            onClick={handleOpenDatePicker}
            style={{ marginTop: 8, marginLeft: 8 }}
          >
            <AddIcon />
          </Button>
          <Box ml={1}></Box>
          {(formData.blocked_days || []).map((date) => (
            <Chip
              key={date}
              label={date}
              onDelete={() => handleRemoveDate(date)}
              style={{ marginRight: 8, marginTop: 8 }}
            />
          ))}
          {/* Campo de texto clickeable para abrir el DatePicker */}
          {/* <TextField
            label="Seleccionar fecha"
            onClick={handleOpenDatePicker}
            fullWidth
            InputProps={{ readOnly: true }}
            style={{ cursor: 'pointer', marginTop: 8 }}
          /> */}
          {/* Botón + con variante 'contained' */}
        </Box>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <DatePicker
            open={openBlockedDayPicker}
            onClose={() => {
              setOpenBlockedDayPicker(false);
              setAnchorEl(null);
            }}
            value={null}
            onChange={(newValue) => {
              if (newValue) {
                const formattedDate = format(newValue, "yyyy-MM-dd");
                if (!formData.blocked_days.includes(formattedDate)) {
                  setFormData((prev) => ({
                    ...prev,
                    blocked_days: [...(prev.blocked_days || []), formattedDate],
                  }));
                }
              }
              setOpenBlockedDayPicker(false);
              setAnchorEl(null);
            }}
            minDate={new Date(minDate)}
            maxDate={new Date(maxDate)}
            slots={{ textField: TextField }}
            slotProps={{
              textField: { style: { display: "none" } },
              popper: { anchorEl: anchorEl },
            }}
          />
        </LocalizationProvider>
      </Box>
      <Box mt={2} display="flex" justifyContent="flex-end">
        <Button
          variant="outlined"
          onClick={onCancel}
          style={{ marginRight: 16 }}
        >
          Cancelar
        </Button>
        <Button variant="contained" color="primary" type="submit">
          {initialData ? "Actualizar Proceso" : "Crear Proceso"}
        </Button>
      </Box>
    </Box>
  );
};

export default ProcessForm;
