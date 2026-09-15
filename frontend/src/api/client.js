export const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export class ApiError extends Error {
  constructor(message, status, errorType = 'API_ERROR') {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.errorType = errorType;
  }
}

export async function request(endpoint, options = {}) {
  const token = localStorage.getItem('hirelens_token');
  const headers = {
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (options.body && !(options.body instanceof FormData)) {
    if (!headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }
    if (headers['Content-Type'] === 'application/json' && typeof options.body === 'object') {
      options.body = JSON.stringify(options.body);
    }
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    // Auto handle 401 token expiry
    if (response.status === 401 && endpoint !== '/api/v1/auth/login') {
      localStorage.removeItem('hirelens_token');
      // Dispatch custom event for auth context
      window.dispatchEvent(new Event('hirelens_unauthorized'));
    }

    if (!response.ok) {
      let errorMessage = 'An error occurred while communicating with the server.';
      let errorType = 'SERVER_ERROR';

      try {
        const errorData = await response.json();
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map(e => e.msg).join(', ');
          } else {
            errorMessage = errorData.detail;
          }
        }
        if (errorData.error_type) {
          errorType = errorData.error_type;
        }
      } catch (e) {
        // Fallback if response is not JSON
      }

      throw new ApiError(errorMessage, response.status, errorType);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      error.message || 'Network error. Please check your internet connection.',
      0,
      'NETWORK_ERROR'
    );
  }
}
