import React, { createContext, FC, ReactNode, useEffect, useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import { getUserDataWithUsername, IUserProps } from '../common/data/userDummyData';

export interface IAuthContextProps {
	user: string; // Mantén string, '' indica no logueado o estado inicial
	setUser?(user: string): void; // Especifica el tipo de argumento
	userData: Partial<IUserProps>;
	loading: boolean; // <-- Añade el estado de carga
}
// Inicializa con valores por defecto que coincidan con el estado inicial
const AuthContext = createContext<IAuthContextProps>({
	user: '',
	setUser: () => {},
	userData: {},
	loading: true, // <-- Inicialmente cargando
});

interface IAuthContextProviderProps {
	children: ReactNode;
}
export const AuthContextProvider: FC<IAuthContextProviderProps> = ({ children }) => {
	// Inicializa 'user' a '' consistentemente en server y client inicial.
	const [user, setUser] = useState<string>('');
	// Inicializa 'loading' a true.
	const [loading, setLoading] = useState<boolean>(true);
	const [userData, setUserData] = useState<Partial<IUserProps>>({});

	// Efecto para leer localStorage SOLO en el cliente DESPUÉS del montaje inicial
	useEffect(() => {
		// Lee el usuario almacenado
		const storedUser = localStorage.getItem('facit_authUsername');

		// Si se encuentra un usuario válido en localStorage (y no es 'null' o 'undefined' como string)
		// Actualiza el estado 'user'. Si no, se queda como ''.
		if (storedUser && storedUser !== 'null' && storedUser !== 'undefined') {
			setUser(storedUser);
		}

		// Marca la carga como completa DESPUÉS de intentar leer localStorage.
		setLoading(false);
	}, []); // El array vacío asegura que se ejecute solo una vez al montar en el cliente

	// Efecto para guardar en localStorage cuando 'user' cambia (después de la carga inicial)
	useEffect(() => {
		// Solo guarda si no estamos en el estado inicial '' o si realmente cambió
		// Y evita guardar durante el renderizado del servidor (aunque useEffect no corre ahí)
		if (typeof window !== 'undefined') {
			localStorage.setItem('facit_authUsername', user);
		}
	}, [user]);

	// Efecto para obtener datos del usuario cuando 'user' cambia (y no está vacío)
	useEffect(() => {
		if (user) {
			// Comprueba si user tiene un valor (no es '')
			setUserData(getUserDataWithUsername(user));
		} else {
			setUserData({});
		}
	}, [user]); // Depende solo de 'user'

	// Memoiza el valor del contexto
	const value = useMemo(
		() => ({
			user,
			setUser, // Asegúrate de que la función setUser se pasa correctamente
			userData,
			loading, // <-- Incluye loading en el valor del contexto
		}),
		[user, userData, loading], // <-- Añade loading a las dependencias
	);

	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
AuthContextProvider.propTypes = {
	children: PropTypes.node.isRequired,
};

// Exporta el contexto para usar con useContext o un hook personalizado si lo prefieres
export default AuthContext;

// (Opcional pero recomendado) Hook personalizado para consumir el contexto
export const useAuth = () => {
	const context = React.useContext(AuthContext);
	if (context === undefined) {
		throw new Error('useAuth must be used within an AuthContextProvider');
	}
	return context;
};
