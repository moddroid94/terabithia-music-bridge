import React from 'react';
import { Icons } from './ui/Icons';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: 'blueprints' | 'schedules';
  onTabChange: (tab: 'blueprints' | 'schedules') => void;
  isDark: boolean;
  toggleTheme: () => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, activeTab, onTabChange, isDark, toggleTheme }) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-950 flex flex-col md:flex-row">

      {/* Sidebar / Navigation */}
      <aside className="w-full md:w-64 bg-white dark:bg-zinc-900 border-b md:border-b-0 md:border-r border-gray-200 dark:border-zinc-800 flex-shrink-0 flex flex-col z-20 sticky top-0 md:h-screen">
        <div className="p-6 flex items-center justify-between md:justify-start gap-3 border-b border-gray-100 dark:border-zinc-800/50">
          <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400">
            <div className="w-8 h-8 rounded-lg bg-primary-600 text-white flex items-center justify-center shadow-lg shadow-primary-500/30">
              <Icons.Music size={18} />
            </div>
            <span className="font-bold text-lg tracking-tight text-gray-900 dark:text-white">Terabithia</span>
          </div>

          {/* Mobile Theme Toggle */}
          <button onClick={toggleTheme} className="md:hidden p-2 text-gray-500 dark:text-gray-400 rounded-md hover:bg-gray-100 dark:hover:bg-zinc-800">
            {isDark ? <Icons.Sun size={20} /> : <Icons.Moon size={20} />}
          </button>
        </div>

        <nav className="p-4 space-y-2 flex-1">
          <button
            onClick={() => onTabChange('blueprints')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${activeTab === 'blueprints'
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-300'
                : 'text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-zinc-800'
              }`}
          >
            <Icons.Dashboard size={20} />
            Blueprints
          </button>

          <button
            onClick={() => onTabChange('schedules')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${activeTab === 'schedules'
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-300'
                : 'text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-zinc-800'
              }`}
          >
            <Icons.Schedule size={20} />
            Schedules
          </button>
        </nav>

        <div className="p-4 border-t border-gray-100 dark:border-zinc-800 hidden md:block">
          <button
            onClick={toggleTheme}
            className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-zinc-800 transition-colors"
          >
            {isDark ? <Icons.Sun size={18} /> : <Icons.Moon size={18} />}
            <span>{isDark ? 'Light Mode' : 'Dark Mode'}</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 min-w-0 overflow-y-auto h-[calc(100vh-64px)] md:h-screen">
        <header className="px-6 py-5 md:py-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white capitalize">
            {activeTab} Management
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {activeTab === 'blueprints'
              ? 'Create and configure your playlist generation rules.'
              : 'Monitor upcoming playlist generation jobs.'}
          </p>
        </header>
        <div className="px-6 pb-12">
          {children}
        </div>
      </main>
    </div>
  );
};
