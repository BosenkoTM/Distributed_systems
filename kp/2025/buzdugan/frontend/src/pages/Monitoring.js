import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Alert,
  Space,
  Progress,
} from 'antd';
import {
  DatabaseOutlined,
  ShieldOutlined,
  UserOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { monitoringAPI } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const Monitoring = () => {
  const { data: healthStatus, isLoading: healthLoading } = useQuery(
    'healthStatus',
    monitoringAPI.getHealthStatus,
    {
      refetchInterval: 10000, // Обновление каждые 10 секунд
    }
  );

  const { data: systemMetrics, isLoading: metricsLoading } = useQuery(
    'systemMetrics',
    monitoringAPI.getSystemMetrics,
    {
      refetchInterval: 30000, // Обновление каждые 30 секунд
    }
  );

  const { data: performanceMetrics, isLoading: performanceLoading } = useQuery(
    'performanceMetrics',
    () => monitoringAPI.getPerformanceMetrics('1h'),
    {
      refetchInterval: 60000, // Обновление каждую минуту
    }
  );

  const { data: privacyMetrics, isLoading: privacyLoading } = useQuery(
    'privacyMetrics',
    () => monitoringAPI.getPrivacyMetrics('24h'),
    {
      refetchInterval: 60000,
    }
  );

  const { data: activeAlerts, isLoading: alertsLoading } = useQuery(
    'activeAlerts',
    monitoringAPI.getActiveAlerts,
    {
      refetchInterval: 15000, // Обновление каждые 15 секунд
    }
  );

  if (healthLoading || metricsLoading || performanceLoading || privacyLoading || alertsLoading) {
    return <LoadingSpinner />;
  }

  const healthColumns = [
    {
      title: 'Сервис',
      dataIndex: 'service',
      key: 'service',
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          healthy: 'green',
          warning: 'orange',
          error: 'red',
        };
        return <Tag color={colors[status]}>{status}</Tag>;
      },
    },
    {
      title: 'Время ответа',
      dataIndex: 'response_time',
      key: 'response_time',
      render: (time) => `${time}мс`,
    },
    {
      title: 'Последняя проверка',
      dataIndex: 'last_check',
      key: 'last_check',
      render: (time) => new Date(time).toLocaleString('ru-RU'),
    },
  ];

  const alertColumns = [
    {
      title: 'Время',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (time) => new Date(time).toLocaleString('ru-RU'),
    },
    {
      title: 'Уровень',
      dataIndex: 'level',
      key: 'level',
      render: (level) => {
        const colors = {
          critical: 'red',
          warning: 'orange',
          info: 'blue',
        };
        return <Tag color={colors[level]}>{level}</Tag>;
      },
    },
    {
      title: 'Сообщение',
      dataIndex: 'message',
      key: 'message',
    },
    {
      title: 'Сервис',
      dataIndex: 'service',
      key: 'service',
    },
  ];

  return (
    <div>
      <Card title="Мониторинг системы">
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="Статус системы"
                value={healthStatus?.status || 'unknown'}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ 
                  color: healthStatus?.status === 'healthy' ? '#3f8600' : '#ff4d4f' 
                }}
              />
            </Card>
          </Col>
          
          <Col span={6}>
            <Card>
              <Statistic
                title="Активных предупреждений"
                value={activeAlerts?.length || 0}
                prefix={<ExclamationCircleOutlined />}
                valueStyle={{ 
                  color: (activeAlerts?.length || 0) > 0 ? '#ff4d4f' : '#3f8600' 
                }}
              />
            </Card>
          </Col>
          
          <Col span={6}>
            <Card>
              <Statistic
                title="Среднее время ответа"
                value={performanceMetrics?.avg_response_time || 0}
                suffix="мс"
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          
          <Col span={6}>
            <Card>
              <Statistic
                title="Запросов в секунду"
                value={performanceMetrics?.requests_per_second || 0}
                prefix={<DatabaseOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={12}>
            <Card title="Здоровье сервисов">
              <Table
                columns={healthColumns}
                dataSource={healthStatus?.services || []}
                rowKey="service"
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
          
          <Col span={12}>
            <Card title="Использование ресурсов">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <span>CPU: </span>
                  <Progress 
                    percent={systemMetrics?.cpu_usage || 0} 
                    size="small" 
                    status={systemMetrics?.cpu_usage > 80 ? 'exception' : 'normal'}
                  />
                </div>
                <div>
                  <span>Память: </span>
                  <Progress 
                    percent={systemMetrics?.memory_usage || 0} 
                    size="small"
                    status={systemMetrics?.memory_usage > 80 ? 'exception' : 'normal'}
                  />
                </div>
                <div>
                  <span>Диск: </span>
                  <Progress 
                    percent={systemMetrics?.disk_usage || 0} 
                    size="small"
                    status={systemMetrics?.disk_usage > 80 ? 'exception' : 'normal'}
                  />
                </div>
              </Space>
            </Card>
          </Col>
        </Row>

        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={24}>
            <Card title="Активные предупреждения">
              {activeAlerts && activeAlerts.length > 0 ? (
                <Table
                  columns={alertColumns}
                  dataSource={activeAlerts}
                  rowKey="id"
                  pagination={false}
                  size="small"
                />
              ) : (
                <Alert
                  message="Нет активных предупреждений"
                  description="Все системы работают нормально"
                  type="success"
                  showIcon
                />
              )}
            </Card>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={8}>
            <Card title="Метрики приватности">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <span>K-анонимность применена: </span>
                  <strong>{privacyMetrics?.k_anonymity_applied || 0}</strong>
                </div>
                <div>
                  <span>L-разнообразие применено: </span>
                  <strong>{privacyMetrics?.l_diversity_applied || 0}</strong>
                </div>
                <div>
                  <span>Дифференциальная приватность: </span>
                  <strong>{privacyMetrics?.differential_privacy_applied || 0}</strong>
                </div>
                <div>
                  <span>Всего анонимизированных запросов: </span>
                  <strong>{privacyMetrics?.total_anonymized_queries || 0}</strong>
                </div>
              </Space>
            </Card>
          </Col>
          
          <Col span={8}>
            <Card title="Производительность">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <span>Среднее время выполнения запроса: </span>
                  <strong>{performanceMetrics?.avg_query_time || 0}мс</strong>
                </div>
                <div>
                  <span>Максимальное время выполнения: </span>
                  <strong>{performanceMetrics?.max_query_time || 0}мс</strong>
                </div>
                <div>
                  <span>Успешных запросов: </span>
                  <strong>{performanceMetrics?.successful_queries || 0}</strong>
                </div>
                <div>
                  <span>Неудачных запросов: </span>
                  <strong>{performanceMetrics?.failed_queries || 0}</strong>
                </div>
              </Space>
            </Card>
          </Col>
          
          <Col span={8}>
            <Card title="Безопасность">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <span>Неудачных попыток входа: </span>
                  <strong>{systemMetrics?.failed_login_attempts || 0}</strong>
                </div>
                <div>
                  <span>Срабатываний rate limit: </span>
                  <strong>{systemMetrics?.rate_limit_hits || 0}</strong>
                </div>
                <div>
                  <span>Активных сессий: </span>
                  <strong>{systemMetrics?.active_sessions || 0}</strong>
                </div>
                <div>
                  <span>Последняя проверка безопасности: </span>
                  <strong>{new Date().toLocaleTimeString('ru-RU')}</strong>
                </div>
              </Space>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Monitoring;
