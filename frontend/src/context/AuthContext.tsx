'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as authLogin, logout as authLogout } from '../lib/authController';
import { useRouter } from 'next/navigation';

interface AuthContextProps {
  user: { email: string } | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextProps>({
  user: null,
  login: async () => {},
  logout: async () => {},
  loading: true,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<{ email: string } | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const router = useRouter();
  
  useEffect(() => {
    // Carga la sesión desde localStorage (esto es asíncrono)
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    console.log("USER EN LOCAL:" + storedUser);

    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const loggedUser = await authLogin(email, password);
    setUser({ email: loggedUser.email });
    localStorage.setItem('user', JSON.stringify({ email: loggedUser.email }));
  };

  const logout = async () => {
    await authLogout();
    setUser(null);
    localStorage.removeItem('user');
    router.push( '/login');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
