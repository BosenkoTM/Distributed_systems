import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import { useAuth } from './hooks/useAuth';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import PrivacyPolicies from './pages/PrivacyPolicies';
import QueryInterface from './pages/QueryInterface';
import AdminPanel from './pages/AdminPanel';
import Monitoring from './pages/Monitoring';
import LoadingSpinner from './components/Common/LoadingSpinner';
import './App.css';

const { Content } = Layout;

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Login />;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      <Layout>
        <Header />
        <Content style={{ padding: '24px', background: '#f5f5f5' }}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/privacy-policies" element={<PrivacyPolicies />} />
            <Route path="/query" element={<QueryInterface />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/monitoring" element={<Monitoring />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
