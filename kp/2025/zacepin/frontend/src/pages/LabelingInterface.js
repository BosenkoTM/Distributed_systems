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
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider
} from '@mui/material';
import {
  Save,
  Refresh,
  Warning,
  CheckCircle,
  Error
} from '@mui/icons-material';
import { useSession } from '../contexts/SessionContext';
import { labelingService } from '../services/api';

const LabelingInterface = () => {
  const { currentSession } = useSession();
  const [labeledData, setLabeledData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedData, setSelectedData] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newLabel, setNewLabel] = useState('');
  const [confidence, setConfidence] = useState(0.5);
  const [conflicts, setConflicts] = useState([]);

  useEffect(() => {
    if (currentSession) {
      loadLabeledData();
      loadConflicts();
    }
  }, [currentSession]);

  const loadLabeledData = async () => {
    if (!currentSession) return;

    try {
      setLoading(true);
      const data = await labelingService.getLabeledDataBySession(currentSession.session_id);
      setLabeledData(data);
    } catch (err) {
      setError('Не удалось загрузить данные разметки');
      console.error('Failed to load labeled data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadConflicts = async () => {
    if (!currentSession) return;

    try {
      const conflictData = await labelingService.getConflicts(currentSession.session_id);
      setConflicts(conflictData);
    } catch (err) {
      console.error('Failed to load conflicts:', err);
    }
  };

  const handleLabelData = (data) => {
    setSelectedData(data);
    setNewLabel(data.label || '');
    setConfidence(data.confidence || 0.5);
    setDialogOpen(true);
  };

  const handleSaveLabel = async () => {
    if (!selectedData || !newLabel.trim()) return;

    try {
      setLoading(true);
      
      // Обновление vector clock
      const updatedClock = { ...selectedData.vector_clock };
      if (currentSession.current_replica in updatedClock) {
        updatedClock[currentSession.current_replica] += 1;
      } else {
        updatedClock[currentSession.current_replica] = 1;
      }

      const updateData = {
        label: newLabel,
        confidence: confidence,
        vector_clock: updatedClock
      };

      await labelingService.updateLabeledData(selectedData.id, updateData);
      
      setDialogOpen(false);
      setSelectedData(null);
      await loadLabeledData();
      await loadConflicts();
    } catch (err) {
      setError('Не удалось сохранить разметку');
      console.error('Failed to save label:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResolveConflict = async (conflict) => {
    try {
      setLoading(true);
      
      const resolution = {
        conflict_id: conflict.id,
        resolution: 'manual',
        chosen_label: conflict.label,
        reason: 'Manual resolution by annotator'
      };

      await labelingService.resolveConflict(resolution);
      await loadConflicts();
      await loadLabeledData();
    } catch (err) {
      setError('Не удалось разрешить конфликт');
      console.error('Failed to resolve conflict:', err);
    } finally {
      setLoading(false);
    }
  };

  const getConflictStatusColor = (isConflict) => {
    return isConflict ? 'error' : 'success';
  };

  const getConflictStatusIcon = (isConflict) => {
    return isConflict ? <Warning /> : <CheckCircle />;
  };

  if (!currentSession) {
    return (
      <Container maxWidth="lg">
        <Alert severity="warning">
          Для работы с разметкой необходимо создать сессию
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Интерфейс разметки
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Сессия: {currentSession.session_id.slice(0, 8)}... | Реплика: {currentSession.current_replica}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {conflicts.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Обнаружено {conflicts.length} конфликт(ов) в данных
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Конфликты */}
        {conflicts.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="error">
                  Конфликты данных
                </Typography>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>ID данных</TableCell>
                        <TableCell>Текст</TableCell>
                        <TableCell>Текущая метка</TableCell>
                        <TableCell>Уверенность</TableCell>
                        <TableCell>Действия</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {conflicts.map((conflict) => (
                        <TableRow key={conflict.id}>
                          <TableCell>{conflict.data_id}</TableCell>
                          <TableCell>{conflict.original_text}</TableCell>
                          <TableCell>{conflict.label}</TableCell>
                          <TableCell>{(conflict.confidence * 100).toFixed(1)}%</TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              variant="outlined"
                              color="error"
                              onClick={() => handleResolveConflict(conflict)}
                              disabled={loading}
                            >
                              Разрешить
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Данные разметки */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Размеченные данные ({labeledData.length})
                </Typography>
                <Button
                  startIcon={<Refresh />}
                  onClick={loadLabeledData}
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
                        <TableCell>ID данных</TableCell>
                        <TableCell>Текст</TableCell>
                        <TableCell>Метка</TableCell>
                        <TableCell>Уверенность</TableCell>
                        <TableCell>Статус</TableCell>
                        <TableCell>Vector Clock</TableCell>
                        <TableCell>Действия</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {labeledData.map((data) => (
                        <TableRow key={data.id}>
                          <TableCell>{data.data_id}</TableCell>
                          <TableCell sx={{ maxWidth: 300 }}>
                            <Typography variant="body2" noWrap>
                              {data.original_text}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={data.label}
                              color={data.label === 'positive' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{(data.confidence * 100).toFixed(1)}%</TableCell>
                          <TableCell>
                            <Chip
                              icon={getConflictStatusIcon(data.is_conflict)}
                              label={data.is_conflict ? 'Конфликт' : 'OK'}
                              color={getConflictStatusColor(data.is_conflict)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption">
                              {JSON.stringify(data.vector_clock)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => handleLabelData(data)}
                              disabled={loading}
                            >
                              Изменить
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Диалог редактирования разметки */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Редактирование разметки
        </DialogTitle>
        <DialogContent>
          {selectedData && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                ID данных: {selectedData.data_id}
              </Typography>
              <Typography variant="body1" sx={{ mb: 3, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                {selectedData.original_text}
              </Typography>

              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Метка</InputLabel>
                <Select
                  value={newLabel}
                  label="Метка"
                  onChange={(e) => setNewLabel(e.target.value)}
                >
                  <MenuItem value="positive">Положительная</MenuItem>
                  <MenuItem value="negative">Отрицательная</MenuItem>
                  <MenuItem value="neutral">Нейтральная</MenuItem>
                </Select>
              </FormControl>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
                  Уверенность: {(confidence * 100).toFixed(1)}%
                </Typography>
                <Slider
                  value={confidence}
                  onChange={(e, newValue) => setConfidence(newValue)}
                  min={0}
                  max={1}
                  step={0.1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <Typography variant="body2" color="text.secondary">
                Текущий Vector Clock: {JSON.stringify(selectedData.vector_clock)}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Отмена
          </Button>
          <Button
            onClick={handleSaveLabel}
            variant="contained"
            startIcon={<Save />}
            disabled={loading || !newLabel.trim()}
          >
            {loading ? <CircularProgress size={20} /> : 'Сохранить'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LabelingInterface;
