import React from 'react';
import { cn } from '../../utils/formatters';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  action?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ children, className, title, action }) => {
  return (
    <div
      className={cn(
        'bg-slate-800 rounded-lg border border-slate-700 shadow-xl',
        className
      )}
    >
      {(title || action) && (
        <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
          {title && <h2 className="text-xl font-bold text-white">{title}</h2>}
          {action}
        </div>
      )}
      <div className="p-6">{children}</div>
    </div>
  );
};

interface MetricCardProps {
  label: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  change,
  icon,
  className,
}) => {
  const isPositive = change !== undefined && change > 0;
  const hasChange = change !== undefined && change !== 0;

  return (
    <div
      className={cn(
        'bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-lg hover:shadow-xl transition-shadow',
        className
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-slate-400 text-sm font-medium">{label}</span>
        {icon && <div className="text-slate-400">{icon}</div>}
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      {hasChange && (
        <div
          className={cn(
            'text-sm font-medium flex items-center',
            isPositive ? 'text-green-400' : 'text-red-400'
          )}
        >
          <span className="mr-1">{isPositive ? '↑' : '↓'}</span>
          {Math.abs(change).toFixed(2)}%
        </div>
      )}
    </div>
  );
};
