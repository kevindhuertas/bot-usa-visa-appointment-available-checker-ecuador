import React, {
	createContext,
	FC,
	ReactNode,
	useEffect,
	useMemo,
	useState,
	useContext, // Para el hook useAuth
} from 'react';
import PropTypes from 'prop-types';

// Asumimos que IUserProps es la estructura de datos del usuario que devuelve tu API
// (sin la contraseña)
export interface IUserProps {
	id: string;
	username: string;
	name: string;
	surname: string;
	position: string;
	email: string;
	src: string;
	isOnline: boolean;
	isReply: boolean;
	color: string;
	checksCount: string;
	processfinished: string;
	processFinishedHistory: string[];
	plan: {
		type: string;
		processProgramationAvalaible: string;
		processChekingAvalaible: string;
		planExpiration: string;
		planRenewed: string;
		planStarted: string;
	};
	// Asegúrate de que no incluya 'password'
}

export interface IAuthContextProps {
	userId: string; // Ahora almacenamos el ID del usuario, '' indica no logueado
	setUserId: (userId: string) => void; // Función para actualizar el userId
	userData: Partial<IUserProps>; // Datos del usuario obtenidos del backend
	loading: boolean; // Estado de carga para operaciones asíncronas
	error: string | null; // Para manejar errores de API
	login: (identifier: string, password: string) => Promise<void>; // Función de login
	logout: () => void; // Función de logout
}

const AuthContext = createContext<IAuthContextProps>({
	userId: '',
	setUserId: () => {},
	userData: {},
	loading: true,
	error: null,
	login: async () => {},
	logout: () => {},
});

interface IAuthContextProviderProps {
	children: ReactNode;
}

export const AuthContextProvider: FC<IAuthContextProviderProps> = ({ children }) => {
	const [userId, setUserIdInternal] = useState<string>('');
	const [userData, setUserData] = useState<Partial<IUserProps>>({});
	const [loading, setLoading] = useState<boolean>(true); // Inicia cargando para la sesión inicial
	const [error, setError] = useState<string | null>(null);

	const API_BASE_URL = process.env.NEXT_PUBLIC_BOT_PUBLIC_API_URL; // Asegúrate que esté definido
	const AUTH_USER_ID_KEY = 'facit_authUserId';

	// --- Funciones de Autenticación ---

	const login = async (identifier: string, password: string) => {
		setLoading(true);
		setError(null);
		try {
			const response = await fetch(`${API_BASE_URL}auth/login`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ identifier, password }),
			});

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.error || 'Failed to login');
			}

			if (data.user && data.user.id) {
				setUserIdInternal(data.user.id);
				// Los datos del usuario ya vienen en data.user, así que los establecemos
				setUserData(data.user);
				localStorage.setItem(AUTH_USER_ID_KEY, data.user.id);
			} else {
				throw new Error('User ID not found in login response');
			}
		} catch (err: any) {
			setError(err.message || 'An unexpected error occurred during login.');
			// Limpiar en caso de error de login
			setUserIdInternal('');
			setUserData({});
			localStorage.removeItem(AUTH_USER_ID_KEY);
			throw err; // Relanzar para que el componente de Login lo maneje
		} finally {
			setLoading(false);
		}
	};

	const logout = () => {
		setUserIdInternal('');
		setUserData({});
		localStorage.removeItem(AUTH_USER_ID_KEY);

		// Para Firebase: await firebase.auth().signOut();
		// Luego la lógica de onAuthStateChanged manejaría la limpieza del estado.
	};

	const setUserId = (newUserId: string) => {
		setUserIdInternal(newUserId);
		if (newUserId) {
			localStorage.setItem(AUTH_USER_ID_KEY, newUserId);
		} else {
			localStorage.removeItem(AUTH_USER_ID_KEY);
			setUserData({}); // Limpiar userData al desloguear
		}
	};

	// Efecto para cargar el ID de usuario desde localStorage al montar (solo en cliente)
	useEffect(() => {
		// Este efecto es para restaurar la sesión si el ID está en localStorage
		const storedUserId = localStorage.getItem(AUTH_USER_ID_KEY);
		if (storedUserId && storedUserId !== 'null' && storedUserId !== 'undefined') {
			setUserIdInternal(storedUserId);
			// No llamamos a fetchUserData aquí directamente,
			// el siguiente useEffect se encargará cuando userId cambie.
		} else {
			setLoading(false); // Si no hay user ID, terminamos de cargar
		}
		// Para Firebase:
		// const unsubscribe = firebase.auth().onAuthStateChanged(async (firebaseUser) => {
		//   if (firebaseUser) {
		//     setUserIdInternal(firebaseUser.uid);
		//     // Aquí podrías obtener datos adicionales del perfil de Firebase o de tu backend (Firestore/RTDB)
		//     // Ejemplo: const userProfile = await fetchUserProfileFromFirestore(firebaseUser.uid);
		//     // setUserData(userProfile);
		//   } else {
		//     setUserIdInternal('');
		//     setUserData({});
		//   }
		//   setLoading(false);
		// });
		// return () => unsubscribe(); // Limpiar el listener al desmontar
	}, []);

	// Efecto para obtener datos del usuario cuando userId cambia (y no está vacío)
	// y no estamos ya cargando por el login.
	useEffect(() => {
		const fetchUserData = async (idToFetch: string) => {
			if (!idToFetch) {
				setUserData({});
				setLoading(false); // Si no hay ID, no hay nada que cargar
				return;
			}

			// Si ya tenemos datos para este userId (posiblemente del login), no volver a cargar
			if (userData.id === idToFetch && Object.keys(userData).length > 0) {
				setLoading(false);
				return;
			}

			setLoading(true);
			setError(null);
			try {
				const response = await fetch(`${API_BASE_URL}/users/${idToFetch}`);
				const data = await response.json();

				if (!response.ok) {
					throw new Error(data.error || 'Failed to fetch user data');
				}
				setUserData(data);
			} catch (err: any) {
				setError(err.message || 'An unexpected error occurred fetching user data.');
				// En caso de error al obtener datos, podríamos desloguear al usuario
				// o manejarlo de otra forma según la UX deseada.
				// logout(); // Opcional: desloguear si no se pueden obtener datos esenciales
			} finally {
				setLoading(false);
			}
		};

		// Solo llamar si userId tiene valor y no es el estado inicial de carga del login.
		// El login ya establece userData.
		if (userId) {
			fetchUserData(userId);
		} else {
			// Si no hay userId (después de logout o al inicio sin sesión), limpiar userData
			setUserData({});
			if (loading) setLoading(false); // Si estaba cargando y ya no hay ID, parar.
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [userId, API_BASE_URL]); // Depende de userId

	const contextValue = useMemo(
		() => ({
			userId,
			setUserId,
			userData,
			loading,
			error,
			login,
			logout,
		}),
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[userId, userData, loading, error], // No incluir setUserId, login, logout si no cambian de referencia
	);

	return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

AuthContextProvider.propTypes = {
	children: PropTypes.node.isRequired,
};

export default AuthContext;

export const useAuth = () => {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error('useAuth must be used within an AuthContextProvider');
	}
	return context;
};
