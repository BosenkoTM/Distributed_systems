import React from 'react';
import { Spin } from 'antd';

const LoadingSpinner = ({ size = 'large', tip = 'Загрузка...' }) => {
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh' 
    }}>
      <Spin size={size} tip={tip} />
    </div>
  );
};

export default LoadingSpinner;
