'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { ProcessData } from './ProcessForm';
import Button from '../../components/bootstrap/Button';

interface ProcessDetailsDialogProps {
	open: boolean;
	proceso: ProcessData | null;
	onClose: () => void;
}

interface LogCounts {
	errors: number;
	warnings: number;
}

// Helper component for the colored dot, using span and inline style
const LogDot: React.FC<{ color: string }> = ({ color }) => (
	<span
		className='d-inline-block rounded-circle me-1'
		style={{ width: '10px', height: '10px', backgroundColor: color }}></span>
);

const ProcessDetailsDialog: React.FC<ProcessDetailsDialogProps> = ({ open, proceso, onClose }) => {
	const [logs, setLogs] = useState<string[]>([]);
	const [loadingLogs, setLoadingLogs] = useState<boolean>(false);

	const logCounts = useMemo<LogCounts>(() => {
		return logs.reduce(
			(acc, log) => {
				const logType = log.split(' - ')[1]?.trim();
				if (logType === 'ERROR') acc.errors++;
				if (logType === 'WARNING') acc.warnings++;
				return acc;
			},
			{ errors: 0, warnings: 0 },
		);
	}, [logs]);

	const loadLogs = async () => {
		if (!process) return;
		setLoadingLogs(true);
		setLogs([]); // Clear previous logs immediately
		try {
			const response = await fetch(
				`${process.env.NEXT_PUBLIC_BOT_PUBLIC_API_URL}logs/${proceso?.USER_EMAIL}?limit=250&offset=0`,
			);
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const data = await response.json();
			setLogs(data.logs || []);
		} catch (error) {
			console.error('Error loading logs:', error);
			setLogs([
				`Error al cargar logs: ${
					error instanceof Error ? error.message : 'Error desconocido'
				}`,
			]);
		} finally {
			setLoadingLogs(false);
		}
	};

	useEffect(() => {
		if (open && process) {
			loadLogs();
		} else {
			setLogs([]);
			setLoadingLogs(false);
		}
	}, [open, proceso?.USER_EMAIL]);

	const getLogColor = (log: string): string => {
		const logType = log.split(' - ')[1]?.trim();
		switch (logType) {
			case 'ERROR':
				return '#dc3545'; // Bootstrap danger color
			case 'WARNING':
				return '#ffc107'; // Bootstrap warning color
			default:
				return 'inherit'; // Default text color
		}
	};

	// Render nothing if not open
	if (!open) {
		return null;
	}

	return (
		// Bootstrap Modal Structure
		<>
			{/* Backdrop */}
			<div className='modal-backdrop fade show'></div>

			{/* Modal Dialog */}
			<div
				className='modal fade show'
				style={{ display: 'block' }} // Force display when open
				tabIndex={-1}
				role='dialog'
				aria-modal='true'
				onClick={onClose} // Optional: Close on backdrop click
			>
				<div
					className='modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable' // Large, centered, scrollable body
					role='document'
					onClick={(e) => e.stopPropagation()} // Prevent modal close when clicking inside dialog
				>
					<div className='modal-content'>
						{/* Modal Header */}
						<div className='modal-header'>
							<h5 className='modal-title'>Detalles del Proceso</h5>
							{/* Use Button component for close */}
							<Button
								type='button'
								className='btn-close' // Bootstrap close button class
								onClick={onClose}
								aria-label='Close'
							/>
						</div>

						{/* Modal Body */}
						<div className='modal-body'>
							{/* Process Details Section */}
							{proceso && (
								<div className='mb-4'>
									{' '}
									{/* Added bottom margin */}
									{/* Bootstrap Grid */}
									<div className='row g-2'>
										{' '}
										{/* Added gutter */}
										<div className='col-md-6'>
											<p className='mb-1'>
												{' '}
												{/* Reduced margin */}
												<strong>Usuario:</strong> {proceso.USER_EMAIL}
											</p>
										</div>
										<div className='col-md-6'>
											<p className='mb-1 text-capitalize'>
												{' '}
												{/* Reduced margin */}
												<strong>Estado:</strong> {proceso.status}
											</p>
										</div>
										<div className='col-md-6'>
											<p className='mb-1'>
												{' '}
												{/* Reduced margin */}
												<strong>Ubicaciones:</strong>{' '}
												{proceso.allowed_location_to_save_appointment.join(
													', ',
												)}
											</p>
										</div>
										<div className='col-md-6'>
											<p className='mb-1 text-capitalize'>
												{' '}
												{/* Reduced margin */}
												<strong>Meses:</strong>{' '}
												{proceso.allowed_months_to_save_appointment.join(
													', ',
												)}
											</p>
										</div>
										<div className='col-md-6'>
											<p className='mb-1'>
												{' '}
												{/* Reduced margin */}
												<strong>Días bloqueados:</strong>{' '}
												{proceso.blocked_days &&
												proceso.blocked_days.length > 0 ? (
													proceso.blocked_days.join(', ')
												) : (
													<span className='text-muted'>Ninguno</span>
												)}
											</p>
										</div>
										<div className='col-md-6'>
											<p className='mb-1 text-capitalize'>
												{' '}
												{/* Reduced margin */}
												<strong>Mes Corte:</strong> {proceso.stop_month}
											</p>
										</div>
									</div>
								</div>
							)}

							{/* Logs Section */}
							<div>
								{/* Logs Header */}
								<div className='d-flex flex-column flex-sm-row justify-content-between align-items-sm-center mb-2 gap-2'>
									<h6>Logs Recientes (Últimos 250)</h6>
									<div className='d-flex align-items-center gap-3'>
										{/* Log Counts */}
										<div className='d-flex align-items-center' title='Errores'>
											<LogDot color='#dc3545' />
											<span className='small'>{logCounts.errors}</span>
										</div>
										<div
											className='d-flex align-items-center'
											title='Advertencias'>
											<LogDot color='#ffc107' />
											<span className='small'>{logCounts.warnings}</span>
										</div>
										{/* Refresh Button */}
										<Button
											isOutline
											color='secondary' // Secondary outline for refresh
											icon='Refresh' // Use icon prop
											onClick={loadLogs}
											isDisable={loadingLogs}
											size='sm'>
											{loadingLogs ? 'Cargando...' : 'Actualizar'}
										</Button>
									</div>
								</div>

								{/* Logs Content Area */}
								{loadingLogs && !logs.length ? ( // Show loading only if logs aren't already loaded
									<p className='text-muted'>Cargando logs...</p>
								) : (
									// Replaced Paper with div styled with Bootstrap classes
									<div
										className='border p-2 bg-light overflow-auto font-monospace' // Styling for log container
										style={{ maxHeight: '300px', fontSize: '0.8rem' }} // Max height and smaller font
									>
										{logs.length > 0 ? (
											logs.map((log, index) => (
												// Use pre for preserving whitespace and line breaks
												<pre
													key={index}
													style={{
														color: getLogColor(log),
														margin: 0, // Remove default margin
														whiteSpace: 'pre-wrap', // Wrap long lines
														wordBreak: 'break-word', // Break long words
													}}>
													{log}
												</pre>
											))
										) : (
											<p className='text-muted m-0'>
												No hay logs para mostrar.
											</p> // Message when no logs
										)}
									</div>
								)}
							</div>
						</div>

						{/* Modal Footer */}
						<div className='modal-footer'>
							<Button isOutline color='secondary' onClick={onClose}>
								{' '}
								{/* Outlined secondary */}
								Cerrar
							</Button>
						</div>
					</div>
				</div>
			</div>
		</>
	);
};

export default ProcessDetailsDialog;
