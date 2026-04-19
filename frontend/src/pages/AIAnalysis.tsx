import { useParams, Navigate } from 'react-router-dom';

export default function AIAnalysis() {
  const { ticker } = useParams<{ ticker: string }>();
  return <Navigate to={`/quick-look/${ticker?.toUpperCase()}`} replace />;
}
