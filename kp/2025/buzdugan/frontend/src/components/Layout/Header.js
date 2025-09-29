import React from 'react';
import { Layout, Dropdown, Avatar, Button, Space } from 'antd';
import { UserOutlined, LogoutOutlined, SettingOutlined } from '@ant-design/icons';
import { useAuth } from '../../hooks/useAuth';

const { Header: AntHeader } = Layout;

const Header = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Профиль',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Настройки',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Выйти',
      onClick: handleLogout,
    },
  ];

  return (
    <AntHeader style={{ 
      background: '#001529', 
      padding: '0 24px', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between' 
    }}>
      <div className="logo" style={{ color: '#fff', fontSize: '18px', fontWeight: 'bold' }}>
        Privacy-Preserving Database Proxy
      </div>
      
      <div className="user-info" style={{ color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span>Добро пожаловать, {user?.username}</span>
        <Dropdown
          menu={{ items: userMenuItems }}
          placement="bottomRight"
          arrow
        >
          <Button type="text" style={{ color: '#fff' }}>
            <Space>
              <Avatar size="small" icon={<UserOutlined />} />
              {user?.role}
            </Space>
          </Button>
        </Dropdown>
      </div>
    </AntHeader>
  );
};

export default Header;
