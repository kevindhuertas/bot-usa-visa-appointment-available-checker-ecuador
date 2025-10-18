'use client';

import type { NextPage } from 'next';
import { GetStaticProps } from 'next';
import useTourStep from '../../hooks/useTourStep';
import useDarkMode from '../../hooks/useDarkMode';
import { useRouter } from 'next/router';
import { getUserDataWithId } from '../../common/data/userDummyData';
import { useContext, useState } from 'react';
import Chart, { IChartOptions } from '../../components/extras/Chart';
import COLORS from '../../common/data/enumColors';
import PageWrapper from '../../layout/PageWrapper/PageWrapper';
import Head from 'next/head';
import SubHeader, {
	SubHeaderLeft,
	SubHeaderRight,
	SubheaderSeparator,
} from '../../layout/SubHeader/SubHeader';
import Button from '../../components/bootstrap/Button';
import { demoPagesMenu } from '../../menu';
import Page from '../../layout/Page/Page';
import Card, {
	CardActions,
	CardBody,
	CardHeader,
	CardLabel,
	CardTitle,
} from '../../components/bootstrap/Card';
import Avatar from '../../components/Avatar';
import Icon from '../../components/icon/Icon';

import moment from 'moment';
import classNames from 'classnames';
import Dropdown, {
	DropdownItem,
	DropdownMenu,
	DropdownToggle,
} from '../../components/bootstrap/Dropdown';

import { priceFormat } from '../../helpers/helpers';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import Badge from '../../components/bootstrap/Badge';
import Alert from '../../components/bootstrap/Alert';
import AuthContext from '../../context/authContext';
import { text } from 'stream/consumers';

const Id: NextPage = () => {
	useTourStep(19);
	const { darkModeStatus } = useDarkMode();

	const router = useRouter();
	const { id } = router.query;

	// const data = getUserDataWithId(String(id));
	const { userData: data } = useContext(AuthContext);

	const [dayHours] = useState<IChartOptions>({
		series: [
			{
				data: [8, 12, 15, 20, 15, 22, 9],
			},
		],
		options: {
			colors: [String(process.env.NEXT_PUBLIC_SUCCESS_COLOR)],
			chart: {
				type: 'radar',
				width: 200,
				height: 200,
				sparkline: {
					enabled: true,
				},
			},
			xaxis: {
				categories: [
					'Monday',
					'Tuesday',
					'Wednesday',
					'Thursday',
					'Friday',
					'Saturday',
					'Sunday',
				],
				// convertedCatToNumeric: false,
			},
			tooltip: {
				theme: 'dark',
				fixed: {
					enabled: false,
				},
				x: {
					show: true,
				},
				y: {
					title: {
						formatter(seriesName) {
							return 'Hours';
						},
					},
				},
			},
			stroke: {
				curve: 'smooth',
				width: 2,
			},
			plotOptions: {
				radar: {
					polygons: {
						strokeColors: `${COLORS.SUCCESS.code}50`,
						strokeWidth: '1',
						connectorColors: `${COLORS.SUCCESS.code}50`,
					},
				},
			},
		},
	});

	// const userTasks = dummyEventsData.filter((f) => f.assigned.username === data?.username);
	const userTasks: any[] = [];

	return (
		<PageWrapper>
			<Head>
				<title>{`${data?.name} ${data?.surname}`}</title>
			</Head>
			<SubHeader>
				{/* <SubHeaderLeft>
					<Button
						color='info'
						isLink
						icon='ArrowBack'
						tag='a'
						to={`../../${demoPagesMenu.appointment.subMenu.employeeList.path}`}>
						Back to List
					</Button>
					<SubheaderSeparator />
					<CommonAvatarTeam isAlignmentEnd>
						<strong>Sports</strong> Team
					</CommonAvatarTeam>
				</SubHeaderLeft> */}
				<SubHeaderRight>
					<span className='text-muted fst-italic me-2'>Last update:</span>
					<span className='fw-bold'>13 hours ago</span>
				</SubHeaderRight>
			</SubHeader>
			<Page>
				<div className='pt-3 pb-5 d-flex align-items-center'>
					<span className='display-4 fw-bold me-3'>{`${data?.name} ${data?.surname}`}</span>
					<span className='border border-success border-2 text-success fw-bold px-3 py-2 rounded'>
						{data?.position}
					</span>
				</div>
				<div className='row'>
					<div className='col-lg-4'>
						<Card className='shadow-3d-info'>
							<CardBody>
								<div className='row g-5'>
									<div className='col-12 d-flex justify-content-center'>
										<Avatar
											src={data?.src}
											color={data?.color}
											isOnline={data?.isOnline}
										/>
									</div>
									<div className='col-12'>
										<div className='row g-2'>
											<div className='col-12'>
												<div className='d-flex align-items-center'>
													<div className='flex-shrink-0'>
														<Icon icon='Mail' size='3x' color='info' />
													</div>
													<div className='flex-grow-1 ms-3'>
														<div className='fw-bold fs-5 mb-0'>
															{`${data?.email}`}
														</div>
														<div className='text-muted'>
															Email Address
														</div>
													</div>
												</div>
											</div>
											<div className='col-12'>
												<div className='d-flex align-items-center'>
													<div className='flex-shrink-0'>
														<Icon icon='Tag' size='3x' color='info' />
													</div>
													<div className='flex-grow-1 ms-3'>
														<div className='fw-bold fs-5 mb-0'>
															{`@${data?.username}`}
														</div>
														{/* <div className='text-muted'>
															Social name
														</div> */}
													</div>
												</div>
											</div>
										</div>
									</div>
								</div>
							</CardBody>
						</Card>
						{/* <Card>
							<CardHeader>
								<CardLabel icon='Stream' iconColor='warning'>
									<CardTitle>Skill</CardTitle>
								</CardLabel>
							</CardHeader>
							<CardBody>
								{data?.services ? (
									<div className='row g-2'>
										{data?.services.map((service: any) => (
											<div key={service.name} className='col-auto'>
												<Badge
													isLight
													color={service.color}
													className='px-3 py-2'>
													<Icon
														icon={service.icon}
														size='lg'
														className='me-1'
													/>
													{service.name}
												</Badge>
											</div>
										))}
									</div>
								) : (
									<div className='row'>
										<div className='col'>
											<Alert
												color='warning'
												isLight
												icon='Report'
												className='mb-0'>
												No results to show
											</Alert>
										</div>
									</div>
								)}
							</CardBody>
						</Card> */}
						<Card>
							<CardHeader>
								<CardLabel icon='ShowChart' iconColor='secondary'>
									<CardTitle>Plan</CardTitle>
								</CardLabel>
								<CardActions>
									<span className='text-muted fst-italic me-2'>
										Expiración del plan:
									</span>
									<span className='fw-bold'> {data?.plan?.planExpiration}</span>
									{/* Only in <strong>{moment().format('MMM')}</strong>. */}
								</CardActions>
							</CardHeader>
							<CardBody>
								<div className='row g-4 align-items-center '>
									<div className='col-xl-6'>
										<div
											className={classNames(
												'd-flex align-items-center rounded-2 p-3 align-items-stretch ',
												{
													'bg-l10-warning': !darkModeStatus,
													'bg-lo25-warning': darkModeStatus,
												},
											)}>
											<div className='flex-shrink-0'>
												<Icon icon='DoneAll' size='3x' color='warning' />
											</div>
											<div className='flex-grow-1 ms-3'>
												<div className='fw-bold fs-3 mb-0'>
													{data?.checksCount}
												</div>
												<div className='text-muted mt-n2 '>
													Chequeos <br />
													Totales
												</div>
											</div>
										</div>
									</div>
									<div className='col-xl-6'>
										<div
											className={classNames(
												'd-flex align-items-center rounded-2 p-3',
												{
													'bg-l10-primary': !darkModeStatus,
													'bg-lo25-primary': darkModeStatus,
												},
											)}>
											<div className='flex-shrink-0'>
												<Icon
													icon='Celebration'
													size='3x'
													color='primary'
												/>
											</div>
											<div className='flex-grow-1 ms-3'>
												<div className='fw-bold fs-3 mb-0'>
													{data?.plan?.processProgramationAvalaible}
												</div>
												<div className='text-muted mt-n2 '>
													Max procesos activos
												</div>
											</div>
										</div>
									</div>
									<div className='col-xl-6'>
										<div
											className={classNames(
												'd-flex align-items-center rounded-2 p-3 ',
												{
													'bg-l10-info': !darkModeStatus,
													'bg-lo25-info': darkModeStatus,
												},
											)}>
											<div className='flex-shrink-0'>
												<Icon icon='Savings' size='3x' color='info' />
											</div>
											<div className='flex-grow-1 ms-3'>
												<div className='fw-bold fs-3 mb-0'>
													{data?.processfinished}
												</div>
												<div className='text-muted mt-n2 '>
													Procesos finalizados
												</div>
											</div>
										</div>
									</div>
									<div className='col-xl-6'>
										<div
											className={classNames(
												'd-flex align-items-center rounded-2 p-3',
												{
													'bg-l10-success': !darkModeStatus,
													'bg-lo25-success': darkModeStatus,
												},
											)}>
											<div className='flex-shrink-0'>
												<Icon icon='Timer' size='3x' color='success' />
											</div>
											<div className='flex-grow-1 ms-3'>
												<div className='fw-bold fs-3 mb-0'>
													{data?.plan?.processChekingAvalaible}
												</div>
												<div className='text-muted mt-n2 '>
													Procesos Disponibles
												</div>
											</div>
										</div>
									</div>
								</div>
							</CardBody>
						</Card>
					</div>
					<div className='col-lg-8'>
						<Card className='shadow-3d-primary'>
							<CardHeader>
								<CardLabel icon='Summarize' iconColor='success'>
									<CardTitle tag='h4' className='h5'>
										<div className='d-flex gap-2'>
											Estadísticas{'   '}
											<span className='text-muted fst-italic fw-light ml-4'></span>
										</div>
									</CardTitle>
								</CardLabel>
								<CardActions>
									<Dropdown>
										<DropdownToggle>
											<Button color='info' icon='Compare' isLight>
												Últimos
												<strong>
													{/* {Number(moment().format('YYYY')) - 1} */}
													{' 30 días'}
												</strong>
												.
											</Button>
										</DropdownToggle>
										<DropdownMenu isAlignmentEnd size='sm'>
											<DropdownItem>
												<span>{' 30 días'}</span>
											</DropdownItem>
											{/* <DropdownItem>
												<span>{Number(moment().format('YYYY')) - 3}</span>
											</DropdownItem> */}
										</DropdownMenu>
									</Dropdown>
								</CardActions>
							</CardHeader>
							<CardBody>
								<div className='row g-4'>
									<div className='col-md-6'>
										<Card
											className={`bg-l${
												darkModeStatus ? 'o25' : '25'
											}-warning bg-l${
												darkModeStatus ? 'o50' : '10'
											}-warning-hover transition-base rounded-2 mb-4`}
											shadow='sm'>
											<CardHeader className='bg-transparent'>
												<CardLabel>
													<CardTitle tag='h4' className='h5'>
														Chequeos
													</CardTitle>
												</CardLabel>
											</CardHeader>
											<CardBody>
												<div className='d-flex align-items-center pb-3'>
													<div className='flex-shrink-0'>
														<Icon
															icon='DoneAll'
															size='3x'
															color='warning'
														/>
													</div>
													<div className='flex-grow-1 ms-3'>
														<div className='fw-bold fs-3 mb-0'>
															<div className='fw-bold fs-3 mb-0'>
																{data?.checksCount}
															</div>
														</div>
														<div className='text-muted'>
															Últimos 30 días
														</div>
													</div>
												</div>
											</CardBody>
										</Card>
										<Card
											className={`bg-l${
												darkModeStatus ? 'o25' : '25'
											}-success bg-l${
												darkModeStatus ? 'o50' : '10'
											}-success-hover transition-base rounded-2 mb-0`}
											shadow='sm'>
											<CardHeader className='bg-transparent'>
												<CardLabel>
													<CardTitle tag='h4' className='h5'>
														Procesos finalizados
													</CardTitle>
												</CardLabel>
											</CardHeader>
											<CardBody>
												<div className='d-flex align-items-center pb-3'>
													<div className='flex-shrink-0'>
														<Icon
															icon='Celebration'
															size='4x'
															color='success'
														/>
													</div>
													<div className='flex-grow-1 ms-3'>
														<div className='fw-bold fs-3 mb-0'>
															{data?.processfinished}
															{/* <span className='text-danger fs-5 fw-bold ms-3'>
																-50%
																<Icon icon='TrendingDown' />
															</span> */}
														</div>
														{/* <div className='text-muted'>
															Compared to (2 last week)
														</div> */}
													</div>
												</div>
											</CardBody>
										</Card>
									</div>
									<div className='col-md-6'>
										<Card
											className={`bg-l${
												darkModeStatus ? 'o25' : '10'
											}-light bg-l${
												darkModeStatus ? 'o50' : '10'
											}-light-hover transition-base rounded-2 mb-0`}
											stretch
											shadow='sm'>
											<CardHeader className='bg-transparent'>
												<CardLabel>
													<CardTitle tag='h4' className='h5'>
														Chequeos por día
													</CardTitle>
												</CardLabel>
											</CardHeader>
											<CardBody className='pt-0'>
												<Chart
													className='d-flex justify-content-center'
													series={dayHours.series}
													options={{
														...dayHours.options,
													}}
													type={'line'}
													height={dayHours.options.chart?.height}
													width={dayHours.options.chart?.width}
												/>
												<div className='d-flex align-items-center pb-3'>
													<div className='flex-shrink-0'>
														<Icon
															icon='Timer'
															size='4x'
															color='success'
														/>
													</div>
													<div className='flex-grow-1 ms-3'>
														<div className='fw-bold fs-3 mb-0'>
															~ {data?.checksCount}
															{/* <span className='text-success fs-5 fw-bold ms-3'>
																+12.5%
																<Icon icon='TrendingUp' />
															</span> */}
														</div>
														<div className='text-muted'>
															Última semana
														</div>
													</div>
												</div>
											</CardBody>
										</Card>
									</div>
								</div>
							</CardBody>
						</Card>
						<Card>
							<CardHeader>
								<CardLabel icon='Task' iconColor='danger'>
									<CardTitle>
										<CardLabel>Últimos procesos finalizados</CardLabel>
									</CardTitle>
								</CardLabel>
							</CardHeader>
							<CardBody>
								<div className='table-responsive'>
									<table className='table table-modern mb-0'>
										<thead>
											<tr>
												<th>Date / Time</th>
												<th>Customer</th>
												<th>Service</th>
												<th>Duration</th>
												<th>Payment</th>
												<th>Status</th>
											</tr>
										</thead>
										<tbody>
											{userTasks.map((item: any) => (
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
																{moment(
																	`${item.date} ${item.time}`,
																).format('MMM Do YYYY, h:mm a')}
															</span>
														</div>
													</td>
													<td>
														<div>
															<div>{item.customer.name}</div>
															<div className='small text-muted'>
																{item.customer.email}
															</div>
														</div>
													</td>
													<td>{item.service.name}</td>
													<td>{item.duration}</td>
													<td>
														{item.payment && priceFormat(item.payment)}
													</td>
													<td>
														{/* <Dropdown>
															<DropdownToggle hasIcon={false}>
																<Button
																	isLink
																	color={item.status.color}
																	icon='Circle'
																	className='text-nowrap'>
																	{item.status.name}
																</Button>
															</DropdownToggle>
															<DropdownMenu>
																{Object.keys(EVENT_STATUS).map(
																	(key) => (
																		<DropdownItem key={key}>
																			<div>
																				<Icon
																					icon='Circle'
																					color={
																						EVENT_STATUS[
																							key
																						].color
																					}
																				/>
																				{
																					EVENT_STATUS[
																						key
																					].name
																				}
																			</div>
																		</DropdownItem>
																	),
																)}
															</DropdownMenu>
														</Dropdown> */}
													</td>
												</tr>
											))}
										</tbody>
									</table>
								</div>
								{!userTasks.length && (
									<Alert color='warning' isLight icon='Report' className='mt-3'>
										No se ha completado ningún proceso aún
									</Alert>
								)}
							</CardBody>
						</Card>
					</div>
				</div>
			</Page>
		</PageWrapper>
	);
};

export const getStaticProps: GetStaticProps = async ({ locale }) => ({
	props: {
		// @ts-ignore
		...(await serverSideTranslations(locale, ['common', 'menu'])),
	},
});

// export async function getStaticPaths() {
// 	return {
// 		paths: [
// 			// String variant:
// 			// '/appointment/employee/1',
// 			// Object variant:
// 			{ params: { id: '2' } },
// 		],
// 		fallback: true,
// 	};
// }

export default Id;
