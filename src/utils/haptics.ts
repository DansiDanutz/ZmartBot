import * as Haptics from 'expo-haptics';

export class HapticManager {
  // Success feedback - for successful actions
  static async success() {
    try {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  // Error feedback - for failed actions
  static async error() {
    try {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  // Warning feedback - for cautionary actions
  static async warning() {
    try {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  // Light impact - for subtle interactions
  static async light() {
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  // Medium impact - for moderate interactions
  static async medium() {
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  // Heavy impact - for significant interactions
  static async heavy() {
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  // Selection feedback - for UI selection changes
  static async selection() {
    try {
      await Haptics.selectionAsync();
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  // Custom haptic patterns for specific actions
  static async tradeSuccess() {
    try {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      // Add a small delay for pattern
      setTimeout(() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }, 100);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  static async alertTrigger() {
    try {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      setTimeout(() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      }, 150);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  static async creditPurchase() {
    try {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      setTimeout(() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
      }, 200);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  static async biometricSuccess() {
    try {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      setTimeout(() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }, 100);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  static async biometricFailure() {
    try {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      setTimeout(() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      }, 100);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }
}

// Convenience functions for common actions
export const haptics = {
  success: HapticManager.success,
  error: HapticManager.error,
  warning: HapticManager.warning,
  light: HapticManager.light,
  medium: HapticManager.medium,
  heavy: HapticManager.heavy,
  selection: HapticManager.selection,
  tradeSuccess: HapticManager.tradeSuccess,
  alertTrigger: HapticManager.alertTrigger,
  creditPurchase: HapticManager.creditPurchase,
  biometricSuccess: HapticManager.biometricSuccess,
  biometricFailure: HapticManager.biometricFailure,
};
