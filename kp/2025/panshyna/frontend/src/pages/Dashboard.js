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
  Chip
} from '@mui/material';
import {
  PlayArrow,
  Refresh,
  TrendingUp,
  Assignment,
  Verified,
  Monitor
} from '@mui/icons-material';
import { monitoringService, initService } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, healthData] = await Promise.all([
        monitoringService.getStats(),
        monitoringService.getHealth()
      ]);
      setStats(statsData);
      setHealth(healthData);
    } catch (err) {
      setError('Не удалось загрузить данные');
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInitDatabase = async () => {
    try {
      setLoading(true);
      const result = await initService.initDatabase();
      setSuccess('База данных инициализирована успешно');
      await loadData();
    } catch (err) {
      setError('Не удалось инициализировать базу данных');
      console.error('Failed to init database:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    return status === 'healthy' ? 'success' : 'error';
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Упрощенная система верификации SQL-запросов с песочницей
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
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
                  onClick={loadData}
                  disabled={loading}
                >
                  Обновить
                </Button>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress />
                </Box>
              ) : health ? (
                <Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Общий статус
                    </Typography>
                    <Chip
                      label={health.status}
                      color={getStatusColor(health.status)}
                      size="small"
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Сервисы
                    </Typography>
                    {Object.entries(health.services || {}).map(([service, status]) => (
                      <Box key={service} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">{service}</Typography>
                        <Chip
                          label={status}
                          color={getStatusColor(status)}
                          size="small"
                        />
                      </Box>
                    ))}
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

        {/* Статистика */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Статистика
              </Typography>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress />
                </Box>
              ) : stats ? (
                <Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Задачи
                    </Typography>
                    <Typography variant="h6">{stats.tasks?.total || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Успешно: {stats.tasks?.completed || 0} | 
                      Ошибки: {stats.tasks?.failed || 0}
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Верификации
                    </Typography>
                    <Typography variant="h6">{stats.verifications?.total || 0}</Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Логи
                    </Typography>
                    <Typography variant="h6">{stats.logs?.total || 0}</Typography>
                  </Box>
                </Box>
              ) : (
                <Alert severity="warning">
                  Не удалось загрузить статистику
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
                    startIcon={<Code />}
                    onClick={() => window.location.href = '/sql-executor'}
                    fullWidth
                  >
                    SQL Executor
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    variant="outlined"
                    startIcon={<Assignment />}
                    onClick={() => window.location.href = '/tasks'}
                    fullWidth
                  >
                    Tasks
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    variant="outlined"
                    startIcon={<Verified />}
                    onClick={() => window.location.href = '/verifications'}
                    fullWidth
                  >
                    Verifications
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    variant="outlined"
                    startIcon={<Monitor />}
                    onClick={() => window.location.href = '/monitoring'}
                    fullWidth
                  >
                    Monitoring
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Инициализация */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Инициализация системы
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Создать тестовые данные и инициализировать базу данных
              </Typography>
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={handleInitDatabase}
                disabled={loading}
              >
                {loading ? <CircularProgress size={20} /> : 'Инициализировать БД'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
