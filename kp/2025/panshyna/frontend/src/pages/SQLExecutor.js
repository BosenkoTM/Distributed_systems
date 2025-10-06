import React, { useState } from 'react';
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
  MenuItem
} from '@mui/material';
import {
  PlayArrow,
  Clear,
  CheckCircle,
  Error
} from '@mui/icons-material';
import { sqlService } from '../services/api';

const SQLExecutor = () => {
  const [sqlQuery, setSqlQuery] = useState('');
  const [timeout, setTimeout] = useState(30);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleExecute = async () => {
    if (!sqlQuery.trim()) {
      setError('Введите SQL-запрос');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);

      const executionResult = await sqlService.executeSQL(sqlQuery, timeout);
      setResult(executionResult);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSqlQuery('');
    setResult(null);
    setError(null);
  };

  const getResultStatusColor = (success) => {
    return success ? 'success' : 'error';
  };

  const getResultStatusIcon = (success) => {
    return success ? <CheckCircle /> : <Error />;
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          SQL Executor
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Безопасное выполнение SQL-запросов в песочнице
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Ввод SQL */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SQL Query
              </Typography>
              
              <TextField
                fullWidth
                multiline
                rows={8}
                value={sqlQuery}
                onChange={(e) => setSqlQuery(e.target.value)}
                placeholder="Введите SQL-запрос..."
                variant="outlined"
                sx={{ mb: 2 }}
              />

              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                <FormControl sx={{ minWidth: 120 }}>
                  <InputLabel>Timeout</InputLabel>
                  <Select
                    value={timeout}
                    label="Timeout"
                    onChange={(e) => setTimeout(e.target.value)}
                  >
                    <MenuItem value={10}>10 сек</MenuItem>
                    <MenuItem value={30}>30 сек</MenuItem>
                    <MenuItem value={60}>1 мин</MenuItem>
                    <MenuItem value={120}>2 мин</MenuItem>
                  </Select>
                </FormControl>

                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={handleExecute}
                  disabled={loading || !sqlQuery.trim()}
                >
                  {loading ? <CircularProgress size={20} /> : 'Execute'}
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<Clear />}
                  onClick={handleClear}
                  disabled={loading}
                >
                  Clear
                </Button>
              </Box>

              <Alert severity="info">
                <Typography variant="body2">
                  <strong>Безопасность:</strong> Запрещены операции DROP, DELETE, UPDATE, INSERT, ALTER, CREATE и другие опасные команды.
                  Запросы выполняются в изолированной Docker-песочнице с ограниченными ресурсами.
                </Typography>
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Результат */}
        {result && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Chip
                    icon={getResultStatusIcon(result.success)}
                    label={result.success ? 'Success' : 'Error'}
                    color={getResultStatusColor(result.success)}
                    size="small"
                    sx={{ mr: 2 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    Query ID: {result.query_id} | Execution Time: {result.execution_time?.toFixed(3)}s
                  </Typography>
                </Box>

                {result.success ? (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Result ({result.result?.length || 0} rows)
                    </Typography>
                    
                    {result.result && result.result.length > 0 ? (
                      <TableContainer component={Paper}>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              {Object.keys(result.result[0]).map((column) => (
                                <TableCell key={column}><strong>{column}</strong></TableCell>
                              ))}
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {result.result.map((row, index) => (
                              <TableRow key={index}>
                                {Object.values(row).map((value, cellIndex) => (
                                  <TableCell key={cellIndex}>{value}</TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Запрос выполнен успешно, но не вернул данных
                      </Typography>
                    )}
                  </Box>
                ) : (
                  <Box>
                    <Typography variant="h6" gutterBottom color="error">
                      Error
                    </Typography>
                    <Alert severity="error">
                      {result.error}
                    </Alert>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Примеры запросов */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Примеры безопасных запросов
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Простой SELECT
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      SELECT * FROM users LIMIT 10;
                    </Typography>
                    <Button
                      size="small"
                      onClick={() => setSqlQuery('SELECT * FROM users LIMIT 10;')}
                      sx={{ mt: 1 }}
                    >
                      Использовать
                    </Button>
                  </Box>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      SELECT с WHERE
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      SELECT name, email FROM users WHERE active = true;
                    </Typography>
                    <Button
                      size="small"
                      onClick={() => setSqlQuery('SELECT name, email FROM users WHERE active = true;')}
                      sx={{ mt: 1 }}
                    >
                      Использовать
                    </Button>
                  </Box>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Агрегатный запрос
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      SELECT COUNT(*) as total FROM users;
                    </Typography>
                    <Button
                      size="small"
                      onClick={() => setSqlQuery('SELECT COUNT(*) as total FROM users;')}
                      sx={{ mt: 1 }}
                    >
                      Использовать
                    </Button>
                  </Box>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      JOIN запрос
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id;
                    </Typography>
                    <Button
                      size="small"
                      onClick={() => setSqlQuery('SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id;')}
                      sx={{ mt: 1 }}
                    >
                      Использовать
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SQLExecutor;
