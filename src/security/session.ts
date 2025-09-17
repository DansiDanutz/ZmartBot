import * as SecureStore from 'expo-secure-store';
import { AppState } from 'react-native';

const TOKEN_KEY = 'zmart.token';
const SESSION_KEY = 'zmart.session';
let lockTimer: any;

export interface SessionData {
  userId: string;
  email: string;
  permissions: string[];
  lastActive: number;
}

export async function saveToken(token: string) {
  await SecureStore.setItemAsync(TOKEN_KEY, token, { 
    keychainService: 'zmartbot',
    requireAuthentication: true 
  });
}

export async function getToken() {
  return SecureStore.getItemAsync(TOKEN_KEY, { 
    keychainService: 'zmartbot',
    requireAuthentication: true 
  });
}

export async function clearToken() {
  await SecureStore.deleteItemAsync(TOKEN_KEY, { 
    keychainService: 'zmartbot' 
  });
}

export async function saveSession(session: SessionData) {
  await SecureStore.setItemAsync(SESSION_KEY, JSON.stringify(session), { 
    keychainService: 'zmartbot',
    requireAuthentication: true 
  });
}

export async function getSession(): Promise<SessionData | null> {
  const data = await SecureStore.getItemAsync(SESSION_KEY, { 
    keychainService: 'zmartbot',
    requireAuthentication: true 
  });
  return data ? JSON.parse(data) : null;
}

export async function clearSession() {
  await SecureStore.deleteItemAsync(SESSION_KEY, { 
    keychainService: 'zmartbot' 
  });
}

export function enableAutoLock(onLock: () => void, lockDelayMinutes: number = 5) {
  const lockDelayMs = lockDelayMinutes * 60 * 1000;
  
  const handleAppStateChange = (nextAppState: string) => {
    if (nextAppState === 'background') {
      if (lockTimer) clearTimeout(lockTimer);
      lockTimer = setTimeout(() => {
        onLock();
      }, lockDelayMs);
    } else if (nextAppState === 'active') {
      if (lockTimer) {
        clearTimeout(lockTimer);
        lockTimer = null;
      }
    }
  };

  const subscription = AppState.addEventListener('change', handleAppStateChange);
  
  // Return cleanup function
  return () => {
    subscription?.remove();
    if (lockTimer) clearTimeout(lockTimer);
  };
}

export function clearAutoLockTimer() {
  if (lockTimer) {
    clearTimeout(lockTimer);
    lockTimer = null;
  }
}

// Check if device supports biometrics
export async function checkBiometricSupport() {
  try {
    const hasHardware = await SecureStore.isAvailableAsync();
    return hasHardware;
  } catch {
    return false;
  }
}
