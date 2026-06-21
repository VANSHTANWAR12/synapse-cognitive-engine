import { ArrowRight, Brain, Activity, Shield, Sparkles } from 'lucide-react';

interface HomeProps {
  onLaunch: () => void;
}

export default function Home({ onLaunch }: HomeProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30 selection:text-indigo-200 overflow-hidden relative">
      
      {/* Background Effects */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-600/10 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border border-indigo-500/5 rounded-full" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-indigo-500/10 rounded-full" />
      </div>

      {/* Navbar */}
      <nav className="relative z-10 border-b border-white/5 bg-slate-950/50 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/30 shadow-[0_0_15px_rgba(99,102,241,0.2)]">
              <Brain className="h-5 w-5 text-indigo-400" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">SYNAPSE</span>
          </div>
          <button 
            onClick={onLaunch}
            className="px-5 py-2 text-sm font-medium text-white bg-white/5 hover:bg-white/10 border border-white/10 rounded-full transition-colors"
          >
            Enter Workspace
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-6 text-center">
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-200 to-slate-500 max-w-4xl leading-tight mb-6">
          The Emotion-Aware <br className="hidden md:block" /> Workspace
        </h1>
        
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10 leading-relaxed">
          An operating system that actively cures burnout in real-time. Synapse uses zero-click tracking to trigger automatic sensory resets.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 mb-20">
          <button 
            onClick={onLaunch}
            className="group relative inline-flex items-center gap-2 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-full shadow-[0_0_40px_rgba(99,102,241,0.4)] transition-all overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
            <span>Launch Engine</span>
            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </button>
          <a 
            href="http://127.0.0.1:8000/mindsentry/index.html"
            target="_blank"
            rel="noopener noreferrer"
            className="group relative inline-flex items-center gap-2 px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-full border border-slate-700 transition-all overflow-hidden"
          >
            <span>Open MindSentry</span>
            <Brain className="h-4 w-4 text-indigo-400 group-hover:scale-110 transition-transform" />
          </a>
          <a 
            href="https://app.notion.com/p/StudentOS-30d5d0ef8a0283d38d0301a888ce1ee0?pvs=13"
            target="_blank"
            rel="noopener noreferrer"
            className="group relative inline-flex items-center gap-2 px-8 py-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-full border border-slate-850 transition-all overflow-hidden"
          >
            <span>Notion OS</span>
            <Sparkles className="h-4 w-4 text-amber-400 group-hover:rotate-12 transition-transform" />
          </a>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto text-left">
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-sm hover:bg-slate-900/60 transition-colors">
            <div className="h-12 w-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-4">
              <Activity className="h-6 w-6 text-blue-400" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Zero-Click Detection</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Reads facial tension and erratic typing patterns locally to map your cognitive load without interrupting your flow state.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-sm hover:bg-slate-900/60 transition-colors">
            <div className="h-12 w-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-4">
              <Brain className="h-6 w-6 text-emerald-400" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Sensory Reset</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Instead of warnings, Synapse alters the environment, cross-fading ambient focus music and shifting screen warmth.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-sm hover:bg-slate-900/60 transition-colors">
            <div className="h-12 w-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-4">
              <Shield className="h-6 w-6 text-rose-400" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Privacy First AI</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Video is processed locally via Python. Zero privacy breaches. Only anonymized integer scores are synced.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
