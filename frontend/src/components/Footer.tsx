import React from 'react';

interface FooterProps {
  onNavigate: (tab: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer className="app-footer">
      <div className="footer-inner">
        <div>
          <strong>Stock Guardian AI</strong> — Predict demand. Prevent stock-outs. Make smarter inventory decisions.
        </div>

        <div className="footer-links">
          <button className="footer-link" style={{ background: 'none', border: 'none', font: 'inherit' }} onClick={() => onNavigate('overview')}>
            Overview
          </button>
          <button className="footer-link" style={{ background: 'none', border: 'none', font: 'inherit' }} onClick={() => onNavigate('data')}>
            Data Studio
          </button>
          <button className="footer-link" style={{ background: 'none', border: 'none', font: 'inherit' }} onClick={() => onNavigate('simulator')}>
            What-If Simulator
          </button>
          <button className="footer-link" style={{ background: 'none', border: 'none', font: 'inherit' }} onClick={() => onNavigate('models')}>
            Model Performance
          </button>
          <button className="footer-link" style={{ background: 'none', border: 'none', font: 'inherit' }} onClick={() => onNavigate('terms')}>
            Terms of Service
          </button>
          <button className="footer-link" style={{ background: 'none', border: 'none', font: 'inherit' }} onClick={() => onNavigate('privacy')}>
            Privacy Policy
          </button>
        </div>
      </div>
    </footer>
  );
};
