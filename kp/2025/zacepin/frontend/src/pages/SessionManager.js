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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Refresh,
  SwapHoriz,
  Settings,
  Info
} from '@mui/icons-material';
import { useSession } from '../contexts/SessionContext';
import { sessionService } from '../services/api';

const SessionManager = () => {
  const { currentSession, switchReplica, isLoading } = useSession();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedReplica, setSelectedReplica] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);

  const replicas = ['master', 'replica1', 'replica2'];

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const sessionList = await sessionService.listSessions(true);
      setSessions(sessionList);
    } catch (err) {
      setError('Не удалось загрузить список сессий');
      console.error('Failed to load sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSwitchReplica = async () => {
    if (!selectedReplica || !currentSession) return;

    try {
      setLoading(true);
      await switchReplica(selectedReplica);
      setDialogOpen(false);
      setSelectedReplica('');
      await loadSessions();
    } catch (err) {
      setError('Не удалось переключить реплику');
      console.error('Failed to switch replica:', err);
    } finally {
      setLoading(false);
    }
  };

  const getReplicaColor = (replica) => {
    switch (replica) {
      case 'master': return 'primary';
      case 'replica1': return 'secondary';
      case 'replica2': return 'info';
      default: return 'default';
    }
  };

  const formatVectorClock = (clock) => {
    if (!clock || typeof clock !== 'object') return 'N/A';
    return Object.entries(clock)
      .map(([node, value]) => `${node}:${value}`)
      .join(', ');
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Управление сессиями
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Управление сессиями разметчиков и переключение между репликами
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Текущая сессия */}
        {currentSession && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Текущая сессия
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        ID сессии
                      </Typography>
                      <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                        {currentSession.session_id}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Разметчик
                      </Typography>
                      <Typography variant="body1">
                        {currentSession.annotator_id}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Текущая реплика
                      </Typography>
                      <Chip
                        label={currentSession.current_replica}
                        color={getReplicaColor(currentSession.current_replica)}
                        size="small"
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Статус
                      </Typography>
                      <Chip
                        label={currentSession.is_active ? 'Активна' : 'Неактивна'}
                        color={currentSession.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Vector Clock
                      </Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                        {formatVectorClock(currentSession.vector_clock)}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Button
                      variant="outlined"
                      startIcon={<SwapHoriz />}
                      onClick={() => setDialogOpen(true)}
                      disabled={loading}
                    >
                      Переключить реплику
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Список всех сессий */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Все активные сессии ({sessions.length})
                </Typography>
                <Button
                  startIcon={<Refresh />}
                  onClick={loadSessions}
                  disabled={loading}
                >
                  Обновить
                </Button>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>ID сессии</TableCell>
                        <TableCell>Разметчик</TableCell>
                        <TableCell>Реплика</TableCell>
                        <TableCell>Статус</TableCell>
                        <TableCell>Vector Clock</TableCell>
                        <TableCell>Последняя активность</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {sessions.map((session) => (
                        <TableRow key={session.session_id}>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {session.session_id.slice(0, 8)}...
                            </Typography>
                          </TableCell>
                          <TableCell>{session.annotator_id}</TableCell>
                          <TableCell>
                            <Chip
                              label={session.current_replica}
                              color={getReplicaColor(session.current_replica)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={session.is_active ? 'Активна' : 'Неактивна'}
                              color={session.is_active ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                              {formatVectorClock(session.vector_clock)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {session.last_activity ? new Date(session.last_activity).toLocaleString() : 'N/A'}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}

              {sessions.length === 0 && !loading && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    Активные сессии не найдены
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Информация о репликах */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Информация о репликах
              </Typography>
              <Grid container spacing={2}>
                {replicas.map((replica) => (
                  <Grid item xs={12} md={4} key={replica}>
                    <Box sx={{ p: 2, border: 1, borderColor: 'grey.300', borderRadius: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Chip
                          label={replica}
                          color={getReplicaColor(replica)}
                          size="small"
                        />
                        {replica === 'master' && (
                          <Chip
                            label="Master"
                            color="primary"
                            size="small"
                            sx={{ ml: 1 }}
                          />
                        )}
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {replica === 'master' 
                          ? 'Основная база данных для записи'
                          : `Реплика для чтения (${replica})`
                        }
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Диалог переключения реплики */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>
          Переключение реплики
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Текущая реплика: {currentSession?.current_replica}
            </Typography>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Новая реплика</InputLabel>
              <Select
                value={selectedReplica}
                label="Новая реплика"
                onChange={(e) => setSelectedReplica(e.target.value)}
              >
                {replicas
                  .filter(replica => replica !== currentSession?.current_replica)
                  .map((replica) => (
                    <MenuItem key={replica} value={replica}>
                      {replica} {replica === 'master' ? '(Master)' : '(Replica)'}
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                Переключение реплики может повлиять на производительность и доступность данных.
                Убедитесь, что выбранная реплика доступна.
              </Typography>
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Отмена
          </Button>
          <Button
            onClick={handleSwitchReplica}
            variant="contained"
            disabled={loading || !selectedReplica}
          >
            {loading ? <CircularProgress size={20} /> : 'Переключить'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SessionManager;
