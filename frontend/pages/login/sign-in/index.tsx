import type { NextPage } from 'next';
import { GetStaticProps } from 'next';
import Head from 'next/head';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import { useRouter } from 'next/router';
import { FC, useCallback, useContext, useState } from 'react';
import AuthContext, { useAuth } from '../../../context/authContext';
import useDarkMode from '../../../hooks/useDarkMode';
import USERS, { getUserDataWithUsername } from '../../../common/data/userDummyData';
import { useFormik } from 'formik';
import classNames from 'classnames';
import PageWrapper from '../../../layout/PageWrapper/PageWrapper';
import Page from '../../../layout/Page/Page';
import Card, { CardBody } from '../../../components/bootstrap/Card';
import Link from 'next/link';
import Logo from '../../../components/Logo';
import Button from '../../../components/bootstrap/Button';
// import Alert from '../../../components/bootstrap/Alert'; // Alert ya no es necesaria si no mostramos usuario/contraseña
import FormGroup from '../../../components/bootstrap/forms/FormGroup';
import Input from '../../../components/bootstrap/forms/Input';
// import Spinner from '../../../components/bootstrap/Spinner'; // Spinner ya no es necesario sin el botón "Continue"
import PropTypes from 'prop-types';
import Spinner from '../../../components/bootstrap/Spinner';

interface ILoginHeaderProps {
	isNewUser?: boolean;
}
const LoginHeader: FC<ILoginHeaderProps> = ({ isNewUser }) => {
	if (isNewUser) {
		return (
			<>
				<div className='text-center h1 fw-bold mt-5'>Create Account,</div>
				<div className='text-center h4 text-muted mb-5'>Sign up to get started!</div>
			</>
		);
	}
	return (
		<>
			<div className='text-center h1 fw-bold mt-5'>Bienvenido</div>
			<div className='text-center h4 text-muted mb-5'>Inicia sesión para continuar!</div>
		</>
	);
};

interface ILoginProps {
	isSignUp?: boolean;
}
const Login: NextPage<ILoginProps> = ({ isSignUp }) => {
	const router = useRouter();

	const { login, loading, error } = useAuth();

	const { darkModeStatus } = useDarkMode();

	// Ya no necesitamos el estado signInPassword para el login en dos pasos
	// const [signInPassword, setSignInPassword] = useState<boolean>(false);
	const [singUpStatus, setSingUpStatus] = useState<boolean>(!!isSignUp);

	const handleOnClick = useCallback(() => router.push('/'), [router]);

	const usernameCheck = (username: string) => {
		return !!getUserDataWithUsername(username);
	};

	const handleSuccessfulLogin = useCallback(() => {
		router.push('/'); // O a la página que desees después del login
	}, [router]);

	// const passwordCheck = (username: string, password: string) => {
	// 	// Añadir una comprobación por si el usuario no existe para evitar errores
	// 	const userData = getUserDataWithUsername(username);
	// 	return userData && userData.password === password;
	// };

	const formik = useFormik({
		initialValues: {
			// Puedes usar un usuario de prueba o dejar vacío
			// loginIdentifier: USERS.JOHN.username, // Si tenías datos de prueba
			// loginPassword: USERS.JOHN.password,
			loginIdentifier: '',
			loginPassword: '',
		},
		validate: (values) => {
			const errors: { loginIdentifier?: string; loginPassword?: string } = {};
			if (!values.loginIdentifier) {
				errors.loginIdentifier = 'Usuario o Email es requerida';
			}
			if (!values.loginPassword) {
				errors.loginPassword = 'Contraseña es requerida';
			}
			return errors;
		},
		onSubmit: async (values, { setSubmitting, setFieldError }) => {
			// No necesitamos setSubmitting(true/false) aquí si `loading` del contexto
			// ya lo maneja visualmente, o Formik lo hace con isSubmitting.
			// Puedes usar formik.isSubmitting para deshabilitar el botón si lo deseas.
			try {
				await login(values.loginIdentifier, values.loginPassword); // Llama a la función de login del contexto
				// await new Promise((resolve) => setTimeout(resolve, 2000));
				handleSuccessfulLogin();
			} catch (apiError: any) {
				// El error ya fue seteado en el contexto, pero también podemos mostrarlo en el form
				// El 'apiError' aquí es el que relanzamos desde la función login del contexto
				setFieldError(
					'loginPassword',
					apiError.message || 'Login failed. Please check your credentials.',
				);
			} finally {
				// setSubmitting(false); // Formik maneja esto automáticamente si la función onSubmit es async
			}
		},
	});

	return (
		<PageWrapper
			isProtected={false}
			// Aplicar degradado según el modo dark/light
			className={classNames(
				'bg-gradient', // Clase base para degradado de Bootstrap
				'min-vh-100', // Asegura que cubra toda la altura
				{
					// Clases condicionales para el color base del degradado
					'bg-light': !darkModeStatus, // Degradado claro en light mode
					'bg-dark': darkModeStatus, // Degradado oscuro en dark mode
				},
			)}>
			{/* <Head>
				<title>{singUpStatus ? 'Sign Up' : 'Login'}</title>
			</Head> */}
			<Page className='p-0'>
				<div className='row h-100 align-items-center justify-content-center'>
					<div className='col-xl-4 col-lg-6 col-md-8 shadow-3d-container'>
						<Card className='shadow-3d-dark' data-tour='login-page'>
							<CardBody>
								<div className='text-center my-5  bg-light rounded'>
									<Link
										href='/'
										className={classNames(
											'text-decoration-none fw-bold display-2',
											{
												'text-dark': !darkModeStatus,
												'text-light': darkModeStatus,
											},
										)}>
										<Logo width={200} />
									</Link>
								</div>
								{/* Los botones para cambiar entre Login/Sign Up siguen comentados como estaban */}
								{/* <div
									className={classNames('rounded-3', {
										'bg-l10-dark': !darkModeStatus,
										'bg-dark': darkModeStatus,
									})}>
									<div className='row row-cols-2 g-3 pb-3 px-3 mt-0'>
										<div className='col'>
											<Button
												color={darkModeStatus ? 'light' : 'dark'}
												isLight={singUpStatus}
												className='rounded-1 w-100'
												size='lg'
												onClick={() => {
													// setSignInPassword(false); // Ya no existe
													setSingUpStatus(false); // Cambiar a Login
													formik.resetForm(); // Resetear formulario al cambiar
												}}>
												Login
											</Button>
										</div>
										<div className='col'>
											<Button
												color={darkModeStatus ? 'light' : 'dark'}
												isLight={!singUpStatus}
												className='rounded-1 w-100'
												size='lg'
												onClick={() => {
													// setSignInPassword(false); // Ya no existe
													setSingUpStatus(true); // Cambiar a Sign Up
													formik.resetForm(); // Resetear formulario al cambiar
												}}>
												Sign Up
											</Button>
										</div>
									</div>
								</div> */}

								<LoginHeader isNewUser={singUpStatus} />

								{/* El Alert con usuario/contraseña de ejemplo ya no es necesario o puede adaptarse */}
								{/* <Alert isLight icon='Lock' isDismissible>
									<div className='row'>
										<div className='col-12'>
											<strong>Username:</strong> {USERS.JOHN.username}
										</div>
										<div className='col-12'>
											<strong>Password:</strong> {USERS.JOHN.password}
										</div>
									</div>
								</Alert> */}

								{/* Usamos formik.handleSubmit directamente en la etiqueta form */}
								<form className='row g-4' onSubmit={formik.handleSubmit}>
									{singUpStatus ? (
										// FORMULARIO SIGN UP (sin cambios solicitados)
										<>
											<div className='col-12'>
												<FormGroup
													id='signup-email'
													isFloating
													label='Tu email'>
													<Input type='email' autoComplete='email' />
												</FormGroup>
											</div>
											<div className='col-12'>
												<FormGroup
													id='signup-name'
													isFloating
													label='Tu nombre'>
													<Input autoComplete='given-name' />
												</FormGroup>
											</div>
											<div className='col-12'>
												<FormGroup
													id='signup-surname'
													isFloating
													label='Your surname'>
													<Input autoComplete='family-name' />
												</FormGroup>
											</div>
											<div className='col-12'>
												<FormGroup
													id='signup-password'
													isFloating
													label='Password'>
													<Input
														type='password'
														autoComplete='new-password' // Mejor usar new-password para sign up
													/>
												</FormGroup>
											</div>
											<div className='col-12'>
												{/* Cambiar el onClick a un type="submit" si se quiere manejar con un handler */}
												<Button
													color='info'
													className='w-100 py-3'
													onClick={handleOnClick}>
													Sign Up
												</Button>
											</div>
										</>
									) : (
										// FORMULARIO LOGIN (modificado a un solo paso)
										<>
											{/* Campo Usuario/Email */}
											<div className='col-12'>
												<FormGroup
													id='loginIdentifier'
													isFloating
													label='Tu email o usuario'>
													{/* Ya no tiene la clase 'd-none' condicional */}
													<Input
														name='loginIdentifier' // Asegurarse de que el name coincide con initialValues
														autoComplete='username'
														value={formik.values.loginIdentifier}
														isTouched={formik.touched.loginIdentifier}
														invalidFeedback={
															formik.errors.loginIdentifier
														}
														isValid={
															formik.touched.loginIdentifier &&
															!formik.errors.loginIdentifier
														}
														onChange={formik.handleChange}
														onBlur={formik.handleBlur}
														onFocus={() => {
															// Opcional: Limpiar errores específicos al enfocar
															// formik.setFieldError('loginIdentifier', '');
														}}
													/>
												</FormGroup>
											</div>

											{/* Campo Contraseña */}
											<div className='col-12'>
												{/* Ya no tiene el mensaje 'Hi, {username}' */}
												<FormGroup
													id='loginPassword'
													isFloating
													label='Contraseña'>
													{/* Ya no tiene la clase 'd-none' condicional */}
													<Input
														name='loginPassword' // Asegurarse de que el name coincide con initialValues
														type='password'
														autoComplete='current-password'
														value={formik.values.loginPassword}
														isTouched={formik.touched.loginPassword}
														invalidFeedback={
															formik.errors.loginPassword
														}
														isValid={
															formik.touched.loginPassword &&
															!formik.errors.loginPassword
														}
														onChange={formik.handleChange}
														onBlur={formik.handleBlur}
														onFocus={() => {
															// Opcional: Limpiar errores específicos al enfocar
															// formik.setFieldError('loginPassword', '');
														}}
													/>
												</FormGroup>
											</div>

											{/* Botón de Login */}
											<div className='col-12'>
												{/* Ya no hay botón "Continue", solo "Login" */}
												<Button
													color='warning'
													className='w-100 py-3'
													type='submit' // Importante para que funcione con form onSubmit
													isDisable={formik.isSubmitting} // Deshabilitar mientras se envía
												>
													{formik.isSubmitting ? (
														<Spinner
															tag={'span'} // 'div' || 'span'
															color={'dark'} // 'primary' || 'secondary' || 'success' || 'info' || 'warning' || 'danger' || 'light' || 'dark'
															isSmall={true}
															size={'sm'}
															// size={Number || String} // Example: 10, '3vh', '5rem' etc.
															inButton={'onlyIcon'} // true || false || 'onlyIcon'
														/>
													) : (
														'Iniciar sesión'
													)}
												</Button>
											</div>
										</>
									)}
									{/* Espacio opcional que estaba presente */}
									{/* <div>
										<div className='text-center h4 mb-3 fw-bold'>{' '}</div>
									</div> */}

									{/* BEGIN :: Social Login (sigue comentado como estaba) */}
									{/* {!signInPassword && ( // Esta condición ya no aplica, decidir si mostrar siempre o nunca en modo login
										<>
											<div className='col-12 mt-3 text-center text-muted'>
												OR
											</div>
											<div className='col-12 mt-3'>
												<Button
													isOutline
													color={darkModeStatus ? 'light' : 'dark'}
													className={classNames('w-100 py-3', {
														'border-light': !darkModeStatus,
														'border-dark': darkModeStatus,
													})}
													icon='CustomApple'
													onClick={handleOnClick}>
													Sign in with Apple
												</Button>
											</div>
											<div className='col-12'>
												<Button
													isOutline
													color={darkModeStatus ? 'light' : 'dark'}
													className={classNames('w-100 py-3', {
														'border-light': !darkModeStatus,
														'border-dark': darkModeStatus,
													})}
													icon='CustomGoogle'
													onClick={handleOnClick}>
													Continue with Google
												</Button>
											</div>
										</>
									)} */}
									{/* END :: Social Login */}
								</form>
							</CardBody>
						</Card>
						<div className='text-center mt-4'>
							{' '}
							{/* Añadido margen superior para separar del Card */}
							{/* <Link
								href='/'
								className={classNames('text-decoration-none me-3', {
									// Ajustar el color del enlace según el tema, no según singUpStatus
									'link-dark': !darkModeStatus,
									'link-light': darkModeStatus,
								})}>
								Privacy policy
							</Link> */}
							{/* <Link
								href='/'
								className={classNames('text-decoration-none', {
									// Quitado 'link-light' fijo
									// Ajustar el color del enlace según el tema
									'link-dark': !darkModeStatus,
									'link-light': darkModeStatus,
								})}>
								Terms of use
							</Link> */}
						</div>
					</div>
				</div>
			</Page>
		</PageWrapper>
	);
};
// PropTypes y defaultProps siguen igual
Login.propTypes = {
	isSignUp: PropTypes.bool,
};
Login.defaultProps = {
	isSignUp: false,
};

// getStaticProps sigue igual
export const getStaticProps: GetStaticProps = async ({ locale }) => ({
	props: {
		// @ts-ignore
		...(await serverSideTranslations(locale, ['common', 'menu'])),
	},
});

export default Login;
