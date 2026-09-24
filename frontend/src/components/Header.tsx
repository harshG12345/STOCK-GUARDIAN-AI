import React from 'react';
import { 
  BarChart3, 
  Database, 
  TrendingUp, 
  ShieldAlert, 
  ShoppingCart, 
  Sliders, 
  Cpu, 
  RefreshCw,
  FileText,
  ShieldCheck
} from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  activeDataset: string;
  isReady: boolean;
  onOpenRetrainModal: () => void;
  onOpenUploadModal?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  activeDataset,
  isReady,
  onOpenRetrainModal,
}) => {
  const navTabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'data', label: 'Data Studio', icon: Database },
    { id: 'forecast', label: 'Demand Forecast', icon: TrendingUp },
    { id: 'risk', label: 'Inventory Risk', icon: ShieldAlert },
    { id: 'reorder', label: 'Reorder Advisor', icon: ShoppingCart },
    { id: 'simulator', label: 'What-If Simulator', icon: Sliders },
    { id: 'models', label: 'Model Performance', icon: Cpu },
    { id: 'terms', label: 'Terms', icon: FileText },
    { id: 'privacy', label: 'Privacy', icon: ShieldCheck },
  ];

  return (
    <header className="header-wrapper">
      <div className="header-top">
        <div className="brand-section">
          <div className="brand-logo-badge">SG</div>
          <div className="brand-info">
            <span className="brand-title">Stock Guardian AI</span>
            <span className="brand-tagline">Predict demand. Prevent stock-outs. Make smarter inventory decisions.</span>
          </div>
        </div>

        <div className="header-status">
          <div className="source-badge" title="Active dataset in memory">
            <span className="status-dot" style={{ backgroundColor: isReady ? 'var(--status-safe-solid)' : 'var(--status-watch-solid)' }} />
            <span>{activeDataset || 'Loading dataset...'}</span>
          </div>

          <button
            className="btn btn-secondary btn-sm"
            onClick={onOpenRetrainModal}
            title="Configure horizon, service level target, and ML regression model"
          >
            <RefreshCw size={14} />
            <span>Configure & Retrain</span>
          </button>
        </div>
      </div>

      <nav className="nav-tabs-bar" aria-label="Primary navigation">
        {navTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              className={`nav-tab-button ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
              type="button"
            >
              <Icon size={15} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </header>
  );
};
