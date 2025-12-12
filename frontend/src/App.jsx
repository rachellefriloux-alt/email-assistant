import React, { useState, useEffect, useMemo, useRef } from 'react';
import { 
  Mail, Inbox, Tag, Zap, Trash2, Archive, 
  MoreVertical, Search, RefreshCw, Sun, Moon, 
  ChevronLeft, ChevronRight, PenTool, BarChart2, 
  Settings, CheckCircle2, AlertCircle, X, Send,
  Paperclip, Reply, Star, User, Sparkles, 
  ListChecks, Wand2, Eraser
} from 'lucide-react';

/**
 * MOCK DATA GENERATOR
 * Used to simulate backend responses when in Demo Mode.
 */
const GENERATE_MOCK_EMAILS = (count = 15) => {
  const categories = ['Billing', 'Work', 'Personal', 'Promotions', 'Spam'];
  const senders = ['amazon.com', 'google.com', 'boss@company.com', 'mom@gmail.com', 'newsletter@tech.com'];
  const subjects = [
    'Your invoice for AWS Services', 
    'Project Sync: Q4 Goals', 
    'Dinner this weekend?', 
    '50% OFF everything!', 
    'You won a lottery (Claim now)'
  ];
  
  return Array.from({ length: count }).map((_, i) => ({
    id: `msg_${Math.random().toString(36).substr(2, 9)}`,
    gmail_id: `g_${Math.random().toString(36).substr(2, 9)}`,
    subject: subjects[i % subjects.length] + ` #${i + 1}`,
    from_email: `contact@${senders[i % senders.length]}`,
    snippet: `This is a preview of the email content for message ${i + 1}. It contains important details regarding...`,
    body: `Hi there,\n\nI hope this email finds you well. \n\nThis is a full body content mock for message ${i + 1}. It contains significantly more details than the snippet. We need to discuss the Q4 goals and the AWS invoice discrepancies.\n\nPlease review the attached documents by Friday.\n\nBest,\nSender`,
    category: categories[i % categories.length],
    date: new Date(Date.now() - Math.floor(Math.random() * 1000000000)).toISOString(),
    isRead: Math.random() > 0.3,
    isStarred: Math.random() > 0.8,
    urgency: Math.random() > 0.7 ? 'High' : 'Normal',
    sentiment: Math.random() > 0.5 ? 'Positive' : 'Neutral',
  }));
};

/**
 * API CLIENT
 * Handles switching between Real API and Mock Data transparently.
 */
const createClient = (baseUrl, isDemoMode) => {
  const mockStore = {
    emails: GENERATE_MOCK_EMAILS(),
  };

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  return {
    get: async (endpoint, params = {}) => {
      if (isDemoMode) {
        await sleep(600); // Simulate network latency
        if (endpoint === '/gmail/list') return { data: { emails: mockStore.emails } };
        if (endpoint === '/gmail/fetch') return { data: { message: "Fetched" } };
        if (endpoint === '/stats') {
           // Calculate dynamic stats
           const cats = mockStore.emails.reduce((acc, e) => {
             acc[e.category] = (acc[e.category] || 0) + 1;
             return acc;
           }, {});
           return { data: cats };
        }
      } else {
        // Real Fetch Implementation (would use fetch/axios)
        const res = await fetch(`${baseUrl}${endpoint}`);
        return res.json();
      }
    },
    post: async (endpoint, payload) => {
      if (isDemoMode) {
        await sleep(1000);
        // --- GEMINI MOCKS ---
        if (endpoint === '/assistant/gemini/summarize') {
            return { data: { reply: "• The sender is asking about Q4 goals.\n• An AWS invoice needs review.\n• Deadline is Friday." } };
        }
        if (endpoint === '/assistant/gemini/actions') {
            return { data: { reply: "- [ ] Review Q4 Goal Documents\n- [ ] Check AWS Invoice discrepancies\n- [ ] Reply by Friday" } };
        }
        if (endpoint === '/assistant/gemini/rewrite') {
            const tones = {
                'Professional': "Dear Recipient,\n\nPlease find the attached documents regarding our Q4 objectives. I would appreciate your review at your earliest convenience.\n\nSincerely,\nUser",
                'Friendly': "Hey!\n\nHere are the docs for Q4. Take a look when you have a sec!\n\nCheers,\nUser",
                'Concise': "Attached are the Q4 docs. Please review."
            };
            return { data: { reply: tones[payload.tone] || payload.text } };
        }
        // --- LEGACY/STANDARD MOCKS ---
        if (endpoint === '/assistant/reply') {
          return { data: { reply: `Here is a drafted response based on your request: "${payload.prompt}"\n\nDear Sender,\n\nThank you for your email. I have reviewed the contents and...\n\nBest,\nUser` } };
        }
        if (endpoint === '/gmail/delete') {
          mockStore.emails = mockStore.emails.filter(e => !payload.gmail_ids.includes(e.gmail_id));
          return { data: { deleted: payload.gmail_ids.length } };
        }
        if (endpoint === '/gmail/move') {
            return { data: { moved: true }};
        }
      } else {
        const res = await fetch(`${baseUrl}${endpoint}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        return res.json();
      }
    }
  };
};

// --- COMPONENTS ---

const Badge = ({ children, color, className = '' }) => {
  const colors = {
    blue: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    green: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
    red: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300',
    yellow: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
    gray: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400',
    purple: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
    indigo: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300',
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border border-transparent ${colors[color] || colors.gray} ${className}`}>
      {children}
    </span>
  );
};

const EmailRow = ({ email, selected, onSelect, onClick }) => {
  return (
    <div 
      className={`group flex items-center p-4 border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer ${selected ? 'bg-blue-50/50 dark:bg-blue-900/10' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center gap-4 mr-4" onClick={(e) => e.stopPropagation()}>
        <input 
          type="checkbox" 
          checked={selected}
          onChange={() => onSelect(email.gmail_id)}
          className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
        />
        <Star 
          size={18} 
          className={`${email.isStarred ? 'fill-yellow-400 text-yellow-400' : 'text-slate-300 dark:text-slate-600 hover:text-slate-400'}`} 
        />
      </div>
      
      <div className="flex-1 min-w-0 grid grid-cols-12 gap-4 items-center">
        <div className={`col-span-3 font-medium truncate ${!email.isRead ? 'text-slate-900 dark:text-white' : 'text-slate-600 dark:text-slate-400'}`}>
          {email.from_email.split('<')[0].replace(/"/g, '')}
        </div>
        
        <div className="col-span-7 flex items-center gap-2 min-w-0">
            {email.urgency === 'High' && <Badge color="red">Urgent</Badge>}
            <Badge color={getCategoryColor(email.category)}>{email.category}</Badge>
            <span className={`truncate text-sm ${!email.isRead ? 'font-semibold text-slate-800 dark:text-slate-200' : 'text-slate-500'}`}>
                {email.subject}
            </span>
            <span className="text-sm text-slate-400 truncate hidden sm:inline">
                - {email.snippet}
            </span>
        </div>

        <div className="col-span-2 text-right text-xs text-slate-400 font-mono">
            {new Date(email.date).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

const getCategoryColor = (cat) => {
    switch(cat) {
        case 'Billing': return 'blue';
        case 'Work': return 'purple';
        case 'Promotions': return 'yellow';
        case 'Spam': return 'gray';
        case 'Personal': return 'green';
        default: return 'gray';
    }
};

const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div>
            <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">{title}</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-lg bg-${color}-50 dark:bg-${color}-900/20 text-${color}-600`}>
            <Icon size={24} />
        </div>
    </div>
);

// Sidebar Item Component
function SidebarItem({ icon: Icon, label, count, active, onClick }) {
    return (
      <button 
          onClick={onClick}
          className={`w-full flex items-center justify-between px-3 py-2 mb-1 rounded-lg text-sm font-medium transition-all ${
              active 
              ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400' 
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
      >
          <div className="flex items-center gap-3">
              <Icon size={18} />
              <span>{label}</span>
          </div>
          {count > 0 && (
              <span className={`px-2 py-0.5 rounded-full text-xs ${
                  active ? 'bg-blue-100 dark:bg-blue-900/40' : 'bg-slate-100 dark:bg-slate-800'
              }`}>
                  {count}
              </span>
          )}
      </button>
    );
}

// --- MAIN APP ---

export default function App() {
  const [theme, setTheme] = useState('light');
  const [activeTab, setActiveTab] = useState('inbox');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [demoMode, setDemoMode] = useState(true);
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [viewingEmail, setViewingEmail] = useState(null);
  
  // AI State
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [assistantReply, setAssistantReply] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [draftText, setDraftText] = useState("");

  // API Config
  const API_BASE = "http://localhost:8000";
  const api = useMemo(() => createClient(API_BASE, demoMode), [demoMode]);

  // Theme Toggle
  useEffect(() => {
    if (theme === 'dark') document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  }, [theme]);

  // Initial Load
  useEffect(() => {
    refreshEmails();
  }, [api]);

  const refreshEmails = async () => {
    setLoading(true);
    try {
        await api.get('/gmail/fetch');
        const res = await api.get('/gmail/list');
        if (res.data?.emails) {
            setEmails(res.data.emails);
        }
    } catch (e) {
        console.error("Failed to fetch", e);
    } finally {
        setLoading(false);
    }
  };

  const handleSelect = (id) => {
    const newSet = new Set(selectedIds);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedIds(newSet);
  };

  const handleDelete = async () => {
    if (selectedIds.size === 0) return;
    setLoading(true);
    try {
        await api.post('/gmail/delete', { gmail_ids: Array.from(selectedIds) });
        setEmails(prev => prev.filter(e => !selectedIds.has(e.gmail_id)));
        setSelectedIds(new Set());
    } finally {
        setLoading(false);
    }
  };

  const handleGeminiAction = async (action, payload) => {
    setAssistantOpen(true);
    setIsTyping(true);
    setAssistantReply("");
    try {
        let endpoint = '/assistant/reply'; // default
        let body = {};

        if (action === 'summarize') {
            endpoint = '/assistant/gemini/summarize';
            body = { prompt: payload };
        } else if (action === 'actions') {
            endpoint = '/assistant/gemini/actions';
            body = { prompt: payload };
        } else if (action === 'rewrite') {
            endpoint = '/assistant/gemini/rewrite';
            body = { text: payload.text, tone: payload.tone };
        } else {
            body = { prompt: payload };
        }

        const res = await api.post(endpoint, body);
        setIsTyping(false);
        
        // Typewriter effect
        const text = res.data.reply;
        let i = 0;
        const interval = setInterval(() => {
            setAssistantReply(text.substring(0, i));
            i++;
            if (i > text.length) clearInterval(interval);
        }, 10);
        
        // If it's a rewrite, also update draft text after effect
        if (action === 'rewrite') {
             setTimeout(() => setDraftText(text), 100);
        }

    } catch (e) {
        setIsTyping(false);
        setAssistantReply("Error contacting Gemini AI.");
    }
  };

  // Filter Logic
  const filteredEmails = emails.filter(e => {
      if (activeTab === 'inbox') return e.category !== 'Spam' && e.category !== 'Trash';
      if (activeTab === 'urgent') return e.urgency === 'High';
      return e.category.toLowerCase() === activeTab.toLowerCase();
  });

  const unreadCount = emails.filter(e => !e.isRead).length;

  return (
    <div className={`min-h-screen transition-colors duration-300 ${theme === 'dark' ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      
      {/* --- Sidebar --- */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 z-20 hidden md:flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg text-white">
            <Zap size={20} fill="currentColor" />
          </div>
          <span className="font-bold text-xl tracking-tight">MailMind AI</span>
        </div>

        <div className="px-4 py-2">
            <button 
                onClick={() => { setViewingEmail({ id: 'compose' }); setDraftText(""); setAssistantOpen(false); }}
                className="w-full bg-slate-900 dark:bg-blue-600 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity shadow-lg shadow-blue-900/20"
            >
                <PenTool size={18} /> Compose
            </button>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
            <SidebarItem icon={Inbox} label="Inbox" count={unreadCount} active={activeTab === 'inbox'} onClick={() => setActiveTab('inbox')} />
            <SidebarItem icon={AlertCircle} label="Urgent" active={activeTab === 'urgent'} onClick={() => setActiveTab('urgent')} />
            <SidebarItem icon={CheckCircle2} label="Billing" active={activeTab === 'billing'} onClick={() => setActiveTab('billing')} />
            <SidebarItem icon={User} label="Personal" active={activeTab === 'personal'} onClick={() => setActiveTab('personal')} />
            <SidebarItem icon={Tag} label="Promotions" active={activeTab === 'promotions'} onClick={() => setActiveTab('promotions')} />
            <SidebarItem icon={Trash2} label="Spam" active={activeTab === 'spam'} onClick={() => setActiveTab('spam')} />
            
            <div className="pt-6 pb-2">
                <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Analytics</p>
            </div>
            <SidebarItem icon={BarChart2} label="Insights" active={activeTab === 'insights'} onClick={() => setActiveTab('insights')} />
        </nav>

        <div className="p-4 border-t border-slate-200 dark:border-slate-800">
             <div className="flex items-center justify-between">
                <button onClick={() => setSettingsOpen(!settingsOpen)} className="p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors">
                    <Settings size={20} />
                </button>
                <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} className="p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors">
                    {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
                </button>
             </div>
        </div>
      </aside>

      {/* --- Main Content --- */}
      <main className="md:ml-64 min-h-screen">
        
        {/* Header */}
        <header className="sticky top-0 z-10 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-6 py-4 flex items-center justify-between">
            <h1 className="text-xl font-bold capitalize">{activeTab}</h1>
            
            <div className="flex items-center gap-3">
                <div className="relative hidden sm:block">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input 
                        type="text" 
                        placeholder="Search emails..." 
                        className="pl-10 pr-4 py-2 bg-slate-100 dark:bg-slate-900 border-none rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none w-64 transition-all"
                    />
                </div>
                <button onClick={refreshEmails} className={`p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-all ${loading ? 'animate-spin' : ''}`}>
                    <RefreshCw size={20} className="text-slate-600 dark:text-slate-400" />
                </button>
            </div>
        </header>

        {/* Action Bar */}
        {activeTab !== 'insights' && (
            <div className="px-6 py-3 flex items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                <div className="flex items-center gap-3">
                    <input 
                        type="checkbox" 
                        className="w-4 h-4 rounded border-slate-300"
                        checked={filteredEmails.length > 0 && selectedIds.size === filteredEmails.length}
                        onChange={(e) => {
                            if (e.target.checked) setSelectedIds(new Set(filteredEmails.map(e => e.gmail_id)));
                            else setSelectedIds(new Set());
                        }}
                    />
                    <span className="text-sm text-slate-500 dark:text-slate-400">
                        {selectedIds.size > 0 ? `${selectedIds.size} selected` : 'Select all'}
                    </span>
                    
                    {selectedIds.size > 0 && (
                        <div className="flex items-center gap-1 ml-4 animate-in fade-in slide-in-from-left-4 duration-200">
                            <button onClick={handleDelete} className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-rose-600 bg-rose-50 dark:bg-rose-900/20 rounded-md hover:bg-rose-100 dark:hover:bg-rose-900/40 transition-colors">
                                <Trash2 size={14} /> Delete
                            </button>
                            <button className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-600 bg-slate-100 dark:bg-slate-800 rounded-md hover:bg-slate-200 transition-colors">
                                <Archive size={14} /> Archive
                            </button>
                        </div>
                    )}
                </div>
                
                <div className="flex items-center gap-2 text-sm text-slate-500">
                    <span>1-{filteredEmails.length} of {filteredEmails.length}</span>
                    <div className="flex">
                        <button className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"><ChevronLeft size={18} /></button>
                        <button className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"><ChevronRight size={18} /></button>
                    </div>
                </div>
            </div>
        )}

        {/* Content Area */}
        <div className="p-0">
            {activeTab === 'insights' ? (
                <div className="p-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <StatCard title="Total Emails" value={emails.length} icon={Inbox} color="blue" />
                    <StatCard title="Urgent Items" value={emails.filter(e => e.urgency === 'High').length} icon={AlertCircle} color="red" />
                    <StatCard title="Spam Blocked" value={12} icon={Zap} color="yellow" />
                    <StatCard title="Storage Used" value="45%" icon={Archive} color="purple" />
                    
                    <div className="col-span-1 md:col-span-2 bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm h-64 flex items-center justify-center text-slate-400">
                        [Mock Chart Component: Email Volume by Day]
                    </div>
                    <div className="col-span-1 md:col-span-2 bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm h-64 flex items-center justify-center text-slate-400">
                        [Mock Chart Component: Category Distribution]
                    </div>
                </div>
            ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                    {loading ? (
                        <div className="p-8 text-center text-slate-400">Syncing mailbox...</div>
                    ) : filteredEmails.length === 0 ? (
                        <div className="p-12 text-center text-slate-400 flex flex-col items-center">
                            <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-full mb-4">
                                <Inbox size={32} />
                            </div>
                            <p>No emails found in this category.</p>
                        </div>
                    ) : (
                        filteredEmails.map(email => (
                            <EmailRow 
                                key={email.id} 
                                email={email} 
                                selected={selectedIds.has(email.gmail_id)}
                                onSelect={handleSelect}
                                onClick={() => { setViewingEmail(email); setAssistantOpen(false); setAssistantReply(""); }}
                            />
                        ))
                    )}
                </div>
            )}
        </div>
      </main>

      {/* --- Settings Modal --- */}
      {settingsOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
              <div className="bg-white dark:bg-slate-900 w-96 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-800 p-6 animate-in zoom-in-95 duration-200">
                  <div className="flex justify-between items-center mb-6">
                      <h2 className="text-xl font-bold">Settings</h2>
                      <button onClick={() => setSettingsOpen(false)}><X size={20} /></button>
                  </div>
                  
                  <div className="space-y-6">
                      <div className="flex items-center justify-between">
                          <div>
                              <p className="font-medium">Demo Mode</p>
                              <p className="text-xs text-slate-500">Use local mock data instead of API</p>
                          </div>
                          <button 
                            onClick={() => setDemoMode(!demoMode)}
                            className={`w-12 h-6 rounded-full p-1 transition-colors ${demoMode ? 'bg-blue-600' : 'bg-slate-300'}`}
                          >
                              <div className={`w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${demoMode ? 'translate-x-6' : 'translate-x-0'}`} />
                          </button>
                      </div>

                      <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
                          <p className="text-xs text-slate-400 mb-2">API Configuration</p>
                          <input type="text" value={API_BASE} disabled className="w-full bg-slate-100 dark:bg-slate-800 border-none rounded-md px-3 py-2 text-sm text-slate-500" />
                      </div>
                  </div>
              </div>
          </div>
      )}

      {/* --- Email View / Composer Overlay --- */}
      {viewingEmail && (
          <div className="fixed inset-0 z-40 bg-white dark:bg-slate-950 flex flex-col md:flex-row animate-in slide-in-from-right duration-300">
              {/* Overlay Header on Mobile */}
              <div className="md:hidden p-4 border-b border-slate-200 dark:border-slate-800 flex justify-between">
                  <button onClick={() => setViewingEmail(null)} className="flex items-center gap-1 text-slate-600"><ChevronLeft /> Back</button>
              </div>

              {/* Email Content */}
              <div className="flex-1 overflow-y-auto">
                  {viewingEmail.id === 'compose' ? (
                      <div className="max-w-3xl mx-auto p-8 relative">
                          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                             <PenTool size={24} className="text-blue-600" /> New Message
                          </h2>
                          
                          {/* Magic Compose Toolbar */}
                          <div className="absolute top-8 right-8 flex items-center gap-2">
                             <span className="text-xs text-slate-400 font-medium uppercase tracking-wide">Magic Polish</span>
                             <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
                                <button 
                                    onClick={() => handleGeminiAction('rewrite', { text: draftText, tone: 'Professional' })}
                                    className="p-2 hover:bg-white dark:hover:bg-slate-700 rounded-md transition-all text-slate-600 dark:text-slate-300" 
                                    title="Make Professional"
                                >
                                    <Sparkles size={16} className="text-purple-500" />
                                </button>
                                <button 
                                    onClick={() => handleGeminiAction('rewrite', { text: draftText, tone: 'Friendly' })}
                                    className="p-2 hover:bg-white dark:hover:bg-slate-700 rounded-md transition-all text-slate-600 dark:text-slate-300"
                                    title="Make Friendly"
                                >
                                    <User size={16} className="text-blue-500" />
                                </button>
                                <button 
                                    onClick={() => handleGeminiAction('rewrite', { text: draftText, tone: 'Concise' })}
                                    className="p-2 hover:bg-white dark:hover:bg-slate-700 rounded-md transition-all text-slate-600 dark:text-slate-300"
                                    title="Make Concise"
                                >
                                    <Eraser size={16} className="text-amber-500" />
                                </button>
                             </div>
                          </div>

                          <div className="space-y-4 mt-8">
                              <input type="text" placeholder="To" className="w-full border-b border-slate-200 dark:border-slate-800 py-2 bg-transparent outline-none focus:border-blue-500 transition-colors" />
                              <input type="text" placeholder="Subject" className="w-full border-b border-slate-200 dark:border-slate-800 py-2 bg-transparent outline-none font-medium focus:border-blue-500 transition-colors" />
                              <textarea 
                                className="w-full h-96 py-4 bg-transparent outline-none resize-none font-sans text-lg leading-relaxed" 
                                placeholder="Start writing..."
                                value={draftText}
                                onChange={(e) => setDraftText(e.target.value)}
                              ></textarea>
                              
                              <div className="flex justify-between items-center">
                                  <div className="text-xs text-slate-400">
                                      {assistantReply && (
                                          <div className="flex items-center gap-2 text-purple-600 animate-in fade-in">
                                              <Wand2 size={12} />
                                              <span>Rewritten by Gemini</span>
                                          </div>
                                      )}
                                  </div>
                                  <div className="flex justify-end gap-2">
                                      <button onClick={() => setViewingEmail(null)} className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-md">Discard</button>
                                      <button onClick={() => { /* Mock Send */ setViewingEmail(null); }} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2 shadow-lg shadow-blue-600/20">
                                          <Send size={16} /> Send
                                      </button>
                                  </div>
                              </div>
                          </div>
                      </div>
                  ) : (
                      <div className="max-w-4xl mx-auto p-8">
                           <div className="flex items-start justify-between mb-8">
                               <div className="flex items-center gap-4">
                                   <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/30 rounded-full flex items-center justify-center text-indigo-700 dark:text-indigo-300 font-bold text-lg">
                                       {viewingEmail.from_email[0].toUpperCase()}
                                   </div>
                                   <div>
                                       <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{viewingEmail.subject}</h1>
                                       <div className="flex items-center gap-2 text-sm text-slate-500">
                                           <span>{viewingEmail.from_email}</span>
                                           <span>&bull;</span>
                                           <span>{new Date(viewingEmail.date).toLocaleString()}</span>
                                       </div>
                                   </div>
                               </div>
                               <div className="flex items-center gap-2">
                                   <button onClick={() => setViewingEmail(null)} className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full"><X size={24} /></button>
                               </div>
                           </div>

                           <div className="flex items-center gap-2 mb-8">
                                <Badge color={getCategoryColor(viewingEmail.category)}>{viewingEmail.category}</Badge>
                                {viewingEmail.urgency === 'High' && <Badge color="red">Urgent</Badge>}
                                {viewingEmail.sentiment === 'Positive' && <Badge color="green">Positive Sentiment</Badge>}
                           </div>

                           <div className="prose dark:prose-invert max-w-none text-slate-800 dark:text-slate-200 leading-relaxed mb-12">
                               <p className="whitespace-pre-line">{viewingEmail.body}</p>
                           </div>

                           {/* Gemini Action Area */}
                           <div className="bg-slate-50 dark:bg-slate-900/50 rounded-xl p-6 border border-slate-200 dark:border-slate-800">
                               <div className="flex items-center gap-2 mb-4">
                                   <div className="p-1 bg-gradient-to-br from-blue-500 to-purple-500 text-white rounded shadow-sm">
                                       <Sparkles size={16} />
                                   </div>
                                   <span className="font-bold text-sm uppercase tracking-wide text-slate-600 dark:text-slate-300">Gemini Intelligence</span>
                               </div>
                               <div className="flex gap-2 flex-wrap">
                                   <button 
                                     onClick={() => handleGeminiAction('summarize', viewingEmail.body)}
                                     className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-medium hover:border-purple-400 hover:text-purple-600 dark:hover:text-purple-400 transition-all shadow-sm"
                                   >
                                       <Sparkles size={14} className="text-purple-500" />
                                       Summarize
                                   </button>
                                   <button 
                                     onClick={() => handleGeminiAction('actions', viewingEmail.body)}
                                     className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-medium hover:border-blue-400 hover:text-blue-600 dark:hover:text-blue-400 transition-all shadow-sm"
                                   >
                                       <ListChecks size={14} className="text-blue-500" />
                                       Extract Actions
                                   </button>
                                   <button 
                                     onClick={() => handleGeminiAction('reply', `Draft a reply to: ${viewingEmail.body}`)}
                                     className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-medium hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all shadow-sm"
                                   >
                                       <Reply size={14} className="text-indigo-500" />
                                       Draft Reply
                                   </button>
                               </div>

                               {(assistantOpen || assistantReply) && (
                                   <div className="mt-4 p-4 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm relative overflow-hidden">
                                       {isTyping && !assistantReply && (
                                           <div className="flex items-center gap-2 text-sm text-slate-500 animate-pulse">
                                               <Sparkles size={14} /> Gemini is thinking...
                                           </div>
                                       )}
                                       <div className="prose prose-sm dark:prose-invert max-w-none">
                                            <p className="whitespace-pre-wrap font-sans text-slate-700 dark:text-slate-300 leading-relaxed">{assistantReply}</p>
                                       </div>
                                   </div>
                               )}
                           </div>
                      </div>
                  )}
              </div>
          </div>
      )}
    </div>
  );
}
