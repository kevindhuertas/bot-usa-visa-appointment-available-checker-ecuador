// components/RequireAuth.tsx
import React, { useEffect } from 'react'; // Importa React si usas JSX <>
import { useRouter } from 'next/router';
import { useAuth } from '../context/authContext'; // <-- Usa el hook personalizado
// import LoadingSpinner from './LoadingSpinner'; // O cualquier indicador de carga

interface RequireAuthProps {
  children: React.ReactNode;
}

const RequireAuth = ({ children }: RequireAuthProps) => {
  const { user, loading } = useAuth(); // <-- Obtén user y loading
  const router = useRouter();
  const isLoginPage = router.pathname === '/login/sign-in';

  useEffect(() => {
    if (!loading && !user && !isLoginPage) {
      router.push('/login/sign-in');
    }
  }, [user, loading, router, isLoginPage]); 

  if (loading) {
    return null; // O <LoadingSpinner />;
  }

  if (!user && !isLoginPage) {
    return null;
  }

  return <>{children}</>;
};

export default RequireAuth;