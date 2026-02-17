import React, { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { BlueprintList } from './components/BlueprintList';
import { BlueprintForm } from './components/BlueprintForm';
import { ScheduleList } from './components/ScheduleList';
import { api } from './services/api';
import { Blueprint, SchedulerState } from './types';

const App: React.FC = () => {
  // --- State ---
  const [activeTab, setActiveTab] = useState<'blueprints' | 'schedules'>('blueprints');
  const [isDark, setIsDark] = useState(false);
  const [blueprints, setBlueprints] = useState<Blueprint[]>([]);
  const [schedules, setSchedules] = useState<string[]>([]);
  const [schedulerState, setSchedulerState] = useState<SchedulerState>('running');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBlueprint, setEditingBlueprint] = useState<Blueprint | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // --- Effects ---

  // Load Theme
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  // Fetch Data based on active tab
  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      if (activeTab === 'blueprints') {
        const data = await api.getBlueprints();
        setBlueprints(data);
      } else {
        const scheds = await api.getSchedules();
        const state = await api.getSchedulerState();
        setSchedules(scheds);
        setSchedulerState(state);
      }
    } catch (err) {
      console.error("Failed to fetch data", err);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Handlers ---

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const handleCreateOpen = () => {
    setEditingBlueprint(null);
    setIsModalOpen(true);
  };

  const handleEditOpen = (bp: Blueprint) => {
    setEditingBlueprint(bp);
    setIsModalOpen(true);
  };

  const handleSaveBlueprint = async (data: Omit<Blueprint, 'id'>) => {
    setIsLoading(true);
    try {
      if (editingBlueprint) {
        await api.editBlueprint(editingBlueprint.id, data);
      } else {
        await api.createBlueprint(data);
      }
      setIsModalOpen(false);
      fetchData(); // Refresh list
    } catch (err) {
      alert("Error saving blueprint");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteBlueprint = async (name: string) => {
    if (!window.confirm("Are you sure you want to delete this blueprint?")) return;
    setIsLoading(true);
    try {
      await api.deleteBlueprint(name);
      fetchData();
    } catch (err) {
      alert("Error deleting blueprint");
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleScheduler = async () => {
    setIsLoading(true);
    try {
      const newState = await api.toggleSchedulerState();
      setSchedulerState(newState);
      // Refresh schedules as pausing/resuming changes the list
      const newSchedules = await api.getSchedules();
      setSchedules(newSchedules);
    } catch (err) {
      alert("Error toggling scheduler");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout
      activeTab={activeTab}
      onTabChange={setActiveTab}
      isDark={isDark}
      toggleTheme={toggleTheme}
    >
      {activeTab === 'blueprints' ? (
        <BlueprintList
          blueprints={blueprints}
          onCreate={handleCreateOpen}
          onEdit={handleEditOpen}
          onDelete={handleDeleteBlueprint}
        />
      ) : (
        <ScheduleList
          schedules={schedules}
          schedulerState={schedulerState}
          onToggleScheduler={handleToggleScheduler}
        />
      )}

      {isModalOpen && (
        <BlueprintForm
          initialData={editingBlueprint}
          onSave={handleSaveBlueprint}
          onCancel={() => setIsModalOpen(false)}
          isLoading={isLoading}
        />
      )}
    </Layout>
  );
};

export default App;
