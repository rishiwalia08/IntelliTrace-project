import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
});

export const invoiceApi = {
  async getInvoices() {
    const response = await api.get("/v1/invoices");
    return response.data;
  },
  async uploadInvoice(payload) {
    const response = await api.post("/v1/invoices/upload", payload);
    return response.data;
  },
};

export default api;
