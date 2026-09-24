import React, { useState } from 'react';
import { X, Check, AlertTriangle } from 'lucide-react';
import { api } from '../api/client';

interface ColumnMapperModalProps {
  isOpen: boolean;
  onClose: () => void;
  availableColumns: string[];
  missingRequired: string[];
  initialMapping: Record<string, string | null>;
  onSuccess: () => void;
}

export const ColumnMapperModal: React.FC<ColumnMapperModalProps> = ({
  isOpen,
  onClose,
  availableColumns,
  missingRequired,
  initialMapping,
  onSuccess,
}) => {
  const [mapping, setMapping] = useState<Record<string, string>>(() => {
    const init: Record<string, string> = {};
    for (const [canonical, original] of Object.entries(initialMapping)) {
      if (original) {
        init[canonical] = original;
      }
    }
    return init;
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const targetFields = [
    { key: 'date', label: 'Transaction Date Column', required: true, desc: 'Timestamp or Date of sales record' },
    { key: 'sales_units', label: 'Demand / Sales Quantity Column', required: true, desc: 'Units sold or recorded demand volume' },
    { key: 'product_id', label: 'Product SKU / ID Column', required: false, desc: 'Unique identifier for the product' },
    { key: 'product_name', label: 'Product Name / Title Column', required: false, desc: 'Descriptive item name' },
    { key: 'category', label: 'Category / Department Column', required: false, desc: 'Grouping for the SKU' },
    { key: 'stock_on_hand', label: 'Current Inventory / Stock Column', required: false, desc: 'Units on hand at time of record' },
    { key: 'unit_price', label: 'Unit Price / Cost Column', required: false, desc: 'Selling price per unit' },
    { key: 'lead_time_days', label: 'Supplier Lead Time Days Column', required: false, desc: 'Days required for supplier fulfillment' },
    { key: 'promotion_active', label: 'Promotion Active Indicator Column', required: false, desc: '0/1 or True/False promotion flag' },
  ];

  const handleSelectChange = (canonicalKey: string, selectedCol: string) => {
    setMapping((prev) => ({
      ...prev,
      [canonicalKey]: selectedCol,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validate required fields
    if (!mapping['date'] || !mapping['sales_units']) {
      setError('Both Date and Sales / Demand columns must be mapped.');
      setLoading(false);
      return;
    }

    try {
      await api.mapColumns(mapping);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to apply custom column mapping.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3 className="panel-title">Column Mapping Wizard</h3>
            <p className="panel-subtitle">Map columns from your uploaded dataset to the Stock Guardian AI schema</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onClose} aria-label="Close modal">
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {missingRequired.length > 0 && (
              <div className="alert-box alert-high">
                <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Missing Required Mappings:</strong> {missingRequired.join(', ')}. Please assign corresponding dataset columns below.
                </div>
              </div>
            )}

            {error && (
              <div className="alert-box alert-critical">
                <span>{error}</span>
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              {targetFields.map((field) => (
                <div key={field.key} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 'var(--space-2)' }}>
                  <div>
                    <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
                      {field.label} {field.required && <span style={{ color: 'var(--status-critical-solid)' }}>*</span>}
                    </span>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{field.desc}</div>
                  </div>

                  <div>
                    <select
                      className="form-select"
                      value={mapping[field.key] || ''}
                      onChange={(e) => handleSelectChange(field.key, e.target.value)}
                    >
                      <option value="">-- Select matching column --</option>
                      {availableColumns.map((col) => (
                        <option key={col} value={col}>
                          {col}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              <Check size={14} />
              <span>{loading ? 'Applying Mappings...' : 'Confirm & Ingest Dataset'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
