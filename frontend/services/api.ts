import { Blueprint, RunItem, SchedulerState } from '../types';


export const api = {
  // --- Blueprint Operations --- //

  getBlueprints: async (): Promise<Blueprint[]> => {
    const res = await fetch(`http://localhost:8000/blueprints/all`);
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return res.json();
  },

  createBlueprint: async (blueprint: Omit<Blueprint, 'id'>): Promise<Blueprint> => {
    const newBlueprint = { ...blueprint, id: Date.now().toString() };
    const res = await fetch(`http://localhost:8000/blueprint/new`, {
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
    const res = await fetch(`http://localhost:8000/blueprint/${blueprints[index].name}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated),
    });
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return res.json();
  },

  deleteBlueprint: async (name: string): Promise<void> => {
    const res = await fetch(`http://localhost:8000/blueprint/delete?playlistName=${name}`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return res.json();
  },

  // --- Scheduler Operations --- //

  getSchedules: async (): Promise<string[]> => {
    const res = await fetch(`http://localhost:8000/scheduler/all`);
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return res.json();
  },

  getSchedulerState: async (): Promise<SchedulerState> => {
    const res = await fetch(`http://localhost:8000/scheduler/state`);
    if (!res.ok) throw new Error("Failed to fetch blueprints");
    return (res.json() as unknown as SchedulerState);
  },

  toggleSchedulerState: async (): Promise<SchedulerState> => {
    const current = await api.getSchedulerState();
    const next = current === 'Running and processing' ? 'false' : 'true';
    const res = await fetch(`http://localhost:8000/scheduler/${next}`, {
      method: "POST",
    });
    const newstate = await api.getSchedulerState();
    return newstate;
  },

  // --- Reports Operations --- //

  getRuns: async (): Promise<RunItem[]> => {
    const res = await fetch(`http://localhost:8000/reports/all`);
    if (!res.ok) throw new Error("Failed to fetch reports");
    return (res.json());
  }
};