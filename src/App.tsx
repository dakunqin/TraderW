import type { ReactNode } from 'react'
import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom'

import Home from '@/pages/Home'
import Login from '@/pages/Login'
import ForgotPassword from '@/pages/ForgotPassword'
import ResetPassword from '@/pages/ResetPassword'
import Register from '@/pages/Register'
import Dashboard from '@/pages/Dashboard'
import ApiKeys from '@/pages/ApiKeys'
import Mt5Accounts from '@/pages/Mt5Accounts'
import Mt5AccountDetail from '@/pages/Mt5AccountDetail'
import { useAuthStore } from '@/stores/auth'

function Protected(props: { children: ReactNode }) {
  const hasToken = useAuthStore((s) => !!s.tokens?.accessToken)
  if (!hasToken) return <Navigate to="/login" replace />
  return props.children
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <Protected>
              <Dashboard />
            </Protected>
          }
        />
        <Route
          path="/api-keys"
          element={
            <Protected>
              <ApiKeys />
            </Protected>
          }
        />
        <Route
          path="/mt5-accounts"
          element={
            <Protected>
              <Mt5Accounts />
            </Protected>
          }
        />
        <Route
          path="/mt5-accounts/:id"
          element={
            <Protected>
              <Mt5AccountDetail />
            </Protected>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}
