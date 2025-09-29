import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  Space,
  Tag,
  message,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { privacyAPI } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const { TextArea } = Input;
const { Option } = Select;

const PrivacyPolicies = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  const { data: policies, isLoading } = useQuery(
    'privacyPolicies',
    privacyAPI.getPolicies
  );

  const createMutation = useMutation(privacyAPI.createPolicy, {
    onSuccess: () => {
      queryClient.invalidateQueries('privacyPolicies');
      message.success('Политика создана успешно');
      setIsModalVisible(false);
      form.resetFields();
    },
    onError: () => {
      message.error('Ошибка создания политики');
    },
  });

  const updateMutation = useMutation(
    ({ policyId, data }) => privacyAPI.updatePolicy(policyId, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('privacyPolicies');
        message.success('Политика обновлена успешно');
        setIsModalVisible(false);
        setEditingPolicy(null);
        form.resetFields();
      },
      onError: () => {
        message.error('Ошибка обновления политики');
      },
    }
  );

  const deleteMutation = useMutation(privacyAPI.deletePolicy, {
    onSuccess: () => {
      queryClient.invalidateQueries('privacyPolicies');
      message.success('Политика удалена успешно');
    },
    onError: () => {
      message.error('Ошибка удаления политики');
    },
  });

  const handleCreate = () => {
    setEditingPolicy(null);
    setIsModalVisible(true);
    form.resetFields();
  };

  const handleEdit = (policy) => {
    setEditingPolicy(policy);
    setIsModalVisible(true);
    form.setFieldsValue({
      name: policy.name,
      description: policy.description,
      policy_type: policy.policy_type,
      ...policy.parameters,
    });
  };

  const handleDelete = (policyId) => {
    deleteMutation.mutate(policyId);
  };

  const handleSubmit = (values) => {
    const { name, description, policy_type, ...parameters } = values;
    
    if (editingPolicy) {
      updateMutation.mutate({
        policyId: editingPolicy.id,
        data: { name, description, parameters },
      });
    } else {
      createMutation.mutate({
        name,
        description,
        policy_type,
        parameters,
      });
    }
  };

  const columns = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Тип',
      dataIndex: 'policy_type',
      key: 'policy_type',
      render: (type) => {
        const colors = {
          k_anonymity: 'blue',
          l_diversity: 'green',
          differential_privacy: 'purple',
        };
        return <Tag color={colors[type]}>{type}</Tag>;
      },
    },
    {
      title: 'Описание',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Активна' : 'Неактивна'}
        </Tag>
      ),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleEdit(record)}
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          />
          <Popconfirm
            title="Вы уверены, что хотите удалить эту политику?"
            onConfirm={() => handleDelete(record.id)}
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

  const renderPolicyParameters = () => {
    const policyType = form.getFieldValue('policy_type');
    
    switch (policyType) {
      case 'k_anonymity':
        return (
          <>
            <Form.Item
              name="k"
              label="Значение K"
              rules={[{ required: true, message: 'Введите значение K' }]}
            >
              <InputNumber min={1} placeholder="5" />
            </Form.Item>
            <Form.Item
              name="quasi_identifiers"
              label="Квази-идентификаторы"
              rules={[{ required: true, message: 'Введите квази-идентификаторы' }]}
            >
              <Select
                mode="tags"
                placeholder="age, zipcode, gender"
                style={{ width: '100%' }}
              />
            </Form.Item>
          </>
        );
      
      case 'l_diversity':
        return (
          <>
            <Form.Item
              name="l"
              label="Значение L"
              rules={[{ required: true, message: 'Введите значение L' }]}
            >
              <InputNumber min={1} placeholder="3" />
            </Form.Item>
            <Form.Item
              name="sensitive_attribute"
              label="Чувствительный атрибут"
              rules={[{ required: true, message: 'Введите чувствительный атрибут' }]}
            >
              <Input placeholder="disease" />
            </Form.Item>
            <Form.Item
              name="quasi_identifiers"
              label="Квази-идентификаторы"
              rules={[{ required: true, message: 'Введите квази-идентификаторы' }]}
            >
              <Select
                mode="tags"
                placeholder="age, zipcode"
                style={{ width: '100%' }}
              />
            </Form.Item>
          </>
        );
      
      case 'differential_privacy':
        return (
          <>
            <Form.Item
              name="epsilon"
              label="Epsilon"
              rules={[{ required: true, message: 'Введите epsilon' }]}
            >
              <InputNumber min={0.1} step={0.1} placeholder="1.0" />
            </Form.Item>
            <Form.Item
              name="delta"
              label="Delta"
              rules={[{ required: true, message: 'Введите delta' }]}
            >
              <InputNumber min={0} step={0.00001} placeholder="0.00001" />
            </Form.Item>
            <Form.Item
              name="sensitivity"
              label="Чувствительность"
              rules={[{ required: true, message: 'Введите чувствительность' }]}
            >
              <InputNumber min={0.1} step={0.1} placeholder="1.0" />
            </Form.Item>
          </>
        );
      
      default:
        return null;
    }
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <Card
        title="Политики приватности"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            Создать политику
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={policies}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Card>

      <Modal
        title={editingPolicy ? 'Редактировать политику' : 'Создать политику'}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingPolicy(null);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="Название"
            rules={[{ required: true, message: 'Введите название политики' }]}
          >
            <Input placeholder="K-Anonymity Basic" />
          </Form.Item>

          <Form.Item
            name="description"
            label="Описание"
            rules={[{ required: true, message: 'Введите описание' }]}
          >
            <TextArea rows={3} placeholder="Описание политики..." />
          </Form.Item>

          <Form.Item
            name="policy_type"
            label="Тип политики"
            rules={[{ required: true, message: 'Выберите тип политики' }]}
          >
            <Select placeholder="Выберите тип политики">
              <Option value="k_anonymity">K-анонимность</Option>
              <Option value="l_diversity">L-разнообразие</Option>
              <Option value="differential_privacy">Дифференциальная приватность</Option>
            </Select>
          </Form.Item>

          {renderPolicyParameters()}

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createMutation.isLoading || updateMutation.isLoading}
              >
                {editingPolicy ? 'Обновить' : 'Создать'}
              </Button>
              <Button
                onClick={() => {
                  setIsModalVisible(false);
                  setEditingPolicy(null);
                  form.resetFields();
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

export default PrivacyPolicies;
