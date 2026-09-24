import React, { useState, useRef } from 'react';
import { 
  Upload, 
  Database, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw,
  Table as TableIcon,
  Columns
} from 'lucide-react';
import type { DataSummaryResponse } from '../types';
import { api } from '../api/client';
import { MetricCard } from '../components/MetricCard';
import { ColumnMapperModal } from '../components/ColumnMapperModal';

interface DataPageProps {
  dataSummary: DataSummaryResponse | null;
  onRefreshData: () => void;
  onSuccessMessage: (msg: string) => void;
}

export const DataPage: React.FC<DataPageProps> = ({
  dataSummary,
  onRefreshData,
  onSuccessMessage,
}) => {
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [showMapperModal, setShowMapperModal] = useState<boolean>(false);
  const [benchmarkLoading, setBenchmarkLoading] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    setUploadError(null);

    try {
      const res = await api.uploadDataset(file);
      if (res.status === 'mapping_required') {
        setShowMapperModal(true);
        onRefreshData();
      } else {
        onSuccessMessage(`Successfully ingested ${file.name} and trained ML pipeline.`);
        onRefreshData();
      }
    } catch (err: any) {
      setUploadError(err?.response?.data?.detail || 'Failed to parse file. Please verify CSV/Excel format.');
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleLoadBenchmark = async () => {
    setBenchmarkLoading(true);
    setUploadError(null);
    try {
      await api.loadBenchmark();
      onSuccessMessage('Loaded curated 12-SKU retail benchmark dataset.');
      onRefreshData();
    } catch (err: any) {
      setUploadError('Failed to load benchmark dataset.');
    } finally {
      setBenchmarkLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-5)', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h1 className="page-title">Dataset Studio & Dynamic Schema Inspector</h1>
          <p className="page-description">
            Ingest custom CSV or Excel inventory histories. Column aliases and missing fields are dynamically detected.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={handleLoadBenchmark}
            disabled={benchmarkLoading}
          >
            <RefreshCw size={14} className={benchmarkLoading ? 'animate-spin' : ''} />
            <span>Load Curated 12-SKU Benchmark</span>
          </button>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => setShowMapperModal(true)}
          >
            <Columns size={14} />
            <span>Column Mapping Wizard</span>
          </button>
        </div>
      </div>

      {uploadError && (
        <div className="alert-box alert-critical" style={{ marginBottom: 'var(--space-5)' }}>
          <AlertTriangle size={18} style={{ flexShrink: 0 }} />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Upload Zone */}
      <div className="panel" style={{ marginBottom: 'var(--space-6)' }}>
        <div className="panel-header">
          <div>
            <h2 className="panel-title">Upload Inventory & Sales Dataset</h2>
            <p className="panel-subtitle">Accepts standard .csv, .xlsx, or .xls files</p>
          </div>
        </div>
        <div className="panel-body">
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            accept=".csv,.xlsx,.xls"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileUpload(e.target.files[0]);
              }
            }}
          />

          <div
            className={`dropzone ${dragActive ? 'active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={36} style={{ color: 'var(--accent-primary)', margin: '0 auto 12px' }} />
            <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
              {uploading ? 'Processing & Validating Dataset...' : 'Click or Drag & Drop File to Ingest'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Supports comma-separated CSV or Excel spreadsheets containing transaction dates and sales/demand volume.
            </div>
          </div>
        </div>
      </div>

      {/* Dataset Summary Metrics */}
      {dataSummary && (
        <>
          <div className="grid-kpi">
            <MetricCard
              label="Active Source"
              value={dataSummary.active_source}
              subtext="Current active in-memory dataset"
              icon={<Database size={18} />}
            />
            <MetricCard
              label="Total Records"
              value={`${dataSummary.cleaned_rows.toLocaleString()} Rows`}
              subtext={`${dataSummary.total_cols} Columns Detected`}
              icon={<FileText size={18} />}
            />
            <MetricCard
              label="Product SKUs"
              value={dataSummary.product_count}
              subtext={`${dataSummary.categories.length} Categories`}
              icon={<TableIcon size={18} />}
            />
            <MetricCard
              label="Historical Date Range"
              value={dataSummary.date_range ? `${dataSummary.date_range[0]} to ${dataSummary.date_range[1]}` : 'N/A'}
              subtext="Chronological time horizon"
            />
          </div>

          {/* Schema & Detected Column Mappings */}
          <div className="panel" style={{ marginBottom: 'var(--space-6)' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Detected Column Mappings & Validation</h2>
                <p className="panel-subtitle">Canonical schema matching for ML feature extraction</p>
              </div>
            </div>
            <div className="panel-body">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-3)' }}>
                {Object.entries(dataSummary.detected_mapping).map(([canonical, matchedCol]) => (
                  <div
                    key={canonical}
                    style={{
                      padding: 'var(--space-3)',
                      backgroundColor: matchedCol ? 'var(--bg-surface)' : 'var(--bg-surface-subtle)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                        {canonical.replace('_', ' ')}
                      </div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: matchedCol ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                        {matchedCol || 'Not detected (defaults applied)'}
                      </div>
                    </div>
                    {matchedCol ? (
                      <CheckCircle2 size={16} style={{ color: 'var(--status-safe-solid)' }} />
                    ) : (
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Default</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Data Preview Table */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Raw Dataset Preview (First 100 Rows)</h2>
                <p className="panel-subtitle">Standardized columns prepared for feature engineering</p>
              </div>
            </div>
            <div className="panel-body" style={{ padding: 0 }}>
              <div className="table-container" style={{ border: 'none', maxHeight: '450px' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      {dataSummary.columns.map((col) => (
                        <th key={col}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {dataSummary.preview_records.slice(0, 100).map((row, idx) => (
                      <tr key={idx}>
                        {dataSummary.columns.map((col) => (
                          <td key={col}>{row[col] !== null && row[col] !== undefined ? String(row[col]) : '—'}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Column Mapper Modal */}
      {showMapperModal && dataSummary && (
        <ColumnMapperModal
          isOpen={showMapperModal}
          onClose={() => setShowMapperModal(false)}
          availableColumns={dataSummary.columns}
          missingRequired={dataSummary.missing_required || []}
          initialMapping={dataSummary.detected_mapping}
          onSuccess={() => {
            onSuccessMessage('Custom column mappings applied successfully.');
            onRefreshData();
          }}
        />
      )}
    </div>
  );
};
