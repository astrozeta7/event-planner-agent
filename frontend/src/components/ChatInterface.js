import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { sendMessage } from '../services/api';
import './ChatInterface.css';

function ChatInterface({ eventData, setEventData, setResults, isSearching, setIsSearching }) {
  const [messages, setMessages] = useState([
    {
      role: 'agent',
      content: "Hi! I'm your Event Planning AI Assistant. Tell me about your event and I'll help you find the perfect venue and catering options. What kind of event are you planning?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await sendMessage(input, eventData);
      
      setIsTyping(false);

      const agentMessage = {
        role: 'agent',
        content: response.message,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, agentMessage]);

      if (response.updated_data) {
        setEventData(response.updated_data);
      }

      if (response.ready_to_search) {
        setIsSearching(true);
        const searchMessage = {
          role: 'agent',
          content: "Perfect! Let me search for the best options for you...",
          timestamp: new Date()
        };
        setMessages(prev => [...prev, searchMessage]);

        const searchResults = await fetch('/plan-event', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(response.updated_data)
        }).then(res => res.json());

        setResults(searchResults);
        setIsSearching(false);

        const resultsMessage = {
          role: 'agent',
          content: `Great news! I found ${searchResults.catering_analysis?.by_cuisine?.length || 0} catering options and ${searchResults.event_rooms?.length || 0} venues for you. Check them out on the right!`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, resultsMessage]);
      }

    } catch (error) {
      setIsTyping(false);
      setIsSearching(false);
      const errorMessage = {
        role: 'agent',
        content: "I'm sorry, I encountered an error. Could you please try again?",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <Sparkles className="header-icon" />
        <h2>Chat with AI Agent</h2>
      </div>

      <div className="messages-container">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className={`message ${message.role}`}
            >
              <div className="message-avatar">
                {message.role === 'agent' ? '🤖' : '👤'}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="message agent"
          >
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
          rows="3"
          disabled={isSearching}
        />
        <button 
          onClick={handleSend} 
          disabled={!input.trim() || isSearching}
          className="send-button"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;
