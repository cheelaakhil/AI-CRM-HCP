/**
 * ChatAssistant — AI chat interface with message history,
 * suggested actions, and extracted entity display.
 */
import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  TextField, IconButton, Chip, CircularProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';

import { sendMessage, addUserMessage, clearChat } from '../../redux/slices/chatSlice';
import { applyAIEntities } from '../../redux/slices/interactionSlice';
import AIResponseCard from '../AIResponseCard/AIResponseCard';

const SUGGESTED_ACTIONS = [
  { label: '📝 Log a meeting', prompt: 'I want to log a new interaction' },
  { label: '🔍 Find a doctor', prompt: 'Search for Dr. Sharma' },
  { label: '📊 View history', prompt: 'Show my recent interactions' },
  { label: '💡 Get recommendations', prompt: 'Suggest follow-up for Dr. Sharma' },
];

function ChatAssistant() {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((state) => state.chat);
  const { formData } = useSelector((state) => state.interactions);
  const { items: doctors } = useSelector((state) => state.doctors);
  
  const selectedDoctor = doctors.find(d => d.id === formData.hcp_id);
  const currentDoctorName = selectedDoctor ? selectedDoctor.name : null;

  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    // Add user message to state
    dispatch(addUserMessage(trimmed));

    // Build conversation history for context
    const conversationHistory = messages
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .slice(-10)
      .map(m => ({ role: m.role, content: typeof m.content === 'string' ? m.content : '' }));

    // Send to agent
    dispatch(sendMessage({ message: trimmed, conversationHistory, currentDoctor: currentDoctorName }));
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestion = (prompt) => {
    setInput(prompt);
    inputRef.current?.focus();
  };

  const handleApplyToForm = (entities) => {
    dispatch(applyAIEntities(entities));
  };

  const handleClear = () => {
    dispatch(clearChat());
  };

  return (
    <div className="chat-container">
      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <React.Fragment key={idx}>
            <div className={`chat-bubble ${msg.role}`}>
              <div className="bubble-label">
                {msg.role === 'user' ? 'You' : 'AI Assistant'}
              </div>

              {/* Tool badge */}
              {msg.toolUsed && (
                <div className="tool-badge">
                  ⚡ {msg.toolUsed.replace(/_/g, ' ')}
                </div>
              )}

              {/* Message content */}
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
            </div>

            {/* AI Response Card with extracted entities */}
            {msg.extractedEntities && Object.keys(msg.extractedEntities).some(k => msg.extractedEntities[k]) && (
              <AIResponseCard
                entities={msg.extractedEntities}
                onApplyToForm={() => handleApplyToForm(msg.extractedEntities)}
                interactionId={msg.interactionId}
              />
            )}
          </React.Fragment>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="typing-indicator">
            <div className="typing-dot" />
            <div className="typing-dot" />
            <div className="typing-dot" />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Actions */}
      {messages.length <= 2 && (
        <div className="suggested-actions">
          {SUGGESTED_ACTIONS.map((action, idx) => (
            <Chip
              key={idx}
              label={action.label}
              variant="outlined"
              size="small"
              onClick={() => handleSuggestion(action.prompt)}
              sx={{
                borderColor: 'rgba(148,163,184,0.2)',
                color: 'text.secondary',
                fontSize: '0.75rem',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: '#6C63FF',
                  color: '#6C63FF',
                  background: 'rgba(108,99,255,0.08)',
                },
              }}
            />
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="chat-input-area">
        <TextField
          fullWidth
          size="small"
          placeholder="Describe your interaction or ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          inputRef={inputRef}
          multiline
          maxRows={3}
          disabled={loading}
        />
        <IconButton
          onClick={handleSend}
          disabled={!input.trim() || loading}
          sx={{
            background: 'linear-gradient(135deg, #6C63FF 0%, #8B83FF 100%)',
            color: 'white',
            borderRadius: '10px',
            width: 42,
            height: 42,
            '&:hover': {
              background: 'linear-gradient(135deg, #5A52E0 0%, #7A73FF 100%)',
            },
            '&:disabled': {
              background: 'rgba(148,163,184,0.1)',
              color: 'rgba(148,163,184,0.3)',
            },
          }}
        >
          {loading ? <CircularProgress size={18} color="inherit" /> : <SendIcon fontSize="small" />}
        </IconButton>
        <IconButton
          onClick={handleClear}
          size="small"
          sx={{ color: 'text.disabled', '&:hover': { color: '#EF4444' } }}
          title="Clear chat"
        >
          <DeleteSweepIcon fontSize="small" />
        </IconButton>
      </div>
    </div>
  );
}

export default ChatAssistant;
