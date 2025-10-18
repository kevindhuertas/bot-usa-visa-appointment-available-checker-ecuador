import type { NextPage } from 'next';
import { GetStaticProps } from 'next';
import Head from 'next/head';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import useDarkMode from '../../hooks/useDarkMode';
import { useState } from 'react';
import PageWrapper from '../../layout/PageWrapper/PageWrapper';
import { dashboardPagesMenu, demoPagesMenu } from '../../menu';
import SubHeader, { SubHeaderLeft, SubheaderSeparator } from '../../layout/SubHeader/SubHeader';
import Breadcrumb from '../../components/bootstrap/Breadcrumb';
import ScrollspyNav from '../../components/bootstrap/ScrollspyNav';
import Button from '../../components/bootstrap/Button';
import Page from '../../layout/Page/Page';
import Card, { CardBody, CardHeader } from '../../components/bootstrap/Card';
import Icon from '../../components/icon/Icon';
import classNames from 'classnames';

const Index: NextPage = () => {
	const { darkModeStatus } = useDarkMode();
	const [activeElementId, setActiveElementId] = useState<string | null>(null);
	return (
		<PageWrapper>
			<Head>
				<title>{dashboardPagesMenu.pricingTable.text}</title>
			</Head>
			<SubHeader>
				<SubHeaderLeft>
					<Breadcrumb
						list={[
							{
								title: dashboardPagesMenu.pricingTable.text,
								to: `/${dashboardPagesMenu.pricingTable.path}`,
							},
						]}
					/>
				</SubHeaderLeft>
			</SubHeader>
			<Page>
				<div id='first' className='row scroll-margin'>
					<div className='col-md-3'>
						<Card stretch className='bg-transparent' shadow='none'>
							<CardBody>
								<div className='h-100 d-flex align-items-center justify-content-center'>
									<div className='row text-center'>
										<div className='col-12 text-uppercase fw-light'>
											Por Mes
										</div>{' '}
										<div className='col-12 text-uppercase h2 fw-bold mb-2'>
											Selcciona tu plan{' '}
											<Icon icon='Verified' size='2x' color='info' />
										</div>
										<div className='col-12 mb-2'>
											El Plan es válido el por un mes desde su activación.
											Plan extendible con cargos adicionales. Aprox. 1500
											chequeos de citas por proceso activo al dia
										</div>
									</div>
								</div>
							</CardBody>
						</Card>
					</div>
					<div className='col-md-3'>
						<Card>
							<CardBody>
								<div className='row pt-5 g-4 text-center'>
									<div className='col-12'>
										<Icon icon='CustomRocketLaunch' size='7x' color='info' />
									</div>
									<div className='col-12'>
										<h2>Básico</h2>
									</div>
									<div className='col-12'>
										<h3 className='display-1 fw-bold'>
											<span className='display-4 fw-bold'>$</span>59
											<span className='display-6'>/mes</span>
										</h3>
									</div>
									<div className='col-12'>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' />
											<span className=' fw-bold'> 6 </span>
											Procesos finalizados
										</div>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' />{' '}
											<span className=' fw-bold'> 10 </span>
											Procesos activos
										</div>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' />{' '}
											<span className=' fw-bold'> 300k </span>
											chequeos
										</div>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' /> Soporte al
											cliente
										</div>
									</div>
									<div className='col-12'>
										<p>Plan extendible por demanda</p>
									</div>
									<div className='col-12'>
										<Button
											color='info'
											isLight
											className='w-100 py-3 text-uppercase'
											size='lg'>
											Seleccionar Plan
										</Button>
									</div>
								</div>
							</CardBody>
						</Card>
					</div>
					<div className='col-md-3'>
						<Card borderColor={'success'} borderSize={2}>
							<CardBody>
								<div className='row pt-5 g-4 text-center'>
									<div className='col-12'>
										<Icon icon='Maps Home Work' size='7x' color='success' />
									</div>
									<div className='col-12'>
										<h2>Empresa</h2>
									</div>
									<div className='col-12'>
										<h3 className='display-1 fw-bold'>
											<span className='display-4 fw-bold'>$</span>99
											<span className='display-6'>/mes</span>
										</h3>
									</div>
									<div className='col-12'>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' />
											<span className=' fw-bold'> 15 </span>
											Procesos finalizados
										</div>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' />{' '}
											<span className=' fw-bold'> 20 </span>
											Procesos activos
										</div>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' />{' '}
											<span className=' fw-bold'> 800k </span>
											chequeos
										</div>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' /> Soporte al
											cliente
										</div>
									</div>
									<div className='col-12'>
										<p>Plan extendible por demanda</p>
									</div>
									<div className='col-12'>
										<Button
											color='success'
											className='w-100 py-3 text-uppercase'
											size='lg'>
											PLAN ACTIVO
										</Button>
									</div>
								</div>
							</CardBody>
						</Card>
					</div>
					<div className='col-md-3'>
						<Card>
							<CardBody>
								<div className='row pt-5 g-4 text-center'>
									<div className='col-12'>
										<Icon icon='CustomFactory' size='7x' color='info' />
									</div>
									<div className='col-12'>
										<h2>Industria</h2>
									</div>
									<div className='col-12'>
										<h3 className='display-1 fw-bold'>
											<span className='display-4 fw-bold'>$</span>179
											<span className='display-6'>/mes</span>
										</h3>
									</div>
									<div className='col-12'>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' />
											<span className=' fw-bold'> 50 </span>
											Procesos finalizados
										</div>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' />{' '}
											<span className=' fw-bold'> 60 </span>
											Procesos activos
										</div>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' />{' '}
											<span className=' fw-bold'> 5000k </span>
											chequeos
										</div>
										<div className='lead'>
											<Icon icon='Done Outline' color='success' /> Soporte al
											cliente
										</div>
									</div>
									<div className='col-12'>
										<p>Plan extendible por demanda</p>
									</div>
									<div className='col-12'>
										<Button
											color='info'
											isLight
											className='w-100 py-3 text-uppercase'
											size='lg'>
											Seleccionar Plan
										</Button>
									</div>
								</div>
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

export default Index;
