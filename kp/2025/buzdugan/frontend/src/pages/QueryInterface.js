import React, { useState } from 'react';
import {
  Card,
  Input,
  Button,
  Table,
  Select,
  Space,
  message,
  Tag,
  Row,
  Col,
  Statistic,
  Alert,
} from 'antd';
import {
  PlayCircleOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation } from 'react-query';
import { queryAPI, privacyAPI } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const { TextArea } = Input;
const { Option } = Select;

const QueryInterface = () => {
  const [sqlQuery, setSqlQuery] = useState('');
  const [selectedPolicy, setSelectedPolicy] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [validationResult, setValidationResult] = useState(null);

  const { data: policies } = useQuery(
    'privacyPolicies',
    privacyAPI.getPolicies
  );

  const { data: tables } = useQuery(
    'accessibleTables',
    queryAPI.getAccessibleTables
  );

  const executeMutation = useMutation(queryAPI.executeQuery, {
    onSuccess: (data) => {
      setQueryResult(data);
      message.success('Запрос выполнен успешно');
    },
    onError: (error) => {
      message.error('Ошибка выполнения запроса');
      console.error('Query execution error:', error);
    },
  });

  const validateMutation = useMutation(queryAPI.validateQuery, {
    onSuccess: (data) => {
      setValidationResult(data);
      if (data.is_valid) {
        message.success('Запрос валиден');
      } else {
        message.warning('Запрос содержит ошибки');
      }
    },
    onError: (error) => {
      message.error('Ошибка валидации запроса');
      console.error('Query validation error:', error);
    },
  });

  const handleExecute = () => {
    if (!sqlQuery.trim()) {
      message.warning('Введите SQL запрос');
      return;
    }

    executeMutation.mutate({
      sql: sqlQuery,
      privacy_policy_id: selectedPolicy || null,
    });
  };

  const handleValidate = () => {
    if (!sqlQuery.trim()) {
      message.warning('Введите SQL запрос');
      return;
    }

    validateMutation.mutate({
      sql: sqlQuery,
    });
  };

  const handleTableSelect = (tableName) => {
    const basicQuery = `SELECT * FROM ${tableName} LIMIT 10;`;
    setSqlQuery(basicQuery);
  };

  const renderValidationResult = () => {
    if (!validationResult) return null;

    return (
      <Alert
        message="Результат валидации"
        description={
          <div>
            <p><strong>Статус:</strong> {validationResult.is_valid ? 'Валиден' : 'Невалиден'}</p>
            <p><strong>Тип запроса:</strong> {validationResult.query_type}</p>
            <p><strong>Таблицы:</strong> {validationResult.tables_accessed.join(', ')}</p>
            
            {validationResult.potential_privacy_risks.length > 0 && (
              <div>
                <p><strong>Риски приватности:</strong></p>
                <ul>
                  {validationResult.potential_privacy_risks.map((risk, index) => (
                    <li key={index}>{risk}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {validationResult.recommendations.length > 0 && (
              <div>
                <p><strong>Рекомендации:</strong></p>
                <ul>
                  {validationResult.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        }
        type={validationResult.is_valid ? 'success' : 'warning'}
        showIcon
        style={{ marginBottom: '16px' }}
      />
    );
  };

  const renderQueryResult = () => {
    if (!queryResult) return null;

    const columns = queryResult.columns.map(col => ({
      title: col,
      dataIndex: col,
      key: col,
    }));

    return (
      <div>
        <Row gutter={16} style={{ marginBottom: '16px' }}>
          <Col span={8}>
            <Statistic
              title="Количество строк"
              value={queryResult.row_count}
              prefix={<InfoCircleOutlined />}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="Время выполнения"
              value={queryResult.execution_time_ms}
              suffix="мс"
              prefix={<PlayCircleOutlined />}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="Политика приватности"
              value={queryResult.privacy_policy_applied || 'Не применена'}
              prefix={<CheckCircleOutlined />}
            />
          </Col>
        </Row>

        {queryResult.privacy_metrics && (
          <div style={{ marginBottom: '16px' }}>
            <h4>Метрики приватности:</h4>
            <Row gutter={16}>
              {Object.entries(queryResult.privacy_metrics).map(([key, value]) => (
                <Col span={6} key={key}>
                  <Statistic
                    title={key}
                    value={value}
                    valueStyle={{ fontSize: '14px' }}
                  />
                </Col>
              ))}
            </Row>
          </div>
        )}

        <Table
          columns={columns}
          dataSource={queryResult.data}
          rowKey={(record, index) => index}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
          scroll={{ x: true }}
        />
      </div>
    );
  };

  return (
    <div>
      <Card title="SQL Запросы с применением политик приватности">
        <Row gutter={16}>
          <Col span={18}>
            <div style={{ marginBottom: '16px' }}>
              <label>Доступные таблицы:</label>
              <Select
                placeholder="Выберите таблицу для быстрого запроса"
                style={{ width: '100%', marginTop: '8px' }}
                onChange={handleTableSelect}
              >
                {tables?.tables?.map(table => (
                  <Option key={table} value={table}>
                    {table}
                  </Option>
                ))}
              </Select>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label>SQL Запрос:</label>
              <TextArea
                rows={8}
                value={sqlQuery}
                onChange={(e) => setSqlQuery(e.target.value)}
                placeholder="Введите SQL запрос..."
                style={{ marginTop: '8px' }}
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label>Политика приватности (опционально):</label>
              <Select
                placeholder="Выберите политику приватности"
                style={{ width: '100%', marginTop: '8px' }}
                value={selectedPolicy}
                onChange={setSelectedPolicy}
                allowClear
              >
                {policies?.map(policy => (
                  <Option key={policy.id} value={policy.id}>
                    <Tag color="blue">{policy.policy_type}</Tag> {policy.name}
                  </Option>
                ))}
              </Select>
            </div>

            <Space>
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={handleValidate}
                loading={validateMutation.isLoading}
              >
                Валидировать
              </Button>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleExecute}
                loading={executeMutation.isLoading}
              >
                Выполнить
              </Button>
            </Space>
          </Col>

          <Col span={6}>
            <Card title="Примеры запросов" size="small">
              <div style={{ marginBottom: '12px' }}>
                <strong>Простой SELECT:</strong>
                <pre style={{ fontSize: '12px', marginTop: '4px' }}>
                  SELECT * FROM personal_data LIMIT 10;
                </pre>
              </div>
              
              <div style={{ marginBottom: '12px' }}>
                <strong>Агрегирующий запрос:</strong>
                <pre style={{ fontSize: '12px', marginTop: '4px' }}>
                  SELECT age, COUNT(*) FROM personal_data GROUP BY age;
                </pre>
              </div>
              
              <div style={{ marginBottom: '12px' }}>
                <strong>Запрос с JOIN:</strong>
                <pre style={{ fontSize: '12px', marginTop: '4px' }}>
                  SELECT p.name, p.age FROM personal_data p JOIN users u ON p.user_id = u.id;
                </pre>
              </div>
            </Card>
          </Col>
        </Row>

        {renderValidationResult()}
        {renderQueryResult()}
      </Card>
    </div>
  );
};

export default QueryInterface;
