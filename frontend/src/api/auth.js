import { request } from './client';

export async function registerApi(email, password) {
  const payload =
    typeof email === 'object' && email !== null
      ? { email: email.email, password: email.password }
      : { email, password };

  return request('/api/v1/auth/register', {
    method: 'POST',
    body: payload,
  });
}

export async function loginApi(email, password) {
  const userEmail = typeof email === 'object' && email !== null ? email.email : email;
  const userPass = typeof email === 'object' && email !== null ? email.password : password;

  // OAuth2PasswordRequestForm expects form-urlencoded (username = email)
  const formData = new URLSearchParams();
  formData.append('username', userEmail);
  formData.append('password', userPass);

  return request('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });
}

export async function getMeApi() {
  return request('/api/v1/auth/me', {
    method: 'GET',
  });
}

// Named aliases for compatibility
export const registerUser = registerApi;
export const loginUser = loginApi;
export const getCurrentUser = getMeApi;
