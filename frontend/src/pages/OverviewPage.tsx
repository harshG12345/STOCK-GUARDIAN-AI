import React, { useState, useMemo } from 'react';
import { 
  AlertCircle, 
  AlertTriangle, 
  Search, 
  ArrowRight,
  TrendingUp,
  Package,
  DollarSign
} from 'lucide-react';
import type { DashboardSummaryResponse } from '../types';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';

interface OverviewPageProps {
  data: DashboardSummaryResponse;
  onSelectProduct: (productId: string, targetTab?: string) => void;
  onNavigate: (tab: string) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  data,
  onSelectProduct,
  onNavigate,
}) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedRiskFilter, setSelectedRiskFilter] = useState<string>('ALL');

  const { kpis, shock_alerts, critical_alerts, categories, products_table } = data;

  const filteredProducts = useMemo(() => {
    return products_table.filter((p) => {
      const matchesSearch =
        p.product_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.product_name.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCat = selectedCategory === 'ALL' || p.category === selectedCategory;

      const matchesRisk =
        selectedRiskFilter === 'ALL' ||
        (selectedRiskFilter === 'CRITICAL' && p.risk_level === 'CRITICAL') ||
        (selectedRiskFilter === 'HIGH RISK' && p.risk_level === 'HIGH RISK') ||
        (selectedRiskFilter === 'WATCH' && p.risk_level === 'WATCH') ||
        (selectedRiskFilter === 'SAFE' && p.risk_level === 'SAFE');

      return matchesSearch && matchesCat && matchesRisk;
    });
  }, [products_table, searchTerm, selectedCategory, selectedRiskFilter]);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-5)', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h1 className="page-title">Executive Demand & Inventory Overview</h1>
          <p className="page-description">
            Portfolio operational health across {kpis.total_products} tracked SKUs over a {kpis.forecast_horizon_days}-day planning horizon ({kpis.service_level} service level target).
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('data')}>
            Manage Dataset
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => onNavigate('reorder')}>
            Review Reorder Plan
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid-kpi">
        <MetricCard
          label="Total Tracked SKUs"
          value={kpis.total_products}
          subtext="Active SKU Catalog"
          icon={<Package size={18} />}
        />
        <MetricCard
          label="Critical Stockouts"
          value={kpis.critical_stockouts}
          subtext="Immediate reorder required"
          icon={<AlertCircle size={18} style={{ color: 'var(--status-critical-solid)' }} />}
          badge={<StatusBadge status="CRITICAL" />}
        />
        <MetricCard
          label="High Risk SKUs"
          value={kpis.high_risk}
          subtext="Supply deficit impending"
          icon={<AlertTriangle size={18} style={{ color: 'var(--status-high-solid)' }} />}
          badge={<StatusBadge status="HIGH RISK" />}
        />
        <MetricCard
          label="Recommended Reorder"
          value={`${kpis.total_reorder_units.toLocaleString()} Units`}
          subtext="Safety buffer + Demand gap"
          icon={<TrendingUp size={18} />}
        />
        <MetricCard
          label="Procurement Capital"
          value={`$${kpis.total_reorder_capital.toLocaleString()}`}
          subtext="Estimated purchase commitment"
          icon={<DollarSign size={18} />}
        />
      </div>

      {/* Critical Stockout Alerts Banner */}
      {critical_alerts.length > 0 && (
        <div className="alert-box alert-critical" style={{ marginBottom: 'var(--space-5)' }}>
          <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px' }}>
              Action Required: {critical_alerts.length} SKU(s) Face Projected Stockout Within Lead Time
            </div>
            <div style={{ fontSize: '12px', lineHeight: 1.6 }}>
              {critical_alerts.slice(0, 3).map((a) => (
                <span key={a.product_id} style={{ display: 'inline-block', marginRight: '16px' }}>
                  <strong>{a.product_name}</strong>: Stock {a.current_stock} units vs {a.predicted_demand} units forecast ({a.days_of_supply} days supply). Reorder +{a.reorder_units} units.
                </span>
              ))}
            </div>
          </div>
          <button
            className="btn btn-outline btn-sm"
            style={{ borderColor: 'var(--status-critical-border)', color: 'var(--status-critical-text)', backgroundColor: '#FFFFFF' }}
            onClick={() => onNavigate('reorder')}
          >
            <span>View All Reorders</span>
            <ArrowRight size={14} />
          </button>
        </div>
      )}

      {/* Statistical Demand Shock Alerts Banner */}
      {shock_alerts.length > 0 && (
        <div className="alert-box alert-high" style={{ marginBottom: 'var(--space-5)' }}>
          <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px' }}>
              Demand Shock Detection: {shock_alerts.length} SKU(s) Exhibiting Statistically Significant Demand Deviations
            </div>
            <div style={{ fontSize: '12px', lineHeight: 1.6 }}>
              {shock_alerts.map((s) => (
                <span key={s.product_id} style={{ display: 'inline-block', marginRight: '16px' }}>
                  <strong>{s.product_name}</strong>: Recent 7-day average ({s.recent_mean} units/day) deviated {s.pct_deviation > 0 ? `+${s.pct_deviation}%` : `${s.pct_deviation}%`} from baseline (Z = {s.z_score}).
                </span>
              ))}
            </div>
          </div>
          <button
            className="btn btn-outline btn-sm"
            style={{ borderColor: 'var(--status-high-border)', color: 'var(--status-high-text)', backgroundColor: '#FFFFFF' }}
            onClick={() => onNavigate('forecast')}
          >
            <span>Inspect Forecasts</span>
            <ArrowRight size={14} />
          </button>
        </div>
      )}

      {/* Main Table Panel: Products Requiring Attention */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <h2 className="panel-title">Products Requiring Attention & Operational Queue</h2>
            <p className="panel-subtitle">
              Prioritized by calculated decision risk score (Coverage Deficit 45%, Trend 20%, Volatility 20%, Lead Time 15%)
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
            {/* Search Input */}
            <div style={{ position: 'relative', width: '220px' }}>
              <Search size={14} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Search SKU or name..."
                className="form-input"
                style={{ paddingLeft: '30px', fontSize: '12px' }}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Category Filter */}
            <select
              className="form-select"
              style={{ width: '160px', fontSize: '12px' }}
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="ALL">All Categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>

            {/* Risk Filter */}
            <select
              className="form-select"
              style={{ width: '150px', fontSize: '12px' }}
              value={selectedRiskFilter}
              onChange={(e) => setSelectedRiskFilter(e.target.value)}
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="HIGH RISK">High Risk Only</option>
              <option value="WATCH">Watchlist Only</option>
              <option value="SAFE">Safe Only</option>
            </select>
          </div>
        </div>

        <div className="panel-body" style={{ padding: 0 }}>
          <div className="table-container" style={{ border: 'none' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product / SKU</th>
                  <th>Category</th>
                  <th style={{ textAlign: 'right' }}>Current Stock</th>
                  <th style={{ textAlign: 'right' }}>Predicted Demand</th>
                  <th style={{ textAlign: 'right' }}>Demand Gap</th>
                  <th>Risk Score</th>
                  <th>Risk Status</th>
                  <th>Trend</th>
                  <th>Shock Status</th>
                  <th style={{ textAlign: 'right' }}>Days Supply</th>
                  <th style={{ textAlign: 'right' }}>Reorder Qty</th>
                  <th>Recommended Action</th>
                  <th style={{ textAlign: 'center' }}>Inspect</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.length === 0 ? (
                  <tr>
                    <td colSpan={13} style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--text-muted)' }}>
                      No SKUs match the selected search or filter criteria.
                    </td>
                  </tr>
                ) : (
                  filteredProducts.map((p) => (
                    <tr key={p.product_id}>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{p.product_name}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-family-mono)' }}>
                          {p.product_id}
                        </div>
                      </td>
                      <td>
                        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{p.category}</span>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{p.current_stock.toLocaleString()}</td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{p.predicted_demand.toLocaleString()}</td>
                      <td style={{ textAlign: 'right' }}>
                        {p.demand_gap > 0 ? (
                          <span style={{ color: 'var(--status-critical-solid)', fontWeight: 600 }}>
                            +{p.demand_gap.toLocaleString()}
                          </span>
                        ) : (
                          <span style={{ color: 'var(--status-safe-solid)' }}>0</span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{ fontWeight: 700, fontSize: '13px' }}>{p.risk_score}</span>
                          <div style={{ width: '40px', height: '6px', backgroundColor: 'var(--bg-surface-subtle)', borderRadius: '3px', overflow: 'hidden' }}>
                            <div
                              style={{
                                width: `${Math.min(100, p.risk_score)}%`,
                                height: '100%',
                                backgroundColor: p.risk_level === 'CRITICAL' ? 'var(--status-critical-solid)' : p.risk_level === 'HIGH RISK' ? 'var(--status-high-solid)' : p.risk_level === 'WATCH' ? 'var(--status-watch-solid)' : 'var(--status-safe-solid)',
                              }}
                            />
                          </div>
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={p.risk_level} type="risk" />
                      </td>
                      <td>
                        <StatusBadge status={p.trend} type="trend" />
                      </td>
                      <td>
                        <StatusBadge status={p.shock_status} type="shock" />
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <span style={{ fontWeight: 600, color: p.days_of_supply < p.lead_time_days ? 'var(--status-critical-solid)' : 'var(--text-primary)' }}>
                          {p.days_of_supply}d
                        </span>
                        <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>Lead: {p.lead_time_days}d</div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        {p.recommended_additional_stock > 0 ? (
                          <span style={{ fontWeight: 700, color: 'var(--status-critical-solid)' }}>
                            +{p.recommended_additional_stock.toLocaleString()}
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>0</span>
                        )}
                      </td>
                      <td>
                        <span style={{ fontSize: '11px', fontWeight: 600, color: p.risk_level === 'CRITICAL' ? 'var(--status-critical-text)' : p.risk_level === 'HIGH RISK' ? 'var(--status-high-text)' : 'var(--text-secondary)' }}>
                          {p.action_code}
                        </span>
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <button
                          className="btn btn-outline btn-sm"
                          style={{ padding: '2px 8px', fontSize: '11px' }}
                          onClick={() => onSelectProduct(p.product_id, 'forecast')}
                          title="View forecast & historical timeline"
                        >
                          Forecast
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
