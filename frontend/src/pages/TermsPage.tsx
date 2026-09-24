import React from 'react';
import { AlertCircle } from 'lucide-react';

export const TermsPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 'var(--space-5)' }}>
        <h1 className="page-title">Terms of Service (Draft / Review Notice)</h1>
        <p className="page-description">
          Operational terms and conditions governing the Stock Guardian AI analytics application.
        </p>
      </div>

      <div className="alert-box alert-neutral" style={{ marginBottom: 'var(--space-6)' }}>
        <AlertCircle size={18} style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong>Draft Document Notice:</strong> This document represents a working operational draft for review. It does not constitute binding legal commitments without final organizational review.
        </div>
      </div>

      <div className="panel">
        <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)', fontSize: '13px', lineHeight: 1.7 }}>
          <div>
            <h2 className="section-title">1. Purpose and Decision Support Scope</h2>
            <p>
              Stock Guardian AI provides statistical demand forecasting, inventory risk scoring, and automated reorder recommendations. The software is designed as a decision-support platform for inventory analysts and supply chain planners. All recommendations and simulated outcomes should be evaluated in accordance with internal business policies, supplier contracts, and storage constraints.
            </p>
          </div>

          <div>
            <h2 className="section-title">2. Data Ingestion and Ownership</h2>
            <p>
              All historical sales, transaction records, inventory balances, and supplier lead times uploaded to this instance are processed locally in your execution environment. You retain all proprietary rights, ownership, and title to your uploaded business data.
            </p>
          </div>

          <div>
            <h2 className="section-title">3. Forecasting Disclaimer and Variance</h2>
            <p>
              Demand forecasts are empirical statistical estimates generated from historical patterns, rolling metrics, and regression models. Actual market demand may vary due to unforeseen macroeconomic shifts, supplier delays, or extreme market events. Stock Guardian AI does not guarantee zero stock-outs or exact demand matching.
            </p>
          </div>

          <div>
            <h2 className="section-title">4. System Availability and Local Deployment</h2>
            <p>
              This instance is deployed as an internal enterprise analytics service. Maintenance, retraining parameters, and local data persistence are managed within the hosting deployment configuration.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
