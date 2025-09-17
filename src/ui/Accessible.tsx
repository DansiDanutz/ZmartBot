import React from 'react';
import { Pressable, Text, PressableProps, TextProps, ViewStyle, TextStyle } from 'react-native';

interface A11yPressableProps extends PressableProps {
  accessibilityLabel: string;
  accessibilityRole?: 'button' | 'link' | 'tab' | 'menuitem' | 'checkbox' | 'radio' | 'switch';
  accessibilityHint?: string;
  accessibilityState?: {
    disabled?: boolean;
    selected?: boolean;
    checked?: boolean;
    busy?: boolean;
    expanded?: boolean;
  };
  style?: ViewStyle | ViewStyle[];
}

interface A11yTextProps extends TextProps {
  allowFontScaling?: boolean;
  accessibilityRole?: 'header' | 'text' | 'link' | 'button';
  accessibilityLabel?: string;
  style?: TextStyle | TextStyle[];
}

export function A11yPressable({ 
  accessibilityLabel, 
  accessibilityRole = 'button',
  accessibilityHint,
  accessibilityState,
  style,
  ...props 
}: A11yPressableProps) {
  return (
    <Pressable
      accessibilityRole={accessibilityRole}
      accessibilityLabel={accessibilityLabel}
      accessibilityHint={accessibilityHint}
      accessibilityState={accessibilityState}
      style={style}
      {...props}
    />
  );
}

export function A11yText({ 
  allowFontScaling = true,
  accessibilityRole = 'text',
  accessibilityLabel,
  style,
  ...props 
}: A11yTextProps) {
  return (
    <Text
      allowFontScaling={allowFontScaling}
      accessibilityRole={accessibilityRole}
      accessibilityLabel={accessibilityLabel}
      style={style}
      {...props}
    />
  );
}

// Specialized accessible components
export function A11yButton({ 
  title, 
  onPress, 
  disabled = false,
  style,
  ...props 
}: {
  title: string;
  onPress: () => void;
  disabled?: boolean;
  style?: ViewStyle;
} & Omit<A11yPressableProps, 'accessibilityLabel' | 'onPress'>) {
  return (
    <A11yPressable
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityHint={`Double tap to ${title.toLowerCase()}`}
      accessibilityState={{ disabled }}
      onPress={onPress}
      disabled={disabled}
      style={[
        {
          padding: 16,
          borderRadius: 8,
          backgroundColor: disabled ? '#2B3139' : '#0ECB81',
          alignItems: 'center',
          justifyContent: 'center',
        },
        style
      ]}
      {...props}
    >
      <A11yText
        style={{
          color: disabled ? '#6B7280' : '#FFFFFF',
          fontSize: 16,
          fontWeight: '600',
        }}
        accessibilityRole="text"
      >
        {title}
      </A11yText>
    </A11yPressable>
  );
}

export function A11yHeader({ 
  children, 
  level = 1,
  style,
  ...props 
}: {
  children: React.ReactNode;
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  style?: TextStyle;
} & Omit<A11yTextProps, 'accessibilityRole'>) {
  const headerStyles = {
    1: { fontSize: 32, fontWeight: 'bold' as const },
    2: { fontSize: 28, fontWeight: 'bold' as const },
    3: { fontSize: 24, fontWeight: '600' as const },
    4: { fontSize: 20, fontWeight: '600' as const },
    5: { fontSize: 18, fontWeight: '600' as const },
    6: { fontSize: 16, fontWeight: '600' as const },
  };

  return (
    <A11yText
      accessibilityRole="header"
      accessibilityLabel={`Heading level ${level}: ${typeof children === 'string' ? children : 'Header'}`}
      style={[
        {
          color: '#EAECEF',
          ...headerStyles[level],
        },
        style
      ]}
      {...props}
    >
      {children}
    </A11yText>
  );
}

export function A11yLink({ 
  title, 
  url, 
  onPress,
  style,
  ...props 
}: {
  title: string;
  url?: string;
  onPress?: () => void;
  style?: TextStyle;
} & Omit<A11yTextProps, 'accessibilityRole' | 'onPress'>) {
  return (
    <A11yText
      accessibilityRole="link"
      accessibilityLabel={title}
      accessibilityHint={url ? `Opens ${url}` : 'Double tap to activate'}
      onPress={onPress}
      style={[
        {
          color: '#0ECB81',
          textDecorationLine: 'underline',
          fontSize: 16,
        },
        style
      ]}
      {...props}
    >
      {title}
    </A11yText>
  );
}
