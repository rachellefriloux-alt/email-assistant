import React from 'react';

const badgeColors = {
  Billing: 'bg-blue-50 text-blue-700 border-blue-200',
  'Account Info': 'bg-indigo-50 text-indigo-700 border-indigo-200',
  'Work Update': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  Promotion: 'bg-purple-50 text-purple-700 border-purple-200',
  Spam: 'bg-slate-100 text-slate-700 border-slate-200',
  Personal: 'bg-pink-50 text-pink-700 border-pink-200',
};

export default function EmailList({ emails, loading, selectedIds, onToggleSelect }) {
  if (loading) {
    return <div className="p-4 border rounded-md bg-white shadow-sm">Loading emails…</div>;
  }

  if (!emails.length) {
    return <div className="p-4 border rounded-md bg-white shadow-sm">No emails to display yet.</div>;
  }

  return (
    <div className="space-y-3">
      {emails.map((email, idx) => (
        <div key={`${email.gmail_id || email.id || idx}`} className="p-4 border rounded-md bg-white shadow-sm">
          <div className="flex items-start justify-between gap-4">
            <div className="flex gap-3 items-start">
              {onToggleSelect && (
                <input
                  type="checkbox"
                  checked={selectedIds?.has(email.gmail_id)}
                  onChange={() => onToggleSelect(email.gmail_id)}
                  className="mt-1"
                />
              )}
              <div>
                <p className="text-xs text-slate-500">{email.from_email || 'Unknown sender'}</p>
                <h3 className="text-lg font-semibold">{email.subject}</h3>
                <p className="text-[11px] text-slate-400">{email.status || 'keep'}</p>
              </div>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs border ${
              badgeColors[email.category] || 'bg-slate-100 text-slate-700 border-slate-200'
            }`}>
              {email.category || 'Unlabeled'}
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-700 line-clamp-3">{email.snippet || email.body || 'No preview available.'}</p>
        </div>
      ))}
    </div>
  );
}
