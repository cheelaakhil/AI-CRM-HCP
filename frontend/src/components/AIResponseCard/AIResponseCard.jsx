/**
 * AIResponseCard — Displays extracted entities from AI responses
 * with an "Apply to Form" button to auto-fill the left panel.
 */
import React from 'react';
import { Button, Chip, Box } from '@mui/material';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

function AIResponseCard({ entities, onApplyToForm, interactionId }) {
  if (!entities) return null;

  const entityItems = [
    { label: 'Doctor', value: entities.doctor_name, icon: '👨‍⚕️' },
    { label: 'Date', value: entities.date, icon: '📅' },
    { label: 'Topics', value: entities.topics, icon: '💬' },
    { label: 'Summary', value: entities.summary, icon: '📝' },
    { label: 'Sentiment', value: entities.sentiment, icon: '🎯' },
    { label: 'Outcome', value: entities.outcome, icon: '✅' },
    { label: 'Follow-up', value: entities.follow_up, icon: '📆' },
    { label: 'Type', value: entities.interaction_type?.replace(/_/g, ' '), icon: '🏥' },
  ].filter(item => item.value);

  const products = entities.products || [];
  const materials = entities.materials || [];
  const samples = entities.samples || [];

  if (entityItems.length === 0 && products.length === 0) return null;

  return (
    <div className="ai-response-card">
      <div className="card-header">
        <AutoFixHighIcon sx={{ fontSize: 16, color: '#00D4AA' }} />
        <h4>Extracted Entities</h4>
        {interactionId && (
          <Chip
            icon={<CheckCircleIcon sx={{ fontSize: 14 }} />}
            label={`Saved #${interactionId}`}
            size="small"
            sx={{
              ml: 'auto',
              background: 'rgba(16, 185, 129, 0.12)',
              color: '#10B981',
              fontSize: '0.7rem',
              height: 24,
            }}
          />
        )}
      </div>

      {/* Entity Grid */}
      <div className="entity-grid">
        {entityItems.map((item, idx) => (
          <div className="entity-item" key={idx}>
            <div className="entity-label">{item.icon} {item.label}</div>
            <div className="entity-value">
              {item.label === 'Sentiment' ? (
                <Chip
                  label={item.value}
                  size="small"
                  className={`sentiment-${item.value}`}
                  sx={{ height: 22, fontSize: '0.7rem' }}
                />
              ) : (
                item.value
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Products */}
      {products.length > 0 && (
        <Box sx={{ mt: 1.5 }}>
          <div className="entity-label" style={{ marginBottom: 6 }}>💊 Products</div>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {products.map((p, idx) => (
              <Chip key={idx} label={p} size="small" variant="outlined"
                sx={{ fontSize: '0.7rem', borderColor: 'rgba(108,99,255,0.3)', color: '#8B83FF' }} />
            ))}
          </Box>
        </Box>
      )}

      {/* Materials */}
      {materials.length > 0 && (
        <Box sx={{ mt: 1 }}>
          <div className="entity-label" style={{ marginBottom: 6 }}>📦 Materials</div>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {materials.map((m, idx) => (
              <Chip key={idx} label={`${m.medicine_name} (×${m.quantity})`} size="small" variant="outlined"
                sx={{ fontSize: '0.7rem', borderColor: 'rgba(0,212,170,0.3)', color: '#00D4AA' }} />
            ))}
          </Box>
        </Box>
      )}

      {/* Samples */}
      {samples.length > 0 && (
        <Box sx={{ mt: 1 }}>
          <div className="entity-label" style={{ marginBottom: 6 }}>🧪 Samples</div>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {samples.map((s, idx) => (
              <Chip key={idx} label={`${s.sample_name} (×${s.count})`} size="small" variant="outlined"
                sx={{ fontSize: '0.7rem', borderColor: 'rgba(245,158,11,0.3)', color: '#F59E0B' }} />
            ))}
          </Box>
        </Box>
      )}

      {/* Apply to Form Button */}
      <Button
        fullWidth
        variant="outlined"
        startIcon={<AutoFixHighIcon />}
        onClick={onApplyToForm}
        sx={{
          mt: 2,
          borderColor: 'rgba(0,212,170,0.3)',
          color: '#00D4AA',
          fontSize: '0.8rem',
          '&:hover': {
            borderColor: '#00D4AA',
            background: 'rgba(0,212,170,0.08)',
          },
        }}
      >
        Apply to Form
      </Button>
    </div>
  );
}

export default AIResponseCard;
