import React, { createContext, useContext, useState, useEffect } from 'react';
import { sessionService } from '../services/api';

const SessionContext = createContext();

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

export const SessionProvider = ({ children }) => {
  const [currentSession, setCurrentSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const createSession = async (annotatorId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const session = await sessionService.createSession(annotatorId);
      setCurrentSession(session);
      localStorage.setItem('currentSession', JSON.stringify(session));
      return session;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const endSession = async () => {
    if (!currentSession) return;
    
    setIsLoading(true);
    try {
      await sessionService.endSession(currentSession.session_id);
      setCurrentSession(null);
      localStorage.removeItem('currentSession');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const switchReplica = async (replica) => {
    if (!currentSession) return;
    
    setIsLoading(true);
    try {
      await sessionService.switchReplica(currentSession.session_id, replica);
      setCurrentSession(prev => ({
        ...prev,
        current_replica: replica
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const updateActivity = async () => {
    if (!currentSession) return;
    
    try {
      await sessionService.updateActivity(currentSession.session_id);
    } catch (err) {
      console.error('Failed to update activity:', err);
    }
  };

  // Восстановление сессии из localStorage при загрузке
  useEffect(() => {
    const savedSession = localStorage.getItem('currentSession');
    if (savedSession) {
      try {
        setCurrentSession(JSON.parse(savedSession));
      } catch (err) {
        console.error('Failed to restore session:', err);
        localStorage.removeItem('currentSession');
      }
    }
  }, []);

  // Автоматическое обновление активности каждые 30 секунд
  useEffect(() => {
    if (!currentSession) return;

    const interval = setInterval(updateActivity, 30000);
    return () => clearInterval(interval);
  }, [currentSession]);

  const value = {
    currentSession,
    isLoading,
    error,
    createSession,
    endSession,
    switchReplica,
    updateActivity,
    setError
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};
