import * as Location from 'expo-location';
import { usePrefs } from '../store/prefs';

export async function enableCityLevelLocation() {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') return { ok: false, reason: 'perm_denied' };
  const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
  const geo = await Location.reverseGeocodeAsync({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
  const city = geo?.[0]?.city || geo?.[0]?.subregion || 'your city';
  usePrefs.getState().set({ allowLocation: true, lat: pos.coords.latitude, lon: pos.coords.longitude, city });
  return { ok: true, city };
}
