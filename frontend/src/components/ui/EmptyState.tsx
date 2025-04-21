import React, { ReactNode } from 'react';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center min-h-[60vh]">
      {icon && <div className="mb-6">{icon}</div>}
      <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
      {description && <p className="text-gray-600 mb-6 max-w-md">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  );
};

export default EmptyState;