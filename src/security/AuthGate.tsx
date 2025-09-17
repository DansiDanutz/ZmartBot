import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet, Alert } from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

interface AuthGateProps {
  children: React.ReactNode;
  onAuthSuccess?: () => void;
  onAuthFailure?: () => void;
}

export default function AuthGate({ children, onAuthSuccess, onAuthFailure }: AuthGateProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [biometricType, setBiometricType] = useState<'fingerprint' | 'face' | 'iris' | 'none'>('none');

  useEffect(() => {
    checkBiometricSupport();
  }, []);

  const checkBiometricSupport = async () => {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      const supportedTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();

      if (!hasHardware || !isEnrolled) {
        // No biometrics available, proceed without authentication
        setIsAuthenticated(true);
        setIsChecking(false);
        return;
      }

      // Determine biometric type
      if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
        setBiometricType('face');
      } else if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
        setBiometricType('fingerprint');
      } else if (supportedTypes.includes(LocalAuthentication.AuthenticationType.IRIS)) {
        setBiometricType('iris');
      }

      // Attempt authentication
      await authenticateUser();
    } catch (error) {
      console.error('Biometric check failed:', error);
      // Fallback to no authentication
      setIsAuthenticated(true);
      setIsChecking(false);
    }
  };

  const authenticateUser = async () => {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Unlock ZmartBot',
        fallbackEnabled: true,
        cancelLabel: 'Cancel',
        disableDeviceFallback: false,
      });

      if (result.success) {
        setIsAuthenticated(true);
        onAuthSuccess?.();
      } else {
        if (result.error === 'UserCancel') {
          // User cancelled, show alert and retry
          Alert.alert(
            'Authentication Required',
            'Please authenticate to access ZmartBot',
            [
              { text: 'Cancel', style: 'cancel', onPress: () => onAuthFailure?.() },
              { text: 'Try Again', onPress: authenticateUser }
            ]
          );
        } else {
          // Other error, proceed without authentication
          setIsAuthenticated(true);
          onAuthSuccess?.();
        }
      }
    } catch (error) {
      console.error('Authentication failed:', error);
      // Fallback to no authentication
      setIsAuthenticated(true);
      onAuthSuccess?.();
    } finally {
      setIsChecking(false);
    }
  };

  const getBiometricIcon = () => {
    switch (biometricType) {
      case 'face':
        return 'scan-outline';
      case 'fingerprint':
        return 'finger-print-outline';
      case 'iris':
        return 'eye-outline';
      default:
        return 'shield-outline';
    }
  };

  const getBiometricText = () => {
    switch (biometricType) {
      case 'face':
        return 'Face ID';
      case 'fingerprint':
        return 'Touch ID';
      case 'iris':
        return 'Iris Scan';
      default:
        return 'Biometric';
    }
  };

  if (isChecking) {
    return (
      <LinearGradient
        colors={['#0B0E11', '#1E2329']}
        style={styles.container}
      >
        <View style={styles.loadingContainer}>
          <Ionicons name={getBiometricIcon()} size={64} color="#0ECB81" />
          <Text style={styles.loadingTitle}>Securing ZmartBot</Text>
          <Text style={styles.loadingSubtitle}>
            Using {getBiometricText()} for secure access
          </Text>
          <ActivityIndicator size="large" color="#0ECB81" style={styles.spinner} />
        </View>
      </LinearGradient>
    );
  }

  if (!isAuthenticated) {
    return (
      <LinearGradient
        colors={['#0B0E11', '#1E2329']}
        style={styles.container}
      >
        <View style={styles.authContainer}>
          <Ionicons name={getBiometricIcon()} size={80} color="#F6465D" />
          <Text style={styles.authTitle}>Authentication Required</Text>
          <Text style={styles.authSubtitle}>
            Please use {getBiometricText()} to unlock ZmartBot
          </Text>
          <View style={styles.buttonContainer}>
            <Text style={styles.retryButton} onPress={authenticateUser}>
              Try Again
            </Text>
          </View>
        </View>
      </LinearGradient>
    );
  }

  return <>{children}</>;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#EAECEF',
    marginTop: 20,
    textAlign: 'center',
  },
  loadingSubtitle: {
    fontSize: 16,
    color: '#EAECEF',
    marginTop: 10,
    textAlign: 'center',
    opacity: 0.8,
  },
  spinner: {
    marginTop: 30,
  },
  authContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  authTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#EAECEF',
    marginTop: 20,
    textAlign: 'center',
  },
  authSubtitle: {
    fontSize: 18,
    color: '#EAECEF',
    marginTop: 15,
    textAlign: 'center',
    opacity: 0.8,
    lineHeight: 24,
  },
  buttonContainer: {
    marginTop: 40,
  },
  retryButton: {
    fontSize: 18,
    color: '#0ECB81',
    fontWeight: '600',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderWidth: 2,
    borderColor: '#0ECB81',
    borderRadius: 25,
    overflow: 'hidden',
  },
});
