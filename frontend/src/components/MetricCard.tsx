import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  badge?: React.ReactNode;
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtext,
  badge,
  icon,
}) => {
  return (
    <div className="kpi-card">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span className="kpi-label">{label}</span>
          {icon && <span style={{ color: 'var(--text-muted)' }}>{icon}</span>}
        </div>
        <div className="kpi-value">{value}</div>
      </div>
      {(subtext || badge) && (
        <div className="kpi-footer">
          {subtext && <span>{subtext}</span>}
          {badge && <div>{badge}</div>}
        </div>
      )}
    </div>
  );
};
