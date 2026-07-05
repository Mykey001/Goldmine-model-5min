import React from 'react';
import { cn } from '../../utils/formatters';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'danger' | 'warning' | 'info' | 'default';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'default', 
  className 
}) => {
  const variants = {
    success: 'bg-green-900/30 text-green-300 border-green-700',
    danger: 'bg-red-900/30 text-red-300 border-red-700',
    warning: 'bg-yellow-900/30 text-yellow-300 border-yellow-700',
    info: 'bg-blue-900/30 text-blue-300 border-blue-700',
    default: 'bg-slate-700/30 text-slate-300 border-slate-600',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
};
