import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  ShieldOutlined,
  DatabaseOutlined,
  UserOutlined,
  MonitorOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../hooks/useAuth';

const { Sider } = Layout;

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Дашборд',
    },
    {
      key: '/privacy-policies',
      icon: <ShieldOutlined />,
      label: 'Политики приватности',
    },
    {
      key: '/query',
      icon: <DatabaseOutlined />,
      label: 'SQL Запросы',
    },
  ];

  // Добавление административных пунктов для админов
  if (user?.role === 'admin') {
    menuItems.push(
      {
        key: '/admin',
        icon: <UserOutlined />,
        label: 'Администрирование',
      }
    );
  }

  // Добавление мониторинга для админов и аудиторов
  if (user?.role === 'admin' || user?.role === 'auditor') {
    menuItems.push(
      {
        key: '/monitoring',
        icon: <MonitorOutlined />,
        label: 'Мониторинг',
      }
    );
  }

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <Sider
      width={250}
      style={{
        background: '#fff',
        boxShadow: '2px 0 8px rgba(0, 0, 0, 0.1)',
      }}
    >
      <div style={{ 
        height: '64px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        borderBottom: '1px solid #f0f0f0'
      }}>
        <span style={{ fontSize: '16px', fontWeight: 'bold', color: '#001529' }}>
          Меню
        </span>
      </div>
      
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ 
          borderRight: 0,
          height: 'calc(100vh - 64px)',
        }}
      />
    </Sider>
  );
};

export default Sidebar;
