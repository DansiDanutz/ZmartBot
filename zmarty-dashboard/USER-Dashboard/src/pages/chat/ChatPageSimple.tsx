import React, { useState } from 'react'

const ChatPageSimple: React.FC = () => {
  const [messages, setMessages] = useState([
    { id: 1, text: "👋 Hello! I'm Zmarty, your AI trading assistant. How can I help you today?", sender: 'AI', timestamp: new Date() }
  ])
  const [inputText, setInputText] = useState('')

  const sendMessage = () => {
    if (!inputText.trim()) return
    
    const newMessage = {
      id: messages.length + 1,
      text: inputText,
      sender: 'User',
      timestamp: new Date()
    }
    
    setMessages([...messages, newMessage])
    setInputText('')
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        text: "🤖 Thanks for your message! I'm analyzing market data across all your connected exchanges (KuCoin, Binance) and trading orchestration services. How can I assist with your trading strategies?",
        sender: 'AI',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiResponse])
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">💬 Zmarty AI Chat</h1>
            <p className="text-slate-300">Your AI Trading Intelligence Assistant</p>
          </div>
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => window.location.href = '/dashboard'}
              className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              ← Back to Dashboard
            </button>
            <div className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center">
              <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></div>
              All APIs Connected
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 h-[calc(100vh-200px)] flex flex-col">
        {/* Messages Area */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.sender === 'User' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] p-4 rounded-2xl ${
                message.sender === 'User' 
                  ? 'bg-blue-600 text-white ml-auto' 
                  : 'bg-slate-800 text-white'
              }`}>
                <p className="text-sm">{message.text}</p>
                <p className="text-xs opacity-60 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-white/20">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask Zmarty about market trends, trading strategies, portfolio analysis..."
              className="flex-1 bg-slate-800 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={sendMessage}
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-3 rounded-xl font-medium transition-all duration-300 transform hover:scale-105"
            >
              Send 🚀
            </button>
          </div>
          
          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2 mt-4">
            {[
              "📊 Market Analysis",
              "📈 Portfolio Status", 
              "🎯 Trading Signals",
              "⚡ Exchange Status",
              "🤖 AI Insights"
            ].map((action, i) => (
              <button
                key={i}
                onClick={() => setInputText(action.replace(/[📊📈🎯⚡🤖]\s/, ''))}
                className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1 rounded-lg text-sm transition-colors"
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatPageSimple