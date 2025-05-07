'use client';

import React, { useState, ChangeEvent } from 'react';
// Import your custom components
import ProcessDetailsDialog from './ProcessDetailsDialog'; // Keep this if it's already converted or independent
import Button from '../../components/bootstrap/Button';
import Input from '../../components/bootstrap/forms/Input';
import { ProcessData } from './ProcessForm';

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
			{/* Filters Row - Replaced Box with div and flex utilities */}
			<div className='d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-3 gap-2'>
				{/* Replaced TextField with Input */}
				<Input
					type='search' // Use search type for semantics
					placeholder='Filtrar por email'
					size='sm' // Corresponds to MUI size="small"
					value={emailFilter}
					onChange={handleEmailFilterChange}
					className='form-control form-control-sm' // Bootstrap classes
				/>
				{/* Replaced Box with div for filter buttons */}
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
			</div>

			{/* Process List */}
			{filteredProcesses.length === 0 ? (
				// Replaced Typography with p
				<p className='text-muted'>No hay procesos que coincidan con el filtro.</p>
			) : (
				// Replaced List with div.list-group
				<div className='list-group'>
					{filteredProcesses.map((proc) => (
						// Replaced ListItem with div.list-group-item and flex utilities
						<div
							key={proc.USER_EMAIL}
							className='list-group-item d-flex flex-column flex-sm-row align-items-sm-center justify-content-between'>
							<div className='d-flex align-items-center mb-2 mb-sm-0 me-sm-2'>
								{/* Replaced Box (status dot) with span */}
								<span
									className={`d-inline-block rounded-circle me-2 ${
										proc.pid ? 'bg-success' : 'bg-light'
									}`}
									style={{ width: '12px', height: '12px' }}
									title={
										proc.pid
											? 'Corriendo (con PID)'
											: proc.status === 'active'
											? 'Activo (Esperando)'
											: 'Inactivo'
									} // Add title for clarity
								></span>
								{/* Replaced ListItemText with div */}
								<div className='flex-grow-1'>
									<div className='fw-bold'>{proc.USER_EMAIL}</div>
									<small className='text-muted text-capitalize'>
										Estado: {proc.status}
									</small>
								</div>
							</div>

							{/* Replaced ListItemSecondaryAction with div and flex utilities */}
							<div className='d-flex gap-2 align-items-center flex-shrink-0 justify-content-end'>
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
						</div>
					))}
				</div>
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
