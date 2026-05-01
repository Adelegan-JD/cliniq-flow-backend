import { api } from './api';
export const login = (payload: {email: string; password: string}) => api.post('/auth/login', payload);
