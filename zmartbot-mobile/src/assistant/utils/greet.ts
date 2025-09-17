import { usePrefs } from '../store/prefs';

export function smartGreeting(): string {
  const hour = new Date().getHours();
  const hello = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
  const { smartMode, allowLocation, city } = usePrefs.getState();
  if (smartMode && allowLocation && city) return `${hello} from ${city}!`;
  return `${hello}!`;
}
