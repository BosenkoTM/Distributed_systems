import React from 'react';
import { Row, Col, Card, Statistic, Typography, Space } from 'antd';
import {
  DatabaseOutlined,
  ShieldOutlined,
  UserOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { adminAPI, monitoringAPI } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const { Title } = Typography;

const Dashboard = () => {
  const { data: systemStats, isLoading: statsLoading } = useQuery(
    'systemStats',
    adminAPI.getSystemStats,
    {
      refetchInterval: 30000, // Обновление каждые 30 секунд
    }
  );

  const { data: dashboardData, isLoading: dashboardLoading } = useQuery(
    'dashboardData',
    monitoringAPI.getDashboardData,
    {
      refetchInterval: 30000,
    }
  );

  if (statsLoading || dashboardLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <Title level={2}>Дашборд системы</Title>
      
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Всего пользователей"
              value={systemStats?.total_users || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Активных пользователей"
              value={systemStats?.active_users || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Всего запросов"
              value={systemStats?.total_queries || 0}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Политик приватности"
              value={systemStats?.privacy_policies_count || 0}
              prefix={<ShieldOutlined />}
              valueStyle={{ color: '#eb2f96' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Статус системы" extra={<BarChartOutlined />}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <span className="status-indicator status-healthy"></span>
                <span>База данных: Подключена</span>
              </div>
              <div>
                <span className="status-indicator status-healthy"></span>
                <span>Redis: Подключен</span>
              </div>
              <div>
                <span className="status-indicator status-healthy"></span>
                <span>API: Работает</span>
              </div>
              <div>
                <span className="status-indicator status-warning"></span>
                <span>Мониторинг: Внимание</span>
              </div>
            </Space>
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="Последние активности">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>• Пользователь admin создал политику k-анонимности</div>
              <div>• Выполнен запрос к таблице personal_data</div>
              <div>• Применена анонимизация для 150 записей</div>
              <div>• Создан новый пользователь analyst2</div>
              <div>• Обновлена политика l-разнообразия</div>
            </Space>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24}>
          <Card title="Метрики приватности">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <div className="metric-item">
                  <div className="metric-item-value">
                    {dashboardData?.privacy_metrics?.k_anonymity_applied || 0}
                  </div>
                  <div className="metric-item-label">K-анонимность применена</div>
                </div>
              </Col>
              
              <Col xs={24} sm={8}>
                <div className="metric-item">
                  <div className="metric-item-value">
                    {dashboardData?.privacy_metrics?.l_diversity_applied || 0}
                  </div>
                  <div className="metric-item-label">L-разнообразие применено</div>
                </div>
              </Col>
              
              <Col xs={24} sm={8}>
                <div className="metric-item">
                  <div className="metric-item-value">
                    {dashboardData?.privacy_metrics?.differential_privacy_applied || 0}
                  </div>
                  <div className="metric-item-label">Дифференциальная приватность</div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
