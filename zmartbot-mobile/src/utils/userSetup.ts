import AsyncStorage from '@react-native-async-storage/async-storage';
import { useUserStore } from '../stores/userStore';
import { apiClient } from '../api/client';

export const initializeUser = async () => {
  try {
    let userId = await AsyncStorage.getItem('user_id');
    
    if (!userId) {
      // Generate a demo user ID
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      await AsyncStorage.setItem('user_id', userId);
    }
    
    // Set user in store
    useUserStore.getState().setUserId(userId);
    
    // Trigger welcome credits for new users by checking balance
    // Temporarily disabled for demo mode
    console.log('Demo mode: Skipping API calls');
    
    return userId;
  } catch (error) {
    console.error('Failed to initialize user:', error);
    return null;
  }
};