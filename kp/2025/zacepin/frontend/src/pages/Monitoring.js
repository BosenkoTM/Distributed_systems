import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Tabs,
  Tab
} from '@mui/material';
import {
  Refresh,
  HealthAndSafety,
  Analytics,
  Timeline,
  Warning,
  CheckCircle,
  Error
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { monitoringService } from '../services/api';

const Monitoring = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [events, setEvents] = useState([]);
  const [sessionStats, setSessionStats] = useState(null);
  const [conflictStats, setConflictStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [healthData, metricsData, eventsData, sessionData, conflictData] = await Promise.all([
        monitoringService.getHealth(),
        monitoringService.getMetrics(),
        monitoringService.getEvents(),
        monitoringService.getSessionStats(),
        monitoringService.getConflictStats()
      ]);

      setHealth(healthData);
      setMetrics(metricsData);
      setEvents(eventsData.events || []);
      setSessionStats(sessionData);
      setConflictStats(conflictData);
    } catch (err) {
      setError('Не удалось загрузить данные мониторинга');
      console.error('Failed to load monitoring data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle />;
      case 'degraded': return <Warning />;
      case 'error': return <Error />;
      default: return <HealthAndSafety />;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const renderHealthTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Общий статус системы
            </Typography>
            {health ? (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Chip
                    icon={getStatusIcon(health.status)}
                    label={health.status}
                    color={getStatusColor(health.status)}
                    size="large"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Активных сессий: {health.active_sessions || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Всего запросов: {health.total_requests || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Последнее обновление: {formatTimestamp(health.timestamp)}
                </Typography>
              </Box>
            ) : (
              <CircularProgress />
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Статус реплик БД
            </Typography>
            {health?.replicas ? (
              <Box>
                {Object.entries(health.replicas).map(([replica, status]) => (
                  <Box key={replica} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Chip
                      label={`${replica}: ${status ? 'OK' : 'ERROR'}`}
                      color={status ? 'success' : 'error'}
                      size="small"
                      sx={{ mr: 2, minWidth: 120 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {status ? 'Доступна' : 'Недоступна'}
                    </Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <CircularProgress />
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderMetricsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Метрики системы
            </Typography>
            {metrics ? (
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="subtitle1" gutterBottom>
                      Счетчики
                    </Typography>
                    {Object.entries(metrics.counters || {}).map(([key, value]) => (
                      <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">{key}</Typography>
                        <Typography variant="body2" fontWeight="bold">{value}</Typography>
                      </Box>
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="subtitle1" gutterBottom>
                      Временные метрики
                    </Typography>
                    {Object.entries(metrics.timings || {}).map(([key, value]) => (
                      <Box key={key} sx={{ mb: 2 }}>
                        <Typography variant="body2" fontWeight="medium">{key}</Typography>
                        <Typography variant="caption">
                          Среднее: {value.avg?.toFixed(3)}s | 
                          Мин: {value.min?.toFixed(3)}s | 
                          Макс: {value.max?.toFixed(3)}s
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="subtitle1" gutterBottom>
                      Gauge метрики
                    </Typography>
                    {Object.entries(metrics.gauges || {}).map(([key, value]) => (
                      <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">{key}</Typography>
                        <Typography variant="body2" fontWeight="bold">{value}</Typography>
                      </Box>
                    ))}
                  </Box>
                </Grid>
              </Grid>
            ) : (
              <CircularProgress />
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderEventsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              События системы
            </Typography>
            {events.length > 0 ? (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Время</TableCell>
                      <TableCell>Тип события</TableCell>
                      <TableCell>Описание</TableCell>
                      <TableCell>Данные</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {events.slice(0, 50).map((event, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2">
                            {formatTimestamp(event.timestamp)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={event.event_type || event.event}
                            color="primary"
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {event.description || 'Нет описания'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                            {JSON.stringify(event.data || {}, null, 2)}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="text.secondary">
                События не найдены
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderStatsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Статистика сессий
            </Typography>
            {sessionStats ? (
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Всего сессий: {sessionStats.total_sessions}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Активных сессий: {sessionStats.active_sessions}
                </Typography>
                <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                  Распределение по репликам:
                </Typography>
                {Object.entries(sessionStats.replica_distribution || {}).map(([replica, count]) => (
                  <Box key={replica} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{replica}</Typography>
                    <Typography variant="body2" fontWeight="bold">{count}</Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <CircularProgress />
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Статистика конфликтов
            </Typography>
            {conflictStats ? (
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Всего конфликтов: {conflictStats.total_conflicts}
                </Typography>
                <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                  По типам разрешения:
                </Typography>
                {conflictStats.resolution_stats?.map((stat, index) => (
                  <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{stat.resolution}</Typography>
                    <Typography variant="body2" fontWeight="bold">{stat.count}</Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <CircularProgress />
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Мониторинг системы
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Мониторинг состояния системы, метрик и событий
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 3 }}>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadAllData}
          disabled={loading}
        >
          Обновить данные
        </Button>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Здоровье системы" icon={<HealthAndSafety />} />
          <Tab label="Метрики" icon={<Analytics />} />
          <Tab label="События" icon={<Timeline />} />
          <Tab label="Статистика" icon={<Warning />} />
        </Tabs>
      </Box>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {!loading && (
        <>
          {activeTab === 0 && renderHealthTab()}
          {activeTab === 1 && renderMetricsTab()}
          {activeTab === 2 && renderEventsTab()}
          {activeTab === 3 && renderStatsTab()}
        </>
      )}
    </Container>
  );
};

export default Monitoring;
