import React, { useState } from 'react';
import { X, RefreshCw, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';

interface RetrainModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentHorizon: number;
  currentServiceLevel: string;
  onSuccess: (message: string) => void;
}

export const RetrainModal: React.FC<RetrainModalProps> = ({
  isOpen,
  onClose,
  currentHorizon,
  currentServiceLevel,
  onSuccess,
}) => {
  const [horizon, setHorizon] = useState<number>(currentHorizon || 14);
  const [serviceLevel, setServiceLevel] = useState<string>(currentServiceLevel || '95%');
  const [modelType, setModelType] = useState<string>('RandomForest');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.trainModels({
        forecast_horizon_days: horizon,
        service_level: serviceLevel,
        model_type: modelType,
      });
      onSuccess(res.message || 'Models successfully retrained.');
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to retrain models. Please check backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3 className="panel-title">Model Training & Horizon Settings</h3>
            <p className="panel-subtitle">Configure forecast parameters and supervised ML regression algorithm</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onClose} aria-label="Close modal">
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div className="alert-box alert-critical">
                <span>{error}</span>
              </div>
            )}

            <div className="form-group">
              <label className="form-label" htmlFor="horizon-select">
                Forecast Horizon
              </label>
              <select
                id="horizon-select"
                className="form-select"
                value={horizon}
                onChange={(e) => setHorizon(Number(e.target.value))}
              >
                <option value={7}>7 Days (Short-term weekly operational replenishment)</option>
                <option value={14}>14 Days (Standard bi-weekly reorder planning - Recommended)</option>
                <option value={21}>21 Days (3-Week inventory pipeline)</option>
                <option value={30}>30 Days (Monthly demand cycle)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="service-level-select">
                Target Service Level (Z-Factor)
              </label>
              <select
                id="service-level-select"
                className="form-select"
                value={serviceLevel}
                onChange={(e) => setServiceLevel(e.target.value)}
              >
                <option value="90%">90% (Z = 1.282 - Lower holding cost, standard items)</option>
                <option value="95%">95% (Z = 1.645 - Standard retail benchmark - Recommended)</option>
                <option value="98%">98% (Z = 2.054 - High protection against stock-outs)</option>
                <option value="99%">99% (Z = 2.326 - Critical SKUs / Zero tolerance)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="model-type-select">
                Supervised Regression Model
              </label>
              <select
                id="model-type-select"
                className="form-select"
                value={modelType}
                onChange={(e) => setModelType(e.target.value)}
              >
                <option value="RandomForest">Random Forest Regressor (Ensemble of non-linear decision trees)</option>
                <option value="HistGradientBoosting">HistGradientBoosting Regressor (Fast histogram-based gradient boosting)</option>
              </select>
            </div>

            <div className="alert-box alert-neutral" style={{ marginTop: 'var(--space-4)' }}>
              <CheckCircle2 size={16} style={{ color: 'var(--accent-primary)', flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong>Time-Series Integrity:</strong> The pipeline applies strict chronological 80/20 train/test splitting without future data leakage. Lag and rolling statistics are calculated purely on historical periods.
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  <span>Retraining Pipeline...</span>
                </>
              ) : (
                <>
                  <RefreshCw size={14} />
                  <span>Execute Retrain</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
