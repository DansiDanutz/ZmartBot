import React from 'react';
import { View, Text, ViewStyle } from 'react-native';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'compact' | 'dense';
}

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = "", 
  variant = "default" 
}) => {
  const variantClasses = {
    default: "p-4",
    compact: "p-3",
    dense: "p-2"
  };

  return (
    <View className={`bg-binance-bg-secondary border border-binance-border rounded-sm ${variantClasses[variant]} ${className}`}>
      {children}
    </View>
  );
};

export const CardHeader: React.FC<CardHeaderProps> = ({ 
  children, 
  className = "" 
}) => {
  return (
    <View className={`mb-3 ${className}`}>
      {children}
    </View>
  );
};

export const CardTitle: React.FC<CardTitleProps> = ({ 
  children, 
  className = "" 
}) => {
  return (
    <Text className={`text-binance-text-primary text-sm font-medium ${className}`}>
      {children}
    </Text>
  );
};

export const CardContent: React.FC<CardContentProps> = ({ 
  children, 
  className = "" 
}) => {
  return (
    <View className={className}>
      {children}
    </View>
  );
};