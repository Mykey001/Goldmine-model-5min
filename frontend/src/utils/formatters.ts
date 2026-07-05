import { format, formatDistanceToNow } from 'date-fns';

// Format currency
export const formatCurrency = (value: number | undefined | null, decimals: number = 2): string => {
  if (value === undefined || value === null || isNaN(value)) {
    value = 0;
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

// Format percentage
export const formatPercentage = (value: number | undefined | null, decimals: number = 2): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.00%';
  }
  return `${value.toFixed(decimals)}%`;
};

// Format number
export const formatNumber = (value: number | undefined | null, decimals: number = 2): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.00';
  }
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

// Format datetime
export const formatDateTime = (dateString: string): string => {
  return format(new Date(dateString), 'MMM dd, yyyy HH:mm:ss');
};

// Format date
export const formatDate = (dateString: string): string => {
  return format(new Date(dateString), 'MMM dd, yyyy');
};

// Format time
export const formatTime = (dateString: string): string => {
  return format(new Date(dateString), 'HH:mm:ss');
};

// Format relative time
export const formatRelativeTime = (dateString: string): string => {
  return formatDistanceToNow(new Date(dateString), { addSuffix: true });
};

// Format duration in minutes
export const formatDuration = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

// Get color for profit/loss
export const getProfitColor = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'text-gray-400';
  if (value > 0) return 'text-green-400';
  if (value < 0) return 'text-red-400';
  return 'text-gray-400';
};

// Get background color for profit/loss
export const getProfitBgColor = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'bg-gray-900/20 text-gray-400';
  if (value > 0) return 'bg-green-900/20 text-green-400';
  if (value < 0) return 'bg-red-900/20 text-red-400';
  return 'bg-gray-900/20 text-gray-400';
};

// Get direction badge color
export const getDirectionColor = (direction: 'BUY' | 'SELL'): string => {
  return direction === 'BUY' ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300';
};

// Format price with proper decimal places
export const formatPrice = (price: number | undefined | null, digits: number = 2): string => {
  if (price === undefined || price === null || isNaN(price)) {
    return '0.00';
  }
  return price.toFixed(digits);
};

// Calculate percentage change
export const calculatePercentageChange = (current: number, previous: number): number => {
  if (previous === 0) return 0;
  return ((current - previous) / previous) * 100;
};

// Truncate text
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Class name helper (similar to clsx)
export const cn = (...classes: (string | undefined | null | false)[]): string => {
  return classes.filter(Boolean).join(' ');
};
