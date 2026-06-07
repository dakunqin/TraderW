import { Navigate } from 'react-router-dom'

import { useAuthStore } from '@/stores/auth'

export default function Home() {
  const hasToken = useAuthStore((s) => !!s.tokens?.accessToken)
  return <Navigate to={hasToken ? '/dashboard' : '/login'} replace />
}
