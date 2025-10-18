'use client';

import React, { useState, ChangeEvent } from 'react';
// Import your custom components
import ProcessDetailsDialog from './ProcessDetailsDialog'; // Keep this if it's already converted or independent
import Button from '../../components/bootstrap/Button';
import Input from '../../components/bootstrap/forms/Input';
import { ProcessData } from './ProcessForm';
import Alert from '../../components/bootstrap/Alert';
import Card, {
	CardActions,
	CardBody,
	CardHeader,
	CardLabel,
	CardTitle,
} from '../../components/bootstrap/Card';

interface ProcessListProps {
	processes: ProcessData[];
	onEdit: (processData: ProcessData) => void;
	onStop: (userEmail: string) => void;
	onDelete: (userEmail: string) => void;
}

const ProcessList: React.FC<ProcessListProps> = ({ processes, onEdit, onStop, onDelete }) => {
	const [emailFilter, setEmailFilter] = useState('');
	const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
	const [openModal, setOpenModal] = useState(false);
	const [selectedProcess, setSelectedProcess] = useState<ProcessData | null>(null);

	const handleEmailFilterChange = (e: ChangeEvent<HTMLInputElement>) => {
		setEmailFilter(e.target.value);
	};

	const handleStatusFilter = (status: 'all' | 'active' | 'inactive') => {
		setStatusFilter(status);
	};

	const filteredProcesses = processes.filter((proc) => {
		console.log('Filtering process:', proc, proc.status);
		const matchesEmail = proc.USER_EMAIL.toLowerCase().includes(emailFilter.toLowerCase());
		const matchesStatus = statusFilter === 'all' || proc.status === statusFilter;
		return matchesEmail && matchesStatus;
	});

	const handleOpenModal = (proc: ProcessData) => {
		setSelectedProcess(proc);
		setOpenModal(true);
	};

	const handleCloseModal = () => {
		setOpenModal(false);
		setSelectedProcess(null);
	};

	return (
		// Replaced Box with div
		<div>
			<div className='d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-2'>
				<Input
					type='search' // Use search type for semantics
					placeholder='Filtrar por email'
					size='sm' // Corresponds to MUI size="small"
					value={emailFilter}
					onChange={handleEmailFilterChange}
					className='form-control form-control-sm' // Bootstrap classes
				/>
				<div className='d-flex justify-content-start justify-content-md-end gap-2 '>
					{/* Replaced Chip with Button */}
					<Button
						size='sm'
						color={statusFilter === 'all' ? 'primary' : 'light'}
						isOutline={statusFilter !== 'all'}
						onClick={() => handleStatusFilter('all')}>
						Todos
					</Button>
					<Button
						size='sm'
						color={statusFilter === 'active' ? 'primary' : 'light'}
						isOutline={statusFilter !== 'active'}
						onClick={() => handleStatusFilter('active')}>
						Activos
					</Button>
					<Button
						size='sm'
						color={statusFilter === 'inactive' ? 'primary' : 'light'}
						isOutline={statusFilter !== 'inactive'}
						onClick={() => handleStatusFilter('inactive')}>
						Inactivos
					</Button>
				</div>
				{/* Replaced Box with div for filter buttons */}
			</div>
			<div className='table-responsive'>
				<table className='table table-modern mb-0'>
					<thead>
						<tr>
							<th>Proceso</th>
							<th>Localización</th>
							<th></th>
							<th> </th>
						</tr>
					</thead>
					<tbody>
						{filteredProcesses.map((proc) => (
							//Replaced ListItem with div.list-group-item and flex utilities
							<tr key={proc.USER_EMAIL} className=''>
								<td>
									<div className='d-flex align-items-center w-100'>
										<span
											className={`d-inline-block rounded-circle me-2 ${
												proc.pid ? 'bg-success' : 'bg-light'
											}`}
											style={{
												width: '12px',
												height: '12px',
												border: '1px solid #ccc', // borde gris
											}}
											title={
												proc.pid
													? 'Corriendo (con PID)'
													: proc.status === 'active'
													? 'Activo (Esperando)'
													: 'Inactivo'
											}></span>
										<div className='flex-grow-1'>
											<div className='fw-bold'>{proc.USER_EMAIL}</div>
											<small className='text-muted text-capitalize'>
												Estado: {proc.status}
											</small>
										</div>
									</div>
								</td>

								<td>
									<div className='d-flex flex-column'>
										<span className='text-muted'>
											Ubicación:{' '}
											{proc.allowed_location_to_save_appointment.map(
												(loc) => (
													<span
														key={loc}
														className='badge bg-light text-muted light me-1'>
														{loc}{' '}
													</span>
												),
											)}
										</span>
									</div>
								</td>
								<td>
									<div className='d-flex gap-2'>
										<span className='badge bg-success'>Checks: 0</span>
										<span className='badge bg-warning text-dark'>
											Advertencias: 0
										</span>
										<span className='badge bg-danger'>Errores: 0</span>
									</div>
								</td>
								<td>
									{/* Replaced ListItemSecondaryAction with div and flex utilities */}
									<div className='d-flex gap-2  flex-shrink-0 justify-content-end'>
										{/* Replaced IconButton with Button */}
										<Button
											onClick={() => handleOpenModal(proc)}
											color='info' // Using info for view
											isOutline
											size='sm'
											icon='Visibility' // Assuming 'Visibility' matches your Icon component's naming
											title='Ver Detalles' // Tooltip
										>
											{/* Icon inside button if needed, or just use the icon prop */}
											{/* <Icon icon="Visibility" /> */}
										</Button>

										{proc.status === 'active' ? (
											<Button
												color='primary' // Assuming 'primary' is suitable for 'Stop'
												onClick={() => onStop(proc.USER_EMAIL)}
												size='sm'>
												Detener
											</Button>
										) : (
											<>
												<Button
													isOutline
													color='light' // Using secondary for 'Edit'
													onClick={() => onEdit(proc)}
													size='sm'>
													Editar
												</Button>
												<Button
													color='danger' // Corresponds to MUI color="error"
													onClick={() => onDelete(proc.USER_EMAIL)}
													size='sm'>
													Eliminar
												</Button>
											</>
										)}
									</div>
								</td>
							</tr>
						))}
						{/* {userTasks.map((item: any) => (
							<tr key={item.id}>
								<td>
									<div className='d-flex align-items-center'>
										<span
											className={classNames(
												'badge',
												'border border-2 border-light',
												'rounded-circle',
												'bg-success',
												'p-2 me-2',
												`bg-${item.status.color}`,
											)}>
											<span className='visually-hidden'>
												{item.status.name}
											</span>
										</span>
										<span className='text-nowrap'>
											{moment(`${item.date} ${item.time}`).format(
												'MMM Do YYYY, h:mm a',
											)}
										</span>
									</div>
								</td>
								<td></td>
							</tr>
						))} */}
					</tbody>
				</table>
			</div>
			{!filteredProcesses.length && (
				<Alert color='success' isLight icon='Report' className='mt-3'>
					Inicia un proceso
				</Alert>
			)}

			{/* ProcessDetailsDialog remains the same */}
			<ProcessDetailsDialog
				open={openModal}
				proceso={selectedProcess}
				onClose={handleCloseModal}
				// Pass any other required props if the dialog's internals changed
			/>
		</div>
	);
};

export default ProcessList;
