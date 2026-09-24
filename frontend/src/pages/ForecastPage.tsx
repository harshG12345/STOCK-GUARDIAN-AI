import React, { useState, useEffect } from 'react';
import { 
  ResponsiveContainer, 
  ComposedChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid, 
  BarChart, 
  Bar
} from 'recharts';
import { TrendingUp, Package, DollarSign, Layers } from 'lucide-react';
import type { ProductForecastResponse, ProductSummary } from '../types';
import { api } from '../api/client';
import { MetricCard } from '../components/MetricCard';

interface ForecastPageProps {
  products: ProductSummary[];
  selectedProductId: string;
  onSelectProductId: (id: string) => void;
  onNavigate: (tab: string) => void;
}

export const ForecastPage: React.FC<ForecastPageProps> = ({
  products,
  selectedProductId,
  onSelectProductId,
  onNavigate,
}) => {
  const [forecastData, setForecastData] = useState<ProductForecastResponse | null>(null);
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
      const loadForecast = async () => {
        setLoading(true);
        setError(null);
        try {
          const res = await api.getProductForecast(activeId);
          setForecastData(res);
        } catch (err: any) {
          setError(err?.response?.data?.detail || 'Failed to fetch product forecast.');
        } finally {
          setLoading(false);
        }
      };
      loadForecast();
    }
  }, [selectedProductId, products, onSelectProductId]);

  // Merge history and forecast records for continuous charting
  const chartTimeline = React.useMemo(() => {
    if (!forecastData) return [];
    
    // Take recent history (last 45 days) plus future forecast
    const recentHistory = forecastData.history.slice(-45).map((h) => ({
      date: h.Date,
      actualSales: h.Sales_Units,
      forecastDemand: null as number | null,
      stockOnHand: h.Stock_On_Hand,
      type: 'History',
    }));

    // Last historical point connects to forecast
    const lastHist = recentHistory[recentHistory.length - 1];

    const futurePoints = forecastData.forecast_breakdown.map((f) => ({
      date: f.Date,
      actualSales: null as number | null,
      forecastDemand: f.Forecast_Demand,
      stockOnHand: null as number | null,
      type: 'Forecast',
    }));

    if (lastHist && futurePoints.length > 0) {
      // Create bridge point
      lastHist.forecastDemand = lastHist.actualSales;
    }

    return [...recentHistory, ...futurePoints];
  }, [forecastData]);

  // Prepare feature importances for chart
  const featureImportancesList = React.useMemo(() => {
    if (!forecastData?.feature_importances) return [];
    return Object.entries(forecastData.feature_importances)
      .map(([feature, importance]) => ({
        feature: feature.replace('_', ' '),
        importance: Math.round(importance * 1000) / 10, // Convert to percentage
      }))
      .sort((a, b) => b.importance - a.importance)
      .slice(0, 8);
  }, [forecastData]);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-5)', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h1 className="page-title">Demand Forecasting & Historical Trajectory</h1>
          <p className="page-description">
            Recursive multi-step supervised regression demand forecasting with lag dynamics and calendar seasonality.
          </p>
        </div>

        {/* Product SKU Selector */}
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
          Computing recursive forecast series for {selectedProductId}...
        </div>
      )}

      {error && (
        <div className="alert-box alert-critical">
          <span>{error}</span>
        </div>
      )}

      {forecastData && !loading && (
        <>
          {/* Key Metrics Summary */}
          <div className="grid-kpi">
            <MetricCard
              label="Selected Product"
              value={forecastData.product_name}
              subtext={`Category: ${forecastData.category} | SKU: ${forecastData.product_id}`}
              icon={<Package size={18} />}
            />
            <MetricCard
              label="Current Inventory"
              value={`${forecastData.current_stock.toLocaleString()} Units`}
              subtext={`Lead Time: ${forecastData.lead_time_days} days`}
              icon={<Layers size={18} />}
            />
            <MetricCard
              label={`Total ${forecastData.forecast_horizon_days}-Day Forecast`}
              value={`${forecastData.total_predicted_demand.toLocaleString()} Units`}
              subtext={`Avg ${forecastData.avg_daily_forecast} units/day`}
              icon={<TrendingUp size={18} />}
            />
            <MetricCard
              label="Unit Selling Price"
              value={`$${forecastData.unit_price.toFixed(2)}`}
              subtext="Catalog unit price"
              icon={<DollarSign size={18} />}
            />
          </div>

          {/* Main Forecast Timeline Chart */}
          <div className="panel" style={{ marginBottom: 'var(--space-6)' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Historical Sales vs Predicted Demand Timeline</h2>
                <p className="panel-subtitle">
                  Solid blue indicates historical recorded demand; dashed royal blue represents multi-step recursive ML prediction
                </p>
              </div>

              <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('simulator')}>
                  Test in Simulator
                </button>
                <button className="btn btn-primary btn-sm" onClick={() => onNavigate('reorder')}>
                  View Reorder Plan
                </button>
              </div>
            </div>

            <div className="panel-body">
              <div style={{ height: '360px', width: '100%', minHeight: '360px' }}>
                <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={300}>
                  <ComposedChart data={chartTimeline} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
                      stroke="var(--border-strong)"
                      tickFormatter={(val) => val ? val.slice(5) : ''}
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
                        color: 'var(--text-primary)',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Line
                      type="monotone"
                      dataKey="actualSales"
                      name="Historical Sales (Units)"
                      stroke="#475569"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="forecastDemand"
                      name={`Forecast Demand (${forecastData.forecast_horizon_days}D Horizon)`}
                      stroke="var(--accent-primary)"
                      strokeWidth={2.5}
                      strokeDasharray="4 4"
                      dot={{ r: 3, fill: 'var(--accent-primary)' }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Lower Grid: Feature Importances & Daily Breakdown Table */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 'var(--space-6)' }}>
            {/* Feature Importances */}
            <div className="panel" style={{ marginBottom: 0 }}>
              <div className="panel-header">
                <div>
                  <h3 className="panel-title">Model Feature Importances</h3>
                  <p className="panel-subtitle">Key statistical drivers influencing forecast weights</p>
                </div>
              </div>
              <div className="panel-body">
                <div style={{ height: '280px', width: '100%', minHeight: '280px' }}>
                  <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={280}>
                    <BarChart data={featureImportancesList} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" horizontal={false} />
                      <XAxis
                        type="number"
                        unit="%"
                        tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
                        stroke="var(--border-strong)"
                      />
                      <YAxis
                        type="category"
                        dataKey="feature"
                        tick={{ fontSize: 11, fill: 'var(--text-secondary)' }}
                        stroke="var(--border-strong)"
                        width={100}
                      />
                      <Tooltip
                        formatter={(val: any) => [`${val}%`, 'Importance Weight']}
                        contentStyle={{
                          backgroundColor: 'var(--bg-surface)',
                          borderColor: 'var(--border-strong)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '12px',
                        }}
                      />
                      <Bar dataKey="importance" fill="var(--accent-primary)" radius={[0, 3, 3, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Daily Forecast Breakdown Table */}
            <div className="panel" style={{ marginBottom: 0 }}>
              <div className="panel-header">
                <div>
                  <h3 className="panel-title">Daily Forecast Breakdown</h3>
                  <p className="panel-subtitle">Day-by-day projected demand schedule</p>
                </div>
              </div>
              <div className="panel-body" style={{ padding: 0 }}>
                <div className="table-container" style={{ border: 'none', maxHeight: '280px' }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Horizon Day</th>
                        <th>Projected Date</th>
                        <th style={{ textAlign: 'right' }}>Predicted Demand</th>
                      </tr>
                    </thead>
                    <tbody>
                      {forecastData.forecast_breakdown.map((row) => (
                        <tr key={row.Horizon_Day}>
                          <td style={{ fontWeight: 600 }}>Day +{row.Horizon_Day}</td>
                          <td>{row.Date}</td>
                          <td style={{ textAlign: 'right', fontWeight: 600 }}>{row.Forecast_Demand.toFixed(1)} units</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
