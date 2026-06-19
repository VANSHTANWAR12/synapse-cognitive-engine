import { useState, useEffect } from "react";
import {
  Keyboard,
  MousePointer,
  Layout,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Brain,
  TrendingUp
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  Cell
} from "recharts";

// TypeScript Definitions
interface KeyboardMetrics {
  keys_per_min: number;
  backspaces_per_min: number;
  avg_pause: number;
  long_pause_count: number;
  typing_variance: number;
}

interface MouseMetrics {
  mouse_speed: number;
  click_rate: number;
  movement_distance: number;
}

interface WindowMetrics {
  active_window: string | null;
  window_switches: number;
}

interface SessionMetrics {
  session_minutes: number;
  break_count: number;
  time_since_last_break: number;
}

interface Metrics {
  keyboard: KeyboardMetrics;
  mouse: MouseMetrics;
  window: WindowMetrics;
  session: SessionMetrics;
}

interface StressLevel {
  score: number;
  level: string;
}

interface StressContributors {
  typing: number;
  context_switching: number;
  mouse_activity: number;
  fatigue: number;
}

interface Recommendation {
  title: string;
  reason: string;
}

interface StressReport {
  timestamp: string;
  stress: StressLevel;
  contributors: StressContributors;
  recommendation: Recommendation;
  metrics: Metrics;
}

interface TrendPoint {
  time: string;
  score: number;
}

const BACKEND_URL = "http://127.0.0.1:8000";

export default function App() {
  const [report, setReport] = useState<StressReport | null>(null);
  const [trendData, setTrendData] = useState<TrendPoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Poll API for new report every 5 seconds
  const fetchReport = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/report`);
      if (!response.ok) {
        throw new Error(`API returned status ${response.status}`);
      }
      const data: StressReport = await response.json();
      setReport(data);
      setError(null);

      // Append to trend array (limit to last 100 points)
      const timeLabel = new Date(data.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      });

      setTrendData((prev) => {
        const next = [...prev, { time: timeLabel, score: data.stress.score }];
        if (next.length > 100) {
          return next.slice(next.length - 100);
        }
        return next;
      });
    } catch (err: any) {
      console.error("Polling error:", err);
      setError(err.message || "Failed to fetch stress report");
    }
  };

  useEffect(() => {
    fetchReport(); // initial fetch
    const interval = setInterval(fetchReport, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!report) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-slate-950 text-slate-100">
        <div className="flex flex-col items-center gap-4">
          <Brain className="h-12 w-12 animate-pulse text-indigo-500" />
          <p className="text-lg font-medium text-slate-400">Connecting to Synapse Engine...</p>
          {error && <p className="text-sm text-red-400 mt-2 font-mono">{error}</p>}
        </div>
      </div>
    );
  }

  // Stress Level Colors & UI mappings
  const getStressLevelConfig = (level: string) => {
    const norm = level.toLowerCase();
    if (norm.includes("relaxed")) {
      return {
        color: "text-emerald-400",
        border: "border-emerald-500/20",
        bg: "bg-emerald-500/10",
        gaugeColor: "#10b981"
      };
    }
    if (norm.includes("mild")) {
      return {
        color: "text-amber-400",
        border: "border-amber-500/20",
        bg: "bg-amber-500/10",
        gaugeColor: "#f59e0b"
      };
    }
    if (norm.includes("high")) {
      return {
        color: "text-orange-400",
        border: "border-orange-500/20",
        bg: "bg-orange-500/10",
        gaugeColor: "#f97316"
      };
    }
    return {
      color: "text-rose-400",
      border: "border-rose-500/20",
      bg: "bg-rose-500/10",
      gaugeColor: "#f43f5e"
    };
  };

  const levelConfig = getStressLevelConfig(report.stress.level);
  
  // Contributors format for Recharts
  const contributorsData = [
    { name: "Typing Frustration", value: report.contributors.typing },
    { name: "Context Switching", value: report.contributors.context_switching },
    { name: "Mouse Activity", value: report.contributors.mouse_activity },
    { name: "Fatigue Level", value: report.contributors.fatigue }
  ];

  const COLORS = ["#818cf8", "#fbbf24", "#f43f5e", "#10b981"];

  // SVG circular gauge calculation
  const gaugeRadius = 80;
  const gaugeCircumference = 2 * Math.PI * gaugeRadius;
  const strokeDashoffset = gaugeCircumference - (report.stress.score / 100) * gaugeCircumference;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Top Banner / Navbar */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/30">
              <Brain className="h-5 w-5 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white">SYNAPSE</h1>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Cognitive Intelligence</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {error && (
              <span className="flex items-center gap-1 text-xs text-rose-400 bg-rose-950/30 border border-rose-500/20 px-2 py-1 rounded">
                <AlertTriangle className="h-3 w-3" /> Connection Interrupted
              </span>
            )}
            <div className="flex items-center gap-2 rounded-full bg-slate-900 border border-slate-800 px-3.5 py-1.5 text-xs text-slate-400">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span>LIVE POLLING</span>
              <span className="text-slate-600 font-mono">|</span>
              <span className="text-slate-300 font-mono">5s</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="mx-auto max-w-7xl px-6 py-8">
        
        {/* KPI Top Cards */}
        <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="rounded-xl border border-slate-900 bg-slate-900/50 p-5">
            <p className="text-sm font-medium text-slate-400">Stress Score</p>
            <div className="flex items-baseline justify-between mt-2">
              <p className="text-3xl font-semibold tracking-tight text-white">{report.stress.score}%</p>
              <span className={`text-xs font-semibold px-2 py-1 rounded ${levelConfig.bg} ${levelConfig.color} border ${levelConfig.border}`}>
                {report.stress.level}
              </span>
            </div>
          </div>

          <div className="rounded-xl border border-slate-900 bg-slate-900/50 p-5">
            <p className="text-sm font-medium text-slate-400">Active Window</p>
            <div className="flex items-center justify-between mt-2 gap-4">
              <p className="text-lg font-medium text-white truncate max-w-[200px]" title={report.metrics.window.active_window || "None"}>
                {report.metrics.window.active_window || "System Idle"}
              </p>
              <Layout className="h-5 w-5 text-indigo-400 shrink-0" />
            </div>
          </div>

          <div className="rounded-xl border border-slate-900 bg-slate-900/50 p-5">
            <p className="text-sm font-medium text-slate-400">Keys per Minute</p>
            <div className="flex items-baseline justify-between mt-2">
              <p className="text-3xl font-semibold tracking-tight text-white">{report.metrics.keyboard.keys_per_min}</p>
              <Keyboard className="h-5 w-5 text-slate-500" />
            </div>
          </div>

          <div className="rounded-xl border border-slate-900 bg-slate-900/50 p-5">
            <p className="text-sm font-medium text-slate-400">Work Duration</p>
            <div className="flex items-baseline justify-between mt-2">
              <p className="text-3xl font-semibold tracking-tight text-white">{report.metrics.session.session_minutes}m</p>
              <Clock className="h-5 w-5 text-slate-500" />
            </div>
          </div>
        </section>

        {/* Dashboard Grid Row 1: Stress Gauge + Recommendation + Contributors */}
        <section className="grid grid-cols-1 gap-8 lg:grid-cols-3 mb-8">
          
          {/* Circular Gauge */}
          <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-6 flex flex-col items-center justify-center">
            <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-6 self-start">Live Stress Index</h2>
            <div className="relative flex items-center justify-center">
              <svg className="h-44 w-44 transform -rotate-90">
                {/* Background Circle */}
                <circle
                  cx="88"
                  cy="88"
                  r={gaugeRadius}
                  stroke="#1e293b"
                  strokeWidth="14"
                  fill="transparent"
                />
                {/* Value Circle */}
                <circle
                  cx="88"
                  cy="88"
                  r={gaugeRadius}
                  stroke={levelConfig.gaugeColor}
                  strokeWidth="14"
                  fill="transparent"
                  strokeDasharray={gaugeCircumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              {/* Inner Label */}
              <div className="absolute text-center">
                <span className="text-4xl font-extrabold tracking-tight text-white">{report.stress.score}%</span>
                <span className={`block text-xs font-semibold uppercase mt-1 tracking-wide ${levelConfig.color}`}>
                  {report.stress.level}
                </span>
              </div>
            </div>
          </div>

          {/* Recommendation Card */}
          <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-6 flex flex-col justify-between">
            <div>
              <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-4">AI Engine Suggestion</h2>
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl ${levelConfig.bg} ${levelConfig.color} border ${levelConfig.border}`}>
                  {report.recommendation.title === "Keep Working" ? (
                    <CheckCircle2 className="h-6 w-6" />
                  ) : (
                    <AlertTriangle className="h-6 w-6" />
                  )}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white leading-tight">{report.recommendation.title}</h3>
                  <p className="text-sm text-slate-400 mt-1.5 leading-relaxed">{report.recommendation.reason}</p>
                </div>
              </div>
            </div>
            
            <div className="mt-6 border-t border-slate-900 pt-4 text-xs text-slate-500">
              Analysis based on keyboard variance, active window switches, and session break interval metrics.
            </div>
          </div>

          {/* Contributors Bar Chart */}
          <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-6 flex flex-col">
            <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-4">Stress Contributors</h2>
            <div className="flex-1 min-h-[160px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={contributorsData} layout="vertical" margin={{ left: -10, right: 10, top: 5, bottom: 5 }}>
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis
                    dataKey="name"
                    type="category"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#94a3b8", fontSize: 11 }}
                    width={110}
                  />
                  <Tooltip
                    cursor={{ fill: "rgba(30, 41, 59, 0.4)" }}
                    contentStyle={{
                      backgroundColor: "#020617",
                      borderColor: "#1e293b",
                      borderRadius: "8px",
                      color: "#fff"
                    }}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={12}>
                    {contributorsData.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        {/* Dashboard Grid Row 2: Live Stress Trend */}
        <section className="rounded-xl border border-slate-900 bg-slate-900/30 p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-indigo-400" />
              <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase">Live Stress Trend (Last 100 points)</h2>
            </div>
            {trendData.length > 0 && (
              <span className="text-xs text-slate-500 font-mono">
                Showing {trendData.length} data point{trendData.length > 1 ? "s" : ""}
              </span>
            )}
          </div>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 10, right: 5, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="time"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  dy={10}
                />
                <YAxis
                  domain={[0, 100]}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  dx={-10}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#020617",
                    borderColor: "#1e293b",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "12px"
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="score"
                  stroke="#6366f1"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorScore)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Dashboard Grid Row 3: Raw Metric Cards */}
        <section>
          <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-4">Raw Metric Monitors</h2>
          
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
            
            {/* Keyboard Metrics */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/20 p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Keyboard className="h-4 w-4 text-indigo-400" />
                  <h3 className="text-sm font-bold text-white">Keyboard Activity</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Keys / Min</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.keyboard.keys_per_min}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Backspaces / Min</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.keyboard.backspaces_per_min}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Avg Pause Time</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.keyboard.avg_pause}s</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Long Pauses ({">"}5s)</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.keyboard.long_pause_count}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Typing Variance</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.keyboard.typing_variance}s</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Mouse Metrics */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/20 p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <MousePointer className="h-4 w-4 text-amber-400" />
                  <h3 className="text-sm font-bold text-white">Mouse Activity</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Mouse Speed</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.mouse.mouse_speed} px/s</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Click Rate</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.mouse.click_rate} /min</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Movement Dist</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.mouse.movement_distance} px</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Window Metrics */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/20 p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Layout className="h-4 w-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Window Switcher</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Switches / Min</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.window.window_switches}</span>
                  </div>
                  <div className="text-xs pt-1.5 border-t border-slate-900">
                    <span className="text-slate-400 block mb-1">Active Window:</span>
                    <span className="text-white block font-medium break-all line-clamp-3">
                      {report.metrics.window.active_window || "None"}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Session Metrics */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/20 p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Clock className="h-4 w-4 text-rose-400" />
                  <h3 className="text-sm font-bold text-white">Session Timer</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Session Minutes</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.session.session_minutes} min</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Break Count</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.session.break_count}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Time Since Break</span>
                    <span className="font-mono text-white font-semibold">{report.metrics.session.time_since_last_break} min</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </section>
        
      </main>
    </div>
  );
}
