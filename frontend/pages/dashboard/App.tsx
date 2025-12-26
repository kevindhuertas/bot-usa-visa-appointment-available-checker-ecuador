'use client';

import React, { useState, useEffect, useContext } from 'react';
import Button from '../../components/bootstrap/Button';
import ProcessForm, { ProcessData } from './ProcessForm';
import ProcessList from './ProcessList';
import Card, {
	CardActions,
	CardBody,
	CardHeader,
	CardLabel,
	CardTitle,
} from '../../components/bootstrap/Card';
import SubHeader, { SubHeaderLeft, SubHeaderRight } from '../../layout/SubHeader/SubHeader';
import AuthContext from '../../context/authContext';

// A simple console-based replacement for the 'notify' function
const consoleNotify = (message: string, type: 'success' | 'error' | 'info' | 'warning') => {
	if (type === 'error') {
		console.error(`Notify (${type}): ${message}`);
	} else {
		console.log(`Notify (${type}): ${message}`);
	}
	// In a real app, you would integrate a toast library here
};

const App: React.FC = () => {
	const [showForm, setShowForm] = useState<boolean>(false);
	const [processes, setProcesses] = useState<ProcessData[]>([]);
	const [editProcess, setEditProcess] = useState<ProcessData | null>(null);
	const { userData } = useContext(AuthContext);

	const fetchProcesses = async () => {
		try {
			const apiUrl = process.env.NEXT_PUBLIC_BOT_PUBLIC_API_URL;
			// console.info('Fetching processes from:', apiUrl + 'processes');
			const response = await fetch(apiUrl + 'processes?user_id=' + userData.id + '');
			console.log(userData);
			if (!response.ok) {
				consoleNotify(`Error fetching processes: ${response.statusText}`, 'error');
				setProcesses([]);
				return;
			}
			const data: ProcessData[] = await response.json();
			setProcesses(data);
			consoleNotify('Processes fetched successfully', 'success');
		} catch (error) {
			console.error('Network or other error fetching processes:', error);
			consoleNotify(
				`Network or other error: ${
					error instanceof Error ? error.message : 'Unknown error'
				}`,
				'error',
			);
			setProcesses([]);
		}
	};

	useEffect(() => {
		fetchProcesses();
		const interval = setInterval(fetchProcesses, 30000);
		return () => clearInterval(interval);
	}, []);

	// Optional: Fetch wrapper for centralized error notification (using consoleNotify)
	useEffect(() => {
		const originalFetch = window.fetch;
		window.fetch = async (...args) => {
			let response: Response;
			try {
				response = await originalFetch(...args);

				// Check if response is NOT ok (status >= 400)
				if (!response.ok) {
					let errorMsg = `Request failed with status ${response.status}`;
					try {
						// Try to parse error message from server response body
						const cloned = response.clone();
						const data = await cloned.json();
						errorMsg = data.error || data.message || errorMsg; // Use server message if available
					} catch (e) {
						// Ignore if response body isn't JSON or empty
						console.warn('Could not parse error response body as JSON');
					}
					consoleNotify(`${errorMsg}`, 'error');
					// Throw an error to be caught by calling function's catch block if needed
					// throw new Error(errorMsg);
				}
				// No success notification here to avoid spamming console on every successful fetch

				return response; // Return the original response object
			} catch (error) {
				// Handle network errors or errors thrown by the !response.ok block
				const networkErrorMsg = `Fetch error: ${
					error instanceof Error ? error.message : 'Unknown fetch error'
				}`;
				consoleNotify(networkErrorMsg, 'error');
				// Re-throw the error so the calling function's catch block can handle it
				throw error;
			}
		};

		// Cleanup function to restore original fetch
		return () => {
			window.fetch = originalFetch;
		};
	}, []); // Empty dependency array means this runs once on mount and cleans up on unmount

	const handleFormSubmit = async (formData: ProcessData) => {
		try {
			const url = editProcess
				? `${process.env.NEXT_PUBLIC_BOT_PUBLIC_API_URL}processes/${formData.USER_EMAIL}`
				: `${process.env.NEXT_PUBLIC_BOT_PUBLIC_API_URL}processes`;

			const method = editProcess ? 'PUT' : 'POST';

			const response = await fetch(url, {
				method: method,
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(formData),
			});

			// The fetch wrapper already notified on error
			if (response.ok) {
				consoleNotify(
					`Process ${editProcess ? 'updated' : 'created'} successfully`,
					'success',
				);
				setShowForm(false);
				setEditProcess(null);
				fetchProcesses();
			}
		} catch (error) {
			console.error('Error submitting form:', error);
		}
	};

	const handleEdit = (processData: ProcessData) => {
		setEditProcess(processData);
		setShowForm(true);
	};

	const handleStop = async (userEmail: string) => {
		try {
			const response = await fetch(
				`${process.env.NEXT_PUBLIC_BOT_PUBLIC_API_URL}processes/${userEmail}/stop`,
				{ method: 'POST' },
			);
			if (response.ok) {
				consoleNotify(`Stop request sent for ${userEmail}`, 'success');
				fetchProcesses(); // Refresh list to show updated status
			}
			// Error handled by fetch wrapper
		} catch (error) {
			console.error(`Error stopping process ${userEmail}:`, error);
			// consoleNotify likely called by fetch wrapper
		}
	};

	const handleDelete = async (userEmail: string) => {
		// Optional: Add confirmation dialog here
		if (!window.confirm(`Are you sure you want to delete the process for ${userEmail}?`)) {
			return;
		}

		try {
			const response = await fetch(
				`${process.env.NEXT_PUBLIC_BOT_PUBLIC_API_URL}processes/${userEmail}`,
				{ method: 'DELETE' },
			);
			if (response.ok) {
				consoleNotify(`Process for ${userEmail} deleted successfully`, 'success');
				fetchProcesses(); // Refresh list
			}
			// Error handled by fetch wrapper
		} catch (error) {
			console.error(`Error deleting process ${userEmail}:`, error);
			// consoleNotify likely called by fetch wrapper
		}
	};

	return (
		<>
			{/* <SubHeader>
				<SubHeaderLeft></SubHeaderLeft>
				<SubHeaderRight></SubHeaderRight>
			</SubHeader> */}
			<SubHeader className='zindex-dropdown'>
				<SubHeaderLeft>
					<span className='h4 mb-0 fw-bold'>Procesos</span>
					{/* <SubheaderSeparator /> */}
					<div className='text-muted'>
						<small>
							Procesos activos:{' '}
							<span className='text-info fw-bold'>
								{' '}
								{userData.plan?.processProgramationActive} /{' '}
								{userData.plan?.processProgramationAvalaible}
							</span>
						</small>
					</div>
				</SubHeaderLeft>
				{/* <SubHeaderRight>
					<CommonAvatarTeam>
						<strong>Marketing</strong> Team
					</CommonAvatarTeam>
				</SubHeaderRight> */}
			</SubHeader>

			<div className='container mt-4'>
				<Card>
					<CardHeader>
						<CardLabel iconColor='secondary'>
							<CardTitle>Lista de Procesos</CardTitle>
						</CardLabel>
						<CardActions>
							<Button
								color='primary'
								onClick={() => {
									setShowForm(!showForm);
									if (showForm || editProcess) {
										setEditProcess(null);
									}
								}}
								icon={showForm ? undefined : 'Add'}>
								{showForm ? 'Cerrar Formulario' : 'Agregar Nueva Búsqueda'}
							</Button>
						</CardActions>
					</CardHeader>
					<CardBody>
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
						<div className=' '>
							<ProcessList
								processes={processes}
								onEdit={handleEdit}
								onStop={handleStop}
								onDelete={handleDelete}
							/>
						</div>
					</CardBody>
				</Card>
			</div>
		</>
	);
};

export default App;
