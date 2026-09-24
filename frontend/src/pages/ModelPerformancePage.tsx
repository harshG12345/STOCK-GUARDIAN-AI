import React, { useState, useEffect } from 'react';
import { 
  ResponsiveContainer, 
  ComposedChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid
} from 'recharts';
import { 
  Cpu, 
  TrendingUp, 
  RefreshCw, 
  Target,
  Award
} from 'lucide-react';
import type { ModelPerformanceResponse, ProductSummary } from '../types';
import { api } from '../api/client';
import { MetricCard } from '../components/MetricCard';

interface ModelPerformancePageProps {
  products: ProductSummary[];
  selectedProductId: string;
  onSelectProductId: (id: string) => void;
  onOpenRetrainModal: () => void;
}

export const ModelPerformancePage: React.FC<ModelPerformancePageProps> = ({
  products,
  selectedProductId,
  onSelectProductId,
  onOpenRetrainModal,
}) => {
  const [perfData, setPerfData] = useState<ModelPerformanceResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let activeId = selectedProductId;
    if (products.length > 0) {
      if (!activeId || !products.some((p) => p.product_id === activeId)) {
        activeId = products[0].product_id;
        onSelectProductId(activeId);
      }
    }

    const loadPerf = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.getModelPerformance(activeId || undefined);
        setPerfData(res);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to fetch model performance.');
      } finally {
        setLoading(false);
      }
    };

    loadPerf();
  }, [selectedProductId, products, onSelectProductId]);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-5)', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h1 className="page-title">Model Evaluation & Benchmark Comparison</h1>
          <p className="page-description">
            Head-to-head empirical evaluation of Baseline (7-Day Moving Average) versus Supervised ML Regression on unseen chronological holdout test records.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          {/* SKU Selector */}
          <select
            className="form-select"
            style={{ width: '260px', fontWeight: 600 }}
            value={selectedProductId}
            onChange={(e) => onSelectProductId(e.target.value)}
          >
            {products.map((p) => (
              <option key={p.product_id} value={p.product_id}>
                {p.product_name} ({p.product_id})
              </option>
            ))}
          </select>

          <button className="btn btn-primary btn-sm" onClick={onOpenRetrainModal}>
            <RefreshCw size={14} />
            <span>Retrain Models</span>
          </button>
        </div>
      </div>

      {loading && (
        <div className="panel" style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
          Evaluating model performance metrics for {selectedProductId}...
        </div>
      )}

      {error && (
        <div className="alert-box alert-critical">
          <span>{error}</span>
        </div>
      )}

      {perfData && !loading && (
        <>
          {/* Portfolio-Wide Aggregate Metrics */}
          <div className="grid-kpi">
            <MetricCard
              label="Selected ML Model"
              value={perfData.portfolio_aggregate.model_type}
              subtext={`Across ${perfData.portfolio_aggregate.total_skus_evaluated} evaluated SKUs`}
              icon={<Cpu size={18} />}
            />
            <MetricCard
              label="Portfolio Mean MAE"
              value={`${perfData.portfolio_aggregate.avg_ml_mae} Units`}
              subtext={`Baseline MAE: ${perfData.portfolio_aggregate.avg_base_mae} units`}
              icon={<Target size={18} />}
            />
            <MetricCard
              label="MAE Accuracy Gain"
              value={`${perfData.portfolio_aggregate.mae_improvement_pct}%`}
              subtext="Error reduction vs 7D Moving Average"
              badge={<span className="badge badge-safe">Empirical Win</span>}
              icon={<Award size={18} style={{ color: 'var(--status-safe-solid)' }} />}
            />
            <MetricCard
              label="Portfolio Mean R² Score"
              value={typeof perfData.portfolio_aggregate.avg_ml_r2 === 'number' ? perfData.portfolio_aggregate.avg_ml_r2.toFixed(3) : 'N/A'}
              subtext="Coefficient of determination"
              icon={<TrendingUp size={18} />}
            />
          </div>

          {/* Side-by-Side Model Comparison Table */}
          <div className="panel" style={{ marginBottom: 'var(--space-6)' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">
                  Performance on Unseen Holdout Set: <strong>{perfData.selected_product.product_name}</strong>
                </h2>
                <p className="panel-subtitle">
                  Evaluated on chronological holdout set ({perfData.selected_product.split_meta?.test_size ?? 0} test days from {perfData.selected_product.split_meta?.test_date_range?.[0] || perfData.selected_product.split_meta?.test_start_date || 'Start'} to {perfData.selected_product.split_meta?.test_date_range?.[1] || perfData.selected_product.split_meta?.test_end_date || 'End'})
                </p>
              </div>
            </div>

            <div className="panel-body" style={{ padding: 0 }}>
              <div className="table-container" style={{ border: 'none' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Candidate Model Architecture</th>
                      <th style={{ textAlign: 'right' }}>MAE (Units)</th>
                      <th style={{ textAlign: 'right' }}>RMSE (Units)</th>
                      <th style={{ textAlign: 'right' }}>R² Score</th>
                      <th style={{ textAlign: 'right' }}>Safe MAPE (%)</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>
                        <div style={{ fontWeight: 600 }}>Model 1: Baseline (7-Day Moving Average)</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Naive historical rolling mean</div>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{perfData.selected_product.base_mae}</td>
                      <td style={{ textAlign: 'right' }}>{perfData.selected_product.base_rmse}</td>
                      <td style={{ textAlign: 'right' }}>{perfData.selected_product.base_r2}</td>
                      <td style={{ textAlign: 'right' }}>{perfData.selected_product.base_mape}%</td>
                      <td>
                        <span className="badge badge-neutral">Baseline</span>
                      </td>
                    </tr>
                    <tr style={{ backgroundColor: 'var(--bg-surface-subtle)' }}>
                      <td>
                        <div style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>
                          Model 2: Supervised ML ({perfData.portfolio_aggregate.model_type})
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                          Non-linear regression with lag dynamics & seasonality features
                        </div>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 700, color: 'var(--accent-primary)' }}>
                        {perfData.selected_product.ml_mae}
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{perfData.selected_product.ml_rmse}</td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{perfData.selected_product.ml_r2}</td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{perfData.selected_product.ml_mape}%</td>
                      <td>
                        <span className="badge badge-safe">Production ML</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Test Set Evaluation Chart: Actual vs Baseline vs ML */}
          <div className="panel" style={{ marginBottom: 'var(--space-6)' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Holdout Test Set Prediction Alignment</h2>
                <p className="panel-subtitle">Comparing model predictions against ground truth actual recorded demand</p>
              </div>
            </div>
            <div className="panel-body">
              <div style={{ height: '320px', width: '100%', minHeight: '320px' }}>
                <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={300}>
                  <ComposedChart data={perfData.selected_product.test_evaluation_records} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                    <XAxis
                      dataKey="Date"
                      tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
                      stroke="var(--border-strong)"
                      tickFormatter={(val) => val ? String(val).slice(5) : ''}
                    />
                    <YAxis
                      tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
                      stroke="var(--border-strong)"
                      label={{ value: 'Units', angle: -90, position: 'insideLeft', fontSize: 11, fill: 'var(--text-muted)' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--bg-surface)',
                        borderColor: 'var(--border-strong)',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '12px',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Line
                      type="monotone"
                      dataKey="Actual"
                      name="Actual Recorded Demand"
                      stroke="#0F172A"
                      strokeWidth={2.5}
                      dot={{ r: 3 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="Baseline_Pred"
                      name="Baseline (7D MA)"
                      stroke="#94A3B8"
                      strokeWidth={1.5}
                      strokeDasharray="3 3"
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="ML_Pred"
                      name={`Supervised ML (${perfData.portfolio_aggregate.model_type})`}
                      stroke="var(--accent-primary)"
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Chronological Split Integrity Note */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3 className="panel-title">Train / Test Split & Data Leakage Prevention</h3>
                <p className="panel-subtitle">Strict chronological partitioning methodology</p>
              </div>
            </div>
            <div className="panel-body">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--space-4)' }}>
                <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--bg-surface-subtle)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                    Training Split (80%)
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '2px' }}>
                    {perfData.selected_product.split_meta?.train_size ?? 0} Days
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {perfData.selected_product.split_meta?.train_date_range?.[0] || perfData.selected_product.split_meta?.train_start_date || 'Start'} to {perfData.selected_product.split_meta?.train_date_range?.[1] || perfData.selected_product.split_meta?.train_end_date || 'End'}
                  </div>
                </div>

                <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--bg-surface-subtle)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                    Holdout Test Split (20%)
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '2px' }}>
                    {perfData.selected_product.split_meta?.test_size ?? 0} Days
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {perfData.selected_product.split_meta?.test_date_range?.[0] || perfData.selected_product.split_meta?.test_start_date || 'Start'} to {perfData.selected_product.split_meta?.test_date_range?.[1] || perfData.selected_product.split_meta?.test_end_date || 'End'}
                  </div>
                </div>

                <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--bg-surface-subtle)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                    Split Cutoff Date
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '2px' }}>
                    {perfData.selected_product.split_meta?.split_date || perfData.selected_product.split_meta?.test_start_date || 'N/A'}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Zero forward-looking feature leakage
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
