import React, { useEffect, useState, useRef } from 'react'

interface ActionLog {
  type: string;
  agent_id: string;
  action: string;
  status: string;
  timestamp?: string;
}

interface Threat {
  id: string;
  type: string;
  description: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
}

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-space-void select-none">
      {/* Header / Substrate Pulse */}
      <header className="h-14 flex items-center justify-between px-6 border-b border-white/10 glass rounded-none">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 bg-space-glow rounded-sm animate-pulse shadow-[0_0_10px_#00f2ff]" />
          <span className="text-xl font-bold tracking-widest text-white uppercase">Tachyon Tongs</span>
          <span className="text-[10px] bg-space-glow/20 text-space-glow px-2 py-0.5 rounded border border-space-glow/40 font-bold ml-2">AIRLOCK ACTIVE</span>
        </div>
        <div className="flex items-center gap-6 text-[11px] text-gray-400">
          <div className="flex flex-col items-end">
            <span className="text-white font-bold uppercase tracking-tighter">Substrate v1.4.2</span>
            <span className="text-space-neon tracking-widest">STABLE // METAL_ACCEL</span>
          </div>
          <div className="w-px h-8 bg-white/10" />
          <div className="flex flex-col items-end">
            <span className="text-white font-bold uppercase tracking-tighter">Enforcement</span>
            <span className="text-space-neon tracking-widest">ACTIVE_PEP</span>
          </div>
        </div>
      </header>
      
      {/* Main Mission Control Area */}
      <main className="flex-1 flex overflow-hidden p-4 gap-4">
        {children}
      </main>
      
      {/* Footer / Doom Telemetry */}
      <footer className="h-10 bg-black/80 flex items-center justify-between px-6 border-t border-white/5 text-[10px] tracking-widest text-gray-500 uppercase">
        <div className="flex gap-6">
          <span>Block Rate: <span className="text-space-neon">99.8%</span></span>
          <span>Latency: <span className="text-space-glow">1.2ms</span></span>
          <span>Uptime: <span className="text-white font-bold">42:13:09</span></span>
        </div>
        <div className="flex gap-4 items-center">
          <span className="animate-pulse">● Global Sync Active</span>
          <span className="text-gray-700">|</span>
          <span>127.0.0.1:3030</span>
        </div>
      </footer>
    </div>
  )
}

const App: React.FC = () => {
  const [logs, setLogs] = useState<ActionLog[]>([]);
  const [threats] = useState<Threat[]>([
    { id: 'CVE-2024-1337', type: 'IPI', description: 'Indirect Prompt Injection via SVG metadata.', severity: 'CRITICAL' },
    { id: 'CVE-2024-1338', type: 'RAG', description: 'Knowledge retrieval poisoning in vector DB.', severity: 'HIGH' },
    { id: 'CVE-2024-1339', type: 'DEP', description: 'Malicious library hallucination detected.', severity: 'CRITICAL' },
  ]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to Airlock API WebSocket
    ws.current = new WebSocket('ws://127.0.0.1:60462/ws/telemetry');
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'ACTION_LOG') {
        data.timestamp = new Date().toLocaleTimeString();
        setLogs(prev => [data, ...prev].slice(0, 50));
      }
    };

    ws.current.onopen = () => {
      console.log('Airlock Telemetry Stream Connected');
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  return (
    <Layout>
      {/* Left Pane: Threat Feed */}
      <div className="w-1/4 flex flex-col gap-4">
        <div className="h-1/2 glass p-4 flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm">Threat Feed</h3>
            <span className="text-[10px] text-gray-500">REAL-TIME</span>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3">
            {threats.map(threat => (
              <div key={threat.id} className="p-3 bg-white/5 border border-white/5 rounded hover:border-space-glow/30 transition-all cursor-pointer group">
                <div className="flex justify-between items-start mb-1">
                  <span className="text-[10px] text-space-glow font-bold">{threat.id}</span>
                  <span className={`text-[9px] ${threat.severity === 'CRITICAL' ? 'text-space-crimson' : 'text-orange-500'}`}>{threat.severity}</span>
                </div>
                <p className="text-[11px] text-gray-400 leading-tight group-hover:text-white font-mono">{threat.description}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="h-1/2 glass p-4 flex flex-col">
          <h3 className="text-sm mb-4">Substrate Logs</h3>
          <div className="flex-1 overflow-y-auto space-y-2 font-mono text-[9px]">
            {logs.length === 0 && <span className="text-gray-600 italic">WAITING FOR SUBSTRATE PULSE...</span>}
            {logs.map((log, i) => (
              <div key={i} className="flex gap-2 border-l border-white/10 pl-2 py-1">
                <span className="text-gray-600 shrink-0">[{log.timestamp}]</span>
                <span className="text-space-glow shrink-0">{log.agent_id}</span>
                <span className="text-white truncate">{log.action}</span>
                <span className={log.status === 'SUCCESS' ? 'text-space-neon' : 'text-space-crimson'}>{log.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Center Pane: Side-by-Side Patch Diff */}
      <div className="flex-1 glass flex flex-col overflow-hidden relative">
        <div className="h-12 border-b border-white/5 flex items-center justify-between px-6 bg-white/2">
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-bold text-gray-400">PATCH PROPOSAL:</span>
            <span className="text-[11px] text-white font-mono">/tachyon/enforcement/daemon.py</span>
          </div>
          <div className="flex gap-2">
            <button className="px-4 py-1 text-[10px] border border-white/20 rounded hover:bg-white/5 transition-all uppercase tracking-widest">Reject</button>
            <button className="px-4 py-1 text-[10px] bg-space-neon text-black font-bold rounded shadow-[0_0_10px_#39ff14] hover:brightness-110 transition-all uppercase tracking-widest">Authorize Patch</button>
          </div>
        </div>
        <div className="flex-1 flex font-mono text-[11px] leading-relaxed">
          <div className="w-1/2 p-6 border-r border-white/5 bg-space-black/50 overflow-y-auto">
            <div className="text-gray-500 mb-2">/* BEFORE */</div>
            <div className="text-gray-300">
              <span className="text-gray-600 mr-4">42</span> async def execute_action(request: ToolRequest):<br/>
              <span className="text-gray-600 mr-4">43</span> &nbsp;&nbsp;&nbsp;&nbsp;request_id = str(uuid.uuid4())<br/>
              <span className="text-space-crimson bg-space-crimson/10 w-full inline-block">- <span className="text-gray-600 mr-3">44</span>&nbsp;result = await router.route(request.agent_id, request.action, request.parameters)</span><br/>
              <span className="text-gray-600 mr-4">45</span> <br/>
              <span className="text-gray-600 mr-4">46</span> &nbsp;&nbsp;&nbsp;&nbsp;return ToolResponse(<br/>
            </div>
          </div>
          <div className="w-1/2 p-6 bg-space-black/80 overflow-y-auto">
            <div className="text-gray-500 mb-2">/* AFTER */</div>
            <div className="text-gray-300">
              <span className="text-gray-600 mr-4">42</span> async def execute_action(request: ToolRequest):<br/>
              <span className="text-gray-600 mr-4">43</span> &nbsp;&nbsp;&nbsp;&nbsp;request_id = str(uuid.uuid4())<br/>
              <span className="text-space-neon bg-space-neon/10 w-full inline-block">+ <span className="text-gray-600 mr-3">44</span>&nbsp;intent = await orchestrator.audit_intent(request)</span><br/>
              <span className="text-space-neon bg-space-neon/10 w-full inline-block">+ <span className="text-gray-600 mr-3">45</span>&nbsp;if intent.is_malicious:</span><br/>
              <span className="text-space-neon bg-space-neon/10 w-full inline-block">+ <span className="text-gray-600 mr-3">46</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return ToolResponse(status="BLOCKED", error=intent.reason)</span><br/>
              <span className="text-space-neon bg-space-neon/10 w-full inline-block">+ <span className="text-gray-600 mr-3">47</span>&nbsp;result = await router.route(request.agent_id, request.action, request.parameters)</span><br/>
              <span className="text-gray-600 mr-4">48</span> <br/>
              <span className="text-gray-600 mr-4">49</span> &nbsp;&nbsp;&nbsp;&nbsp;return ToolResponse(<br/>
            </div>
          </div>
        </div>
      </div>

      {/* Right Pane: Scalable Oversight Debate */}
      <div className="w-1/4 glass p-0 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-white/5 bg-white/2">
          <h3 className="text-sm">Scalable Oversight Debate</h3>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="flex gap-3">
            <div className="w-6 h-6 bg-space-glow rounded-full shrink-0 flex items-center justify-center text-[10px] font-bold text-black font-mono">A</div>
            <div className="space-y-1">
              <div className="flex justify-between items-center text-[10px] font-bold">
                <span className="text-space-glow">Analyst Agent</span>
                <span className="text-gray-500">12:31:04</span>
              </div>
              <p className="text-[11px] text-gray-400 leading-normal font-mono">The patch implements a prophylactic intent audit at the ingestion layer, preventing TOCTOU vulnerabilities.</p>
            </div>
          </div>
          <div className="flex gap-3 pl-6 border-l border-white/10">
            <div className="w-6 h-6 bg-space-pulse rounded-full shrink-0 flex items-center justify-center text-[10px] font-bold text-white font-mono">S</div>
            <div className="space-y-1">
              <div className="flex justify-between items-center text-[10px] font-bold">
                <span className="text-space-pulse">Skeptic Agent</span>
                <span className="text-gray-500">12:31:12</span>
              </div>
              <p className="text-[11px] text-gray-400 leading-normal font-mono">Wait, does the `audit_intent` call have a timeout? If not, we risk a DoS at the enforcement point.</p>
            </div>
          </div>
        </div>
        <div className="p-4 bg-white/2 border-t border-white/5">
          <div className="relative">
            <input type="text" placeholder="QUERY SUBSTRATE..." className="w-full bg-space-black border border-white/10 rounded px-3 py-2 text-[10px] focus:outline-none focus:border-space-glow transition-all" />
            <span className="absolute right-3 top-2.5 text-[10px] text-gray-600 font-bold tracking-tighter cursor-pointer hover:text-white transition-all uppercase">Send</span>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default App
