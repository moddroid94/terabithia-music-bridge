import { Blueprint, RunItem, SchedulerState } from '../types';

let API_BASE_URL = "";

try {
  const url = import.meta.env.VITE_APP_API;
  API_BASE_URL = url;
} catch (error) {
  console.log("Error getting API URL")
}

export const api = {
  // --- Blueprint Operations --- //

  getBlueprints: async (): Promise<Blueprint[]> => {
    const res = await fetch(API_BASE_URL + `/blueprints/all`);
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return res.json();
  },

  createBlueprint: async (blueprint: Omit<Blueprint, 'id'>): Promise<Blueprint> => {
    const newBlueprint = { ...blueprint, id: Date.now().toString() };
    const res = await fetch(API_BASE_URL + `/blueprint/new`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newBlueprint),
    });
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return res.json();
  },

  editBlueprint: async (id: string, updates: Partial<Blueprint>): Promise<Blueprint> => {
    const blueprints = await api.getBlueprints();
    const index = blueprints.findIndex(b => b.id === id);
    if (index === -1) throw new Error('Blueprint not found');

    const updated = { ...blueprints[index], ...updates };
    const res = await fetch(API_BASE_URL + `/blueprint/${blueprints[index].name}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated),
    });
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return res.json();
  },

  deleteBlueprint: async (name: string): Promise<void> => {
    const res = await fetch(API_BASE_URL + `/blueprint/delete?playlistName=${name}`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return res.json();
  },

  // --- Scheduler Operations --- //

  getSchedules: async (): Promise<string[]> => {
    const res = await fetch(API_BASE_URL + `/scheduler/all`);
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return res.json();
  },

  getSchedulerState: async (): Promise<SchedulerState> => {
    const res = await fetch(API_BASE_URL + `/scheduler/state`);
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return (res.json() as unknown as SchedulerState);
  },

  toggleSchedulerState: async (): Promise<SchedulerState> => {
    const current = await api.getSchedulerState();
    const next = current === 'Running and processing' ? 'false' : 'true';
    const res = await fetch(API_BASE_URL + `/scheduler/${next}`, {
      method: "POST",
    });
    const newstate = await api.getSchedulerState();
    return newstate;
  },

  // --- Reports Operations --- //

  getRuns: async (): Promise<RunItem[]> => {
    const res = await fetch(API_BASE_URL + `/reports/all`);
    if (!res.ok) throw new Error("Failed to fetch reports");
    return (res.json());
  }
};