import React, { useState } from 'react';

const suggestions = [
  "Summarize today's important emails",
  'Draft a polite reply to the latest billing email',
  'Mark promotional emails for deletion review',
];

export default function AssistantPanel({ onPrompt, loading, reply, theme }) {
  const [prompt, setPrompt] = useState('');

  const handleSend = async (text) => {
    const content = text || prompt;
    if (!content) return;
    await onPrompt(content);
  };

  return (
    <div className="p-4 border rounded-md bg-white shadow-sm h-full space-y-3 dark:bg-slate-800 dark:border-slate-700">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Assistant</h2>
        <span className="text-xs text-slate-500">{theme === 'dark' ? 'Dark' : 'Light'} mode</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {suggestions.map((s) => (
          <button
            key={s}
            onClick={() => handleSend(s)}
            className="text-xs px-3 py-2 rounded-md bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100"
            disabled={loading}
          >
            {s}
          </button>
        ))}
      </div>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Ask GPT…"
        className="w-full h-24 p-3 border rounded-md resize-none text-sm dark:bg-slate-900 dark:border-slate-700"
      />

      <button
        onClick={() => handleSend()}
        className="w-full px-4 py-2 rounded-md bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-60"
        disabled={loading}
      >
        {loading ? 'Thinking…' : 'Send to GPT'}
      </button>

      <div className="p-3 border rounded-md bg-slate-50 text-sm min-h-[80px] dark:bg-slate-900 dark:border-slate-700">
        {reply || 'Assistant replies will appear here.'}
      </div>
    </div>
  );
}
