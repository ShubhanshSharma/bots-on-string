// lib/visitorService.ts
import fetchClient from "./apiClient";

export interface Visitor {
  id?: number;
  anonymous_id: string;
  created_at?: string;
}

/**
 * Fetch all visitors
 */
export const getVisitors = async (): Promise<Visitor[]> => {
  return await fetchClient<Visitor[]>("/visitor/visiotr/all", {
    method: "GET",
  });
};

/**
 * Create a new visitor
 */
export const createVisitor = async (data: Visitor): Promise<Visitor> => {
  return await fetchClient<Visitor>("/visitor/visitor", {
    method: "POST",
    body: JSON.stringify(data),
  });
};

/**
 * Delete visitor by ID
 */
export const deleteVisitor = async (id: string): Promise<void> => {
  await fetchClient<void>(`/visitor/${id}`, { method: "DELETE" });
};
