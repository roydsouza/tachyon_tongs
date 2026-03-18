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
    <div className="min-h-screen flex flex-col bg-space-void">
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
  const [threats, setThreats] = useState<Threat[]>([]);
  const [isAuthorizing, setIsAuthorizing] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);

  const fetchThreats = async () => {
    try {
      const response = await fetch('http://127.0.0.1:60462/airlock/threats');
      const data = await response.json();
      // Map SQLite columns to component props
      setThreats(data.map((t: any) => ({
        id: t.cve_id,
        type: t.relevance_class || 'CVE',
        description: t.description,
        severity: t.relevance_class === 'CRITICAL' ? 'CRITICAL' : 'HIGH'
      })));
    } catch (error) {
      console.error('Failed to fetch threats:', error);
    }
  };

  const [currentPatch, setCurrentPatch] = useState<any>(null);

  useEffect(() => {
    fetchThreats();
    // Connect to Airlock API WebSocket
    ws.current = new WebSocket('ws://127.0.0.1:60462/ws/telemetry');
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'ACTION_LOG') {
        data.timestamp = new Date().toLocaleTimeString();
        setLogs(prev => [data, ...prev].slice(0, 50));
      } else if (data.type === 'PATCH_PROPOSED') {
        setCurrentPatch({
          id: data.patch_id,
          agent: data.agent_id,
          status: data.status,
          timestamp: new Date().toLocaleTimeString(),
          diff: data.diff || '--- /dev/null\n+++ /tachyon/enforcement/daemon.py\n@@ -0,0 +1,5 @@\n+ # High-Assurance Mitigation\n'
        });
        // Also log the proposal
        setLogs(prev => [{
          agent_id: data.agent_id,
          action: `PROPOSED_PATCH_${data.patch_id}`,
          status: 'PENDING',
          timestamp: new Date().toLocaleTimeString()
        }, ...prev]);
      }
    };

    ws.current.onopen = () => console.log('Airlock Telemetry Stream Connected');
    return () => ws.current?.close();
  }, []);

  const handlePatchAction = async (patchId: string, action: 'AUTHORIZE' | 'REJECT') => {
    setIsAuthorizing(true);
    try {
      const endpoint = action === 'AUTHORIZE' ? 'authorize' : 'reject';
      const response = await fetch(`http://127.0.0.1:60462/airlock/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patch_id: patchId, action })
      });
      const data = await response.json();
      setStatusMessage(`${action} SUCCESS: ${data.message}`);
      if (action === 'AUTHORIZE' || action === 'REJECT') setCurrentPatch(null);
      setTimeout(() => setStatusMessage(null), 3000);
    } catch (error) {
      setStatusMessage(`ERROR: Failed to ${action.toLowerCase()} patch.`);
    } finally {
      setIsAuthorizing(false);
    }
  };

  return (
    <Layout>
      {/* Left Pane: Threat Feed */}
      <div className="w-1/4 flex flex-col gap-4">
        <div className="h-1/2 glass p-4 flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm">Threat Feed</h3>
            <span className="text-[10px] text-gray-500" onClick={fetchThreats} style={{cursor: 'pointer'}}>REFRESH</span>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3">
            {threats.length === 0 && <span className="text-[10px] text-gray-600 italic">SECURE GATEWAY: NO ACTIVE THREATS</span>}
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
        {statusMessage && (
          <div className="absolute top-16 left-1/2 -translate-x-1/2 z-50 bg-space-glow text-black px-6 py-2 rounded font-bold text-xs shadow-[0_0_20px_#00f2ff] animate-bounce">
            {statusMessage}
          </div>
        )}
        <div className="h-12 border-b border-white/5 flex items-center justify-between px-6 bg-white/2">
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-bold text-gray-400 uppercase">{currentPatch ? 'PENDING PATCH:' : 'SYSTEM ARCHITECTURE:'}</span>
            <span className="text-[11px] text-white font-mono">{currentPatch ? currentPatch.id : 'NO PENDING MITIGATIONS'}</span>
          </div>
          {currentPatch && (
            <div className="flex gap-2">
              <button 
                disabled={isAuthorizing}
                onClick={() => handlePatchAction(currentPatch.id, 'REJECT')}
                className="px-4 py-1 text-[10px] border border-white/20 rounded hover:bg-white/5 transition-all uppercase tracking-widest disabled:opacity-50"
              >
                Reject
              </button>
              <button 
                disabled={isAuthorizing}
                onClick={() => handlePatchAction(currentPatch.id, 'AUTHORIZE')}
                className="px-4 py-1 text-[10px] bg-space-neon text-black font-bold rounded shadow-[0_0_10px_#39ff14] hover:brightness-110 transition-all uppercase tracking-widest disabled:opacity-50"
              >
                {isAuthorizing ? 'AUTHORIZING...' : 'Authorize Patch'}
              </button>
            </div>
          )}
        </div>
        <div className="flex-1 overflow-auto bg-black/40 p-6 font-mono text-[11px] text-gray-300 whitespace-pre">
          {currentPatch ? (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
              {currentPatch.diff.split('\n').map((line: string, i: number) => (
                <div key={i} className={`${line.startsWith('+') ? 'text-space-neon bg-space-neon/5' : line.startsWith('-') ? 'text-space-crimson bg-space-crimson/5' : ''} px-2 py-0.5`}>
                  {line}
                </div>
              ))}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-700 italic opacity-40">
              <div className="w-24 h-24 mb-4 border-2 border-dashed border-gray-800 rounded-full flex items-center justify-center animate-spin-slow">
                <span className="not-italic text-2xl">🛡️</span>
              </div>
              <span>SUBSTRATE IMMUTABILITY ACTIVE</span>
              <span className="text-[9px] mt-2 tracking-[0.3em]">WAITING FOR ENGINEER PROPOSAL...</span>
            </div>
          )}
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
