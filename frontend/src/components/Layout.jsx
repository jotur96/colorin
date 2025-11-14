import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { authAPI } from '../api/client';
import './Layout.css';

export default function Layout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const username = localStorage.getItem('username');
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordData, setPasswordData] = useState({
    password_actual: '',
    password_nueva: '',
    password_nueva_confirmar: '',
  });
  const [passwordError, setPasswordError] = useState('');

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    if (confirm('¿Estás seguro de cerrar sesión?')) {
      authAPI.logout();
      navigate('/login');
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setPasswordError('');

    // Validaciones
    if (!passwordData.password_actual || !passwordData.password_nueva || !passwordData.password_nueva_confirmar) {
      setPasswordError('Todos los campos son requeridos');
      return;
    }

    if (passwordData.password_nueva !== passwordData.password_nueva_confirmar) {
      setPasswordError('Las contraseñas nuevas no coinciden');
      return;
    }

    if (passwordData.password_nueva.length < 6) {
      setPasswordError('La nueva contraseña debe tener al menos 6 caracteres');
      return;
    }

    try {
      await authAPI.cambiarPassword(passwordData.password_actual, passwordData.password_nueva);
      alert('✅ Contraseña actualizada correctamente');
      setShowPasswordModal(false);
      setPasswordData({
        password_actual: '',
        password_nueva: '',
        password_nueva_confirmar: '',
      });
    } catch (error) {
      setPasswordError(
        error.response?.data?.detail || 'Error al cambiar la contraseña'
      );
    }
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <div>
            <h1>🎨 Colorin</h1>
            <p className="subtitle">Gestión de Eventos</p>
          </div>
          <div className="user-info">
            <span className="username">👤 {username}</span>
            <button
              className="btn-change-password"
              onClick={() => setShowPasswordModal(true)}
              title="Cambiar contraseña"
            >
              🔐 Cambiar Contraseña
            </button>
            <button className="btn-logout" onClick={handleLogout}>
              🚪 Cerrar Sesión
            </button>
          </div>
        </div>
      </header>

      <nav className="nav">
        <Link to="/" className={isActive('/') ? 'nav-link active' : 'nav-link'}>
          📊 Dashboard
        </Link>
        <Link to="/profesores" className={isActive('/profesores') ? 'nav-link active' : 'nav-link'}>
          👥 Profesores
        </Link>
        <Link to="/eventos" className={isActive('/eventos') ? 'nav-link active' : 'nav-link'}>
          🎉 Eventos
        </Link>
        <Link to="/reportes" className={isActive('/reportes') ? 'nav-link active' : 'nav-link'}>
          📈 Reportes
        </Link>
        <Link to="/tareas" className={isActive('/tareas') ? 'nav-link active' : 'nav-link'}>
          ✅ Tareas
        </Link>
      </nav>

      <main className="main-content">
        {children}
      </main>

      {showPasswordModal && (
        <div
          className="modal-overlay"
          onClick={() => {
            setShowPasswordModal(false);
            setPasswordData({
              password_actual: '',
              password_nueva: '',
              password_nueva_confirmar: '',
            });
            setPasswordError('');
          }}
        >
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🔐 Cambiar Contraseña</h3>
              <button
                className="close-btn"
                onClick={() => {
                  setShowPasswordModal(false);
                  setPasswordData({
                    password_actual: '',
                    password_nueva: '',
                    password_nueva_confirmar: '',
                  });
                  setPasswordError('');
                }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleChangePassword}>
              {passwordError && (
                <div className="error-message">{passwordError}</div>
              )}

              <div className="form-group">
                <label>Contraseña Actual:</label>
                <input
                  type="password"
                  value={passwordData.password_actual}
                  onChange={(e) =>
                    setPasswordData({
                      ...passwordData,
                      password_actual: e.target.value,
                    })
                  }
                  required
                  placeholder="Ingresa tu contraseña actual"
                />
              </div>

              <div className="form-group">
                <label>Nueva Contraseña:</label>
                <input
                  type="password"
                  value={passwordData.password_nueva}
                  onChange={(e) =>
                    setPasswordData({
                      ...passwordData,
                      password_nueva: e.target.value,
                    })
                  }
                  required
                  placeholder="Ingresa tu nueva contraseña"
                  minLength={6}
                />
              </div>

              <div className="form-group">
                <label>Confirmar Nueva Contraseña:</label>
                <input
                  type="password"
                  value={passwordData.password_nueva_confirmar}
                  onChange={(e) =>
                    setPasswordData({
                      ...passwordData,
                      password_nueva_confirmar: e.target.value,
                    })
                  }
                  required
                  placeholder="Confirma tu nueva contraseña"
                  minLength={6}
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowPasswordModal(false);
                    setPasswordData({
                      password_actual: '',
                      password_nueva: '',
                      password_nueva_confirmar: '',
                    });
                    setPasswordError('');
                  }}
                >
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary">
                  ✅ Cambiar Contraseña
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

