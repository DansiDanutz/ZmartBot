import { create } from 'zustand';

export interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  symbol?: string;
  data?: any;
}

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  currentSymbol: string;
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  setLoading: (loading: boolean) => void;
  setCurrentSymbol: (symbol: string) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [
    {
      id: '1',
      type: 'bot',
      content: 'Hey there! I\'m Zmarty, your personal trading buddy! 🤝 Before we dive into some sick crypto signals, what should I call you? Drop me your name and let\'s get this party started! 💎🚀',
      timestamp: new Date(),
    },
  ],
  isLoading: false,
  currentSymbol: 'ETH',
  addMessage: (message) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    set((state) => ({
      messages: [...state.messages, newMessage],
    }));
  },
  setLoading: (loading) => set({ isLoading: loading }),
  setCurrentSymbol: (symbol) => set({ currentSymbol: symbol }),
  clearMessages: () =>
    set({
      messages: [
        {
          id: '1',
          type: 'bot',
          content: 'Hey there! I\'m Zmarty, your personal trading buddy! 🤝 Before we dive into some sick crypto signals, what should I call you? Drop me your name and let\'s get this party started! 💎🚀',
          timestamp: new Date(),
        },
      ],
    }),
}));