import React from 'react';
import { Card, Badge } from './ui/Common';
import { Icons } from './ui/Icons';
import { RunItem } from '../types';

interface RunListProps {
    runs: RunItem[];
}

// Helper to parse the raw cron string into a readable format

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

const onToggleScheduler = () => {
    return
}

export const RunsList: React.FC<RunListProps> = ({ runs }) => {
    const isRunning = true
    const schedulerState = "on"
    return (
        <div className="max-w-4xl mx-auto space-y-6">

            {/* Scheduler Control Panel */}
            <Card className="flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-zinc-900 dark:to-zinc-800 border-l-4 border-l-primary-500">
                <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                        Runs Statistic
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Job Runned: {runs.length} <br></br> Last Run: {runs[0].runnedAt.slice(0, 19)}
                    </p>
                </div>

            </Card>

            {/* Schedule Items */}
            <div className="space-y-4">
                <h3 className="text-md font-medium text-gray-900 dark:text-gray-200 uppercase tracking-wider text-xs ml-1 flex items-center gap-2">
                    <Icons.Clock size={14} /> Past Jobs
                </h3>

                {runs.length === 0 ? (
                    <div className="text-center py-12 bg-white dark:bg-zinc-900/50 rounded-xl border border-dashed border-gray-300 dark:border-zinc-700">
                        <Icons.Schedule size={32} className="mx-auto text-gray-400 mb-3" />
                        <p className="text-gray-500 dark:text-gray-400">
                            No Jobs completed.
                        </p>
                    </div>
                ) : (
                    runs.map((runitem: RunItem, idx) => {

                        return (
                            <div
                                key={runitem.name + runitem.runnedAt}
                                className="group flex flex-col sm:flex-row sm:items-center p-5 bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-lg shadow-sm hover:border-primary-300 dark:hover:border-primary-800 transition-colors"
                            >
                                <div className="flex items-center flex-1">
                                    <div className="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400 mr-4 shrink-0">
                                        <Icons.Music size={20} />
                                    </div>
                                    <div className="min-w-0">
                                        <h4 className="text-base text-gray-900 dark:text-white truncate">
                                            <b>Name:</b> {runitem.name}
                                        </h4>
                                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 break-all line-clamp-2">
                                            <b>With prompt:</b> {runitem.blueprint.prompt}
                                        </p>
                                    </div>
                                </div>

                                <div className="mt-4 sm:mt-0 sm:pl-6 sm:text-right border-t sm:border-t-0 sm:border-l border-gray-100 dark:border-zinc-800 pt-3 sm:pt-0 shrink-0">
                                    <div className="text-xs text-gray-400 uppercase tracking-wide font-medium">Executed At:</div>
                                    <div className="text-sm font-semibold text-primary-700 dark:text-primary-300 mt-1 font-mono">
                                        {runitem.runnedAt.slice(0, 19)}
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