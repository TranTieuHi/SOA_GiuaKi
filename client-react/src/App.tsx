import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './features/authentication/pages/LoginPage'; 
import { Dashboard } from './features/dashboard/components/Dashboard';
import { SearchStudentPage } from './features/tuition/pages/SearchStudentPage';
import { OTPVerifyPage } from './features/tuition/pages/OTPVerifyPage';
import { PaymentSuccessPage } from './features/tuition/pages/PaymentSuccessPage';
import { PaymentHistoryPage } from './features/payment-history/PaymentHistoryPage'; // ✅ Add
import { isAuthenticated } from './features/authentication/services/authService';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return isAuthenticated() ? <>{children}</> : <Navigate to="/login" replace />;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  return isAuthenticated() ? <Navigate to="/dashboard" replace /> : <>{children}</>;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            isAuthenticated() ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />

        <Route 
          path="/login" 
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          } 
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/tuition"
          element={
            <ProtectedRoute>
              <SearchStudentPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/tuition/otp-verify"
          element={
            <ProtectedRoute>
              <OTPVerifyPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/tuition/success"
          element={
            <ProtectedRoute>
              <PaymentSuccessPage />
            </ProtectedRoute>
          }
        />

        {/* ✅ Add Payment History Route */}
        <Route
          path="/payment-history"
          element={
            <ProtectedRoute>
              <PaymentHistoryPage />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;