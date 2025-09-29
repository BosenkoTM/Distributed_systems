import React from 'react';

function UserTable({ users }) {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ru-RU');
  };

  return (
    <div className="table-container">
      <div style={{ padding: '20px', borderBottom: '1px solid #ddd' }}>
        <h3>Пользователи системы</h3>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя пользователя</th>
            <th>Email</th>
            <th>Роль</th>
            <th>Статус</th>
            <th>Дата регистрации</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>
                <span className={`status-badge ${user.role === 'admin' ? 'status-completed' : 'status-pending'}`}>
                  {user.role}
                </span>
              </td>
              <td>
                <span className={`status-badge ${user.is_active ? 'status-completed' : 'status-failed'}`}>
                  {user.is_active ? 'Активен' : 'Неактивен'}
                </span>
              </td>
              <td>{formatDate(user.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default UserTable;
