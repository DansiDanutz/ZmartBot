import { create } from 'zustand';

type Prefs = {
  smartMode: boolean;
  allowLocation: boolean;
  allowVoice: boolean;
  city?: string;
  lat?: number;
  lon?: number;
  set: (p: Partial<Prefs>) => void;
};

export const usePrefs = create<Prefs>((set) => ({
  smartMode: false,
  allowLocation: false,
  allowVoice: false,
  set: (p) => set(p),
}));
