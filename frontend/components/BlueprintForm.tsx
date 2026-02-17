import React, { useState, useEffect } from 'react';
import { Blueprint } from '../types';
import { Button, Input, Select, Textarea, Card } from './ui/Common';
import { Icons } from './ui/Icons';

interface BlueprintFormProps {
  initialData?: Blueprint | null;
  onSave: (data: Omit<Blueprint, 'id'>) => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
}

const DEFAULT_BLUEPRINT: Omit<Blueprint, 'id'> = {
  name: '',
  metaApi: 'lbz',
  audioApi: 'hifi',
  prompt: '',
  enabled: true,
  every: 'weekly',
  hour: '09',
  minute: '00',
  weekday: '1',
  day: '1',
  month: '*',
  description: '',
  mode: 'easy'
};

export const BlueprintForm: React.FC<BlueprintFormProps> = ({ initialData, onSave, onCancel, isLoading }) => {
  const [formData, setFormData] = useState<Omit<Blueprint, 'id'>>(DEFAULT_BLUEPRINT);

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (field: keyof Blueprint, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-0 flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between border-b border-gray-200 bg-gray-50 p-4 dark:border-zinc-800 dark:bg-zinc-900/50 sticky top-0 z-10 backdrop-blur-md">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            {initialData ? 'Edit Blueprint' : 'Create New Blueprint'}
          </h2>
          <button onClick={onCancel} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
            <Icons.X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Main Info */}
          <div className="grid gap-6 md:grid-cols-2">
            <Input 
              label="Playlist Name" 
              value={formData.name} 
              onChange={e => handleChange('name', e.target.value)} 
              placeholder="e.g., Weekly Discover" 
              required 
            />
            
            <div className="flex items-end mb-2 md:justify-start">
               {/* Spacer or Checkbox could go here if needed to balance grid, 
                   but moved checkbox to schedule section for cleaner flow */}
            </div>
          </div>

          <Textarea 
            label="Description" 
            value={formData.description} 
            onChange={e => handleChange('description', e.target.value)} 
            placeholder="What is this playlist about?" 
            rows={2}
          />

          <div className="grid gap-6 md:grid-cols-2">
            <Input 
              label="Meta API" 
              value={formData.metaApi} 
              onChange={e => handleChange('metaApi', e.target.value)} 
            />
            <Input 
              label="Audio API" 
              value={formData.audioApi} 
              onChange={e => handleChange('audioApi', e.target.value)} 
            />
          </div>

          <div className="space-y-4">
             <div className="flex items-center justify-between">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Generation Logic</label>
             </div>
             <div className="grid md:grid-cols-4 gap-4">
                <div className="md:col-span-1">
                  <Select 
                    label="Search Effort"
                    value={formData.mode}
                    onChange={e => handleChange('mode', e.target.value as 'easy' | 'medium' | 'hard')}
                    options={[
                      { label: 'Easy', value: 'easy' },
                      { label: 'Medium', value: 'medium' },
                      { label: 'Hard', value: 'hard' }
                    ]}
                  />
                </div>
                <div className="md:col-span-3">
                  <Textarea 
                    label="Prompt" 
                    value={formData.prompt} 
                    onChange={e => handleChange('prompt', e.target.value)} 
                    placeholder="e.g., tag:(jazz) mood:relaxing bpm:90" 
                    rows={1}
                    className="font-mono text-sm h-[42px] min-h-[42px] resize-none overflow-hidden py-2"
                  />
                </div>
             </div>
          </div>

          <div className="border-t border-gray-100 dark:border-zinc-800 pt-6">
             <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Icons.Clock size={16} /> Scheduling Configuration
                </h3>
                
                <label className="flex items-center space-x-2 cursor-pointer select-none">
                  <input 
                    type="checkbox" 
                    checked={formData.enabled} 
                    onChange={e => handleChange('enabled', e.target.checked)}
                    className="w-4 h-4 rounded text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-zinc-700 dark:bg-zinc-800"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Enable Schedule</span>
                </label>
             </div>

             <div className="grid gap-6 md:grid-cols-12 bg-gray-50 dark:bg-zinc-800/50 p-4 rounded-lg">
                <div className="md:col-span-12">
                   <Select 
                    label="Frequency" 
                    value={formData.every} 
                    onChange={e => handleChange('every', e.target.value)}
                    options={[
                      { label: 'Weekly', value: 'weekly' },
                      { label: 'Monthly', value: 'monthly' },
                    ]}
                  />
                </div>
                
                {/* Weekly Fields */}
                {formData.every === 'weekly' && (
                  <>
                     <div className="md:col-span-6">
                       <Input 
                        label="Day of Week (0=Sun, 6=Sat)" 
                        placeholder="e.g. 1, 3, 5"
                        value={formData.weekday} 
                        onChange={e => handleChange('weekday', e.target.value)}
                       />
                     </div>
                     <div className="md:col-span-3">
                        <Input 
                          label="Hours (0-23)" 
                          placeholder="e.g. 09, 21"
                          value={formData.hour} 
                          onChange={e => handleChange('hour', e.target.value)} 
                        />
                     </div>
                     <div className="md:col-span-3">
                        <Input 
                          label="Minutes (0-59)" 
                          placeholder="e.g. 00, 30"
                          value={formData.minute} 
                          onChange={e => handleChange('minute', e.target.value)} 
                        />
                     </div>
                  </>
                )}

                {/* Monthly Fields */}
                {formData.every === 'monthly' && (
                  <>
                     <div className="md:col-span-3">
                        <Input 
                          label="Day of Month" 
                          placeholder="e.g. 1, 15"
                          value={formData.day} 
                          onChange={e => handleChange('day', e.target.value)} 
                        />
                     </div>
                     <div className="md:col-span-3">
                        <Input 
                          label="Month (1-12)" 
                          placeholder="e.g. 1, 6, 12 or *"
                          value={formData.month} 
                          onChange={e => handleChange('month', e.target.value)} 
                        />
                     </div>
                     <div className="md:col-span-3">
                        <Input 
                          label="Hours (0-23)" 
                          placeholder="e.g. 09, 21"
                          value={formData.hour} 
                          onChange={e => handleChange('hour', e.target.value)} 
                        />
                     </div>
                     <div className="md:col-span-3">
                        <Input 
                          label="Minutes (0-59)" 
                          placeholder="e.g. 00, 30"
                          value={formData.minute} 
                          onChange={e => handleChange('minute', e.target.value)} 
                        />
                     </div>
                  </>
                )}
                
                <div className="md:col-span-12">
                  <p className="text-xs text-gray-400">
                    Tip: You can use comma separated values for multiple schedules (e.g. "09, 18" for 9AM and 6PM).
                  </p>
                </div>
             </div>
          </div>
        </form>

        <div className="flex items-center justify-end gap-3 p-4 border-t border-gray-200 bg-gray-50 dark:border-zinc-800 dark:bg-zinc-900 sticky bottom-0 z-10">
          <Button variant="ghost" onClick={onCancel} disabled={isLoading}>Cancel</Button>
          <Button variant="primary" onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? <Icons.Refresh className="animate-spin" /> : <Icons.Save size={18} className="mr-2" />}
            Save Blueprint
          </Button>
        </div>
      </Card>
    </div>
  );
};