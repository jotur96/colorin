import { useEffect, useState } from 'react';
import { reportesAPI, profesoresAPI } from '../api/client';
import './Reportes.css';

export default function Reportes() {
  const [estadisticas, setEstadisticas] = useState([]);
  const [distribucion, setDistribucion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [profesorSeleccionado, setProfesorSeleccionado] = useState(null);
  const [eventosProfe, setEventosProfe] = useState([]);

  useEffect(() => {
    cargarReportes();
  }, []);

  const cargarReportes = async () => {
    try {
      const [statsRes, distRes] = await Promise.all([
        reportesAPI.estadisticasProfesores(),
        reportesAPI.distribucionEquitativa(),
      ]);
      setEstadisticas(statsRes.data.estadisticas || []);
      setDistribucion(distRes.data);
    } catch (error) {
      console.error('Error cargando reportes:', error);
      alert('Error al cargar reportes');
    } finally {
      setLoading(false);
    }
  };

  const verEventosProfe = async (profesorId) => {
    try {
      const response = await reportesAPI.eventosPorProfe(profesorId);
      setEventosProfe(response.data.eventos || []);
      setProfesorSeleccionado(response.data.profesor);
    } catch (error) {
      console.error('Error cargando eventos del profesor:', error);
      alert('Error al cargar eventos del profesor');
    }
  };

  if (loading) {
    return <div className="loading">Cargando reportes...</div>;
  }

  return (
    <div className="reportes-page">
      <h2>📈 Reportes y Estadísticas</h2>

      {distribucion && distribucion.analisis && (
        <div className="reporte-card distribucion-card">
          <h3>📊 Distribución Equitativa de Eventos</h3>
          <div className="analisis-grid">
            <div className="analisis-item">
              <span className="label">Mínimo de eventos:</span>
              <strong className="value">{distribucion.analisis.minimo_eventos}</strong>
            </div>
            <div className="analisis-item">
              <span className="label">Máximo de eventos:</span>
              <strong className="value">{distribucion.analisis.maximo_eventos}</strong>
            </div>
            <div className="analisis-item">
              <span className="label">Diferencia:</span>
              <strong className="value">{distribucion.analisis.diferencia}</strong>
            </div>
            <div className="analisis-item">
              <span className="label">Estado:</span>
              <strong
                className={`value ${distribucion.analisis.es_equitativo ? 'success' : 'warning'}`}
              >
                {distribucion.analisis.es_equitativo ? '✅ Equitativo' : '⚠️ Requiere ajuste'}
              </strong>
            </div>
          </div>
        </div>
      )}

      <div className="reporte-card">
        <h3>👥 Estadísticas por Profesor</h3>
        <div className="estadisticas-table">
          <div className="table-header">
            <div>Profesor</div>
            <div>Estado</div>
            <div>Eventos</div>
            <div>Acción</div>
          </div>
          {estadisticas.map((stat) => (
            <div key={stat.profesor_id} className="table-row">
              <div className="profesor-nombre">{stat.nombre}</div>
              <div>
                <span className={`badge ${stat.activo ? 'badge-success' : 'badge-secondary'}`}>
                  {stat.activo ? '✓ Activo' : '✗ Inactivo'}
                </span>
              </div>
              <div className="eventos-count">
                <strong>{stat.total_eventos}</strong>
              </div>
              <div>
                <button
                  className="btn btn-sm btn-primary"
                  onClick={() => verEventosProfe(stat.profesor_id)}
                >
                  👁️ Ver
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {estadisticas.length > 0 && (
        <div className="reporte-card resumen-card">
          <h3>📋 Resumen General</h3>
          <div className="resumen-grid">
            <div className="resumen-item">
              <span className="resumen-label">Total Profesores:</span>
              <span className="resumen-value">{estadisticas.length}</span>
            </div>
            <div className="resumen-item">
              <span className="resumen-label">Total Eventos Asignados:</span>
              <span className="resumen-value">
                {estadisticas.reduce((sum, stat) => sum + stat.total_eventos, 0)}
              </span>
            </div>
            <div className="resumen-item">
              <span className="resumen-label">Promedio por Profesor:</span>
              <span className="resumen-value">
                {estadisticas.length > 0
                  ? (
                      estadisticas.reduce((sum, stat) => sum + stat.total_eventos, 0) /
                      estadisticas.length
                    ).toFixed(2)
                  : 0}
              </span>
            </div>
          </div>
        </div>
      )}

      {profesorSeleccionado && (
        <div className="modal-overlay" onClick={() => setProfesorSeleccionado(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Eventos de {profesorSeleccionado.nombre}</h3>
              <button className="close-btn" onClick={() => setProfesorSeleccionado(null)}>
                ✕
              </button>
            </div>
            <div className="eventos-list-modal">
              {eventosProfe.length === 0 ? (
                <p className="empty-message">No hay eventos asignados.</p>
              ) : (
                eventosProfe.map((evento) => (
                  <div key={evento.evento_id} className="evento-item">
                    <div className="evento-item-header">
                      <strong>{evento.nombre}</strong>
                      <span className="evento-rol">{evento.rol}</span>
                    </div>
                    <div className="evento-item-details">
                      <span>📅 {new Date(evento.fecha).toLocaleDateString('es-ES')}</span>
                      {evento.ubicacion && <span>📍 {evento.ubicacion}</span>}
                      <span className="badge badge-primary">{evento.tipo}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

