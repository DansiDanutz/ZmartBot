import React from 'react';
import { View, Text, StyleSheet, ViewProps } from 'react-native';

interface CardProps extends ViewProps {
  children: React.ReactNode;
  variant?: string;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, style, ...props }) => {
  return (
    <View style={[styles.card, style]} {...props}>
      {children}
    </View>
  );
};

export const CardHeader: React.FC<CardProps> = ({ children, style, ...props }) => {
  return (
    <View style={[styles.cardHeader, style]} {...props}>
      {children}
    </View>
  );
};

export const CardContent: React.FC<CardProps> = ({ children, style, ...props }) => {
  return (
    <View style={[styles.cardContent, style]} {...props}>
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'rgba(30, 41, 59, 0.8)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(71, 85, 105, 0.3)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    overflow: 'hidden',
  },
  cardHeader: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(71, 85, 105, 0.3)',
  },
  cardContent: {
    padding: 16,
  },
});