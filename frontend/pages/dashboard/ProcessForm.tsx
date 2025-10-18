'use client';

import React, { useState, useEffect, ChangeEvent, FormEvent, useContext } from 'react';
import { format } from 'date-fns';
import FormGroup from '../../components/bootstrap/forms/FormGroup';
import Input from '../../components/bootstrap/forms/Input';
import Button from '../../components/bootstrap/Button';
import Select from '../../components/bootstrap/forms/Select';
import AuthContext from '../../context/authContext';
import Popovers from '../../components/bootstrap/Popovers';
import Icon from '../../components/icon/Icon';

export interface ProcessData {
	pid?: string;
	user_id: string;
	USER_EMAIL: string;
	USER_PASSWORD: string;
	process_id: string;
	allowed_location_to_save_appointment: string[];
	allowed_months_to_save_appointment: string[];
	stop_month: string;
	blocked_days: string[];
	status: 'active' | 'inactive';
}

const getMonthName = (date: Date): string => date.toLocaleString('es-ES', { month: 'long' });

interface ProcessFormProps {
	initialData: ProcessData | null;
	onSubmit: (formData: ProcessData) => void;
	onCancel: () => void;
}

const allowedLocations = ['Quito', 'Guayaquil'];

const ProcessForm: React.FC<ProcessFormProps> = ({ initialData, onSubmit, onCancel }) => {
	const [dynamicAllowedMonths, setDynamicAllowedMonths] = useState<string[]>([]);
	const [maxDate, setMaxDate] = useState<string>('');
	const [selectedBlockedDate, setSelectedBlockedDate] = useState('');
	const { userData, userId } = useContext(AuthContext);

	useEffect(() => {
		const months: string[] = [];
		const now = new Date();
		for (let i = 0; i < 5; i++) {
			const date = new Date(now.getFullYear(), now.getMonth() + i, 1);
			months.push(getMonthName(date));
		}
		setDynamicAllowedMonths(months);
		const fifthMonth = new Date(now.getFullYear(), now.getMonth() + 5, 0);
		setMaxDate(format(fifthMonth, 'yyyy-MM-dd'));
	}, []);

	const [formData, setFormData] = useState<ProcessData>({
		USER_EMAIL: initialData?.USER_EMAIL || '',
		USER_PASSWORD: initialData?.USER_PASSWORD || '',
		process_id: initialData?.process_id || '',
		allowed_location_to_save_appointment:
			initialData?.allowed_location_to_save_appointment || [],
		allowed_months_to_save_appointment: initialData?.allowed_months_to_save_appointment || [],
		stop_month: initialData?.stop_month || '',
		blocked_days: initialData?.blocked_days || [],
		status: initialData?.status || 'inactive',
		user_id: initialData?.user_id || userId,
	});

	useEffect(() => {
		if (initialData) {
			setFormData({
				USER_EMAIL: initialData.USER_EMAIL,
				USER_PASSWORD: initialData.USER_PASSWORD,
				process_id: initialData.process_id,
				allowed_location_to_save_appointment:
					initialData.allowed_location_to_save_appointment,
				allowed_months_to_save_appointment: initialData.allowed_months_to_save_appointment,
				stop_month: initialData.stop_month,
				blocked_days: initialData.blocked_days || [],
				status: initialData.status,
				pid: initialData.pid,
				user_id: initialData.user_id,
			});
		} else {
			setFormData({
				USER_EMAIL: '',
				USER_PASSWORD: '',
				process_id: '',
				allowed_location_to_save_appointment: [],
				allowed_months_to_save_appointment: [],
				stop_month: '',
				blocked_days: [],
				status: 'inactive',
				user_id: userId,
			});
		}
	}, [initialData, userId]);

	useEffect(() => {
		if (!formData.stop_month && dynamicAllowedMonths.length === 5) {
			setFormData((prev) => ({ ...prev, stop_month: dynamicAllowedMonths[4] }));
		}
	}, [dynamicAllowedMonths, formData.stop_month]); // Dependencia actualizada

	const handleChange = (
		e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
	) => {
		const { name, value } = e.target;
		setFormData((prev) => ({ ...prev, [name]: value }));
	};

	// Este handler asume que tu componente Select pasa un evento similar al de un <select> HTML
	// Si pasa directamente el valor, necesitarás ajustarlo así:
	// const handleSelectChange = (newValue: string | string[]) => {
	//    setFormData(prev => ({ ...prev, stop_month: newValue as string })); // Asumiendo que 'name' es fijo o lo manejas diferente
	// }
	const handleSelectChange = (e: ChangeEvent<HTMLSelectElement>) => {
		// Manteniendo el tipo estándar por ahora
		const { name, value } = e.target;
		setFormData((prev) => ({ ...prev, [name]: value }));
	};

	const handleChipToggle = (
		field: keyof Pick<
			ProcessData,
			'allowed_location_to_save_appointment' | 'allowed_months_to_save_appointment'
		>,
		option: string,
	) => {
		setFormData((prev) => {
			const current = prev[field] as string[];
			const updated = current.includes(option)
				? current.filter((item) => item !== option)
				: [...current, option];
			return { ...prev, [field]: updated };
		});
	};

	const handleRemoveDate = (dateToRemove: string) => {
		setFormData((prev) => ({
			...prev,
			blocked_days: (prev.blocked_days || []).filter((d) => d !== dateToRemove),
		}));
	};

	const handleAddBlockedDate = () => {
		if (selectedBlockedDate && !formData.blocked_days.includes(selectedBlockedDate)) {
			setFormData((prev) => ({
				...prev,
				blocked_days: [...(prev.blocked_days || []), selectedBlockedDate].sort(), // Opcional: mantener ordenado
			}));
			setSelectedBlockedDate('');
		}
	};

	const handleSubmit = (e: FormEvent) => {
		e.preventDefault();
		if (formData.allowed_location_to_save_appointment.length === 0) {
			alert('Selecciona al menos una ubicación');
			return;
		}
		if (formData.allowed_months_to_save_appointment.length === 0) {
			alert('Selecciona al menos un mes');
			return;
		}
		onSubmit(formData);
	};

	const minDate = format(new Date(), 'yyyy-MM-dd');

	// Preparar datos para el componente Select
	const monthOptions = dynamicAllowedMonths.map((month) => ({
		value: month,
		text: month.charAt(0).toUpperCase() + month.slice(1), // Capitalizar
	}));

	const stopMonthDescId = 'stop-month-desc'; // ID para aria-describedby

	return (
		<form
			onSubmit={handleSubmit}
			className='mb-4 p-3 border rounded border-light-subtle shadow-sm'>
			<FormGroup className='mb-3' label='Correo Electrónico' id='user-email'>
				<Input
					id='user-email'
					name='USER_EMAIL'
					type='email'
					value={formData.USER_EMAIL}
					onChange={handleChange}
					required
					placeholder='ejemplo@dominio.com'
				/>
			</FormGroup>

			<FormGroup className='mb-3' label='Contraseña' id='user-password'>
				<Input
					id='user-password'
					name='USER_PASSWORD'
					type='password'
					value={formData.USER_PASSWORD}
					onChange={handleChange}
					required
					placeholder='Ingresa la contraseña'
				/>
			</FormGroup>

			<div className='mb-3'>
				<label htmlFor='process-id' className='form-label d-flex align-items-center gap-2'>
					Id del proceso
					<Popovers
						trigger='hover'
						desc={
							<>
								<div className='h6'>{`Al ingresar a la Página de ais.usvisa-info.com/, se debe ingresar al proceso activo con la que se quiere trabajar. Un ejemplo del link: ais.usvisa-info.com/es-ec/niv/schedule/47908012/continue_actions. El ID del proceso seria 47908012 `}</div>
							</>
						}>
						<Icon icon='Info' size='lg' color='success' />
					</Popovers>
				</label>

				<FormGroup id='process-id'>
					<Input
						id='process-id'
						name='process_id'
						type='text'
						value={formData.process_id}
						onChange={handleChange}
						required
						placeholder='Ingresa el ID del proceso'
					/>
				</FormGroup>
			</div>

			{/* <FormGroup className='mb-3' label='Id del proceso' id='process-id'>
				<Input
					id='process-id'
					name='PROCESS_ID'
					type='text'
					value={formData.USER_PASSWORD}
					onChange={handleChange}
					required
					placeholder='Ingresa el ID del proceso'
				/>
			</FormGroup> */}

			<div className='mb-3'>
				<label className='form-label'>Ubicaciones Permitidas</label>
				<div>
					{allowedLocations.map((loc) => (
						<Button
							key={loc}
							type='button'
							color={
								formData.allowed_location_to_save_appointment.includes(loc)
									? 'primary'
									: 'light'
							}
							isOutline={!formData.allowed_location_to_save_appointment.includes(loc)}
							onClick={() =>
								handleChipToggle('allowed_location_to_save_appointment', loc)
							}
							className='me-2 mt-1'
							size='sm'>
							{loc}
						</Button>
					))}
				</div>
				{formData.allowed_location_to_save_appointment.length === 0 && (
					<div className='form-text text-danger mt-1'>
						Selecciona al menos una ubicación
					</div>
				)}
			</div>

			<div className='mb-3'>
				<label className='form-label'>Meses Permitidos</label>
				<div>
					{dynamicAllowedMonths.map((month) => (
						<Button
							key={month}
							type='button'
							color={
								formData.allowed_months_to_save_appointment.includes(month)
									? 'primary'
									: 'light'
							}
							isOutline={!formData.allowed_months_to_save_appointment.includes(month)}
							onClick={() =>
								handleChipToggle('allowed_months_to_save_appointment', month)
							}
							className='me-2 mt-1 text-capitalize'
							size='sm'>
							{month}
						</Button>
					))}
				</div>
				{formData.allowed_months_to_save_appointment.length === 0 && (
					<div className='form-text text-danger mt-1'>Selecciona al menos un mes</div>
				)}
			</div>

			{/* <FormGroup
				className='mb-3'
				label='Mes de Corte'
				id='stop-month'
				formText='Se asigna automáticamente el último mes permitido'
				// formText={stopMonthDescId} // Pasar ID para aria-describedby
			>
				<Select
					id='stop-month'
					name='stop_month'
					ariaLabel='stop month'
					value={formData.stop_month}
					onChange={handleSelectChange} // Asegúrate que este handler es compatible
					disabled
					required
					list={monthOptions} // Pasar la lista formateada
					ariaDescribedby={stopMonthDescId} // Mejorar accesibilidad
				/>
			</FormGroup> */}

			<div className='mb-3'>
				<label htmlFor='blocked-date-picker' className='form-label'>
					Días Bloqueados
				</label>
				<div className='d-flex align-items-start align-items-sm-center flex-column flex-sm-row mb-2'>
					<Input
						type='date'
						id='blocked-date-picker'
						className='form-control me-sm-2 mb-2 mb-sm-0'
						style={{ maxWidth: '200px' }}
						// min={minDate}
						// max={maxDate}
						value={selectedBlockedDate}
						onChange={(e: any) => setSelectedBlockedDate(e.target.value)}
					/>
					<Button
						type='button'
						color='primary'
						icon='Add'
						onClick={handleAddBlockedDate}
						className='flex-shrink-0'
						isDisable={
							!selectedBlockedDate ||
							formData.blocked_days.includes(selectedBlockedDate)
						} // Deshabilitar si no hay fecha o ya está añadida
					>
						Añadir Día
					</Button>
				</div>

				{!!formData.blocked_days?.length && ( // Mejor comprobación
					<div className='mt-2 d-flex flex-wrap gap-2'>
						{formData.blocked_days.map((date) => (
							<div
								key={date}
								className='badge text-bg-primary d-inline-flex align-items-center '>
								<span className='me-2'>{date}</span>
								<Button
									tag='button'
									type='button'
									className='btn-close  p-0'
									aria-label='Remove'
									onClick={() => handleRemoveDate(date)}
									size='sm'
								/>
							</div>
						))}
					</div>
				)}
			</div>

			<div className='mt-4 d-flex justify-content-end gap-2'>
				<Button type='button' isOutline color='light' onClick={onCancel}>
					Cancelar
				</Button>
				<Button color='primary' type='submit'>
					{initialData ? 'Actualizar Proceso' : 'Crear Proceso'}
				</Button>
			</div>
		</form>
	);
};

export default ProcessForm;
