import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginApi, registerApi, getMeApi } from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('hirelens_token'));
  const [loading, setLoading] = useState(true);

  // Sync token changes and verify user on mount
  useEffect(() => {
    async function loadUser() {
      if (token) {
        try {
          const userData = await getMeApi();
          setUser(userData);
        } catch (err) {
          console.error('Failed to load user session:', err);
          logout();
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    }

    loadUser();

    // Global listener for 401 unauthorized events
    const handleUnauthorized = () => {
      logout();
    };

    window.addEventListener('hirelens_unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('hirelens_unauthorized', handleUnauthorized);
    };
  }, [token]);

  const login = async (email, password) => {
    const res = await loginApi(email, password);
    localStorage.setItem('hirelens_token', res.access_token);
    setToken(res.access_token);
    const userData = await getMeApi();
    setUser(userData);
    return userData;
  };

  const register = async (email, password) => {
    await registerApi(email, password);
    return await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('hirelens_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
