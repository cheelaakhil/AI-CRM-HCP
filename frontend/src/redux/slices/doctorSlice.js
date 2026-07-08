/**
 * Doctor Redux slice — manages HCP state.
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchDoctors = createAsyncThunk(
  'doctors/fetchAll',
  async (query = '') => {
    const params = query ? { q: query } : {};
    const response = await api.get('/doctors', { params });
    return response.data;
  }
);

const doctorSlice = createSlice({
  name: 'doctors',
  initialState: {
    items: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDoctors.pending, (state) => { state.loading = true; })
      .addCase(fetchDoctors.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchDoctors.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export default doctorSlice.reducer;
