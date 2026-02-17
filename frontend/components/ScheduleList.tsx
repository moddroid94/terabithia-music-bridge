import React from 'react';
import { Card, Badge } from './ui/Common';
import { Icons } from './ui/Icons';
import { SchedulerState } from '../types';

interface ScheduleListProps {
  schedules: string[];
  schedulerState: SchedulerState;
  onToggleScheduler: () => void;
}

// Helper to parse the raw cron string into a readable format
// Input example: "trigger: cron[day_of_week='*', hour='*', minute='10']"
const parseTrigger = (triggerStr: string) => {
  if (!triggerStr) return "Unknown Schedule";

  const getVal = (key: string) => {
    const match = triggerStr.match(new RegExp(`${key}='([^']*)'`));
    return match ? match[1] : null;
  };

  const dayOfWeek = getVal('day_of_week');
  const day = getVal('day');
  const month = getVal('month');
  const hour = getVal('hour') || '0';
  const minute = getVal('minute') || '0';

  const formatTime = (hStr: string, mStr: string) => {
    const hours = hStr.split(',').map(h => h.trim().padStart(2, '0'));
    const mins = mStr.split(',').map(m => m.trim().padStart(2, '0'));

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

  const time = formatTime(hour, minute);

  // Weekly logic
  if (dayOfWeek && dayOfWeek !== '*') {
    const daysMap = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const days = dayOfWeek.split(',').map(d => {
      const i = parseInt(d);
      return isNaN(i) ? d : (daysMap[i] || d);
    }).join(', ');

    return `Weekly on ${days} at ${time}`;
  }

  // Monthly logic
  if (day && day !== '*') {
    const monthMap = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    let mStr = 'Monthly';
    if (month && month !== '*') {
      mStr = month.split(',').map(m => {
        const i = parseInt(m);
        return isNaN(i) ? m : (monthMap[i] || m);
      }).join(', ');
    }

    return `${mStr} on the ${day} at ${time}`;
  }

  // Daily / Catch-all
  if (dayOfWeek === '*' && (day === undefined || day === '*')) {
    return `Daily at ${time}`;
  }

  return triggerStr.replace('trigger: ', '').replace('cron[', '').replace(']', '');
};

export const ScheduleList: React.FC<ScheduleListProps> = ({ schedules, schedulerState, onToggleScheduler }) => {
  const isRunning = schedulerState === 'Running and processing';

  return (
    <div className="max-w-4xl mx-auto space-y-6">

      {/* Scheduler Control Panel */}
      <Card className="flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-zinc-900 dark:to-zinc-800 border-l-4 border-l-primary-500">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            Scheduler Status
            <Badge variant={isRunning ? 'success' : 'warning'}>
              {schedulerState}
            </Badge>
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {isRunning
              ? "The scheduler is actively processing your enabled blueprints."
              : "Scheduler is paused. No playlists will be generated."}
          </p>
        </div>
        <button
          onClick={onToggleScheduler}
          className={`relative inline-flex h-12 w-20 items-center rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${isRunning ? 'bg-primary-600' : 'bg-gray-200 dark:bg-zinc-700'
            }`}
        >
          <span
            className={`inline-block h-10 w-10 transform rounded-full bg-white shadow transition duration-300 ease-in-out ${isRunning ? 'translate-x-9' : 'translate-x-1'
              } flex items-center justify-center`}
          >
            {isRunning ? <Icons.Play size={20} className="text-primary-600" /> : <Icons.Pause size={20} className="text-gray-400" />}
          </span>
        </button>
      </Card>

      {/* Schedule Items */}
      <div className="space-y-4">
        <h3 className="text-md font-medium text-gray-900 dark:text-gray-200 uppercase tracking-wider text-xs ml-1 flex items-center gap-2">
          <Icons.Clock size={14} /> Upcoming Jobs
        </h3>

        {schedules.length === 0 ? (
          <div className="text-center py-12 bg-white dark:bg-zinc-900/50 rounded-xl border border-dashed border-gray-300 dark:border-zinc-700">
            <Icons.Schedule size={32} className="mx-auto text-gray-400 mb-3" />
            <p className="text-gray-500 dark:text-gray-400">
              {isRunning
                ? "No active schedules. Enable some blueprints to see them here."
                : "Scheduler is paused. Resume to see upcoming jobs."}
            </p>
          </div>
        ) : (
          schedules.map((scheduleRaw, idx) => {
            // Raw: "Releases Radar (trigger: cron[day_of_week='*', hour='*', minute='10'], next run at: 2026-02-16 23:10:00 CET)"

            const nameMatch = scheduleRaw.match(/^(.*?)\s\(/);
            const nextRunMatch = scheduleRaw.match(/next run at:\s(.*?)\)/);
            const triggerMatch = scheduleRaw.match(/trigger:\s(cron\[.*?\])/);

            const name = nameMatch ? nameMatch[1] : "Unknown Job";
            const nextRun = nextRunMatch ? nextRunMatch[1] : "Unknown";
            const rawTrigger = triggerMatch ? triggerMatch[1] : "";

            const readableTrigger = parseTrigger(rawTrigger);

            return (
              <div
                key={idx}
                className="group flex flex-col sm:flex-row sm:items-center p-5 bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-lg shadow-sm hover:border-primary-300 dark:hover:border-primary-800 transition-colors"
              >
                <div className="flex items-center flex-1">
                  <div className="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400 mr-4 shrink-0">
                    <Icons.Music size={20} />
                  </div>
                  <div className="min-w-0">
                    <h4 className="text-base font-semibold text-gray-900 dark:text-white truncate">
                      {name}
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 break-all line-clamp-2">
                      {readableTrigger}
                    </p>
                  </div>
                </div>

                <div className="mt-4 sm:mt-0 sm:pl-6 sm:text-right border-t sm:border-t-0 sm:border-l border-gray-100 dark:border-zinc-800 pt-3 sm:pt-0 shrink-0">
                  <div className="text-xs text-gray-400 uppercase tracking-wide font-medium">Next Execution</div>
                  <div className="text-sm font-semibold text-primary-700 dark:text-primary-300 mt-1 font-mono">
                    {nextRun}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};