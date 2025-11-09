// lib/visitorService.ts
import { api } from "./apiClient";
import apiClient from "./apiClient";

export interface Visitor {
  id: number;
  anonymous_id: string;
  created_at?: string;
}

export const getVisitors = async (): Promise<Visitor[]> => {
  const { data } = await apiClient.get("/visitor/all");
  return data;
};

export const createVisitor = async (data: Visitor): Promise<Visitor> => {
  const res = await api.post("/api/v1/visitor", data);
  return res.data;
};

export const deleteVisitor = async (id: string): Promise<void> => {
  await api.delete(`/api/v1/visitor/${id}`);
};
