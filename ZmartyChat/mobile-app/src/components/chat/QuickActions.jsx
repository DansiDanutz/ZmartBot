import React from 'react';

const QuickActions = ({ onActionSelect }) => {
  const actions = [
    { id: 'btc-price', label: '📊 BTC Price', query: 'What is the current BTC price?' },
    { id: 'hot-coins', label: '🔥 Hot Coins', query: 'Show me trending cryptocurrencies' },
    { id: 'whale-activity', label: '🐋 Whale Alert', query: 'Any recent whale movements?' },
    { id: 'market-analysis', label: '📈 Analysis', query: 'Analyze the crypto market' }
  ];

  return (
    <div className="quick-actions">
      {actions.map(action => (
        <button
          key={action.id}
          className="quick-action-btn"
          onClick={() => onActionSelect(action.query)}
        >
          {action.label}
        </button>
      ))}
    </div>
  );
};

export default QuickActions;