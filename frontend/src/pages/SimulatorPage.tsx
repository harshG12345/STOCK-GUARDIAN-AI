import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  AlertCircle, 
  TrendingUp, 
  Clock, 
  Package,
  ArrowRight
} from 'lucide-react';
import type { ProductSummary, WhatIfResponse } from '../types';
import { api } from '../api/client';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';

interface SimulatorPageProps {
  products: ProductSummary[];
  selectedProductId: string;
  onSelectProductId: (id: string) => void;
  onNavigate: (tab: string) => void;
}

export const SimulatorPage: React.FC<SimulatorPageProps> = ({
  products,
  selectedProductId,
  onSelectProductId,
  onNavigate,
}) => {
  const [demandChangePct, setDemandChangePct] = useState<number>(0);
  const [inventoryOverride, setInventoryOverride] = useState<number | null>(null);
  const [safetyMultiplier, setSafetyMultiplier] = useState<number>(1.0);
  const [simResult, setSimResult] = useState<WhatIfResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize selected product
  useEffect(() => {
    if (products.length > 0) {
      if (!selectedProductId || !products.some((p) => p.product_id === selectedProductId)) {
        onSelectProductId(products[0].product_id);
      }
    }
  }, [selectedProductId, products, onSelectProductId]);

  // Set default inventory override whenever selected SKU changes
  useEffect(() => {
    const currentProd = products.find((p) => p.product_id === selectedProductId);
    if (currentProd) {
      setInventoryOverride(currentProd.current_stock);
    }
  }, [selectedProductId]);

  // Run dynamic simulation whenever parameters change
  useEffect(() => {
    if (!selectedProductId) return;

    const runSimulation = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.simulateScenario({
          product_id: selectedProductId,
          demand_pct_change: demandChangePct,
          current_inventory_override: inventoryOverride,
          safety_buffer_multiplier: safetyMultiplier,
        });
        setSimResult(res);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to simulate scenario.');
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(() => {
      runSimulation();
    }, 120);

    return () => clearTimeout(timer);
  }, [selectedProductId, demandChangePct, inventoryOverride, safetyMultiplier]);

  const handleReset = () => {
    const currentProd = products.find((p) => p.product_id === selectedProductId);
    setDemandChangePct(0);
    setInventoryOverride(currentProd ? currentProd.current_stock : null);
    setSafetyMultiplier(1.0);
  };

  const selectedProdObj = products.find((p) => p.product_id === selectedProductId);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-5)', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h1 className="page-title">What-If Scenario & Stress Simulator</h1>
          <p className="page-description">
            Stress-test inventory resilience against demand spikes, promotional surges, supplier disruptions, and safety buffer adjustments.
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

      {error && (
        <div className="alert-box alert-critical" style={{ marginBottom: 'var(--space-5)' }}>
          <span>{error}</span>
        </div>
      )}

      {/* Simulator Control Panel */}
      <div className="panel" style={{ marginBottom: 'var(--space-6)' }}>
        <div className="panel-header">
          <div>
            <h2 className="panel-title">Interactive Stress Parameters</h2>
            <p className="panel-subtitle">Adjust variables to immediately recalculate supply-chain consequence</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            {loading && (
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <RefreshCw size={12} className="animate-spin" /> Simulating...
              </span>
            )}
            <button className="btn btn-secondary btn-sm" onClick={handleReset}>
              <RefreshCw size={13} />
              <span>Reset to Baseline</span>
            </button>
          </div>
        </div>

        <div className="panel-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-6)' }}>
            {/* Slider 1: Expected Demand Change % */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
                <label className="form-label" style={{ marginBottom: 0 }}>
                  Expected Demand Surge / Drop (%):
                </label>
                <span className="metric-pill" style={{ fontWeight: 700, color: demandChangePct > 0 ? 'var(--status-critical-solid)' : demandChangePct < 0 ? 'var(--status-safe-solid)' : 'var(--text-primary)' }}>
                  {demandChangePct > 0 ? `+${demandChangePct}%` : `${demandChangePct}%`}
                </span>
              </div>
              <input
                type="range"
                min={-50}
                max={100}
                step={5}
                value={demandChangePct}
                onChange={(e) => setDemandChangePct(Number(e.target.value))}
                className="slider-input"
                style={{ width: '100%' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                <span>-50% (Slump)</span>
                <span>0% (Baseline)</span>
                <span>+50% (Promo)</span>
                <span>+100% (Flash Surge)</span>
              </div>
            </div>

            {/* Input 2: Current Inventory Override */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
                <label className="form-label" style={{ marginBottom: 0 }}>
                  Current Inventory Level Override:
                </label>
                <span className="metric-pill" style={{ fontWeight: 700 }}>
                  {inventoryOverride ?? (selectedProdObj?.current_stock || 0)} Units
                </span>
              </div>
              <input
                type="number"
                min={0}
                max={5000}
                value={inventoryOverride ?? ''}
                onChange={(e) => setInventoryOverride(e.target.value === '' ? null : Number(e.target.value))}
                className="form-input"
                placeholder="Enter custom inventory..."
              />
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Catalog baseline: {selectedProdObj?.current_stock ?? 0} units on hand
              </div>
            </div>

            {/* Selector 3: Safety Buffer Multiplier */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
                <label className="form-label" style={{ marginBottom: 0 }}>
                  Safety Stock Buffer Multiplier:
                </label>
                <span className="metric-pill" style={{ fontWeight: 700 }}>
                  {safetyMultiplier.toFixed(1)}x
                </span>
              </div>
              <select
                className="form-select"
                value={safetyMultiplier}
                onChange={(e) => setSafetyMultiplier(Number(e.target.value))}
              >
                <option value={0.5}>0.5x (Lean / Low holding cost)</option>
                <option value={1.0}>1.0x (Standard 95% Service Level - Recommended)</option>
                <option value={1.5}>1.5x (Elevated buffer / Promo contingency)</option>
                <option value={2.0}>2.0x (High resilience / Disruptive risk)</option>
              </select>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Multiplies statistical Z-score safety stock
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Simulated Consequence Results */}
      {simResult && (
        <>
          <div className="grid-kpi">
            <MetricCard
              label="Adjusted Forecast Demand"
              value={`${simResult.simulation.adjusted_predicted_demand.toLocaleString()} Units`}
              subtext={`Base: ${simResult.simulation.base_predicted_demand} units (${demandChangePct > 0 ? `+${demandChangePct}%` : `${demandChangePct}%`})`}
              icon={<TrendingUp size={18} />}
            />
            <MetricCard
              label="Simulated Risk Level"
              value={simResult.simulation.simulated_risk_level}
              subtext={`Coverage: ${simResult.simulation.coverage_ratio.toFixed(2)}x`}
              badge={<StatusBadge status={simResult.simulation.simulated_risk_level} type="risk" />}
              icon={<AlertCircle size={18} style={{ color: simResult.simulation.badge_color }} />}
            />
            <MetricCard
              label="Days to Potential Stockout"
              value={`${simResult.simulation.estimated_days_to_stockout} Days`}
              subtext={simResult.simulation.stockout_occurs ? `Stockout before ${simResult.simulation.forecast_horizon_days}d horizon!` : 'Sufficient across horizon'}
              icon={<Clock size={18} style={{ color: simResult.simulation.stockout_occurs ? 'var(--status-critical-solid)' : 'var(--status-safe-solid)' }} />}
            />
            <MetricCard
              label="Simulated Reorder Needed"
              value={`+${simResult.simulation.simulated_additional_stock.toLocaleString()} Units`}
              subtext={`Target Stock: ${simResult.simulation.simulated_target_stock} units`}
              icon={<Package size={18} />}
            />
          </div>

          {/* Detailed Decision Impact Card */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2 className="panel-title">
                  Simulated Scenario Outcome: <strong>{simResult.product_name}</strong>
                </h2>
                <p className="panel-subtitle">Calculated operational consequences of modified scenario</p>
              </div>

              <button className="btn btn-primary btn-sm" onClick={() => onNavigate('reorder')}>
                <span>Apply & Review Reorder Plan</span>
                <ArrowRight size={14} />
              </button>
            </div>

            <div className="panel-body">
              {/* Simulation Result Banner */}
              <div
                className={`alert-box ${
                  simResult.simulation.simulated_risk_level === 'CRITICAL'
                    ? 'alert-critical'
                    : simResult.simulation.simulated_risk_level === 'HIGH RISK'
                    ? 'alert-high'
                    : simResult.simulation.simulated_risk_level === 'WATCH'
                    ? 'alert-watch'
                    : 'alert-safe'
                }`}
                style={{ marginBottom: 'var(--space-5)' }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: '14px', marginBottom: '2px' }}>
                    Operational Verdict: {simResult.simulation.action_summary}
                  </div>
                  <div style={{ fontSize: '12px' }}>
                    {simResult.simulation.potential_shortage > 0
                      ? `At ${simResult.simulation.current_stock} units current inventory, a ${demandChangePct}% demand change triggers a direct shortage of ${simResult.simulation.potential_shortage} units before the period ends. Target inventory must be increased to ${simResult.simulation.simulated_target_stock} units.`
                      : `Inventory of ${simResult.simulation.current_stock} units is projected to absorb the scenario with a remaining surplus of ${simResult.simulation.net_stock_after_period} units after the ${simResult.simulation.forecast_horizon_days}-day horizon.`}
                  </div>
                </div>
              </div>

              {/* Side-by-side comparison table */}
              <div className="table-container" style={{ border: 'none' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Scenario Metric</th>
                      <th style={{ textAlign: 'right' }}>Baseline Status</th>
                      <th style={{ textAlign: 'right' }}>What-If Simulated Status</th>
                      <th style={{ textAlign: 'right' }}>Delta / Impact</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Forecast Demand</td>
                      <td style={{ textAlign: 'right' }}>{simResult.simulation.base_predicted_demand} units</td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{simResult.simulation.adjusted_predicted_demand} units</td>
                      <td style={{ textAlign: 'right', fontWeight: 600, color: demandChangePct > 0 ? 'var(--status-critical-solid)' : 'var(--status-safe-solid)' }}>
                        {demandChangePct > 0 ? `+${(simResult.simulation.adjusted_predicted_demand - simResult.simulation.base_predicted_demand).toFixed(1)}` : `${(simResult.simulation.adjusted_predicted_demand - simResult.simulation.base_predicted_demand).toFixed(1)}`} units
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Current Stock on Hand</td>
                      <td style={{ textAlign: 'right' }}>{selectedProdObj?.current_stock ?? 0} units</td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{simResult.simulation.current_stock} units</td>
                      <td style={{ textAlign: 'right' }}>
                        {simResult.simulation.current_stock - (selectedProdObj?.current_stock ?? 0) !== 0 ? (
                          <span>{(simResult.simulation.current_stock - (selectedProdObj?.current_stock ?? 0)) > 0 ? `+${simResult.simulation.current_stock - (selectedProdObj?.current_stock ?? 0)}` : simResult.simulation.current_stock - (selectedProdObj?.current_stock ?? 0)} units</span>
                        ) : (
                          'Unchanged'
                        )}
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Safety Stock Buffer</td>
                      <td style={{ textAlign: 'right' }}>—</td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{simResult.simulation.simulated_buffer} units</td>
                      <td style={{ textAlign: 'right' }}>{safetyMultiplier}x Multiplier</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Reorder Quantity Needed</td>
                      <td style={{ textAlign: 'right' }}>{selectedProdObj?.recommended_additional_stock ?? 0} units</td>
                      <td style={{ textAlign: 'right', fontWeight: 700, color: simResult.simulation.simulated_additional_stock > 0 ? 'var(--status-critical-solid)' : 'var(--status-safe-solid)' }}>
                        +{simResult.simulation.simulated_additional_stock} units
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>
                        ${(simResult.simulation.simulated_additional_stock * simResult.unit_price).toFixed(2)} Capital
                      </td>
                    </tr>
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
