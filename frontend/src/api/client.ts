import axios from 'axios';
import type {
  HealthResponse,
  DashboardSummaryResponse,
  ProductSummary,
  ProductForecastResponse,
  ProductRiskResponse,
  WhatIfResponse,
  ModelPerformanceResponse,
  DataSummaryResponse,
} from '../types';

const API_BASE_URL = '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health
  getHealth: async (): Promise<HealthResponse> => {
    const res = await apiClient.get('/health');
    return res.data;
  },

  // Dashboard Overview
  getDashboardSummary: async (): Promise<DashboardSummaryResponse> => {
    const res = await apiClient.get('/dashboard/summary');
    return res.data;
  },

  // Product List
  getProducts: async (): Promise<ProductSummary[]> => {
    const res = await apiClient.get('/products');
    return res.data;
  },

  // Product Forecast
  getProductForecast: async (productId: string): Promise<ProductForecastResponse> => {
    const res = await apiClient.get(`/products/${encodeURIComponent(productId)}/forecast`);
    return res.data;
  },

  // Product Risk
  getProductRisk: async (productId: string): Promise<ProductRiskResponse> => {
    const res = await apiClient.get(`/products/${encodeURIComponent(productId)}/risk`);
    return res.data;
  },

  // What-If Simulator
  simulateScenario: async (payload: {
    product_id: string;
    demand_pct_change: number;
    current_inventory_override?: number | null;
    safety_buffer_multiplier: number;
  }): Promise<WhatIfResponse> => {
    const res = await apiClient.post('/simulator/what-if', payload);
    return res.data;
  },

  // Model Performance
  getModelPerformance: async (productId?: string): Promise<ModelPerformanceResponse> => {
    const url = productId ? `/models/performance?product_id=${encodeURIComponent(productId)}` : '/models/performance';
    const res = await apiClient.get(url);
    return res.data;
  },

  // Retrain Models
  trainModels: async (payload: {
    forecast_horizon_days: number;
    service_level: string;
    model_type: string;
  }) => {
    const res = await apiClient.post('/models/train', payload);
    return res.data;
  },

  // Data Summary
  getDataSummary: async (): Promise<DataSummaryResponse> => {
    const res = await apiClient.get('/data/summary');
    return res.data;
  },

  // Upload File
  uploadDataset: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  // Custom Column Mapping
  mapColumns: async (custom_mapping: Record<string, string>) => {
    const res = await apiClient.post('/data/map-columns', { custom_mapping });
    return res.data;
  },

  // Load Benchmark
  loadBenchmark: async () => {
    const res = await apiClient.post('/data/load-benchmark');
    return res.data;
  },
};
