/**
 * InteractionForm — Traditional form for logging doctor interactions.
 * Includes doctor search, date/time, topics, materials, samples,
 * sentiment, outcome, and follow-up.
 */
import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  TextField, Button, MenuItem, Select, FormControl, InputLabel,
  Autocomplete, IconButton, Chip, Box, Alert, CircularProgress,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import SaveIcon from '@mui/icons-material/Save';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import CheckCircleOutlinedIcon from '@mui/icons-material/CheckCircleOutlined';

import { fetchDoctors } from '../../redux/slices/doctorSlice';
import {
  setFormData, resetFormData, createInteraction, clearSaveSuccess,
} from '../../redux/slices/interactionSlice';

function InteractionForm() {
  const dispatch = useDispatch();
  const { formData, loading, saveSuccess, error } = useSelector((state) => state.interactions);
  const { items: doctors, loading: doctorsLoading } = useSelector((state) => state.doctors);
  const [doctorSearch, setDoctorSearch] = useState('');

  useEffect(() => {
    dispatch(fetchDoctors());
  }, [dispatch]);

  useEffect(() => {
    if (doctorSearch.length >= 1) {
      dispatch(fetchDoctors(doctorSearch));
    } else {
      dispatch(fetchDoctors()); // Fetch all when cleared
    }
  }, [doctorSearch, dispatch]);

  const handleChange = (field) => (e) => {
    dispatch(setFormData({ [field]: e.target.value }));
  };

  const handleDoctorSelect = (event, doctor) => {
    if (doctor) {
      dispatch(setFormData({ hcp_id: doctor.id }));
    }
  };

  // ─── Materials Management ───────────────────────────────────────
  const addMaterial = () => {
    const materials = [...(formData.materials || []), { medicine_name: '', quantity: 1 }];
    dispatch(setFormData({ materials }));
  };

  const updateMaterial = (index, field, value) => {
    const materials = [...(formData.materials || [])];
    materials[index] = { ...materials[index], [field]: value };
    dispatch(setFormData({ materials }));
  };

  const removeMaterial = (index) => {
    const materials = (formData.materials || []).filter((_, i) => i !== index);
    dispatch(setFormData({ materials }));
  };

  // ─── Samples Management ────────────────────────────────────────
  const addSample = () => {
    const samples = [...(formData.samples || []), { sample_name: '', count: 1 }];
    dispatch(setFormData({ samples }));
  };

  const updateSample = (index, field, value) => {
    const samples = [...(formData.samples || [])];
    samples[index] = { ...samples[index], [field]: value };
    dispatch(setFormData({ samples }));
  };

  const removeSample = (index) => {
    const samples = (formData.samples || []).filter((_, i) => i !== index);
    dispatch(setFormData({ samples }));
  };

  // ─── Submit ─────────────────────────────────────────────────────
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.hcp_id) return;

    const payload = {
      ...formData,
      hcp_id: parseInt(formData.hcp_id),
      materials: (formData.materials || []).filter(m => m.medicine_name),
      samples: (formData.samples || []).filter(s => s.sample_name),
    };
    dispatch(createInteraction(payload));
  };

  const handleReset = () => {
    dispatch(resetFormData());
  };

  const selectedDoctor = doctors.find(d => d.id === formData.hcp_id);

  return (
    <form onSubmit={handleSubmit}>
      {/* Success Banner */}
      {saveSuccess && (
        <div className="success-banner">
          <CheckCircleOutlinedIcon sx={{ color: '#10B981' }} />
          <span style={{ fontSize: '0.85rem', color: '#10B981', fontWeight: 500 }}>
            Interaction saved successfully!
          </span>
          <Button
            size="small"
            onClick={() => dispatch(clearSaveSuccess())}
            sx={{ ml: 'auto', color: '#10B981', fontSize: '0.75rem' }}
          >
            Dismiss
          </Button>
        </div>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>
      )}

      {/* Doctor Selection */}
      <div className="form-section">
        <div className="form-section-title">Doctor Information</div>
        <Autocomplete
          options={doctors}
          getOptionLabel={(option) => `${option.name}${option.specialization ? ` — ${option.specialization}` : ''}${option.hospital ? ` (${option.hospital})` : ''}`}
          value={selectedDoctor || null}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          onChange={handleDoctorSelect}
          onInputChange={(e, val, reason) => {
            if (reason === 'input') {
              setDoctorSearch(val);
            } else if (reason === 'clear') {
              setDoctorSearch('');
            }
          }}
          loading={doctorsLoading}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Search Doctor / HCP"
              placeholder="Start typing doctor name..."
              size="small"
              required
            />
          )}
          renderOption={(props, option) => {
            const { key, ...rest } = props;
            return (
              <li key={key} {...rest} style={{ padding: '8px 16px' }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{option.name}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>
                    {option.specialization} • {option.hospital} • {option.city}
                  </div>
                </div>
              </li>
            );
          }}
          sx={{ mb: 1 }}
        />
      </div>

      {/* Date & Type */}
      <div className="form-section">
        <div className="form-section-title">Interaction Details</div>
        <div className="form-row">
          <TextField
            label="Date"
            type="date"
            size="small"
            value={formData.date}
            onChange={handleChange('date')}
            slotProps={{ inputLabel: { shrink: true } }}
          />
          <FormControl size="small" sx={{ flex: 1 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={formData.interaction_type}
              label="Type"
              onChange={handleChange('interaction_type')}
            >
              <MenuItem value="in_person">In Person</MenuItem>
              <MenuItem value="virtual">Virtual</MenuItem>
              <MenuItem value="phone">Phone</MenuItem>
              <MenuItem value="email">Email</MenuItem>
              <MenuItem value="conference">Conference</MenuItem>
            </Select>
          </FormControl>
        </div>

        <TextField
          label="Topics Discussed"
          size="small"
          fullWidth
          multiline
          rows={2}
          value={formData.topics}
          onChange={handleChange('topics')}
          placeholder="e.g., Diabetes management, drug efficacy..."
          sx={{ mb: 1.5 }}
        />

        <TextField
          label="Summary"
          size="small"
          fullWidth
          multiline
          rows={3}
          value={formData.summary}
          onChange={handleChange('summary')}
          placeholder="Brief summary of the interaction..."
          sx={{ mb: 1.5 }}
        />
      </div>

      {/* Materials */}
      <div className="form-section">
        <div className="form-section-title">Materials Discussed</div>
        <div className="dynamic-list">
          {(formData.materials || []).map((mat, idx) => (
            <div className="dynamic-list-item" key={idx}>
              <TextField
                size="small"
                placeholder="Medicine name"
                value={mat.medicine_name}
                onChange={(e) => updateMaterial(idx, 'medicine_name', e.target.value)}
                sx={{ flex: 2 }}
              />
              <TextField
                size="small"
                type="number"
                placeholder="Qty"
                value={mat.quantity}
                onChange={(e) => updateMaterial(idx, 'quantity', parseInt(e.target.value) || 0)}
                sx={{ flex: 0.5, minWidth: 70 }}
              />
              <IconButton size="small" onClick={() => removeMaterial(idx)} sx={{ color: '#EF4444' }}>
                <DeleteOutlinedIcon fontSize="small" />
              </IconButton>
            </div>
          ))}
        </div>
        <Button
          startIcon={<AddIcon />}
          size="small"
          onClick={addMaterial}
          className="add-item-btn"
          sx={{ color: 'text.secondary', fontSize: '0.75rem', mt: 0.5 }}
        >
          Add Material
        </Button>
      </div>

      {/* Samples */}
      <div className="form-section">
        <div className="form-section-title">Samples Distributed</div>
        <div className="dynamic-list">
          {(formData.samples || []).map((samp, idx) => (
            <div className="dynamic-list-item" key={idx}>
              <TextField
                size="small"
                placeholder="Sample name"
                value={samp.sample_name}
                onChange={(e) => updateSample(idx, 'sample_name', e.target.value)}
                sx={{ flex: 2 }}
              />
              <TextField
                size="small"
                type="number"
                placeholder="Count"
                value={samp.count}
                onChange={(e) => updateSample(idx, 'count', parseInt(e.target.value) || 0)}
                sx={{ flex: 0.5, minWidth: 70 }}
              />
              <IconButton size="small" onClick={() => removeSample(idx)} sx={{ color: '#EF4444' }}>
                <DeleteOutlinedIcon fontSize="small" />
              </IconButton>
            </div>
          ))}
        </div>
        <Button
          startIcon={<AddIcon />}
          size="small"
          onClick={addSample}
          className="add-item-btn"
          sx={{ color: 'text.secondary', fontSize: '0.75rem', mt: 0.5 }}
        >
          Add Sample
        </Button>
      </div>

      {/* Sentiment & Outcome */}
      <div className="form-section">
        <div className="form-section-title">Outcome & Sentiment</div>
        <div className="form-row">
          <FormControl size="small" sx={{ flex: 1 }}>
            <InputLabel>Sentiment</InputLabel>
            <Select
              value={formData.sentiment}
              label="Sentiment"
              onChange={handleChange('sentiment')}
            >
              <MenuItem value="positive">
                <Chip label="Positive" size="small" className="sentiment-positive" sx={{ cursor: 'pointer' }} />
              </MenuItem>
              <MenuItem value="neutral">
                <Chip label="Neutral" size="small" className="sentiment-neutral" sx={{ cursor: 'pointer' }} />
              </MenuItem>
              <MenuItem value="negative">
                <Chip label="Negative" size="small" className="sentiment-negative" sx={{ cursor: 'pointer' }} />
              </MenuItem>
            </Select>
          </FormControl>
        </div>

        <TextField
          label="Outcome"
          size="small"
          fullWidth
          multiline
          rows={2}
          value={formData.outcome}
          onChange={handleChange('outcome')}
          placeholder="e.g., Doctor agreed to prescribe..."
          sx={{ mb: 1.5 }}
        />

        <TextField
          label="Follow-up Plan"
          size="small"
          fullWidth
          value={formData.follow_up}
          onChange={handleChange('follow_up')}
          placeholder="e.g., Next visit on Tuesday..."
        />
      </div>

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 1.5, mt: 3 }}>
        <Button
          type="submit"
          variant="contained"
          startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <SaveIcon />}
          disabled={loading || !formData.hcp_id}
          sx={{ flex: 1 }}
        >
          {loading ? 'Saving...' : 'Save Interaction'}
        </Button>
        <Button
          variant="outlined"
          startIcon={<RestartAltIcon />}
          onClick={handleReset}
          sx={{ color: 'text.secondary', borderColor: 'rgba(148,163,184,0.2)' }}
        >
          Reset
        </Button>
      </Box>
    </form>
  );
}

export default InteractionForm;
