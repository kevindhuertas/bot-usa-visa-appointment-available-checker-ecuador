'use client';

import React, { useEffect } from 'react';
import App from './App';
import LoadingScreen from '@/components/LoadingScreen';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

const DashboardPage: React.FC = () => {
const { user, loading } = useAuth();
const router = useRouter();

useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading || !user) {
    return <LoadingScreen />;
  }

  return <App />;
};

export default DashboardPage;
