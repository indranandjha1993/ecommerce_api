import { Navigate, useLocation } from 'react-router-dom';
import { AuthGuard } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const location = useLocation();

  return (
    <AuthGuard
      fallback={
        <Navigate to="/login" state={{ from: location }} replace />
      }
    >
      {children}
    </AuthGuard>
  );
};

export default ProtectedRoute;