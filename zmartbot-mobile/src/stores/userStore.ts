import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface UserState {
  userId: string | null;
  userName: string | null;
  isAuthenticated: boolean;
  setUserId: (id: string) => void;
  setUserName: (name: string) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      userId: null,
      userName: null,
      isAuthenticated: false,
      setUserId: (id: string) => set({ userId: id, isAuthenticated: true }),
      setUserName: (name: string) => set({ userName: name }),
      logout: () => set({ userId: null, userName: null, isAuthenticated: false }),
    }),
    {
      name: 'user-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);