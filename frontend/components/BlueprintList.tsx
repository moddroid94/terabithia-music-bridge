import React from 'react';
import { Blueprint } from '../types';
import { Card, Badge, Button } from './ui/Common';
import { Icons } from './ui/Icons';

interface BlueprintListProps {
  blueprints: Blueprint[];
  onEdit: (blueprint: Blueprint) => void;
  onDelete: (name: string) => void;
  onCreate: () => void;
}

const WEEKDAY_MAP: Record<string, string> = {
  '0': 'Sun', '1': 'Mon', '2': 'Tue', '3': 'Wed',
  '4': 'Thu', '5': 'Fri', '6': 'Sat', '*': 'Daily'
};

const MONTH_MAP: Record<string, string> = {
  '1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun',
  '7': 'Jul', '8': 'Aug', '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec', '*': 'Every Month'
};

const formatTime = (hourStr: string, minStr: string) => {
  const hours = hourStr.split(',').map(h => h.trim().padStart(2, '0'));
  const mins = minStr.split(',').map(m => m.trim().padStart(2, '0'));

  // If simplified single time
  if (hours.length === 1 && mins.length === 1) {
    return `${hours[0]}:${mins[0]}`;
  }

  // If small number of combinations, list them
  if (hours.length * mins.length <= 4) {
    const times: string[] = [];
    hours.forEach(h => mins.forEach(m => times.push(`${h}:${m}`)));
    return times.join(', ');
  }

  // Otherwise shorthand
  return `${hours.join(',')}h ${mins.join(',')}m`;
};

const getReadableSchedule = (bp: Blueprint) => {
  const time = formatTime(bp.hour, bp.minute);

  if (bp.every === 'weekly') {
    if (bp.weekday === '*') return `Daily at ${time}`;
    const days = bp.weekday.split(',').map(d => WEEKDAY_MAP[d.trim()] || d).join(', ');
    return `${days} at ${time}`;
  }

  if (bp.every === 'monthly') {
    const months = bp.month === '*' ? 'Monthly' : bp.month.split(',').map(m => MONTH_MAP[m.trim()] || m).join(', ');
    const days = bp.day === '*' ? 'every day' : `on the ${bp.day}`;

    if (bp.month === '*') {
      return `${months} ${days} at ${time}`;
    }
    return `${months} ${days} at ${time}`;
  }

  return 'Custom Schedule';
};

const ModeBadge: React.FC<{ mode: string }> = ({ mode }) => {
  const colors = {
    easy: 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-900/20',
    medium: 'text-yellow-600 bg-yellow-50 dark:text-yellow-400 dark:bg-yellow-900/20',
    hard: 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-900/20',
  };
  const colorClass = colors[mode as keyof typeof colors] || colors.easy;

  return (
    <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded tracking-wide ${colorClass}`}>
      {mode}
    </span>
  );
};

export const BlueprintList: React.FC<BlueprintListProps> = ({ blueprints, onEdit, onDelete, onCreate }) => {
  if (blueprints.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4 dark:bg-zinc-800">
          <Icons.Music size={32} className="text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">No blueprints yet</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-1 mb-6">Create your first playlist generation blueprint to get started.</p>
        <Button onClick={onCreate}>
          <Icons.Plus size={18} className="mr-2" />
          Create Blueprint
        </Button>
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {blueprints.map((bp) => (
        <Card key={bp.id} className="group relative flex flex-col h-full hover:border-primary-500/50 dark:hover:border-primary-500/50 transition-all duration-200">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1 min-w-0 mr-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate" title={bp.name}>
                {bp.name}
              </h3>
              <div className="flex items-center gap-2 mt-1">
                <ModeBadge mode={bp.mode} />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Badge variant={bp.enabled ? 'success' : 'neutral'}>
                {bp.enabled ? 'Active' : 'Disabled'}
              </Badge>
            </div>
          </div>

          {/* Prompt Preview */}
          <div className="mb-4 relative">
            <div className="text-xs font-mono text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-zinc-800/50 p-2 rounded border border-gray-100 dark:border-zinc-800 h-16 overflow-hidden">
              <span className="opacity-50 select-none mr-2">$</span>
              {bp.prompt || "No prompt configured..."}
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-gray-50 dark:from-zinc-900/10 to-transparent pointer-events-none"></div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs mb-4">
            <div className="flex flex-col">
              <span className="text-gray-400 dark:text-gray-500">Meta API</span>
              <span className="font-medium text-gray-700 dark:text-gray-200 truncate" title={bp.metaApi}>{bp.metaApi}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-400 dark:text-gray-500">Audio API</span>
              <span className="font-medium text-gray-700 dark:text-gray-200 truncate" title={bp.audioApi}>{bp.audioApi}</span>
            </div>
          </div>

          {/* Schedule Info & Actions */}
          <div className="mt-auto pt-4 border-t border-gray-100 dark:border-zinc-800 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-300 max-w-[70%]">
              <Icons.Clock size={14} className="text-primary-500 shrink-0" />
              <span className="font-medium truncate" title={getReadableSchedule(bp)}>{getReadableSchedule(bp)}</span>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={(e) => { e.stopPropagation(); onEdit(bp); }}
                className="flex items-center justify-center w-8 h-8 rounded-lg text-gray-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all"
                title="Edit Blueprint"
              >
                <Icons.Edit size={16} />
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); onDelete(bp.name); }}
                className="flex items-center justify-center w-8 h-8 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
                title="Delete Blueprint"
              >
                <Icons.Trash size={16} />
              </button>
            </div>
          </div>
        </Card>
      ))}

      {/* Add New Card */}
      <button
        onClick={onCreate}
        className="flex flex-col items-center justify-center h-full min-h-[250px] rounded-xl border-2 border-dashed border-gray-300 bg-gray-50/50 text-gray-500 hover:border-primary-500 hover:text-primary-500 hover:bg-primary-50/10 transition-all dark:border-zinc-700 dark:bg-zinc-900/30 dark:hover:border-primary-500"
      >
        <div className="w-12 h-12 rounded-full bg-white dark:bg-zinc-800 flex items-center justify-center shadow-sm mb-3">
          <Icons.Plus size={24} />
        </div>
        <span className="font-medium">Create New Blueprint</span>
      </button>
    </div>
  );
};