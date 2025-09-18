/**
 * Settings - User settings and preferences management
 * Secure settings interface with privacy controls
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './Settings.css';

const Settings = ({ user, onBack }) => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Default settings structure
  const defaultSettings = {
    notifications: {
      whaleAlerts: true,
      patternAlerts: true,
      marketNews: true,
      priceAlerts: true,
      pushNotifications: true,
      emailNotifications: false,
      alertThreshold: 1000000 // $1M minimum for whale alerts
    },
    trading: {
      defaultProvider: 'grok',
      autoRefresh: true,
      refreshInterval: 30, // seconds
      showProfitLoss: true,
      riskLevel: 'medium'
    },
    privacy: {
      shareAnalytics: false,
      shareUsage: false,
      trackLocation: false,
      dataRetention: '30days'
    },
    ui: {
      theme: 'auto', // auto, light, dark
      fontSize: 'medium',
      animations: true,
      compactMode: false,
      language: 'en'
    },
    security: {
      biometricAuth: false,
      sessionTimeout: 30, // minutes
      autoLogout: true,
      encryptLocalData: true
    },
    advanced: {
      developerMode: false,
      debugMode: false,
      apiTimeout: 10000,
      maxRetries: 3
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      // Load settings from localStorage with fallback to defaults
      const savedSettings = localStorage.getItem('zmartychat_settings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        setSettings({ ...defaultSettings, ...parsed });
      } else {
        setSettings(defaultSettings);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
      setSettings(defaultSettings);
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async (newSettings) => {
    setSaving(true);
    try {
      // Validate settings before saving
      const validatedSettings = validateSettings(newSettings);

      // Save to localStorage
      localStorage.setItem('zmartychat_settings', JSON.stringify(validatedSettings));

      // Update state
      setSettings(validatedSettings);

      // Apply settings immediately
      applySettings(validatedSettings);

      // Show success feedback
      showSuccessMessage('Settings saved successfully!');

    } catch (error) {
      console.error('Error saving settings:', error);
      showErrorMessage('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const validateSettings = (settings) => {
    // Ensure all required fields are present and valid
    const validated = { ...defaultSettings };

    // Deep merge with validation
    Object.keys(settings).forEach(category => {
      if (validated[category]) {
        Object.keys(settings[category]).forEach(key => {
          if (validated[category].hasOwnProperty(key)) {
            validated[category][key] = settings[category][key];
          }
        });
      }
    });

    // Specific validations
    if (validated.notifications.alertThreshold < 1000) {
      validated.notifications.alertThreshold = 1000;
    }

    if (validated.security.sessionTimeout < 5) {
      validated.security.sessionTimeout = 5;
    }

    if (validated.advanced.apiTimeout < 5000) {
      validated.advanced.apiTimeout = 5000;
    }

    return validated;
  };

  const applySettings = (settings) => {
    // Apply theme
    if (settings.ui.theme === 'dark') {
      document.body.classList.add('dark-theme');
    } else if (settings.ui.theme === 'light') {
      document.body.classList.remove('dark-theme');
    }

    // Apply font size
    document.documentElement.style.fontSize = {
      small: '14px',
      medium: '16px',
      large: '18px'
    }[settings.ui.fontSize] || '16px';

    // Apply animations
    if (!settings.ui.animations) {
      document.body.classList.add('no-animations');
    } else {
      document.body.classList.remove('no-animations');
    }
  };

  const updateSetting = (category, key, value) => {
    const newSettings = {
      ...settings,
      [category]: {
        ...settings[category],
        [key]: value
      }
    };
    setSettings(newSettings);
  };

  const handleNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      updateSetting('notifications', 'pushNotifications', permission === 'granted');
    }
  };

  const exportSettings = () => {
    const dataStr = JSON.stringify(settings, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

    const exportFileDefaultName = `zmartychat-settings-${new Date().toISOString().split('T')[0]}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const importSettings = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target.result);
          const validatedSettings = validateSettings(importedSettings);
          setSettings(validatedSettings);
          showSuccessMessage('Settings imported successfully!');
        } catch (error) {
          showErrorMessage('Invalid settings file. Please check the format.');
        }
      };
      reader.readAsText(file);
    }
  };

  const resetSettings = () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
      setSettings(defaultSettings);
      localStorage.removeItem('zmartychat_settings');
      showSuccessMessage('Settings reset to defaults.');
    }
  };

  const showSuccessMessage = (message) => {
    // Simple success notification - could be replaced with toast system
    console.log('✅', message);
  };

  const showErrorMessage = (message) => {
    // Simple error notification - could be replaced with toast system
    console.error('❌', message);
  };

  if (loading) {
    return (
      <div className="settings loading">
        <div className="settings-header">
          <button className="back-btn" onClick={onBack}>←</button>
          <h1>Settings</h1>
        </div>
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings">
      {/* Header */}
      <div className="settings-header">
        <button className="back-btn" onClick={onBack}>
          ←
        </button>
        <h1>⚙️ Settings</h1>
        <button
          className="save-btn"
          onClick={() => saveSettings(settings)}
          disabled={saving}
        >
          {saving ? '💾...' : '💾'}
        </button>
      </div>

      {/* Settings Content */}
      <div className="settings-content">

        {/* Notifications Section */}
        <motion.div
          className="settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h2>🔔 Notifications</h2>

          <div className="setting-item">
            <div className="setting-info">
              <h3>Push Notifications</h3>
              <p>Receive real-time alerts on your device</p>
            </div>
            <div className="setting-control">
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.pushNotifications}
                  onChange={(e) => {
                    if (e.target.checked) {
                      handleNotificationPermission();
                    } else {
                      updateSetting('notifications', 'pushNotifications', false);
                    }
                  }}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <h3>Whale Alerts</h3>
              <p>Large transaction notifications</p>
            </div>
            <div className="setting-control">
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.whaleAlerts}
                  onChange={(e) => updateSetting('notifications', 'whaleAlerts', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <h3>Alert Threshold</h3>
              <p>Minimum amount for whale alerts (USD)</p>
            </div>
            <div className="setting-control">
              <select
                value={settings.notifications.alertThreshold}
                onChange={(e) => updateSetting('notifications', 'alertThreshold', parseInt(e.target.value))}
              >
                <option value={100000}>$100K</option>
                <option value={500000}>$500K</option>
                <option value={1000000}>$1M</option>
                <option value={5000000}>$5M</option>
                <option value={10000000}>$10M</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Trading Section */}
        <motion.div
          className="settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h2>📊 Trading</h2>

          <div className="setting-item">
            <div className="setting-info">
              <h3>Default AI Provider</h3>
              <p>Your preferred AI for analysis</p>
            </div>
            <div className="setting-control">
              <select
                value={settings.trading.defaultProvider}
                onChange={(e) => updateSetting('trading', 'defaultProvider', e.target.value)}
              >
                <option value="grok">🚀 Grok</option>
                <option value="openai">🧠 OpenAI</option>
                <option value="claude">🤖 Claude</option>
                <option value="gemini">💎 Gemini</option>
              </select>
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <h3>Auto Refresh</h3>
              <p>Automatically update market data</p>
            </div>
            <div className="setting-control">
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.trading.autoRefresh}
                  onChange={(e) => updateSetting('trading', 'autoRefresh', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </motion.div>

        {/* Privacy Section */}
        <motion.div
          className="settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2>🔒 Privacy</h2>

          <div className="setting-item">
            <div className="setting-info">
              <h3>Share Analytics</h3>
              <p>Help improve the app with usage data</p>
            </div>
            <div className="setting-control">
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.privacy.shareAnalytics}
                  onChange={(e) => updateSetting('privacy', 'shareAnalytics', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <h3>Encrypt Local Data</h3>
              <p>Encrypt data stored on your device</p>
            </div>
            <div className="setting-control">
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.security.encryptLocalData}
                  onChange={(e) => updateSetting('security', 'encryptLocalData', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </motion.div>

        {/* UI Section */}
        <motion.div
          className="settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2>🎨 Appearance</h2>

          <div className="setting-item">
            <div className="setting-info">
              <h3>Theme</h3>
              <p>Choose your preferred color scheme</p>
            </div>
            <div className="setting-control">
              <select
                value={settings.ui.theme}
                onChange={(e) => updateSetting('ui', 'theme', e.target.value)}
              >
                <option value="auto">🔄 Auto</option>
                <option value="light">☀️ Light</option>
                <option value="dark">🌙 Dark</option>
              </select>
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <h3>Font Size</h3>
              <p>Adjust text size for readability</p>
            </div>
            <div className="setting-control">
              <select
                value={settings.ui.fontSize}
                onChange={(e) => updateSetting('ui', 'fontSize', e.target.value)}
              >
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Management Section */}
        <motion.div
          className="settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2>🔧 Management</h2>

          <div className="setting-actions">
            <button
              className="action-btn export"
              onClick={exportSettings}
            >
              📤 Export Settings
            </button>

            <label className="action-btn import">
              📥 Import Settings
              <input
                type="file"
                accept=".json"
                onChange={importSettings}
                style={{ display: 'none' }}
              />
            </label>

            <button
              className="action-btn reset"
              onClick={resetSettings}
            >
              🔄 Reset to Defaults
            </button>
          </div>
        </motion.div>

        {/* Version Info */}
        <div className="version-section">
          <h2>ℹ️ About</h2>
          <div className="version-info">
            <p><strong>ZmartyChat Mobile</strong></p>
            <p>Version 1.0.0</p>
            <p>Build: {process.env.REACT_APP_BUILD_NUMBER || 'development'}</p>
            <p>© 2025 ZmartBot. All rights reserved.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;