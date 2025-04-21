import React, { createContext, useContext, useState, useCallback } from 'react';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (type: NotificationType, message: string) => void;
  removeNotification: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Add a new notification
  const addNotification = useCallback((type: NotificationType, message: string) => {
    const id = Date.now().toString();
    
    setNotifications((prev) => [
      ...prev,
      {
        id,
        type,
        message,
      },
    ]);

    // Auto-remove notification after 5 seconds
    setTimeout(() => {
      removeNotification(id);
    }, 5000);
  }, []);

  // Remove a notification by ID
  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id));
  }, []);

  const value = {
    notifications,
    addNotification,
    removeNotification,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

// Custom hook to use notification context
export const useNotification = () => {
  const context = useContext(NotificationContext);
  
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  
  return context;
};