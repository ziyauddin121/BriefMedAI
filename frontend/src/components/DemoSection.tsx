import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Upload, Play, Terminal, FileText, MessageSquare, Send } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { MarkdownOutput } from "./MarkdownOutput";

export default function DemoSection() {
  const ref = useScrollReveal();
  const [rawText, setRawText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [showOutput, setShowOutput] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const [logs, setLogs] = useState<{time: string, msg: string, type: string}[]>([]);
  const [summary, setSummary] = useState("");
  const [urgency, setUrgency] = useState<string | null>(null);

  const [chatMessages, setChatMessages] = useState<{ role: string; content: string }[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isChatting, setIsChatting] = useState(false);

  const fileRef = useRef<HTMLInputElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  // Auto-scroll chat
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages, isChatting]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const startGeneration = async () => {
    setIsGenerating(true);
    setShowOutput(true);
    setLogs([{ time: new Date().toLocaleTimeString('en-GB', { hour12: false }), msg: "System Ready. Awaiting input...", type: "log" }]);
    setSummary("");
    setUrgency(null);
    setChatMessages([]);

    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    formData.append('report_text', rawText);

    try {
      const response = await fetch('http://127.0.0.1:5000/stream_generate', {
        method: 'POST',
        body: formData
      });

      if (!response.body) throw new Error("No response body");
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            const timeStr = new Date().toLocaleTimeString('en-GB', { hour12: false });
            
            if (data.type === 'log' || data.type === 'error') {
              setLogs(prev => [...prev, { time: timeStr, msg: data.message, type: data.type }]);
            } else if (data.type === 'result') {
              setSummary(data.content);
              if (data.urgency) setUrgency(data.urgency);
            }
          } catch (e) {
            console.error("Parse error", e);
          }
        }
      }
    } catch (err: any) {
      setLogs(prev => [...prev, { time: "00:00:00", msg: `NETWORK ERROR: ${err.message}`, type: "error" }]);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleChat = async () => {
    if(!chatInput.trim() || isChatting) return;

    const userMsg = chatInput.trim();
    setChatInput("");
    setChatMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsChatting(true);

    try {
      const currentHistory = chatMessages.map(m => ({ role: m.role, content: m.content }));
      
      const response = await fetch('http://127.0.0.1:5000/stream_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMsg, history: currentHistory })
      });

      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            if (data.type === 'result') {
              setChatMessages(prev => [...prev, { role: 'ai', content: data.content }]);
            } else if (data.type === 'error') {
               setChatMessages(prev => [...prev, { role: 'ai', content: `[ERROR]: ${data.message}` }]);
            }
          } catch (e) {
            console.error("Parse error", e);
          }
        }
      }
    } catch (err: any) {
      setChatMessages(prev => [...prev, { role: 'ai', content: `[NETWORK ERROR]: ${err.message}` }]);
    } finally {
      setIsChatting(false);
    }
  };

  return (
    <section id="demo" className="py-24 px-4 bg-background">
      <div ref={ref} className="reveal container mx-auto max-w-6xl">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-primary text-center mb-2 flex items-center justify-center gap-2">
          <Terminal className="w-4 h-4" /> Live Demo
        </h2>
        <p className="text-2xl sm:text-3xl font-bold text-foreground text-center mb-4">
          See it in action
        </p>
        <p className="text-center text-muted-foreground text-sm mb-12 max-w-xl mx-auto">
          BriefMed AI analyzes raw medical records and extracts structured, easily readable formats.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Panel */}
          <div className="space-y-4">
            {/* Upload */}
            <div
              onClick={() => fileRef.current?.click()}
              className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors hover:border-primary/40 hover:bg-secondary/30 relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <input ref={fileRef} type="file" accept=".pdf,.txt" className="hidden" onChange={handleFileSelect} />
              <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2 group-hover:text-primary transition-colors" />
              <p className="text-sm font-medium text-foreground">
                {file ? `File Loaded: ${file.name}` : "Drop a PDF or TXT file"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {file ? "Click to change file" : "or click to browse"}
              </p>
            </div>

            {/* Raw text */}
            <Textarea
              placeholder="Or paste raw medical text here..."
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="min-h-[120px] font-mono text-sm resize-none border-border"
            />

            <Button onClick={startGeneration} disabled={isGenerating} className="w-full rounded-full gap-2 relative overflow-hidden group border-border">
              <span className="relative z-10 flex items-center gap-2">
                {isGenerating ? <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div> : <Play className="w-4 h-4" />} 
                {isGenerating ? "Processing Sequence..." : "Execute Summary Protocol"}
              </span>
              <div className="absolute inset-0 bg-primary/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
            </Button>

            {/* Terminal Logs */}
            {showOutput && (
              <div ref={terminalRef} className="rounded-lg bg-[#000000] border border-border text-primary-foreground p-4 font-mono text-xs space-y-1 max-h-48 overflow-y-auto w-full scrollbar-thin shadow-inner">
                <div className="flex items-center gap-2 text-primary mb-2 border-b border-primary/20 pb-2">
                  <Terminal className="w-3.5 h-3.5" /> SYSTEM ACTIVITY LOG
                </div>
                {logs.map((log, i) => (
                  <div key={i} className={log.type === 'error' ? "text-destructive" : (log.msg.includes("COMPLETED") ? "text-green-500" : "text-muted-foreground hover:text-white transition-colors")}>
                    <span className="text-secondary mr-2">[{log.time}]</span>
                    {log.msg}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Output Panel */}
          <div className="space-y-4">
            {showOutput && summary ? (
              <>
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="border-primary/50 text-foreground">
                    :: SYNTHESIS COMPLETE ::
                  </Badge>
                  {urgency && (
                    <Badge variant={urgency === "Critical" ? "destructive" : urgency === "Urgent" ? "secondary" : "default"} className="uppercase font-semibold tracking-wider">
                      {urgency}
                    </Badge>
                  )}
                </div>

                {/* Summary */}
                <div className="rounded-lg border bg-card p-5 prose prose-sm max-w-none shadow-sm relative overflow-hidden group text-foreground">
                  <div className="absolute right-0 top-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                     <Button size="sm" variant="ghost" className="border" onClick={() => navigator.clipboard.writeText(summary)}>Copy</Button>
                  </div>
                  <MarkdownOutput content={summary} />
                </div>

              </>
            ) : (
              <div className="rounded-lg border-2 border-dashed border-border p-16 flex flex-col items-center justify-center text-center h-full bg-card/50">
                <FileText className="w-12 h-12 text-muted-foreground mb-4 opacity-50" />
                <p className="text-sm font-medium text-foreground mb-2">
                  Waiting for input...
                </p>
                <p className="text-xs text-muted-foreground max-w-xs">
                  Upload a document and click "Execute Summary Protocol" to interface with the AI models.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Chat Interface (Full Width) */}
        {showOutput && summary && (
          <div className="mt-6 rounded-lg border bg-card p-6 shadow-sm text-foreground">
            <div className="flex items-center justify-between mb-4 border-b pb-3">
              <div className="flex items-center gap-2 text-base font-semibold text-foreground">
                <MessageSquare className="w-5 h-5 text-primary" /> Medical Chat Interface
              </div>
            </div>
            <div ref={chatScrollRef} className="space-y-4 max-h-96 overflow-y-auto mb-4 pr-3 scrollbar-thin text-foreground">
              {chatMessages.length === 0 && (
                <div className="text-center text-sm text-muted-foreground my-6 font-mono">
                  Ask questions about the diagnosed medical report.<br/>Conversation context is retained.
                </div>
              )}
              {chatMessages.map((m, i) => (
                <div
                  key={i}
                  className={`text-sm px-5 py-3 rounded-2xl flex items-start gap-4 ${
                    m.role === "user"
                      ? "bg-primary/5 text-primary ml-12 border border-primary/20 font-medium"
                      : "bg-secondary text-foreground mr-8 border border-border"
                  }`}
                >
                  {m.role === "ai" && <Terminal className="w-5 h-5 mt-0.5 text-muted-foreground flex-shrink-0" />}
                  <div className="flex-1">
                    {m.role === 'ai' ? <MarkdownOutput content={m.content} /> : m.content}
                  </div>
                </div>
              ))}
              {isChatting && (
                 <div className="text-sm px-5 py-3 rounded-2xl bg-secondary text-foreground mr-8 flex items-center gap-2 w-fit border border-border">
                   <div className="w-2 h-2 rounded-full bg-primary/60 animate-bounce"></div>
                   <div className="w-2 h-2 rounded-full bg-primary/60 animate-bounce" style={{animationDelay: '150ms'}}></div>
                   <div className="w-2 h-2 rounded-full bg-primary/60 animate-bounce" style={{animationDelay: '300ms'}}></div>
                 </div>
              )}
            </div>
            <div className="flex gap-3">
              <input
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleChat()}
                disabled={isChatting}
                placeholder="Ask about symptoms, treatments, or terms..."
                className="flex-1 text-sm border rounded-full px-6 py-3 bg-background focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow disabled:opacity-50 font-sans shadow-inner text-foreground"
              />
              <Button size="icon" disabled={isChatting || !chatInput.trim()} onClick={handleChat} className="rounded-full shadow-md w-12 h-12 flex-shrink-0">
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
