import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="navbar-brand">
          SQL Dataset Generator - Админ
        </div>
        <ul className="navbar-nav">
          {user ? (
            <>
              <li>
                <Link to="/dashboard">Дашборд</Link>
              </li>
              <li>
                <span>Администратор: {user.username}</span>
              </li>
              <li>
                <button 
                  className="btn btn-danger" 
                  onClick={handleLogout}
                  style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}
                >
                  Выйти
                </button>
              </li>
            </>
          ) : (
            <li>
              <Link to="/login">Вход</Link>
            </li>
          )}
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
