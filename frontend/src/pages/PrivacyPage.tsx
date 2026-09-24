import React from 'react';
import { AlertCircle } from 'lucide-react';

export const PrivacyPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 'var(--space-5)' }}>
        <h1 className="page-title">Privacy Policy & Data Processing Notice</h1>
        <p className="page-description">
          Information regarding data handling, local execution, and storage practices within Stock Guardian AI.
        </p>
      </div>

      <div className="alert-box alert-neutral" style={{ marginBottom: 'var(--space-6)' }}>
        <AlertCircle size={18} style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong>Draft Document Notice:</strong> This privacy notice outlines technical data flows for review. If deploying in a regulated multi-tenant production environment, conduct formal compliance review.
        </div>
      </div>

      <div className="panel">
        <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)', fontSize: '13px', lineHeight: 1.7 }}>
          <div>
            <h2 className="section-title">1. Local and On-Premise Execution</h2>
            <p>
              Stock Guardian AI executes all machine learning models, statistical computations, and file validations directly on your designated backend service. Uploaded CSV and Excel datasets are parsed in memory and not transmitted to external third-party AI APIs or external servers.
            </p>
          </div>

          <div>
            <h2 className="section-title">2. Information Ingested</h2>
            <p>
              The platform processes operational inventory attributes including transaction dates, sales quantities, current stock levels, unit pricing, supplier lead times, and promotional indicators. No customer personally identifiable information (PII) is required or collected for demand forecasting calculations.
            </p>
          </div>

          <div>
            <h2 className="section-title">3. Model Training and Data Persistence</h2>
            <p>
              Trained supervised regression models (Random Forest, HistGradientBoosting) derive parameters directly from the currently active dataset. In-memory data structures are refreshed upon new file uploads or explicit benchmark resets.
            </p>
          </div>

          <div>
            <h2 className="section-title">4. Security and Access Controls</h2>
            <p>
              Network communication between the React interface and the FastAPI backend occurs over standard HTTP/REST channels within your network perimeter. Access control and network security should be governed by your organization's infrastructure policies.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
