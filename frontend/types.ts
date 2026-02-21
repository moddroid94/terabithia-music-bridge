export interface Blueprint {
  id: string; // Internal ID for frontend management
  name: string;
  metaApi: string;
  audioApi: string;
  prompt: string;
  enabled: boolean;
  every: 'weekly' | 'monthly';
  hour: string;
  minute: string;
  weekday: string;
  day: string;
  month: string;
  description: string;
  mode: 'easy' | 'medium' | 'hard';
  quantity: number;
}

export type SchedulerState = 'Running and processing' | 'Processing Paused' | 'Not Running' | 'Status Unknown';

export interface ScheduleItem {
  raw: string; // The raw string returned by API
  id: string;  // Parsed ID for list management
  name: string;
  nextRun: string;
  trigger: string;
}

export interface RunItem {
  name: string;
  runnedAt: string;
  blueprint: Blueprint;
  tracklist: [];

}