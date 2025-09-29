import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  Tag,
  message,
  Popconfirm,
  Tabs,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  DatabaseOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { adminAPI } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const { Option } = Select;
const { TabPane } = Tabs;

const AdminPanel = () => {
  const [isUserModalVisible, setIsUserModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [userForm] = Form.useForm();
  const queryClient = useQueryClient();

  const { data: users, isLoading: usersLoading } = useQuery(
    'adminUsers',
    () => adminAPI.getUsers(50, 0)
  );

  const { data: systemStats, isLoading: statsLoading } = useQuery(
    'systemStats',
    adminAPI.getSystemStats
  );

  const { data: systemLogs, isLoading: logsLoading } = useQuery(
    'systemLogs',
    () => adminAPI.getSystemLogs('all', 100, 0)
  );

  const createUserMutation = useMutation(adminAPI.createUser, {
    onSuccess: () => {
      queryClient.invalidateQueries('adminUsers');
      message.success('Пользователь создан успешно');
      setIsUserModalVisible(false);
      userForm.resetFields();
    },
    onError: () => {
      message.error('Ошибка создания пользователя');
    },
  });

  const updateUserMutation = useMutation(
    ({ userId, data }) => adminAPI.updateUser(userId, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('adminUsers');
        message.success('Пользователь обновлен успешно');
        setIsUserModalVisible(false);
        setEditingUser(null);
        userForm.resetFields();
      },
      onError: () => {
        message.error('Ошибка обновления пользователя');
      },
    }
  );

  const deleteUserMutation = useMutation(adminAPI.deleteUser, {
    onSuccess: () => {
      queryClient.invalidateQueries('adminUsers');
      message.success('Пользователь удален успешно');
    },
    onError: () => {
      message.error('Ошибка удаления пользователя');
    },
  });

  const handleCreateUser = () => {
    setEditingUser(null);
    setIsUserModalVisible(true);
    userForm.resetFields();
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setIsUserModalVisible(true);
    userForm.setFieldsValue({
      username: user.username,
      email: user.email,
      role: user.role,
      is_active: user.is_active,
    });
  };

  const handleDeleteUser = (userId) => {
    deleteUserMutation.mutate(userId);
  };

  const handleUserSubmit = (values) => {
    const { username, email, password, role } = values;
    
    if (editingUser) {
      updateUserMutation.mutate({
        userId: editingUser.id,
        data: { username, email, role },
      });
    } else {
      createUserMutation.mutate({
        username,
        email,
        password,
        role,
      });
    }
  };

  const userColumns = [
    {
      title: 'Имя пользователя',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Роль',
      dataIndex: 'role',
      key: 'role',
      render: (role) => {
        const colors = {
          admin: 'red',
          analyst: 'blue',
          researcher: 'green',
          auditor: 'orange',
        };
        return <Tag color={colors[role]}>{role}</Tag>;
      },
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Активен' : 'Неактивен'}
        </Tag>
      ),
    },
    {
      title: 'Дата создания',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString('ru-RU'),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditUser(record)}
          />
          <Popconfirm
            title="Вы уверены, что хотите удалить этого пользователя?"
            onConfirm={() => handleDeleteUser(record.id)}
            okText="Да"
            cancelText="Нет"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const logColumns = [
    {
      title: 'Время',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString('ru-RU'),
    },
    {
      title: 'Тип',
      dataIndex: 'log_type',
      key: 'log_type',
      render: (type) => {
        const colors = {
          query: 'blue',
          access: 'green',
          error: 'red',
          security: 'orange',
        };
        return <Tag color={colors[type] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: 'Пользователь',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'Действие',
      dataIndex: 'action',
      key: 'action',
    },
    {
      title: 'IP адрес',
      dataIndex: 'ip_address',
      key: 'ip_address',
    },
  ];

  if (usersLoading || statsLoading || logsLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <Card title="Администрирование системы">
        <Tabs defaultActiveKey="users">
          <TabPane tab="Пользователи" key="users">
            <Card
              title="Управление пользователями"
              extra={
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleCreateUser}
                >
                  Создать пользователя
                </Button>
              }
            >
              <Table
                columns={userColumns}
                dataSource={users}
                rowKey="id"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                }}
              />
            </Card>
          </TabPane>

          <TabPane tab="Статистика системы" key="stats">
            <Row gutter={16}>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="Всего пользователей"
                    value={systemStats?.total_users || 0}
                    prefix={<UserOutlined />}
                    valueStyle={{ color: '#3f8600' }}
                  />
                </Card>
              </Col>
              
              <Col span={6}>
                <Card>
                  <Statistic
                    title="Активных пользователей"
                    value={systemStats?.active_users || 0}
                    prefix={<UserOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              
              <Col span={6}>
                <Card>
                  <Statistic
                    title="Всего запросов"
                    value={systemStats?.total_queries || 0}
                    prefix={<DatabaseOutlined />}
                    valueStyle={{ color: '#722ed1' }}
                  />
                </Card>
              </Col>
              
              <Col span={6}>
                <Card>
                  <Statistic
                    title="Политик приватности"
                    value={systemStats?.privacy_policies_count || 0}
                    prefix={<FileTextOutlined />}
                    valueStyle={{ color: '#eb2f96' }}
                  />
                </Card>
              </Col>
            </Row>

            <Card title="Здоровье системы" style={{ marginTop: '24px' }}>
              <Row gutter={16}>
                <Col span={8}>
                  <div>
                    <span className="status-indicator status-healthy"></span>
                    <span>База данных: Подключена</span>
                  </div>
                </Col>
                <Col span={8}>
                  <div>
                    <span className="status-indicator status-healthy"></span>
                    <span>Redis: Подключен</span>
                  </div>
                </Col>
                <Col span={8}>
                  <div>
                    <span className="status-indicator status-healthy"></span>
                    <span>API: Работает</span>
                  </div>
                </Col>
              </Row>
            </Card>
          </TabPane>

          <TabPane tab="Системные логи" key="logs">
            <Card title="Последние системные события">
              <Table
                columns={logColumns}
                dataSource={systemLogs}
                rowKey="id"
                pagination={{
                  pageSize: 20,
                  showSizeChanger: true,
                  showQuickJumper: true,
                }}
                scroll={{ x: true }}
              />
            </Card>
          </TabPane>
        </Tabs>
      </Card>

      <Modal
        title={editingUser ? 'Редактировать пользователя' : 'Создать пользователя'}
        open={isUserModalVisible}
        onCancel={() => {
          setIsUserModalVisible(false);
          setEditingUser(null);
          userForm.resetFields();
        }}
        footer={null}
        width={500}
      >
        <Form
          form={userForm}
          layout="vertical"
          onFinish={handleUserSubmit}
        >
          <Form.Item
            name="username"
            label="Имя пользователя"
            rules={[{ required: true, message: 'Введите имя пользователя' }]}
          >
            <Input placeholder="username" />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Введите email' },
              { type: 'email', message: 'Введите корректный email' }
            ]}
          >
            <Input placeholder="user@example.com" />
          </Form.Item>

          {!editingUser && (
            <Form.Item
              name="password"
              label="Пароль"
              rules={[{ required: true, message: 'Введите пароль' }]}
            >
              <Input.Password placeholder="password" />
            </Form.Item>
          )}

          <Form.Item
            name="role"
            label="Роль"
            rules={[{ required: true, message: 'Выберите роль' }]}
          >
            <Select placeholder="Выберите роль">
              <Option value="admin">Администратор</Option>
              <Option value="analyst">Аналитик</Option>
              <Option value="researcher">Исследователь</Option>
              <Option value="auditor">Аудитор</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createUserMutation.isLoading || updateUserMutation.isLoading}
              >
                {editingUser ? 'Обновить' : 'Создать'}
              </Button>
              <Button
                onClick={() => {
                  setIsUserModalVisible(false);
                  setEditingUser(null);
                  userForm.resetFields();
                }}
              >
                Отмена
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AdminPanel;
