import React from 'react';
import { View } from 'react-native';

interface AuthGateProps {
  children: React.ReactNode;
}

export const AuthGate: React.FC<AuthGateProps> = ({ children }) => {
  // Simple auth gate - always allow for demo
  return <View style={{ flex: 1 }}>{children}</View>;
};

export default AuthGate;