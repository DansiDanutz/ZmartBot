import React, { useEffect, useState } from 'react';
import { StatusBar } from 'react-native';
import MainApp from './src/screens/MainApp';
import AuthScreen from './src/screens/AuthScreen';
import { PrefsProvider } from './src/assistant/store/prefs';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Check if user has valid session
      // For now, we'll just simulate a check
      setTimeout(() => {
        setIsAuthenticated(false);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsLoading(false);
    }
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  if (isLoading) {
    return null; // You could add a splash screen here
  }

  return (
    <PrefsProvider>
      <StatusBar barStyle="light-content" backgroundColor="#0A0E1B" />
      {isAuthenticated ? (
        <MainApp />
      ) : (
        <AuthScreen onLogin={handleLogin} />
      )}
    </PrefsProvider>
  );
}