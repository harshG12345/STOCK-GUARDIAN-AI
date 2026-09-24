import React, { useState, useEffect, useCallback } from 'react';
import { api } from './api/client';
import type { DashboardSummaryResponse, DataSummaryResponse, ProductSummary } from './types';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { RetrainModal } from './components/RetrainModal';
import { OverviewPage } from './pages/OverviewPage';
import { DataPage } from './pages/DataPage';
import { ForecastPage } from './pages/ForecastPage';
import { RiskPage } from './pages/RiskPage';
import { ReorderAdvisorPage } from './pages/ReorderAdvisorPage';
import { SimulatorPage } from './pages/SimulatorPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { TermsPage } from './pages/TermsPage';
import { PrivacyPage } from './pages/PrivacyPage';
import { AlertTriangle, CheckCircle2, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  
  // Dashboard & Dataset State
  const [dashboardData, setDashboardData] = useState<DashboardSummaryResponse | null>(null);
  const [dataSummary, setDataSummary] = useState<DataSummaryResponse | null>(null);
  const [products, setProducts] = useState<ProductSummary[]>([]);
  
  // Status states
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [showRetrainModal, setShowRetrainModal] = useState<boolean>(false);

  // Fetch all primary dataset information
  const loadAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [dash, summary, prods] = await Promise.all([
        api.getDashboardSummary(),
        api.getDataSummary(),
        api.getProducts(),
      ]);

      setDashboardData(dash);
      setDataSummary(summary);
      setProducts(prods);

      if (prods.length > 0) {
        setSelectedProductId((prev) => {
          if (!prev || !prods.some((p) => p.product_id === prev)) {
            return prods[0].product_id;
          }
          return prev;
        });
      }
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError(
        err?.response?.data?.detail ||
          'Unable to connect to Stock Guardian AI backend server. Please verify FastAPI is running.'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  // Handle SKU selection from child components and navigate to a target tab
  const handleSelectProduct = (productId: string, targetTab?: string) => {
    setSelectedProductId(productId);
    if (targetTab) {
      setActiveTab(targetTab);
    }
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  return (
    <div className="app-container">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeDataset={dashboardData?.kpis.active_dataset || 'Curated Benchmark (12 SKUs)'}
        isReady={!!dashboardData}
        onOpenRetrainModal={() => setShowRetrainModal(true)}
      />

      <main className="main-content">
        {/* Toast Notification */}
        {toastMessage && (
          <div className="alert-box alert-safe" style={{ marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <CheckCircle2 size={16} />
              <span>{toastMessage}</span>
            </div>
            <button
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: 600, color: 'var(--status-safe-text)' }}
              onClick={() => setToastMessage(null)}
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Global Error Banner */}
        {error && (
          <div className="alert-box alert-critical" style={{ marginBottom: 'var(--space-5)' }}>
            <AlertTriangle size={18} style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Connection Error:</strong> {error}
            </div>
            <button className="btn btn-secondary btn-sm" onClick={loadAllData}>
              <RefreshCw size={13} />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* Global Loading State */}
        {loading && !dashboardData ? (
          <div className="panel" style={{ padding: 'var(--space-10)', textAlign: 'center', color: 'var(--text-muted)' }}>
            <RefreshCw size={24} className="animate-spin" style={{ margin: '0 auto 12px', color: 'var(--accent-primary)' }} />
            <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
              Initializing Stock Guardian AI Data Pipeline...
            </div>
            <div style={{ fontSize: '12px' }}>
              Extracting time-series features and calculating inventory risk models.
            </div>
          </div>
        ) : (
          <>
            {/* View Switching */}
            {activeTab === 'overview' && dashboardData && (
              <OverviewPage
                data={dashboardData}
                onSelectProduct={handleSelectProduct}
                onNavigate={setActiveTab}
              />
            )}

            {activeTab === 'data' && (
              <DataPage
                dataSummary={dataSummary}
                onRefreshData={loadAllData}
                onSuccessMessage={showToast}
              />
            )}

            {activeTab === 'forecast' && (
              <ForecastPage
                products={products}
                selectedProductId={selectedProductId}
                onSelectProductId={setSelectedProductId}
                onNavigate={setActiveTab}
              />
            )}

            {activeTab === 'risk' && (
              <RiskPage
                products={products}
                selectedProductId={selectedProductId}
                onSelectProductId={setSelectedProductId}
                onNavigate={setActiveTab}
              />
            )}

            {activeTab === 'reorder' && (
              <ReorderAdvisorPage
                products={products}
                selectedProductId={selectedProductId}
                onSelectProductId={setSelectedProductId}
                onSuccessMessage={showToast}
              />
            )}

            {activeTab === 'simulator' && (
              <SimulatorPage
                products={products}
                selectedProductId={selectedProductId}
                onSelectProductId={setSelectedProductId}
                onNavigate={setActiveTab}
              />
            )}

            {activeTab === 'models' && (
              <ModelPerformancePage
                products={products}
                selectedProductId={selectedProductId}
                onSelectProductId={setSelectedProductId}
                onOpenRetrainModal={() => setShowRetrainModal(true)}
              />
            )}

            {activeTab === 'terms' && <TermsPage />}

            {activeTab === 'privacy' && <PrivacyPage />}
          </>
        )}
      </main>

      <Footer onNavigate={setActiveTab} />

      {/* Retrain Configuration Modal */}
      {showRetrainModal && (
        <RetrainModal
          isOpen={showRetrainModal}
          onClose={() => setShowRetrainModal(false)}
          currentHorizon={dashboardData?.kpis.forecast_horizon_days || 14}
          currentServiceLevel={dashboardData?.kpis.service_level || '95%'}
          onSuccess={(msg) => {
            showToast(msg);
            loadAllData();
          }}
        />
      )}
    </div>
  );
};

export default App;
