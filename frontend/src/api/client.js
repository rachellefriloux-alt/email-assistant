import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 8000,
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config || {};
    if (!config.__retryCount) config.__retryCount = 0;
    if (config.__retryCount < 2 && (!error.response || error.code === 'ECONNABORTED')) {
      config.__retryCount += 1;
      return client(config);
    }
    return Promise.reject(error);
  }
);

export { client };
