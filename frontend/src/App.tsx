import { useState, useEffect } from "react";
import Home from "./Home";
import Chatbot from "./Chatbot";
import Resonance from "./components/Resonance";
import {
  Keyboard,
  MousePointer,
  Layout,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Brain,
  TrendingUp,
  Activity,
  Eye,
  Camera,
  HeartPulse
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

interface CVMetrics {
  posture_score: number;
  blink_rate: number;
  eye_fatigue_score: number;
  yawn_count: number;
  attention_score: number;
  screen_distance_cm: number;
  head_stability_score: number;
  presence_percentage: number;
  fatigue_index: number;
  engagement_index: number;
  wellness_score: number;
  head_tilt: number;
  neck_angle: number;
  slouch_detected: boolean;
  focused: boolean;
  face_present: boolean;
  distance_risk: number;
}

interface Metrics {
  keyboard: KeyboardMetrics;
  mouse: MouseMetrics;
  window: WindowMetrics;
  session: SessionMetrics;
  cv: CVMetrics;
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
  posture: number;
  attention: number;
  frustration: number;
  stress_expression: number;
}

interface Recommendation {
  title: string;
  reason: string;
}

interface ManagerAlert {
  alert: boolean;
  severity: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  reason: string;
}

interface ManagerEvent {
  timestamp: string;
  event_type: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  score: number;
  details: any;
}

interface SessionSummary {
  yawn_count: number;
  frustration_events: number;
  attention_drops: number;
  posture_violations: number;
  fatigue_spikes: number;
  cognitive_overload_events: number;
  wellness_alerts: number;
}

interface StressReport {
  timestamp: string;
  stress: StressLevel;
  contributors: StressContributors;
  recommendation: Recommendation;
  alert: ManagerAlert;
  recent_events: ManagerEvent[];
  session_summary: SessionSummary;
  metrics: Metrics;
}

interface TrendPoint {
  time: string;
  score: number;
  blinkRate?: number;
  fatigueIndex?: number;
  attentionScore?: number;
  wellnessScore?: number;
  frustrationScore?: number;
  stressScore?: number;
}

const BACKEND_URL = "http://127.0.0.1:8000";

function Dashboard() {
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
        const next = [...prev, { 
          time: timeLabel, 
          score: data.stress.score,
          blinkRate: data.metrics.cv?.blink_rate || 0,
          fatigueIndex: data.metrics.cv?.fatigue_index || 0,
          attentionScore: data.metrics.cv?.attention_score || 0,
          wellnessScore: data.metrics.cv?.wellness_score || 0,
          frustrationScore: data.metrics.cv?.frustration_score || 0,
          stressScore: data.stress.score
        }];
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
    const interval = setInterval(fetchReport, 2000);
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

  const getWellnessGaugeColor = (score: number, invert = false) => {
    if (invert) {
      if (score < 30) return "text-emerald-400 stroke-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      if (score < 60) return "text-amber-400 stroke-amber-400 bg-amber-500/10 border-amber-500/20";
      return "text-rose-400 stroke-rose-400 bg-rose-500/10 border-rose-500/20";
    } else {
      if (score > 75) return "text-emerald-400 stroke-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      if (score > 45) return "text-amber-400 stroke-amber-400 bg-amber-500/10 border-amber-500/20";
      return "text-rose-400 stroke-rose-400 bg-rose-500/10 border-rose-500/20";
    }
  };

  const renderMiniGauge = (title: string, value: number, invert = false, icon: React.ReactNode) => {
    const config = getWellnessGaugeColor(value, invert);
    const radius = 35;
    const circ = 2 * Math.PI * radius;
    const offset = circ - (value / 100) * circ;
    
    // Determine glow color class based on the text color from config
    const glowClass = config.includes("emerald") ? "drop-shadow-[0_0_8px_rgba(16,185,129,0.5)]" :
                      config.includes("amber") ? "drop-shadow-[0_0_8px_rgba(245,158,11,0.5)]" :
                      config.includes("orange") ? "drop-shadow-[0_0_8px_rgba(249,115,22,0.5)]" :
                      "drop-shadow-[0_0_8px_rgba(244,63,94,0.5)]";

    const isCritical = invert ? value >= 60 : value <= 45;
    
    return (
      <div className="glass-card p-5 flex flex-col items-center justify-between group">
        <div className="flex items-center gap-1.5 self-start mb-2 opacity-80 group-hover:opacity-100 transition-opacity">
          <div className={isCritical ? "animate-pulse-fast" : ""}>{icon}</div>
          <span className="text-[11px] font-bold text-slate-300 tracking-wider uppercase">LIVE {title}</span>
        </div>
        <div className="relative flex items-center justify-center my-2">
          <svg className="h-24 w-24 transform -rotate-90">
            <circle cx="48" cy="48" r={radius} stroke="#1e293b" strokeWidth="6" fill="transparent" />
            <circle 
              cx="48" 
              cy="48" 
              r={radius} 
              stroke="currentColor" 
              strokeWidth="6" 
              fill="transparent" 
              strokeDasharray={circ}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className={`transition-all duration-1000 ease-out ${config.split(' ')[1]} ${glowClass}`}
            />
          </svg>
          <div className="absolute text-center flex flex-col items-center">
            <span className={`text-2xl font-bold tracking-tight ${config.split(' ')[0]}`}>{value}%</span>
          </div>
        </div>
        <span className={`text-[10px] font-semibold mt-3 px-3 py-1 rounded-full ${config.split(' ')[2]} ${config.split(' ')[0]} border ${config.split(' ')[3]}`}>
          {invert ? (value < 30 ? "Optimal" : value < 60 ? "Moderate" : "Elevated") : (value > 75 ? "Excellent" : value > 45 ? "Fair" : "Poor")}
        </span>
      </div>
    );
  };

  const levelConfig = getStressLevelConfig(report.stress.level);

  const getEventEmojiAndLabel = (type: string) => {
    switch (type) {
      case "YAWN_DETECTED": return { emoji: "😴", label: "Yawn Detected" };
      case "HIGH_FRUSTRATION": return { emoji: "😠", label: "High Frustration" };
      case "LOW_ATTENTION": return { emoji: "👀", label: "Attention Drop" };
      case "ATTENTION_RECOVERED": return { emoji: "👁", label: "Attention Recovered" };
      case "POOR_POSTURE": return { emoji: "🧍", label: "Poor Posture" };
      case "POSTURE_RECOVERED": return { emoji: "💪", label: "Posture Recovered" };
      case "FATIGUE_SPIKE": return { emoji: "⚡", label: "Fatigue Spike" };
      case "COGNITIVE_OVERLOAD": return { emoji: "🧠", label: "Cognitive Overload" };
      case "FACE_NOT_PRESENT": return { emoji: "🚫", label: "Face Not Present" };
      case "WELLNESS_ALERT": return { emoji: "⚠", label: "Wellness Alert" };
      case "ENGAGEMENT_DROP": return { emoji: "📉", label: "Engagement Drop" };
      case "NEGATIVE_EMOTIONAL_STATE": return { emoji: "🌧", label: "Negative Emotional State" };
      default: return { emoji: "📝", label: type };
    }
  };

  const formatEventTime = (isoString: string) => {
    try {
      const d = new Date(isoString);
      const hh = String(d.getHours()).padStart(2, '0');
      const mm = String(d.getMinutes()).padStart(2, '0');
      return `${hh}:${mm}`;
    } catch {
      return "00:00";
    }
  };

  const eventCounts: { [key: string]: number } = {};
  (report.recent_events || []).forEach(evt => {
    const { label } = getEventEmojiAndLabel(evt.event_type);
    eventCounts[label] = (eventCounts[label] || 0) + 1;
  });
  const eventFrequencyData = Object.keys(eventCounts).map(name => ({
    name,
    count: eventCounts[name]
  })).sort((a, b) => b.count - a.count);
  
  // Contributors format for Recharts
  const contributorsData = [
    { name: "Typing Frustration", value: report.contributors.typing },
    { name: "Context Switching", value: report.contributors.context_switching },
    { name: "Mouse Activity", value: report.contributors.mouse_activity },
    { name: "Fatigue Level", value: report.contributors.fatigue },
    { name: "Poor Posture", value: report.contributors.posture },
    { name: "Low Attention", value: report.contributors.attention },
    { name: "Frustration Signals", value: report.contributors.frustration },
    { name: "Stress Expression", value: report.contributors.stress_expression }
  ];

  const COLORS = ["#818cf8", "#fbbf24", "#f43f5e", "#10b981", "#c084fc", "#facc15", "#fb923c", "#38bdf8"];

  // SVG circular gauge calculation
  const gaugeRadius = 80;
  const gaugeCircumference = 2 * Math.PI * gaugeRadius;
  const strokeDashoffset = gaugeCircumference - (report.stress.score / 100) * gaugeCircumference;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30 selection:text-indigo-200">
      <Resonance />
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
              <span className="text-slate-300 font-mono">2s</span>
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

        {/* Manager Alerts System Section */}
        <section id="manager-alerts-section" className="mb-8">
          <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-rose-400" />
                <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase">Manager Alert System</h2>
              </div>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                report.alert?.alert 
                  ? "bg-rose-500/10 text-rose-400 border-rose-500/20" 
                  : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
              }`}>
                {report.alert?.alert ? `Active - ${report.alert.severity}` : "Inactive"}
              </span>
            </div>
            {report.alert?.alert ? (
              <div className="p-4 rounded-lg bg-rose-950/20 border border-rose-500/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <span className="text-[10px] uppercase font-bold text-rose-400 tracking-wider">Severity: {report.alert.severity}</span>
                  <p className="text-sm text-slate-200 mt-1">{report.alert.reason}</p>
                </div>
                <div className="text-xs text-rose-300 font-medium whitespace-nowrap bg-rose-500/10 px-3 py-1.5 rounded border border-rose-500/20 self-start md:self-auto">
                  Action Recommended
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-slate-900/10 border border-slate-800 text-center text-xs text-slate-500">
                All wellness metrics are within normal parameters. No active alerts.
              </div>
            )}
          </div>
        </section>

        {/* Dashboard Grid Row 4: Workplace Wellness Analytics (CV) */}
        <section className="mt-8">
          <div className="flex items-center gap-2 mb-4">
            <Camera className="h-5 w-5 text-indigo-400" />
            <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase">Workplace Wellness Analytics</h2>
          </div>
          
          {/* Session Summary Counts */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-8">
            <div className="glass-card p-5 flex flex-col justify-between group">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Session Yawns</span>
              <p className="text-4xl font-bold mt-3 text-amber-400 text-glow-amber group-hover:scale-105 transition-transform transform origin-left">{report.session_summary?.yawn_count || 0}</p>
            </div>
            <div className="glass-card p-5 flex flex-col justify-between group">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Total Frustrations</span>
              <p className="text-4xl font-bold mt-3 text-orange-400 text-glow-orange group-hover:scale-105 transition-transform transform origin-left">{report.session_summary?.frustration_events || 0}</p>
            </div>
            <div className="glass-card p-5 flex flex-col justify-between group">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Attention Drops</span>
              <p className="text-4xl font-bold mt-3 text-indigo-400 text-glow-indigo group-hover:scale-105 transition-transform transform origin-left">{report.session_summary?.attention_drops || 0}</p>
            </div>
            <div className="glass-card p-5 flex flex-col justify-between group">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Posture Issues</span>
              <p className="text-4xl font-bold mt-3 text-emerald-400 text-glow-emerald group-hover:scale-105 transition-transform transform origin-left">{report.session_summary?.posture_violations || 0}</p>
            </div>
            <div className="glass-card p-5 flex flex-col justify-between group">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Fatigue Spikes</span>
              <p className="text-4xl font-bold mt-3 text-rose-400 text-glow-rose group-hover:scale-105 transition-transform transform origin-left">{report.session_summary?.fatigue_spikes || 0}</p>
            </div>
            <div className="glass-card border-red-500/30 p-5 flex flex-col justify-between group">
              <span className="text-[10px] uppercase font-bold text-red-400 tracking-wider">Wellness Alerts</span>
              <p className="text-4xl font-bold mt-3 text-red-500 font-mono tracking-tight text-glow-red animate-pulse">{report.session_summary?.wellness_alerts || 0}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-12">
            {renderMiniGauge("Stress", report.stress.score, true, <HeartPulse className="h-5 w-5 text-rose-400" />)}
            {renderMiniGauge("Frustration", report.metrics.cv?.frustration_score || 0, true, <AlertTriangle className="h-5 w-5 text-orange-400" />)}
            {renderMiniGauge("Overload", report.metrics.cv?.cognitive_overload_score || 0, true, <Brain className="h-5 w-5 text-purple-400" />)}
            {renderMiniGauge("Fatigue", report.metrics.cv?.fatigue_index || 0, true, <Clock className="h-5 w-5 text-amber-400" />)}
            {renderMiniGauge("Engagement", report.metrics.cv?.engagement_score || 0, false, <Activity className="h-5 w-5 text-indigo-400" />)}
            {renderMiniGauge("Wellness", report.metrics.cv?.wellness_score || 0, false, <CheckCircle2 className="h-5 w-5 text-emerald-400" />)}
          </div>

          {/* Behavioral Timeline Widget */}
          <div className="glass-card p-6 mb-12">
            <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-6 flex items-center gap-2">
              <Clock className="h-4 w-4 text-indigo-400" /> Event Timeline
            </h3>
            <div className="max-h-[400px] overflow-y-auto pr-4 scrollbar-thin scrollbar-thumb-slate-800 relative">
              {/* Vertical connecting line */}
              <div className="absolute left-[27px] top-4 bottom-4 w-0.5 bg-slate-800/50 rounded-full"></div>
              
              {(!report.recent_events || report.recent_events.length === 0) ? (
                <p className="text-xs text-slate-500 text-center py-6">No events logged yet for this session.</p>
              ) : (
                <div className="space-y-6">
                  {report.recent_events.map((evt, idx) => {
                    const info = getEventEmojiAndLabel(evt.event_type);
                    const timeStr = formatEventTime(evt.timestamp);
                    const isCritical = evt.severity === "CRITICAL" || evt.severity === "HIGH";
                    
                    const sevColor = evt.severity === "CRITICAL" ? "bg-rose-500/10 text-rose-400 border-rose-500/30 drop-shadow-[0_0_5px_rgba(244,63,94,0.5)]" :
                                     evt.severity === "HIGH" ? "bg-orange-500/10 text-orange-400 border-orange-500/30 drop-shadow-[0_0_5px_rgba(249,115,22,0.5)]" :
                                     evt.severity === "MEDIUM" ? "bg-amber-500/10 text-amber-400 border-amber-500/20" :
                                     "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
                                     
                    const nodeColor = evt.severity === "CRITICAL" ? "bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.8)]" :
                                      evt.severity === "HIGH" ? "bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.8)]" :
                                      evt.severity === "MEDIUM" ? "bg-amber-500" :
                                      "bg-emerald-500";

                    return (
                      <div key={`${evt.timestamp}-${idx}`} className="relative flex items-start gap-6 group animate-in fade-in slide-in-from-right-4 duration-500 fill-mode-both" style={{ animationDelay: `${idx * 50}ms` }}>
                        {/* Timeline Node */}
                        <div className="relative z-10 flex flex-col items-center mt-1">
                          <div className={`h-3 w-3 rounded-full border-[3px] border-slate-950 ${nodeColor} ${isCritical ? 'animate-pulse' : ''}`}></div>
                        </div>
                        
                        {/* Event Card */}
                        <div className="flex-1 bg-slate-950/50 hover:bg-slate-900/80 border border-slate-800/50 hover:border-slate-700 rounded-xl p-4 transition-all duration-300">
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xl leading-none">{info.emoji}</span>
                              <span className="text-sm font-bold text-slate-200 tracking-wide">{info.label}</span>
                            </div>
                            <span className="text-[10px] font-mono text-slate-500 bg-slate-900 px-2 py-1 rounded-md">{timeStr}</span>
                          </div>
                          <div className="flex items-center justify-between mt-3">
                            <div className="flex items-center gap-2 flex-wrap">
                              {evt.details && Object.keys(evt.details).length > 0 && (
                                Object.entries(evt.details).map(([k, v]) => (
                                  <span key={k} className="text-[10px] text-slate-400 font-mono bg-slate-900/50 border border-slate-800 px-2 py-0.5 rounded">
                                    <span className="opacity-60">{k}:</span> <span className="text-slate-300">{v as string}</span>
                                  </span>
                                ))
                              )}
                            </div>
                            <span className={`text-[9px] font-black px-2.5 py-1 rounded uppercase tracking-widest border ${sevColor}`}>
                              {evt.severity}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-5 w-5 text-indigo-400" />
            <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase">Wellness Trends</h2>
          </div>

          {/* Wellness Trend Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Stress Trend */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-5">
              <h3 className="text-xs font-semibold tracking-wider text-slate-400 uppercase mb-4">Stress Trend</h3>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorStress" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#818cf8" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b", borderRadius: "8px" }} />
                    <Area type="monotone" dataKey="stressScore" stroke="#818cf8" fillOpacity={1} fill="url(#colorStress)" name="Stress" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Fatigue Trend */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-5">
              <h3 className="text-xs font-semibold tracking-wider text-slate-400 uppercase mb-4">Fatigue Trend</h3>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorFatigue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b", borderRadius: "8px" }} />
                    <Area type="monotone" dataKey="fatigueIndex" stroke="#f43f5e" fillOpacity={1} fill="url(#colorFatigue)" name="Fatigue" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Frustration Trend */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-5">
              <h3 className="text-xs font-semibold tracking-wider text-slate-400 uppercase mb-4">Frustration Trend</h3>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorFrustration" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#fb923c" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#fb923c" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b", borderRadius: "8px" }} />
                    <Area type="monotone" dataKey="frustrationScore" stroke="#fb923c" fillOpacity={1} fill="url(#colorFrustration)" name="Frustration" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Attention Trend */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-5">
              <h3 className="text-xs font-semibold tracking-wider text-slate-400 uppercase mb-4">Attention Trend</h3>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorAttention" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#818cf8" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b", borderRadius: "8px" }} />
                    <Area type="monotone" dataKey="attentionScore" stroke="#818cf8" fillOpacity={1} fill="url(#colorAttention)" name="Attention" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Wellness Trend */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-5">
              <h3 className="text-xs font-semibold tracking-wider text-slate-400 uppercase mb-4">Wellness Trend</h3>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorWellness" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b", borderRadius: "8px" }} />
                    <Area type="monotone" dataKey="wellnessScore" stroke="#10b981" fillOpacity={1} fill="url(#colorWellness)" name="Wellness" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Event Frequency Chart */}
            <div className="rounded-xl border border-slate-900 bg-slate-900/30 p-5">
              <h3 className="text-xs font-semibold tracking-wider text-slate-400 uppercase mb-4">Event Frequency</h3>
              <div className="h-[200px]">
                {eventFrequencyData.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-xs text-slate-500">
                    No events in this session to graph
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={eventFrequencyData} layout="vertical" margin={{ left: -10, right: 10, top: 5, bottom: 5 }}>
                      <XAxis type="number" hide />
                      <YAxis
                        dataKey="name"
                        type="category"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: "#94a3b8", fontSize: 9 }}
                        width={90}
                      />
                      <Tooltip
                        cursor={{ fill: "rgba(30, 41, 59, 0.4)" }}
                        contentStyle={{
                          backgroundColor: "#020617",
                          borderColor: "#1e293b",
                          borderRadius: "8px",
                          color: "#fff",
                          fontSize: "11px"
                        }}
                      />
                      <Bar dataKey="count" fill="#38bdf8" radius={[0, 4, 4, 0]} barSize={10} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>
        </section>
        
      </main>
      <Chatbot />
    </div>
  );
}

export default function App() {
  const [view, setView] = useState<'home' | 'dashboard'>('home');

  if (view === 'home') {
    return <Home onLaunch={() => setView('dashboard')} />;
  }

  return <Dashboard />;
}
