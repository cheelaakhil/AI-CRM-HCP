/**
 * Chat Redux slice — manages AI assistant state.
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ message, conversationHistory, currentDoctor }) => {
    const response = await api.post('/chat', {
      message,
      conversation_history: conversationHistory || [],
      current_doctor: currentDoctor,
    });
    return response.data;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      {
        role: 'assistant',
        content: 'Hello! I\'m your AI CRM assistant. I can help you log interactions, search for doctors, view history, and more. Just describe your meeting or ask me anything!',
      },
    ],
    loading: false,
    error: null,
    extractedEntities: null,
    lastToolUsed: null,
    lastInteractionId: null,
  },
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({ role: 'user', content: action.payload });
    },
    clearChat: (state) => {
      state.messages = [
        {
          role: 'assistant',
          content: 'Chat cleared. How can I help you?',
        },
      ];
      state.extractedEntities = null;
      state.lastToolUsed = null;
      state.lastInteractionId = null;
    },
    clearEntities: (state) => {
      state.extractedEntities = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.messages.push({
          role: 'assistant',
          content: action.payload.message,
          extractedEntities: action.payload.extracted_entities,
          toolUsed: action.payload.tool_used,
          interactionId: action.payload.interaction_id,
        });
        state.extractedEntities = action.payload.extracted_entities;
        state.lastToolUsed = action.payload.tool_used;
        state.lastInteractionId = action.payload.interaction_id;
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        state.messages.push({
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        });
      });
  },
});

export const { addUserMessage, clearChat, clearEntities } = chatSlice.actions;
export default chatSlice.reducer;
