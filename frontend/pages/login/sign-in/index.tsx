import type { NextPage } from 'next';
import { GetStaticProps } from 'next';
import Head from 'next/head';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import { useRouter } from 'next/router';
import { FC, useCallback, useContext, useState } from 'react';
import AuthContext from '../../../context/authContext';
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
			<div className='text-center h1 fw-bold mt-5'>Welcome,</div>
			<div className='text-center h4 text-muted mb-5'>Sign in to continue!</div>
		</>
	);
};

interface ILoginProps {
	isSignUp?: boolean;
}
const Login: NextPage<ILoginProps> = ({ isSignUp }) => {
	const router = useRouter();

	const { setUser } = useContext(AuthContext);

	const { darkModeStatus } = useDarkMode();

	// Ya no necesitamos el estado signInPassword para el login en dos pasos
	// const [signInPassword, setSignInPassword] = useState<boolean>(false);
	const [singUpStatus, setSingUpStatus] = useState<boolean>(!!isSignUp);

	const handleOnClick = useCallback(() => router.push('/'), [router]);

	const usernameCheck = (username: string) => {
		return !!getUserDataWithUsername(username);
	};

	const passwordCheck = (username: string, password: string) => {
		// Añadir una comprobación por si el usuario no existe para evitar errores
		const userData = getUserDataWithUsername(username);
		return userData && userData.password === password;
	};

	
	const formik = useFormik({
		enableReinitialize: true,
		initialValues: {
			// Puedes dejar valores iniciales o ponerlos vacíos
			// loginUsername: '', // USERS.JOHN.username,
			// loginPassword: '', // USERS.JOHN.password,
			loginUsername: USERS.JOHN.username,
			loginPassword: USERS.JOHN.password,
		},
		validate: (values) => {
			const errors: { loginUsername?: string; loginPassword?: string } = {};

			if (!values.loginUsername) {
				errors.loginUsername = 'Required';
			} else if (!usernameCheck(values.loginUsername)) {
				// Validación de existencia de usuario aquí si se desea
				errors.loginUsername = 'User not found.';
			}

			if (!values.loginPassword) {
				errors.loginPassword = 'Required';
			}

			return errors;
		},
		validateOnChange: false, // Validar solo al enviar o perder foco si se prefiere
		validateOnBlur: true,
		onSubmit: (values) => {
			// Ya no necesitamos setIsLoading(true/false) aquí si la validación es síncrona
			// La validación de existencia ya se hizo en 'validate'
			// Solo necesitamos comprobar la contraseña
			if (passwordCheck(values.loginUsername, values.loginPassword)) {
				if (setUser) {
					setUser(values.loginUsername);
				}
				handleOnClick(); // Redirigir al dashboard o página principal
			} else {
				// Asegurarse de que el error de usuario no existente no sobreescriba este
				if (usernameCheck(values.loginUsername)) {
					formik.setFieldError('loginPassword', 'Incorrect password.');
				}
				// Si el usuario no existe, el error ya estará en loginUsername por la validación
			}
		},
	});

	// Ya no necesitamos isLoading ni handleContinue
	// const [isLoading, setIsLoading] = useState<boolean>(false);
	// const handleContinue = () => { ... };

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
					'bg-dark': darkModeStatus,   // Degradado oscuro en dark mode
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
								<div className='text-center my-5'>
									<Link
										href='/'
										className={classNames(
											'text-decoration-none  fw-bold display-2',
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
													label='Your email'>
													<Input type='email' autoComplete='email' />
												</FormGroup>
											</div>
											<div className='col-12'>
												<FormGroup
													id='signup-name'
													isFloating
													label='Your name'>
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
													id='loginUsername'
													isFloating
													label='Your email or username'>
													{/* Ya no tiene la clase 'd-none' condicional */}
													<Input
														name='loginUsername' // Asegurarse de que el name coincide con initialValues
														autoComplete='username'
														value={formik.values.loginUsername}
														isTouched={formik.touched.loginUsername}
														invalidFeedback={
															formik.errors.loginUsername
														}
														isValid={formik.touched.loginUsername && !formik.errors.loginUsername}
														onChange={formik.handleChange}
														onBlur={formik.handleBlur}
														onFocus={() => {
															// Opcional: Limpiar errores específicos al enfocar
															// formik.setFieldError('loginUsername', '');
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
													label='Password'>
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
														isValid={formik.touched.loginPassword && !formik.errors.loginPassword}
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
													{formik.isSubmitting ? 'Logging in...' : 'Login'}
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
						<div className='text-center mt-4'> {/* Añadido margen superior para separar del Card */}
							<Link
								href='/'
								className={classNames('text-decoration-none me-3', {
									// Ajustar el color del enlace según el tema, no según singUpStatus
									'link-dark': !darkModeStatus,
									'link-light': darkModeStatus,
								})}>
								Privacy policy
							</Link>
							<Link
								href='/'
								className={classNames('text-decoration-none', { // Quitado 'link-light' fijo
									// Ajustar el color del enlace según el tema
									'link-dark': !darkModeStatus,
									'link-light': darkModeStatus,
								})}>
								Terms of use
							</Link>
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