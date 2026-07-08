/**
 * Interaction Redux slice — manages form CRUD state.
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// ─── Async Thunks ───────────────────────────────────────────────────

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchAll',
  async ({ skip = 0, limit = 50, hcp_id } = {}) => {
    const params = { skip, limit };
    if (hcp_id) params.hcp_id = hcp_id;
    const response = await api.get('/interactions', { params });
    return response.data;
  }
);

export const createInteraction = createAsyncThunk(
  'interactions/create',
  async (data) => {
    const response = await api.post('/interactions', data);
    return response.data;
  }
);

export const updateInteraction = createAsyncThunk(
  'interactions/update',
  async ({ id, data }) => {
    const response = await api.put(`/interactions/${id}`, data);
    return response.data;
  }
);

export const deleteInteraction = createAsyncThunk(
  'interactions/delete',
  async (id) => {
    await api.delete(`/interactions/${id}`);
    return id;
  }
);

// ─── Slice ──────────────────────────────────────────────────────────

const initialFormData = {
  hcp_id: '',
  date: new Date().toISOString().split('T')[0],
  interaction_type: 'in_person',
  topics: '',
  summary: '',
  sentiment: 'neutral',
  outcome: '',
  follow_up: '',
  materials: [],
  samples: [],
};

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    items: [],
    total: 0,
    loading: false,
    error: null,
    selectedInteraction: null,
    formData: { ...initialFormData },
    saveSuccess: false,
  },
  reducers: {
    setFormData: (state, action) => {
      state.formData = { ...state.formData, ...action.payload };
    },
    resetFormData: (state) => {
      state.formData = { ...initialFormData, date: new Date().toISOString().split('T')[0] };
      state.saveSuccess = false;
    },
    setSelectedInteraction: (state, action) => {
      state.selectedInteraction = action.payload;
    },
    clearSaveSuccess: (state) => {
      state.saveSuccess = false;
    },
    applyAIEntities: (state, action) => {
      const entities = action.payload;
      if (entities.doctor_id) state.formData.hcp_id = entities.doctor_id;
      if (entities.date) state.formData.date = entities.date;
      if (entities.interaction_type) state.formData.interaction_type = entities.interaction_type;
      if (entities.topics) state.formData.topics = entities.topics;
      if (entities.summary) state.formData.summary = entities.summary;
      if (entities.sentiment) state.formData.sentiment = entities.sentiment;
      if (entities.outcome) state.formData.outcome = entities.outcome;
      if (entities.follow_up) state.formData.follow_up = entities.follow_up;
      if (entities.materials?.length) state.formData.materials = entities.materials;
      if (entities.samples?.length) state.formData.samples = entities.samples;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch
      .addCase(fetchInteractions.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.interactions;
        state.total = action.payload.total;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Create
      .addCase(createInteraction.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.items.unshift(action.payload);
        state.total += 1;
        state.saveSuccess = true;
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Update
      .addCase(updateInteraction.fulfilled, (state, action) => {
        const idx = state.items.findIndex(i => i.id === action.payload.id);
        if (idx !== -1) state.items[idx] = action.payload;
      })
      // Delete
      .addCase(deleteInteraction.fulfilled, (state, action) => {
        state.items = state.items.filter(i => i.id !== action.payload);
        state.total -= 1;
      });
  },
});

export const { setFormData, resetFormData, setSelectedInteraction, clearSaveSuccess, applyAIEntities } = interactionSlice.actions;
export default interactionSlice.reducer;
