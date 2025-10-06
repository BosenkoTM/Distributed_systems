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
  TextField
} from '@mui/material';
import {
  Add,
  PlayArrow,
  Refresh,
  Visibility
} from '@mui/icons-material';
import { taskService } from '../services/api';

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    sql_query: '',
    expected_result: ''
  });

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const tasksData = await taskService.getTasks();
      setTasks(tasksData);
    } catch (err) {
      setError('Не удалось загрузить задачи');
      console.error('Failed to load tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    try {
      setLoading(true);
      await taskService.createTask(newTask);
      setDialogOpen(false);
      setNewTask({ title: '', description: '', sql_query: '', expected_result: '' });
      await loadTasks();
    } catch (err) {
      setError('Не удалось создать задачу');
      console.error('Failed to create task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteTask = async (taskId) => {
    try {
      setLoading(true);
      await taskService.executeTask(taskId);
      await loadTasks();
    } catch (err) {
      setError('Не удалось выполнить задачу');
      console.error('Failed to execute task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewTask = async (taskId) => {
    try {
      const task = await taskService.getTask(taskId);
      setSelectedTask(task);
    } catch (err) {
      setError('Не удалось загрузить задачу');
      console.error('Failed to load task:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'running': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Tasks
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Управление задачами SQL-запросов
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Список задач */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Tasks ({tasks.length})
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    startIcon={<Refresh />}
                    onClick={loadTasks}
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
                    Add Task
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
                        <TableCell>Title</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Execution Time</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tasks.map((task) => (
                        <TableRow key={task.id}>
                          <TableCell>{task.id}</TableCell>
                          <TableCell>{task.title}</TableCell>
                          <TableCell>
                            <Chip
                              label={task.status}
                              color={getStatusColor(task.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {task.execution_time ? `${task.execution_time.toFixed(3)}s` : '-'}
                          </TableCell>
                          <TableCell>
                            {new Date(task.created_at).toLocaleString()}
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              startIcon={<Visibility />}
                              onClick={() => handleViewTask(task.id)}
                              sx={{ mr: 1 }}
                            >
                              View
                            </Button>
                            <Button
                              size="small"
                              startIcon={<PlayArrow />}
                              onClick={() => handleExecuteTask(task.id)}
                              disabled={task.status === 'running'}
                            >
                              Execute
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

      {/* Диалог создания задачи */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Task</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Title"
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Description"
              value={newTask.description}
              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              multiline
              rows={6}
              label="SQL Query"
              value={newTask.sql_query}
              onChange={(e) => setNewTask({ ...newTask, sql_query: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Expected Result"
              value={newTask.expected_result}
              onChange={(e) => setNewTask({ ...newTask, expected_result: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateTask}
            variant="contained"
            disabled={loading || !newTask.title || !newTask.sql_query}
          >
            {loading ? <CircularProgress size={20} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог просмотра задачи */}
      <Dialog open={!!selectedTask} onClose={() => setSelectedTask(null)} maxWidth="md" fullWidth>
        <DialogTitle>Task Details</DialogTitle>
        <DialogContent>
          {selectedTask && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                {selectedTask.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {selectedTask.description}
              </Typography>
              
              <Typography variant="subtitle2" gutterBottom>
                SQL Query:
              </Typography>
              <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1, mb: 2 }}>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                  {selectedTask.sql_query}
                </Typography>
              </Box>

              {selectedTask.expected_result && (
                <>
                  <Typography variant="subtitle2" gutterBottom>
                    Expected Result:
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {selectedTask.expected_result}
                  </Typography>
                </>
              )}

              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <Chip
                  label={`Status: ${selectedTask.status}`}
                  color={getStatusColor(selectedTask.status)}
                  size="small"
                />
                {selectedTask.execution_time && (
                  <Chip
                    label={`Time: ${selectedTask.execution_time.toFixed(3)}s`}
                    size="small"
                  />
                )}
              </Box>

              {selectedTask.result && (
                <>
                  <Typography variant="subtitle2" gutterBottom>
                    Result:
                  </Typography>
                  <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {selectedTask.result}
                    </Typography>
                  </Box>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedTask(null)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Tasks;
