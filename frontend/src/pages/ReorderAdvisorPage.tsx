import React, { useState, useEffect } from 'react';
import { 
  ShoppingCart, 
  DollarSign, 
  Package, 
  Copy, 
  Check 
} from 'lucide-react';
import type { ProductRiskResponse, ProductSummary } from '../types';
import { api } from '../api/client';
import { MetricCard } from '../components/MetricCard';

interface ReorderAdvisorPageProps {
  products: ProductSummary[];
  selectedProductId: string;
  onSelectProductId: (id: string) => void;
  onSuccessMessage: (msg: string) => void;
}

export const ReorderAdvisorPage: React.FC<ReorderAdvisorPageProps> = ({
  products,
  selectedProductId,
  onSelectProductId,
  onSuccessMessage,
}) => {
  const [riskData, setRiskData] = useState<ProductRiskResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    let activeId = selectedProductId;
    if (products.length > 0) {
      if (!activeId || !products.some((p) => p.product_id === activeId)) {
        activeId = products[0].product_id;
        onSelectProductId(activeId);
      }
    }

    if (activeId) {
      const loadData = async () => {
        setLoading(true);
        try {
          const res = await api.getProductRisk(activeId);
          setRiskData(res);
        } catch (err) {
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      loadData();
    }
  }, [selectedProductId, products, onSelectProductId]);

  const totalCapitalAllSKUs = React.useMemo(() => {
    return products.reduce((acc, p) => acc + (p.estimated_capital || 0), 0);
  }, [products]);

  const totalUnitsToOrder = React.useMemo(() => {
    return products.reduce((acc, p) => acc + (p.recommended_additional_stock || 0), 0);
  }, [products]);

  const skusRequiringOrder = React.useMemo(() => {
    return products.filter((p) => p.recommended_additional_stock > 0);
  }, [products]);

  const handleCopyOrder = () => {
    if (!riskData) return;
    const plan = riskData.reorder_plan;
    const text = `PURCHASE ORDER DRAFT\nProduct: ${plan.product_name}\nCurrent Stock: ${plan.current_inventory} units\nPredicted Demand: ${plan.predicted_demand} units\nSafety Stock: ${plan.safety_buffer} units\nRecommended Order Quantity: ${plan.recommended_additional_stock} units\nUnit Cost: $${plan.unit_cost.toFixed(2)}\nEstimated Total Capital: $${plan.estimated_capital_required.toFixed(2)}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    onSuccessMessage('Purchase order details copied to clipboard.');
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-5)', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h1 className="page-title">Smart Reorder Advisor & Safety Stock Calculator</h1>
          <p className="page-description">
            Mathematically rigorous inventory replenishment based on demand variance, supplier lead time, and target service levels.
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

      {/* High-level portfolio reorder metrics */}
      <div className="grid-kpi">
        <MetricCard
          label="SKUs Requiring Reorder"
          value={`${skusRequiringOrder.length} of ${products.length} SKUs`}
          subtext="Immediate purchase order triggers"
          icon={<ShoppingCart size={18} />}
        />
        <MetricCard
          label="Total Units to Procure"
          value={`${totalUnitsToOrder.toLocaleString()} Units`}
          subtext="Portfolio-wide replenishment"
          icon={<Package size={18} />}
        />
        <MetricCard
          label="Total Procurement Commitment"
          value={`$${totalCapitalAllSKUs.toLocaleString()}`}
          subtext="Estimated capital expenditure"
          icon={<DollarSign size={18} />}
        />
      </div>

      {riskData && !loading && (
        <>
          {/* Detailed SKU Reorder Breakdown */}
          <div className="panel" style={{ marginBottom: 'var(--space-6)' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">
                  Reorder Formulation for: <strong>{riskData.reorder_plan.product_name}</strong>
                </h2>
                <p className="panel-subtitle">
                  Service Level: {riskData.reorder_plan.service_level} (Z = {riskData.reorder_plan.z_factor}) | Lead Time: {riskData.reorder_plan.lead_time_days} Days
                </p>
              </div>

              <button className="btn btn-secondary btn-sm" onClick={handleCopyOrder}>
                {copied ? <Check size={14} style={{ color: 'var(--status-safe-solid)' }} /> : <Copy size={14} />}
                <span>{copied ? 'Copied' : 'Copy PO Summary'}</span>
              </button>
            </div>

            <div className="panel-body">
              {/* 4 Steps Formula Panel */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)', marginBottom: 'var(--space-5)' }}>
                {/* Step 1 */}
                <div style={{ padding: 'var(--space-4)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-surface)' }}>
                  <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Step 1: Safety Buffer (SS)
                  </div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--accent-primary)', marginBottom: '4px' }}>
                    +{riskData.reorder_plan.safety_buffer} Units
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Formula: {riskData.reorder_plan.formula_breakdown.step_1_safety_buffer}
                  </div>
                </div>

                {/* Step 2 */}
                <div style={{ padding: 'var(--space-4)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-surface)' }}>
                  <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Step 2: Target Target Stock
                  </div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                    {riskData.reorder_plan.recommended_target_inventory} Units
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Formula: {riskData.reorder_plan.formula_breakdown.step_2_target_inventory}
                  </div>
                </div>

                {/* Step 3 */}
                <div style={{ padding: 'var(--space-4)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-surface)' }}>
                  <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Step 3: Recommended Reorder Qty
                  </div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: riskData.reorder_plan.recommended_additional_stock > 0 ? 'var(--status-critical-solid)' : 'var(--status-safe-solid)', marginBottom: '4px' }}>
                    +{riskData.reorder_plan.recommended_additional_stock} Units
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Formula: {riskData.reorder_plan.formula_breakdown.step_3_reorder_qty}
                  </div>
                </div>

                {/* Step 4 */}
                <div style={{ padding: 'var(--space-4)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-surface)' }}>
                  <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Step 4: Capital Commitment
                  </div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                    ${riskData.reorder_plan.estimated_capital_required.toFixed(2)}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    At ${riskData.reorder_plan.unit_cost.toFixed(2)} / unit procurement cost
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Portfolio Reorder Plan Master Table */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <h2 className="panel-title">Portfolio Reorder & Purchase Order Schedule</h2>
            <p className="panel-subtitle">Calculated replenishment orders across all tracked catalog items</p>
          </div>
        </div>

        <div className="panel-body" style={{ padding: 0 }}>
          <div className="table-container" style={{ border: 'none' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product Name / SKU</th>
                  <th>Category</th>
                  <th style={{ textAlign: 'right' }}>On-Hand Stock</th>
                  <th style={{ textAlign: 'right' }}>Forecast Demand</th>
                  <th style={{ textAlign: 'right' }}>Days Supply</th>
                  <th style={{ textAlign: 'right' }}>Lead Time</th>
                  <th style={{ textAlign: 'right' }}>Recommended Reorder</th>
                  <th style={{ textAlign: 'right' }}>Unit Price</th>
                  <th style={{ textAlign: 'right' }}>Capital Required</th>
                  <th style={{ textAlign: 'center' }}>Inspect</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.product_id} style={{ backgroundColor: p.product_id === selectedProductId ? 'var(--bg-surface-subtle)' : undefined }}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{p.product_name}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-family-mono)' }}>{p.product_id}</div>
                    </td>
                    <td>{p.category}</td>
                    <td style={{ textAlign: 'right', fontWeight: 600 }}>{p.current_stock.toLocaleString()}</td>
                    <td style={{ textAlign: 'right', fontWeight: 600 }}>{p.predicted_demand.toLocaleString()}</td>
                    <td style={{ textAlign: 'right' }}>{p.days_of_supply}d</td>
                    <td style={{ textAlign: 'right' }}>{p.lead_time_days}d</td>
                    <td style={{ textAlign: 'right' }}>
                      {p.recommended_additional_stock > 0 ? (
                        <span style={{ fontWeight: 700, color: 'var(--status-critical-solid)' }}>
                          +{p.recommended_additional_stock.toLocaleString()} units
                        </span>
                      ) : (
                        <span style={{ color: 'var(--status-safe-solid)', fontWeight: 600 }}>Sufficient</span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      {p.recommended_additional_stock > 0 && p.estimated_capital > 0
                        ? `$${(p.estimated_capital / p.recommended_additional_stock).toFixed(2)}`
                        : '—'}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 600 }}>
                      {p.estimated_capital > 0 ? `$${p.estimated_capital.toLocaleString()}` : '$0.00'}
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        className="btn btn-secondary btn-sm"
                        style={{ padding: '2px 8px', fontSize: '11px' }}
                        onClick={() => onSelectProductId(p.product_id)}
                      >
                        {p.product_id === selectedProductId ? 'Active' : 'Details'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
