/**
 * LogInteraction — Split-screen page: Form (left) + AI Chat (right).
 */
import React from 'react';
import InteractionForm from '../components/InteractionForm/InteractionForm';
import ChatAssistant from '../components/ChatAssistant/ChatAssistant';

function LogInteraction() {
  return (
    <div className="split-screen">
      {/* Left Panel — Traditional Form */}
      <div className="split-panel form-panel">
        <div className="panel-header">
          <div className="header-icon form-icon">📋</div>
          <div>
            <h2>Traditional Form</h2>
          </div>
          <span className="header-badge form-badge">Manual Entry</span>
        </div>
        <InteractionForm />
      </div>

      {/* Right Panel — AI Chat Assistant */}
      <div className="split-panel">
        <div className="panel-header">
          <div className="header-icon chat-icon">🤖</div>
          <div>
            <h2>AI Assistant</h2>
          </div>
          <span className="header-badge chat-badge">Powered by Llama 3</span>
        </div>
        <ChatAssistant />
      </div>
    </div>
  );
}

export default LogInteraction;
