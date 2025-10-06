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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider
} from '@mui/material';
import {
  Add,
  Refresh,
  CheckCircle,
  Cancel
} from '@mui/icons-material';
import { verificationService, taskService } from '../services/api';

const Verifications = () => {
  const [verifications, setVerifications] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newVerification, setNewVerification] = useState({
    task_id: '',
    verifier_name: '',
    is_correct: true,
    confidence: 0.5,
    comments: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tasksData] = await Promise.all([
        taskService.getTasks()
      ]);
      setTasks(tasksData);
      
      // Загружаем верификации для всех задач
      const allVerifications = [];
      for (const task of tasksData) {
        try {
          const taskVerifications = await verificationService.getTaskVerifications(task.id);
          allVerifications.push(...taskVerifications);
        } catch (err) {
          console.error(`Failed to load verifications for task ${task.id}:`, err);
        }
      }
      setVerifications(allVerifications);
    } catch (err) {
      setError('Не удалось загрузить данные');
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateVerification = async () => {
    try {
      setLoading(true);
      await verificationService.createVerification({
        ...newVerification,
        task_id: parseInt(newVerification.task_id)
      });
      setDialogOpen(false);
      setNewVerification({
        task_id: '',
        verifier_name: '',
        is_correct: true,
        confidence: 0.5,
        comments: ''
      });
      await loadData();
    } catch (err) {
      setError('Не удалось создать верификацию');
      console.error('Failed to create verification:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTaskTitle = (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    return task ? task.title : `Task ${taskId}`;
  };

  const getCorrectnessColor = (isCorrect) => {
    return isCorrect ? 'success' : 'error';
  };

  const getCorrectnessIcon = (isCorrect) => {
    return isCorrect ? <CheckCircle /> : <Cancel />;
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Verifications
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Верификация результатов SQL-запросов
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Список верификаций */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Verifications ({verifications.length})
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    startIcon={<Refresh />}
                    onClick={loadData}
                    disabled={loading}
                  >
                    Refresh
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setDialogOpen(true)}
                    disabled={loading}
                  >
                    Add Verification
                  </Button>
                </Box>
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
                        <TableCell>ID</TableCell>
                        <TableCell>Task</TableCell>
                        <TableCell>Verifier</TableCell>
                        <TableCell>Correct</TableCell>
                        <TableCell>Confidence</TableCell>
                        <TableCell>Comments</TableCell>
                        <TableCell>Created</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {verifications.map((verification) => (
                        <TableRow key={verification.id}>
                          <TableCell>{verification.id}</TableCell>
                          <TableCell>{getTaskTitle(verification.task_id)}</TableCell>
                          <TableCell>{verification.verifier_name}</TableCell>
                          <TableCell>
                            <Chip
                              icon={getCorrectnessIcon(verification.is_correct)}
                              label={verification.is_correct ? 'Correct' : 'Incorrect'}
                              color={getCorrectnessColor(verification.is_correct)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {(verification.confidence * 100).toFixed(1)}%
                          </TableCell>
                          <TableCell>
                            {verification.comments || '-'}
                          </TableCell>
                          <TableCell>
                            {new Date(verification.created_at).toLocaleString()}
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

        {/* Статистика */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Statistics
              </Typography>
              
              {verifications.length > 0 ? (
                <Grid container spacing={2}>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {verifications.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Verifications
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="success.main">
                        {verifications.filter(v => v.is_correct).length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Correct
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="error.main">
                        {verifications.filter(v => !v.is_correct).length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Incorrect
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="info.main">
                        {((verifications.filter(v => v.is_correct).length / verifications.length) * 100).toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Accuracy
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No verifications available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Диалог создания верификации */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Verification</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Task</InputLabel>
              <Select
                value={newVerification.task_id}
                label="Task"
                onChange={(e) => setNewVerification({ ...newVerification, task_id: e.target.value })}
              >
                {tasks.map((task) => (
                  <MenuItem key={task.id} value={task.id}>
                    {task.title}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Verifier Name"
              value={newVerification.verifier_name}
              onChange={(e) => setNewVerification({ ...newVerification, verifier_name: e.target.value })}
              sx={{ mb: 2 }}
            />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Is Correct</InputLabel>
              <Select
                value={newVerification.is_correct}
                label="Is Correct"
                onChange={(e) => setNewVerification({ ...newVerification, is_correct: e.target.value })}
              >
                <MenuItem value={true}>Correct</MenuItem>
                <MenuItem value={false}>Incorrect</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>
                Confidence: {(newVerification.confidence * 100).toFixed(1)}%
              </Typography>
              <Slider
                value={newVerification.confidence}
                onChange={(e, newValue) => setNewVerification({ ...newVerification, confidence: newValue })}
                min={0}
                max={1}
                step={0.1}
                marks
                valueLabelDisplay="auto"
              />
            </Box>

            <TextField
              fullWidth
              multiline
              rows={3}
              label="Comments"
              value={newVerification.comments}
              onChange={(e) => setNewVerification({ ...newVerification, comments: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateVerification}
            variant="contained"
            disabled={loading || !newVerification.task_id || !newVerification.verifier_name}
          >
            {loading ? <CircularProgress size={20} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Verifications;
