import React from 'react';
import { View, Text } from 'react-native';

type Evidence = { source: string; text: string };

export default function EvidenceChips({ evidence }: { evidence: Evidence[] }) {
  if (!evidence?.length) return null;
  
  const sourceColors = {
    'RSI': { bg: 'rgba(147, 51, 234, 0.1)', border: 'rgba(147, 51, 234, 0.3)', text: '#C4B5FD' },
    'MACD': { bg: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.3)', text: '#93C5FD' },
    'Volume': { bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.3)', text: '#86EFAC' },
    'Price': { bg: 'rgba(249, 115, 22, 0.1)', border: 'rgba(249, 115, 22, 0.3)', text: '#FDBA74' },
    'Default': { bg: 'rgba(100, 116, 139, 0.1)', border: 'rgba(100, 116, 139, 0.3)', text: '#CBD5E1' }
  };
  
  const getSourceStyle = (source: string) => {
    const upperSource = source.toUpperCase();
    if (upperSource.includes('RSI')) return sourceColors.RSI;
    if (upperSource.includes('MACD')) return sourceColors.MACD;
    if (upperSource.includes('VOLUME')) return sourceColors.Volume;
    if (upperSource.includes('PRICE')) return sourceColors.Price;
    return sourceColors.Default;
  };
  
  return (
    <View>
      <Text style={{color: '#94A3B8', fontSize: 12, fontWeight: '500', marginBottom: 8}}>
        📋 Evidence
      </Text>
      <View style={{flexDirection: 'row', flexWrap: 'wrap', gap: 8}}>
        {evidence.slice(0, 4).map((e, idx) => {
          const style = getSourceStyle(e.source);
          return (
            <View 
              key={idx} 
              style={{
                backgroundColor: style.bg,
                borderColor: style.border,
                borderWidth: 1,
                borderRadius: 12,
                paddingHorizontal: 12,
                paddingVertical: 8,
                maxWidth: '100%'
              }}
            >
              <Text style={{
                color: style.text,
                fontSize: 12,
                fontWeight: '500',
                marginBottom: 4
              }}>
                {e.source}
              </Text>
              <Text style={{
                color: '#CBD5E1',
                fontSize: 12,
                lineHeight: 16
              }}>
                {e.text.length > 60 ? `${e.text.substring(0, 60)}...` : e.text}
              </Text>
            </View>
          );
        })}
      </View>
      {evidence.length > 4 && (
        <Text style={{
          color: '#64748B',
          fontSize: 12,
          marginTop: 8
        }}>
          +{evidence.length - 4} more signals
        </Text>
      )}
    </View>
  );
}
