import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, Info, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  type?: 'risk' | 'trend' | 'shock' | 'model';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'risk' }) => {
  const norm = (status || '').toUpperCase().trim();

  if (type === 'trend') {
    if (norm === 'INCREASING') {
      return (
        <span className="badge badge-critical" title="Demand trending upward">
          <TrendingUp size={12} />
          <span>Increasing</span>
        </span>
      );
    }
    if (norm === 'DECREASING') {
      return (
        <span className="badge badge-safe" title="Demand trending downward">
          <TrendingDown size={12} />
          <span>Decreasing</span>
        </span>
      );
    }
    return (
      <span className="badge badge-neutral" title="Demand is stable">
        <Minus size={12} />
        <span>Stable</span>
      </span>
    );
  }

  if (type === 'shock') {
    if (norm === 'UNUSUAL INCREASE') {
      return (
        <span className="badge badge-critical" title="Significant positive statistical surge">
          <AlertCircle size={12} />
          <span>Demand Surge</span>
        </span>
      );
    }
    if (norm === 'UNUSUAL DECREASE') {
      return (
        <span className="badge badge-watch" title="Significant drop in demand">
          <AlertTriangle size={12} />
          <span>Demand Drop</span>
        </span>
      );
    }
    return (
      <span className="badge badge-neutral" title="Within normal statistical variance">
        <span>Normal</span>
      </span>
    );
  }

  // Default: Risk levels
  if (norm === 'CRITICAL') {
    return (
      <span className="badge badge-critical">
        <AlertCircle size={12} />
        <span>Critical</span>
      </span>
    );
  }
  if (norm === 'HIGH RISK' || norm === 'HIGH') {
    return (
      <span className="badge badge-high">
        <AlertTriangle size={12} />
        <span>High Risk</span>
      </span>
    );
  }
  if (norm === 'WATCH') {
    return (
      <span className="badge badge-watch">
        <Info size={12} />
        <span>Watch</span>
      </span>
    );
  }
  return (
    <span className="badge badge-safe">
      <CheckCircle size={12} />
      <span>Safe</span>
    </span>
  );
};
