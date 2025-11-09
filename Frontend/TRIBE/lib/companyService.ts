// lib/companyService.ts
import { api } from "./apiClient";

export interface Company {
  id?: number;
  name: string;
  description?: string;
  created_at?: string;
}

export const getCompanies = async (): Promise<Company[]> => {
  const res = await api.get("/api/v1/company");
  return res.data;
};

export const createCompany = async (data: Company): Promise<Company> => {
  const res = await api.post("/api/v1/company", data);
  return res.data;
};

export const updateCompany = async (
  id: number,
  data: Partial<Company>
): Promise<Company> => {
  const res = await api.put(`/api/v1/company/${id}`, data);
  return res.data;
};

export const deleteCompany = async (id: number): Promise<void> => {
  await api.delete(`/api/v1/company/${id}`);
};
