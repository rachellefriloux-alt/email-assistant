import React from 'react';

export default function Dashboard({
  children,
  theme,
  onToggleTheme,
  onRefresh,
  onRefreshLive,
  tabs,
  activeTab,
  setActiveTab,
  loading,
}) {
  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-4">
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">Gmail AI Assistant</p>
          <h1 className="text-3xl font-bold">Inbox Insights</h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onRefresh}
            className="px-4 py-2 rounded-md bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-60"
            disabled={loading}
          >
            {loading ? 'Refreshing…' : 'Refresh (Sample)'}
          </button>
          <button
            onClick={onRefreshLive}
            className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
            disabled={loading}
          >
            {loading ? 'Refreshing…' : 'Refresh (Live)'}
          </button>
          <button
            onClick={onToggleTheme}
            className="px-3 py-2 rounded-md border border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
          >
            {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>
      </header>

      <nav className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-2 rounded-md text-sm border ${
              activeTab === tab
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-slate-700 border-slate-200 hover:border-blue-200'
            }`}
          >
            {tab}
          </button>
        ))}
      </nav>

      {children}
    </div>
  );
}
