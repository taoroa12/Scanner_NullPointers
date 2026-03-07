import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "";

const instance = axios.create({
  baseURL: API_BASE,
  timeout: 30_000,
  withCredentials: false,
  headers: {
    "Accept": "application/json",
  },
});

instance.interceptors.response.use(
  r => r,
  error => {
    if (error.response) {
      const data = error.response.data;
      const message =
        (data && (data.detail || data.message || data.error)) ||
        error.response.statusText ||
        "Server error";
      return Promise.reject(new Error(`${error.response.status}: ${message}`));
    } else if (error.request) {
      return Promise.reject(new Error("No response from server"));
    } else {
      return Promise.reject(new Error(error.message));
    }
  }
);

export default instance;