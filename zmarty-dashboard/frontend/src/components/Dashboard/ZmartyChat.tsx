import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, CreditCard, Loader2, AlertCircle, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { useMCPAsset, useMCPIcon } from '../../hooks/useMCP';
import { useZmartyChat } from '../../hooks/useZmartyChat';
import { useAuthStore } from '../../stores/authStore';

interface Message {
  id: string;
  content: string;
  type: 'user' | 'system' | 'zmarty';
  timestamp: Date;
  credits_cost?: number;
  request_id?: string;
  processing?: boolean;
}

interface QuickTemplate {
  id: string;
  label: string;
  query: string;
  type: string;
  credits: number;
  icon: string;
}

const QUICK_TEMPLATES: QuickTemplate[] = [
  {
    id: 'btc-analysis',
    label: 'BTC Analysis',
    query: 'What\'s the current technical analysis for Bitcoin?',
    type: 'market_analysis',
    credits: 3,
    icon: 'bitcoin'
  },
  {
    id: 'trading-strategy',
    label: 'Trading Strategy',
    query: 'Suggest a trading strategy for current market conditions',
    type: 'trading_strategy',
    credits: 5,
    icon: 'strategy'
  },
  {
    id: 'market-signals',
    label: 'Market Signals',
    query: 'Show me live trading signals for major cryptocurrencies',
    type: 'live_signals',
    credits: 10,
    icon: 'signals'
  },
  {
    id: 'ai-prediction',
    label: 'AI Prediction',
    query: 'What are your price predictions for the next 24 hours?',
    type: 'ai_predictions',
    credits: 8,
    icon: 'prediction'
  }
];

const ZmartyChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: '👋 Hello! I\'m Zmarty, your AI trading assistant. How can I help you today?',
      type: 'zmarty',
      timestamp: new Date()
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [requestType, setRequestType] = useState('basic_query');
  const [estimatedCost, setEstimatedCost] = useState(1);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { user } = useAuthStore();
  const { sendMessage, isLoading } = useZmartyChat();
  
  // MCP Assets
  const zmartyAvatar = useMCPAsset('zmarty-avatar', '/default-avatars/zmarty.svg');
  const userAvatar = useMCPAsset('user-avatar', '/default-avatars/user.svg');
  const sendIcon = useMCPIcon('send', 'send');
  const creditIcon = useMCPIcon('credit', 'credit-card');

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Calculate estimated cost based on request type and input complexity
    const baseCosts: Record<string, number> = {
      'basic_query': 1,
      'market_analysis': 3,
      'trading_strategy': 5,
      'ai_predictions': 8,
      'live_signals': 10,
      'custom_research': 25
    };
    
    let cost = baseCosts[requestType] || 1;
    
    // Add complexity multiplier based on input length
    if (inputValue.length > 100) cost *= 1.2;
    if (inputValue.length > 200) cost *= 1.5;
    
    setEstimatedCost(Math.ceil(cost));
  }, [requestType, inputValue]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    if (!user || user.credit_balance < estimatedCost) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: '❌ Insufficient credits. Please purchase more credits to continue.',
        type: 'system',
        timestamp: new Date()
      }]);
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      type: 'user',
      timestamp: new Date()
    };

    // Add processing message
    const processingMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: 'Processing your request...',
      type: 'zmarty',
      timestamp: new Date(),
      processing: true,
      credits_cost: estimatedCost
    };

    setMessages(prev => [...prev, userMessage, processingMessage]);
    
    const query = inputValue;
    setInputValue('');

    try {
      const response = await sendMessage({
        query,
        request_type: requestType,
        parameters: {
          complexity: query.length > 100 ? 'high' : 'medium',
          user_tier: user.tier
        }
      });

      // Remove processing message and add response
      setMessages(prev => {
        const withoutProcessing = prev.filter(m => m.id !== processingMessage.id);
        return [...withoutProcessing, {
          id: response.request_id,
          content: response.response,
          type: 'zmarty',
          timestamp: new Date(),
          credits_cost: response.credits_used,
          request_id: response.request_id
        }];
      });

    } catch (error: any) {
      // Remove processing message and add error
      setMessages(prev => {
        const withoutProcessing = prev.filter(m => m.id !== processingMessage.id);
        return [...withoutProcessing, {
          id: Date.now().toString(),
          content: `❌ Error: ${error.message || 'Failed to process request'}`,
          type: 'system',
          timestamp: new Date()
        }];
      });
    }
  };

  const handleQuickTemplate = (template: QuickTemplate) => {
    setInputValue(template.query);
    setRequestType(template.type);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <TooltipProvider>
      <Card className="h-[600px] flex flex-col">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Avatar className="h-10 w-10">
                <AvatarImage src={zmartyAvatar.url} alt="Zmarty" />
                <AvatarFallback>
                  <Bot className="h-5 w-5" />
                </AvatarFallback>
              </Avatar>
              <div>
                <h3 className="font-semibold">Zmarty AI Assistant</h3>
                <p className="text-sm text-muted-foreground">
                  {isLoading ? 'Processing...' : 'Online'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Tooltip>
                <TooltipTrigger>
                  <Badge variant="secondary" className="flex items-center space-x-1">
                    {creditIcon.url ? (
                      <img src={creditIcon.url} alt="Credits" className="h-3 w-3" />
                    ) : (
                      <CreditCard className="h-3 w-3" />
                    )}
                    <span>{user?.credit_balance || 0}</span>
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Your credit balance</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden">
          <div className="h-full flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 pb-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`flex space-x-2 max-w-[80%] ${
                      message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                    }`}
                  >
                    <Avatar className="h-8 w-8 flex-shrink-0">
                      {message.type === 'user' ? (
                        <>
                          <AvatarImage src={userAvatar.url} alt="User" />
                          <AvatarFallback>
                            <User className="h-4 w-4" />
                          </AvatarFallback>
                        </>
                      ) : message.type === 'zmarty' ? (
                        <>
                          <AvatarImage src={zmartyAvatar.url} alt="Zmarty" />
                          <AvatarFallback>
                            <Bot className="h-4 w-4" />
                          </AvatarFallback>
                        </>
                      ) : (
                        <AvatarFallback>
                          <AlertCircle className="h-4 w-4" />
                        </AvatarFallback>
                      )}
                    </Avatar>
                    
                    <div
                      className={`rounded-lg px-4 py-2 ${
                        message.type === 'user'
                          ? 'bg-primary text-primary-foreground ml-2'
                          : message.type === 'system'
                          ? 'bg-muted text-muted-foreground'
                          : 'bg-muted mr-2'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          {message.processing ? (
                            <div className="flex items-center space-x-2">
                              <Loader2 className="h-4 w-4 animate-spin" />
                              <span>{message.content}</span>
                            </div>
                          ) : (
                            <div className="whitespace-pre-wrap">{message.content}</div>
                          )}
                        </div>
                        
                        {message.credits_cost && (
                          <Badge variant="outline" className="ml-2 text-xs">
                            {message.credits_cost} credits
                          </Badge>
                        )}
                      </div>
                      
                      <div className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Templates */}
            <div className="mb-4">
              <p className="text-sm text-muted-foreground mb-2">Quick Actions:</p>
              <div className="flex flex-wrap gap-2">
                {QUICK_TEMPLATES.map((template) => (
                  <Button
                    key={template.id}
                    variant="outline"
                    size="sm"
                    onClick={() => handleQuickTemplate(template)}
                    className="text-xs"
                  >
                    <TrendingUp className="h-3 w-3 mr-1" />
                    {template.label}
                    <Badge variant="secondary" className="ml-1 text-xs">
                      {template.credits}
                    </Badge>
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>

        <CardFooter className="pt-3">
          <div className="w-full space-y-3">
            {/* Request Type Selector */}
            <div className="flex items-center space-x-2">
              <Select value={requestType} onValueChange={setRequestType}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="basic_query">Basic Query (1 credit)</SelectItem>
                  <SelectItem value="market_analysis">Market Analysis (3 credits)</SelectItem>
                  <SelectItem value="trading_strategy">Trading Strategy (5 credits)</SelectItem>
                  <SelectItem value="ai_predictions">AI Predictions (8 credits)</SelectItem>
                  <SelectItem value="live_signals">Live Signals (10 credits)</SelectItem>
                  <SelectItem value="custom_research">Custom Research (25 credits)</SelectItem>
                </SelectContent>
              </Select>
              
              <Badge variant={estimatedCost > (user?.credit_balance || 0) ? 'destructive' : 'secondary'}>
                ~{estimatedCost} credits
              </Badge>
            </div>

            {/* Input */}
            <div className="flex space-x-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask Zmarty anything about cryptocurrency trading..."
                disabled={isLoading}
                className="flex-1"
              />
              
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading || (user?.credit_balance || 0) < estimatedCost}
                size="icon"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : sendIcon.url ? (
                  <img src={sendIcon.url} alt="Send" className="h-4 w-4" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>

            {estimatedCost > (user?.credit_balance || 0) && (
              <p className="text-sm text-destructive">
                Insufficient credits. You need {estimatedCost} credits but only have {user?.credit_balance || 0}.
              </p>
            )}
          </div>
        </CardFooter>
      </Card>
    </TooltipProvider>
  );
};

export default ZmartyChat;