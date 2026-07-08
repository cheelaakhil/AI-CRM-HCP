/**
 * Redux Toolkit store configuration.
 */
import { configureStore } from '@reduxjs/toolkit';
import interactionReducer from './slices/interactionSlice';
import chatReducer from './slices/chatSlice';
import doctorReducer from './slices/doctorSlice';

const store = configureStore({
  reducer: {
    interactions: interactionReducer,
    chat: chatReducer,
    doctors: doctorReducer,
  },
  devTools: import.meta.env.DEV,
});

export default store;
