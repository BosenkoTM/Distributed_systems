import React, { useState, useCallback } from 'react';
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
  LinearProgress,
  Chip,
  IconButton
} from '@mui/material';
import {
  CloudUpload,
  Delete,
  Refresh,
  GetApp
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import Papa from 'papaparse';
import { fileService } from '../services/api';

const FileUpload = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const fileList = await fileService.listFiles();
      setFiles(fileList);
    } catch (err) {
      setError('Не удалось загрузить список файлов');
      console.error('Failed to load files:', err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadFiles();
  }, []);

  const onDrop = useCallback(async (acceptedFiles) => {
    const csvFiles = acceptedFiles.filter(file => file.name.endsWith('.csv'));
    
    if (csvFiles.length === 0) {
      setError('Пожалуйста, выберите CSV файлы');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      for (const file of csvFiles) {
        await fileService.uploadFile(file, 'current_user');
      }

      setSuccess(`Успешно загружено ${csvFiles.length} файл(ов)`);
      await loadFiles();
    } catch (err) {
      setError('Не удалось загрузить файлы');
      console.error('Failed to upload files:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: true
  });

  const handleDeleteFile = async (fileId) => {
    try {
      setLoading(true);
      await fileService.deleteFile(fileId);
      setSuccess('Файл удален');
      await loadFiles();
    } catch (err) {
      setError('Не удалось удалить файл');
      console.error('Failed to delete file:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePreviewFile = async (fileId) => {
    try {
      const data = await fileService.getFileData(fileId, 10, 0);
      console.log('File preview:', data);
      // В реальном приложении здесь можно открыть модальное окно с предпросмотром
      alert(`Предпросмотр файла (первые 10 строк):\n${JSON.stringify(data.data, null, 2)}`);
    } catch (err) {
      setError('Не удалось загрузить предпросмотр файла');
      console.error('Failed to preview file:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'uploaded': return 'info';
      case 'processing': return 'warning';
      case 'completed': return 'success';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'uploaded': return 'Загружен';
      case 'processing': return 'Обрабатывается';
      case 'completed': return 'Завершен';
      case 'error': return 'Ошибка';
      default: return status;
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Загрузка файлов
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Загрузите CSV файлы для разметки данных
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
        {/* Область загрузки */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Загрузка CSV файлов
              </Typography>
              
              <Box
                {...getRootProps()}
                sx={{
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 2,
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.hover'
                  }
                }}
              >
                <input {...getInputProps()} />
                <CloudUpload sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                {isDragActive ? (
                  <Typography variant="h6" color="primary">
                    Отпустите файлы здесь...
                  </Typography>
                ) : (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Перетащите CSV файлы сюда или нажмите для выбора
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Поддерживаются только CSV файлы
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Список файлов */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Загруженные файлы ({files.length})
                </Typography>
                <Button
                  startIcon={<Refresh />}
                  onClick={loadFiles}
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
                        <TableCell>Имя файла</TableCell>
                        <TableCell>Статус</TableCell>
                        <TableCell>Прогресс</TableCell>
                        <TableCell>Строк</TableCell>
                        <TableCell>Загружен</TableCell>
                        <TableCell>Действия</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {files.map((file) => (
                        <TableRow key={file.id}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {file.filename}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={getStatusLabel(file.status)}
                              color={getStatusColor(file.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Box sx={{ width: '100%', minWidth: 100 }}>
                              <LinearProgress
                                variant="determinate"
                                value={file.progress_percentage}
                                sx={{ height: 8, borderRadius: 4 }}
                              />
                              <Typography variant="caption" color="text.secondary">
                                {file.progress_percentage.toFixed(1)}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {file.processed_rows} / {file.total_rows}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {new Date(file.uploaded_at).toLocaleDateString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              onClick={() => handlePreviewFile(file.id)}
                              disabled={loading}
                            >
                              <GetApp />
                            </IconButton>
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDeleteFile(file.id)}
                              disabled={loading}
                            >
                              <Delete />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}

              {files.length === 0 && !loading && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    Файлы не загружены
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default FileUpload;
