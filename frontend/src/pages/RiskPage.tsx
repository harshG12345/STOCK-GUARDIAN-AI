import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  AlertCircle, 
  AlertTriangle, 
  CheckCircle, 
  Activity, 
  Layers, 
  TrendingUp
} from 'lucide-react';
import type { ProductRiskResponse, ProductSummary } from '../types';
import { api } from '../api/client';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';

interface RiskPageProps {
  products: ProductSummary[];
  selectedProductId: string;
  onSelectProductId: (id: string) => void;
  onNavigate: (tab: string) => void;
}

export const RiskPage: React.FC<RiskPageProps> = ({
  products,
  selectedProductId,
  onSelectProductId,
  onNavigate,
}) => {
  const [riskData, setRiskData] = useState<ProductRiskResponse | null>(null);
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

    if (activeId) {
      const loadRisk = async () => {
        setLoading(true);
        setError(null);
        try {
          const res = await api.getProductRisk(activeId);
          setRiskData(res);
        } catch (err: any) {
          setError(err?.response?.data?.detail || 'Failed to fetch risk analysis.');
        } finally {
          setLoading(false);
        }
      };
      loadRisk();
    }
  }, [selectedProductId, products, onSelectProductId]);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-5)', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h1 className="page-title">Inventory Risk Engine & Decision Matrix</h1>
          <p className="page-description">
            Transparent composite decision scoring evaluated across stock coverage, trend velocity, volatility, and supplier lead-time exposure.
          </p>
        </div>

        {/* Product Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <label className="form-label" style={{ marginBottom: 0, whiteSpace: 'nowrap' }}>
            Select Product SKU:
          </label>
          <select
            className="form-select"
            style={{ width: '280px', fontWeight: 600 }}
            value={selectedProductId}
            onChange={(e) => onSelectProductId(e.target.value)}
          >
            {products.map((p) => (
              <option key={p.product_id} value={p.product_id}>
                {p.product_name} ({p.product_id})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && (
        <div className="panel" style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
          Calculating composite risk metrics for {selectedProductId}...
        </div>
      )}

      {error && (
        <div className="alert-box alert-critical">
          <span>{error}</span>
        </div>
      )}

      {riskData && !loading && (
        <>
          {/* Key Metrics */}
          <div className="grid-kpi">
            <MetricCard
              label="Composite Risk Score"
              value={`${riskData.risk_info.risk_score} / 100`}
              subtext={`Decision Level: ${riskData.risk_info.risk_level}`}
              badge={<StatusBadge status={riskData.risk_info.risk_level} type="risk" />}
              icon={<ShieldAlert size={18} style={{ color: riskData.risk_info.badge_color }} />}
            />
            <MetricCard
              label="Inventory Coverage Ratio"
              value={`${riskData.risk_info.coverage_ratio.toFixed(2)}x`}
              subtext={`Stock ${riskData.risk_info.current_inventory} vs Forecast ${riskData.risk_info.predicted_demand}`}
              icon={<Layers size={18} />}
            />
            <MetricCard
              label="Demand Trend Direction"
              value={riskData.risk_info.trend}
              subtext={`Velocity: ${riskData.risk_info.trend_details.pct_change > 0 ? '+' : ''}${riskData.risk_info.trend_details.pct_change}%`}
              badge={<StatusBadge status={riskData.risk_info.trend} type="trend" />}
              icon={<TrendingUp size={18} />}
            />
            <MetricCard
              label="Demand Shock Status"
              value={riskData.shock_status}
              subtext={`Z-Score: ${riskData.shock_z} (${riskData.shock_dev_pct > 0 ? '+' : ''}${riskData.shock_dev_pct}%)`}
              badge={<StatusBadge status={riskData.shock_status} type="shock" />}
              icon={<Activity size={18} />}
            />
          </div>

          {/* Action Code Recommendation Banner */}
          <div
            className={`alert-box ${
              riskData.risk_info.risk_level === 'CRITICAL'
                ? 'alert-critical'
                : riskData.risk_info.risk_level === 'HIGH RISK'
                ? 'alert-high'
                : riskData.risk_info.risk_level === 'WATCH'
                ? 'alert-watch'
                : 'alert-safe'
            }`}
            style={{ marginBottom: 'var(--space-6)' }}
          >
            {riskData.risk_info.risk_level === 'CRITICAL' ? (
              <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
            ) : riskData.risk_info.risk_level === 'HIGH RISK' ? (
              <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
            ) : (
              <CheckCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
            )}
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: '14px', marginBottom: '2px' }}>
                Operational Recommendation: {riskData.risk_info.action_code}
              </div>
              <div style={{ fontSize: '12px' }}>
                {riskData.risk_info.demand_gap > 0
                  ? `Forecast demand (${riskData.risk_info.predicted_demand} units) exceeds available inventory (${riskData.risk_info.current_inventory} units) by ${riskData.risk_info.demand_gap} units. Urgent replenishment required.`
                  : `Available inventory (${riskData.risk_info.current_inventory} units) satisfies current forecasted demand (${riskData.risk_info.predicted_demand} units).`}
              </div>
            </div>
            <button className="btn btn-primary btn-sm" onClick={() => onNavigate('reorder')}>
              Generate Purchase Order
            </button>
          </div>

          {/* Transparent Scoring Formula Breakdown */}
          <div className="panel" style={{ marginBottom: 'var(--space-6)' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Transparent 4-Factor Risk Decomposition</h2>
                <p className="panel-subtitle">
                  Formula: Composite Score = 0.45(Coverage Deficit) + 0.20(Trend Acceleration) + 0.20(Volatility) + 0.15(Lead Time Exposure)
                </p>
              </div>
            </div>
            <div className="panel-body">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 'var(--space-4)' }}>
                {/* Factor 1 */}
                <div style={{ padding: 'var(--space-4)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-surface)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
                    <span style={{ fontWeight: 600, fontSize: '13px' }}>1. Coverage Deficit (45%)</span>
                    <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--accent-primary)' }}>
                      {riskData.risk_info.component_scores.coverage_deficit} / 100
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    Ratio: <strong>{riskData.risk_info.coverage_ratio.toFixed(2)}x</strong>. Evaluates if on-hand stock can absorb expected sales over the horizon window.
                  </div>
                </div>

                {/* Factor 2 */}
                <div style={{ padding: 'var(--space-4)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-surface)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
                    <span style={{ fontWeight: 600, fontSize: '13px' }}>2. Trend Acceleration (20%)</span>
                    <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--accent-primary)' }}>
                      {riskData.risk_info.component_scores.trend_acceleration} / 100
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    Direction: <strong>{riskData.risk_info.trend}</strong> ({riskData.risk_info.trend_details.pct_change > 0 ? '+' : ''}{riskData.risk_info.trend_details.pct_change}%). Linear slope indicates demand growth velocity.
                  </div>
                </div>

                {/* Factor 3 */}
                <div style={{ padding: 'var(--space-4)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-surface)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
                    <span style={{ fontWeight: 600, fontSize: '13px' }}>3. Demand Volatility (20%)</span>
                    <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--accent-primary)' }}>
                      {riskData.risk_info.component_scores.demand_volatility} / 100
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    CV: <strong>{riskData.risk_info.volatility_cv}</strong>. Coefficient of variation (std dev / mean) measuring sales unpredictability.
                  </div>
                </div>

                {/* Factor 4 */}
                <div style={{ padding: 'var(--space-4)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-surface)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
                    <span style={{ fontWeight: 600, fontSize: '13px' }}>4. Lead Time Exposure (15%)</span>
                    <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--accent-primary)' }}>
                      {riskData.risk_info.component_scores.lead_time_exposure} / 100
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    Window: <strong>{riskData.risk_info.lead_time_days} Days</strong>. Longer lead times require higher safety buffers due to supplier vulnerability.
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Portfolio-Wide Risk Distribution Table */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Portfolio Risk Distribution</h2>
                <p className="panel-subtitle">Comprehensive risk scores across all tracked catalog items</p>
              </div>
            </div>
            <div className="panel-body" style={{ padding: 0 }}>
              <div className="table-container" style={{ border: 'none' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>SKU</th>
                      <th>Product Name</th>
                      <th>Category</th>
                      <th style={{ textAlign: 'right' }}>Current Stock</th>
                      <th style={{ textAlign: 'right' }}>Forecast Demand</th>
                      <th>Risk Score</th>
                      <th>Risk Status</th>
                      <th>Trend</th>
                      <th style={{ textAlign: 'right' }}>Lead Time</th>
                      <th style={{ textAlign: 'center' }}>Select</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p) => (
                      <tr key={p.product_id} style={{ backgroundColor: p.product_id === selectedProductId ? 'var(--bg-surface-subtle)' : undefined }}>
                        <td style={{ fontFamily: 'var(--font-family-mono)', fontWeight: 600 }}>{p.product_id}</td>
                        <td style={{ fontWeight: 600 }}>{p.product_name}</td>
                        <td>{p.category}</td>
                        <td style={{ textAlign: 'right' }}>{p.current_stock.toLocaleString()}</td>
                        <td style={{ textAlign: 'right' }}>{p.predicted_demand.toLocaleString()}</td>
                        <td style={{ fontWeight: 700 }}>{p.risk_score}</td>
                        <td>
                          <StatusBadge status={p.risk_level} type="risk" />
                        </td>
                        <td>
                          <StatusBadge status={p.trend} type="trend" />
                        </td>
                        <td style={{ textAlign: 'right' }}>{p.lead_time_days}d</td>
                        <td style={{ textAlign: 'center' }}>
                          <button
                            className="btn btn-secondary btn-sm"
                            style={{ padding: '2px 8px', fontSize: '11px' }}
                            onClick={() => onSelectProductId(p.product_id)}
                          >
                            {p.product_id === selectedProductId ? 'Active' : 'Analyze'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
