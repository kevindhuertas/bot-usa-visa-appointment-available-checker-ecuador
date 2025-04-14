'use client';
import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';
import LoadingScreen from '@/components/LoadingScreen';

const HomePage: React.FC = () => {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      // Redirige a dashboard si hay usuario, o a login en caso contrario
      router.push(user ? '/dashboard' : '/login');
    }
  }, [user, loading, router]);
  
  if (loading || !user) {
    return <LoadingScreen />;
  }
  return <LoadingScreen/>;
};

export default HomePage;
