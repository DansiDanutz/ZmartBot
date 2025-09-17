import React from 'react';
import { View, ViewStyle } from 'react-native';
import { cn } from '../../lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  style?: ViewStyle;
  variant?: 'default' | 'elevated' | 'outlined' | 'glass';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
}

export function Card({ 
  children, 
  className, 
  style, 
  variant = 'default',
  padding = 'md' 
}: CardProps) {
  const baseStyles = "rounded-2xl overflow-hidden";
  
  const variantStyles = {
    default: "bg-gray-900 border border-gray-800",
    elevated: "bg-gray-900 shadow-2xl shadow-black/50",
    outlined: "bg-transparent border-2 border-gray-700",
    glass: "bg-gray-900/80 backdrop-blur-xl border border-gray-700/50"
  };
  
  const paddingStyles = {
    none: "",
    sm: "p-3",
    md: "p-4",
    lg: "p-6",
    xl: "p-8"
  };

  return (
    <View 
      className={cn(
        baseStyles,
        variantStyles[variant],
        paddingStyles[padding],
        className
      )}
      style={[
        {
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 8 },
          shadowOpacity: variant === 'elevated' ? 0.3 : 0.1,
          shadowRadius: variant === 'elevated' ? 24 : 12,
          elevation: variant === 'elevated' ? 8 : 4,
        },
        style
      ]}
    >
      {children}
    </View>
  );
}

export function CardHeader({ 
  children, 
  className 
}: { 
  children: React.ReactNode; 
  className?: string; 
}) {
  return (
    <View className={cn("flex-row items-center justify-between p-4 pb-2", className)}>
      {children}
    </View>
  );
}

export function CardContent({ 
  children, 
  className 
}: { 
  children: React.ReactNode; 
  className?: string; 
}) {
  return (
    <View className={cn("px-4 pb-4", className)}>
      {children}
    </View>
  );
}

export function CardFooter({ 
  children, 
  className 
}: { 
  children: React.ReactNode; 
  className?: string; 
}) {
  return (
    <View className={cn("flex-row items-center justify-between p-4 pt-2", className)}>
      {children}
    </View>
  );
}
