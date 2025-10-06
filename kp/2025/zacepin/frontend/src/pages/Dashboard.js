import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  TrendingUp,
  Assignment,
  Warning
} from '@mui/icons-material';
import { useSession } from '../contexts/SessionContext';
import { monitoringService } from '../services/api';

const Dashboard = () => {
  const { currentSession, createSession, endSession, isLoading, error } = useSession();
  const [annotatorId, setAnnotatorId] = useState('');
  const [systemHealth, setSystemHealth] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSystemHealth();
  }, []);

  const loadSystemHealth = async () => {
    try {
      setLoading(true);
      const health = await monitoringService.getHealth();
      setSystemHealth(health);
    } catch (err) {
      console.error('Failed to load system health:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartSession = async () => {
    if (!annotatorId.trim()) {
      return;
    }

    try {
      await createSession(annotatorId.trim());
      setAnnotatorId('');
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleEndSession = async () => {
    try {
      await endSession();
    } catch (err) {
      console.error('Failed to end session:', err);
    }
  };

  const getReplicaStatusColor = (healthy) => {
    return healthy ? 'success' : 'error';
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Панель управления
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Клиент-центричная модель согласованности для разметчиков
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Управление сессией */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Управление сессией
              </Typography>
              
              {!currentSession ? (
                <Box>
                  <TextField
                    fullWidth
                    label="ID разметчика"
                    value={annotatorId}
                    onChange={(e) => setAnnotatorId(e.target.value)}
                    placeholder="Введите ваш ID"
                    sx={{ mb: 2 }}
                  />
                  <Button
                    variant="contained"
                    startIcon={<PlayArrow />}
                    onClick={handleStartSession}
                    disabled={isLoading || !annotatorId.trim()}
                    fullWidth
                  >
                    {isLoading ? <CircularProgress size={20} /> : 'Начать сессию'}
                  </Button>
                </Box>
              ) : (
                <Box>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Активная сессия: {currentSession.session_id.slice(0, 8)}...
                  </Alert>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Разметчик: {currentSession.annotator_id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Реплика: {currentSession.current_replica}
                    </Typography>
                  </Box>
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<Stop />}
                    onClick={handleEndSession}
                    disabled={isLoading}
                    fullWidth
                  >
                    {isLoading ? <CircularProgress size={20} /> : 'Завершить сессию'}
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Статус системы */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Статус системы
                </Typography>
                <Button
                  size="small"
                  startIcon={<Refresh />}
                  onClick={loadSystemHealth}
                  disabled={loading}
                >
                  Обновить
                </Button>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress />
                </Box>
              ) : systemHealth ? (
                <Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Общий статус
                    </Typography>
                    <Chip
                      label={systemHealth.status}
                      color={systemHealth.status === 'healthy' ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Реплики БД
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {Object.entries(systemHealth.replicas || {}).map(([replica, status]) => (
                        <Chip
                          key={replica}
                          label={`${replica}: ${status ? 'OK' : 'ERROR'}`}
                          color={getReplicaStatusColor(status)}
                          size="small"
                        />
                      ))}
                    </Box>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Активных сессий: {systemHealth.active_sessions || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Всего запросов: {systemHealth.total_requests || 0}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Alert severity="warning">
                  Не удалось загрузить статус системы
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Быстрые действия */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Быстрые действия
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    variant="outlined"
                    startIcon={<Assignment />}
                    onClick={() => window.location.href = '/labeling'}
                    fullWidth
                    disabled={!currentSession}
                  >
                    Разметка данных
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    variant="outlined"
                    startIcon={<TrendingUp />}
                    onClick={() => window.location.href = '/monitoring'}
                    fullWidth
                  >
                    Мониторинг
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    variant="outlined"
                    startIcon={<Warning />}
                    onClick={() => window.location.href = '/sessions'}
                    fullWidth
                    disabled={!currentSession}
                  >
                    Управление сессией
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    onClick={loadSystemHealth}
                    fullWidth
                    disabled={loading}
                  >
                    Обновить статус
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
