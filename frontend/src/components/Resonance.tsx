import React, { useState, useEffect, useRef } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { X, HeartPulse, Activity } from 'lucide-react';

interface RPPGData {
  time: string;
  timestamp: number;
  hr: number;
  rmssd: number;
}

export default function Resonance() {
  const [dataHistory, setDataHistory] = useState<RPPGData[]>([]);
  const [isActive, setIsActive] = useState(false);
  const [interventionStartTime, setInterventionStartTime] = useState<number | null>(null);
  const [slowBreathing, setSlowBreathing] = useState(false);
  const [hasBeenDismissed, setHasBeenDismissed] = useState(false);
  
  // Audio context refs
  const audioCtxRef = useRef<AudioContext | null>(null);
  const leftOscRef = useRef<OscillatorNode | null>(null);
  const rightOscRef = useRef<OscillatorNode | null>(null);

  // WebSocket ref
  const wsRef = useRef<WebSocket | null>(null);

  const currentRMSSD = dataHistory.length > 0 ? dataHistory[dataHistory.length - 1].rmssd : 0;
  const currentHR = dataHistory.length > 0 ? dataHistory[dataHistory.length - 1].hr : 0;

  useEffect(() => {
    // Connect to WebSocket
    const connectWS = () => {
      const ws = new WebSocket("ws://127.0.0.1:8000/ws/resonance");
      wsRef.current = ws;

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.hr === 0 && data.rmssd === 0) return; // Ignore empty values initially
        
        const now = Date.now();
        const timeLabel = new Date(now).toLocaleTimeString([], { minute: "2-digit", second: "2-digit" });
        
        const newDataPoint: RPPGData = {
          time: timeLabel,
          timestamp: now,
          hr: Math.round(data.hr),
          rmssd: Math.round(data.rmssd * 10) / 10
        };

        setDataHistory(prev => {
          const next = [...prev, newDataPoint];
          // Keep last 3 minutes (approx 90 points if updated every 2s)
          if (next.length > 90) return next.slice(next.length - 90);
          return next;
        });
      };

      ws.onclose = () => {
        setTimeout(connectWS, 5000); // Reconnect
      };
    };

    connectWS();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Check for trigger condition
  useEffect(() => {
    if (dataHistory.length < 3 || isActive || hasBeenDismissed) return;
    
    const last3 = dataHistory.slice(-3);
    const isDeclining = last3[0].rmssd > last3[1].rmssd && last3[1].rmssd > last3[2].rmssd;
    
    if (last3[2].rmssd < 25 || isDeclining) {
      triggerIntervention();
    }
  }, [dataHistory, isActive, hasBeenDismissed]);

  // Handle 90 second lack of improvement
  useEffect(() => {
    if (!isActive || !interventionStartTime) return;
    
    const checkImprovement = setInterval(() => {
      const elapsedSeconds = (Date.now() - interventionStartTime) / 1000;
      if (elapsedSeconds > 90 && !slowBreathing) {
        if (currentRMSSD < 30) { // Still low
          setSlowBreathing(true);
          updateBinauralBeats(true);
        }
      }
    }, 5000);

    return () => clearInterval(checkImprovement);
  }, [isActive, interventionStartTime, slowBreathing, currentRMSSD]);

  const triggerIntervention = () => {
    setIsActive(true);
    setInterventionStartTime(Date.now());
    setSlowBreathing(false);
    startBinauralBeats(false);
  };

  const closeIntervention = () => {
    setIsActive(false);
    setInterventionStartTime(null);
    stopBinauralBeats();
    setHasBeenDismissed(true);
  };

  const startBinauralBeats = (slow: boolean) => {
    if (!audioCtxRef.current) {
      const Ctx = window.AudioContext || (window as any).webkitAudioContext;
      audioCtxRef.current = new Ctx();
    }
    const ctx = audioCtxRef.current;
    if (ctx.state === 'suspended') ctx.resume();

    // Carrier
    const carrierFreq = 200;
    const offset = slow ? 6 : 10; // 10Hz Alpha or 6Hz Theta

    leftOscRef.current = ctx.createOscillator();
    rightOscRef.current = ctx.createOscillator();

    const leftPan = ctx.createStereoPanner();
    leftPan.pan.value = -1;
    const rightPan = ctx.createStereoPanner();
    rightPan.pan.value = 1;

    const gainNode = ctx.createGain();
    gainNode.gain.value = 0.1; // Low volume

    leftOscRef.current.type = 'sine';
    leftOscRef.current.frequency.value = carrierFreq;
    leftOscRef.current.connect(leftPan);
    leftPan.connect(gainNode);

    rightOscRef.current.type = 'sine';
    rightOscRef.current.frequency.value = carrierFreq + offset;
    rightOscRef.current.connect(rightPan);
    rightPan.connect(gainNode);

    gainNode.connect(ctx.destination);

    leftOscRef.current.start();
    rightOscRef.current.start();
  };

  const updateBinauralBeats = (slow: boolean) => {
    if (rightOscRef.current && audioCtxRef.current) {
      const targetFreq = 200 + (slow ? 6 : 10);
      rightOscRef.current.frequency.exponentialRampToValueAtTime(targetFreq, audioCtxRef.current.currentTime + 5);
    }
  };

  const stopBinauralBeats = () => {
    if (leftOscRef.current) leftOscRef.current.stop();
    if (rightOscRef.current) rightOscRef.current.stop();
    if (audioCtxRef.current) audioCtxRef.current.close();
    audioCtxRef.current = null;
  };

  // Color interpolation based on RMSSD (red for low, teal for high)
  const getInterpolatedColor = (rmssd: number) => {
    const minVal = 10;
    const maxVal = 50;
    const clamped = Math.max(minVal, Math.min(maxVal, rmssd));
    const ratio = (clamped - minVal) / (maxVal - minVal);
    
    // Crimson: 220, 20, 60
    // Teal: 0, 128, 128
    const r = Math.round(220 + ratio * (0 - 220));
    const g = Math.round(20 + ratio * (128 - 20));
    const b = Math.round(60 + ratio * (128 - 60));
    return `rgb(${r},${g},${b})`;
  };

  const currentColor = getInterpolatedColor(currentRMSSD);
  
  // Animation duration
  // Normal: 10s (4s in, 1s hold, 5s out) -> 6 breaths/min
  // Slow: 10.9s -> 5.5 breaths/min
  const animDuration = slowBreathing ? '10.9s' : '10s';

  if (!isActive) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-slate-950 flex flex-col items-center justify-center overflow-hidden">
      {/* Background radial gradient matches color slightly */}
      <div 
        className="absolute inset-0 opacity-20 transition-colors duration-1000"
        style={{ background: `radial-gradient(circle at center, ${currentColor} 0%, transparent 70%)` }}
      />
      
      <button 
        onClick={closeIntervention}
        className="absolute top-6 right-6 p-2 rounded-full bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
      >
        <X className="w-6 h-6" />
      </button>

      <div className="absolute top-8 text-center">
        <h2 className="text-2xl font-bold tracking-widest text-slate-200 uppercase mb-2">Resonance Module</h2>
        <p className="text-slate-400 font-mono text-sm tracking-wide">
          {slowBreathing ? "Theta state activated (6Hz). Slow down." : "Alpha state active (10Hz). Breathe."}
        </p>
      </div>

      {/* Breathing Circle */}
      <div className="relative flex items-center justify-center my-12" style={{ width: '300px', height: '300px' }}>
        <style>
          {`
            @keyframes breathe {
              0% { transform: scale(0.6); opacity: 0.5; }
              40% { transform: scale(1.1); opacity: 0.9; } /* 4s inhale */
              50% { transform: scale(1.1); opacity: 0.9; } /* 1s hold */
              100% { transform: scale(0.6); opacity: 0.5; } /* 5s exhale */
            }
          `}
        </style>
        
        {/* The pulsing circle */}
        <div 
          className="absolute rounded-full blur-[8px]"
          style={{
            width: '100%',
            height: '100%',
            backgroundColor: currentColor,
            animation: `breathe ${animDuration} ease-in-out infinite`,
            transition: 'background-color 2s ease'
          }}
        />

        {/* Inner Metrics Overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center z-10 text-white drop-shadow-lg pointer-events-none">
          <div className="flex items-center gap-2 mb-1">
            <HeartPulse className="w-5 h-5" />
            <span className="text-3xl font-bold">{currentHR} <span className="text-sm font-normal opacity-80">BPM</span></span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 opacity-80" />
            <span className="text-xl font-semibold tracking-tight">{currentRMSSD} <span className="text-xs font-normal opacity-80">ms</span></span>
          </div>
        </div>
      </div>

      {/* Recharts AreaChart */}
      <div className="absolute bottom-8 w-full max-w-4xl px-8 h-[200px]">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 text-center">
          HRV (RMSSD) History
        </div>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={dataHistory}>
            <defs>
              <linearGradient id="colorRmssd" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={currentColor} stopOpacity={0.6}/>
                <stop offset="95%" stopColor={currentColor} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis dataKey="time" hide />
            <YAxis domain={['auto', 'auto']} hide />
            <Tooltip 
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc', borderRadius: '8px' }}
              itemStyle={{ color: currentColor }}
            />
            {interventionStartTime && (
              <ReferenceLine 
                x={dataHistory.find(d => d.timestamp >= interventionStartTime)?.time || ''} 
                stroke="#64748b" 
                strokeDasharray="3 3" 
                label={{ position: 'top', value: 'Intervention', fill: '#94a3b8', fontSize: 10 }} 
              />
            )}
            <Area 
              type="monotone" 
              dataKey="rmssd" 
              stroke={currentColor} 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorRmssd)" 
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
