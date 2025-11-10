// lib/companyService.ts
import fetchClient from "./apiClient";

export interface Company {
  id?: number;
  name: string;
  description?: string;
  created_at?: string;
}

// ✅ Get all companies
export const getCompanies = async (): Promise<Company[]> => {
  return await fetchClient<Company[]>("/company");
};

// ✅ Create new company
export const createCompany = async (data: Company): Promise<Company> => {
  return await fetchClient<Company>("/company/company/create", {
    method: "POST",
    body: JSON.stringify(data),
  });
};

// ✅ Update company
export const updateCompany = async (
  id: number,
  data: Partial<Company>
): Promise<Company> => {
  return await fetchClient<Company>(`/company/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
};

// ✅ Delete company
export const deleteCompany = async (id: number): Promise<void> => {
  await fetchClient<void>(`/company/${id}`, { method: "DELETE" });
};
