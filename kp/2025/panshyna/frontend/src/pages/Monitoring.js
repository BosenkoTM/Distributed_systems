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
  Chip
} from '@mui/material';
import {
  Refresh,
  HealthAndSafety,
  Timeline,
  Analytics
} from '@mui/icons-material';
import { monitoringService } from '../services/api';

const Monitoring = () => {
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, logsData, healthData] = await Promise.all([
        monitoringService.getStats(),
        monitoringService.getLogs(50),
        monitoringService.getHealth()
      ]);
      setStats(statsData);
      setLogs(logsData);
      setHealth(healthData);
    } catch (err) {
      setError('Не удалось загрузить данные мониторинга');
      console.error('Failed to load monitoring data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    return status === 'healthy' ? 'success' : 'error';
  };

  const getLogStatusColor = (success) => {
    return success ? 'success' : 'error';
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Monitoring
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Мониторинг системы и логов выполнения
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
          onClick={loadData}
          disabled={loading}
        >
          Refresh Data
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Статус системы */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Health
              </Typography>
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress />
                </Box>
              ) : health ? (
                <Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Overall Status
                    </Typography>
                    <Chip
                      label={health.status}
                      color={getStatusColor(health.status)}
                      size="small"
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Services
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
                  Unable to load system health
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
                Statistics
              </Typography>
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress />
                </Box>
              ) : stats ? (
                <Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Tasks
                    </Typography>
                    <Typography variant="h6">
                      {stats.tasks?.total || 0} total
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Success: {stats.tasks?.completed || 0} | 
                      Failed: {stats.tasks?.failed || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Success Rate: {((stats.tasks?.success_rate || 0) * 100).toFixed(1)}%
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Verifications
                    </Typography>
                    <Typography variant="h6">{stats.verifications?.total || 0}</Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Execution Logs
                    </Typography>
                    <Typography variant="h6">{stats.logs?.total || 0}</Typography>
                  </Box>
                </Box>
              ) : (
                <Alert severity="warning">
                  Unable to load statistics
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Логи выполнения */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Execution Logs (Last 50)
              </Typography>
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : logs.length > 0 ? (
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Query ID</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Result Count</TableCell>
                        <TableCell>Execution Time</TableCell>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Error</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {logs.map((log, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {log.query_id}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={log.success ? 'Success' : 'Failed'}
                              color={getLogStatusColor(log.success)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{log.result_count || 0}</TableCell>
                          <TableCell>
                            {log.execution_time ? `${log.execution_time.toFixed(3)}s` : '-'}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {formatTimestamp(log.timestamp)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {log.error ? (
                              <Typography variant="body2" color="error" sx={{ maxWidth: 200 }}>
                                {log.error}
                              </Typography>
                            ) : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No execution logs available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Monitoring;
