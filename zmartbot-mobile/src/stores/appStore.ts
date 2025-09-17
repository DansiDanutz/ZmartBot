import { create } from 'zustand';

interface AppState {
  activeTab: string;
  isOnline: boolean;
  notifications: boolean;
  setActiveTab: (tab: string) => void;
  setOnlineStatus: (status: boolean) => void;
  toggleNotifications: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'chat',
  isOnline: true,
  notifications: true,
  setActiveTab: (tab) => set({ activeTab: tab }),
  setOnlineStatus: (status) => set({ isOnline: status }),
  toggleNotifications: () => set((state) => ({ notifications: !state.notifications })),
}));