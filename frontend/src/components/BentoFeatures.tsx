import { Shield, Zap, FileText, FileCode, MessageSquare, Microscope } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const features = [
  {
    icon: Shield,
    title: "Secure & Local",
    desc: "Runs Qwen2.5-3B entirely on your machine. No API keys, no login, no data leaves your device.",
  },
  {
    icon: Zap,
    title: "Local Inference",
    desc: "Hardware-accelerated responses via Ollama. Fast summarization without cloud latency.",
  },
  {
    icon: FileText,
    title: "Multi-Format Support",
    desc: "Upload PDFs or paste raw text. Handles prescriptions, discharge summaries, and lab reports.",
  },
  {
    icon: FileCode,
    title: "Rich Markdown Summaries",
    desc: "Structured output with NER-highlighted entities — medications, diagnoses, and procedures.",
  },
  {
    icon: MessageSquare,
    title: "Follow-Up Chat",
    desc: "Ask contextual follow-up questions. ChromaDB-backed memory for multi-turn conversation.",
  },
  {
    icon: Microscope,
    title: "Jargon Translator",
    desc: "Click any medical term for a plain-language explanation. Makes reports accessible to everyone.",
  },
];

export default function BentoFeatures() {
  const ref = useScrollReveal();
  return (
    <section id="features" className="py-24 px-4">
      <div ref={ref} className="reveal container mx-auto max-w-5xl">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-primary text-center mb-2">
          Features
        </h2>
        <p className="text-2xl sm:text-3xl font-bold text-foreground text-center mb-12">
          Everything you need, nothing you don't
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f) => (
            <div
              key={f.title}
              className="group rounded-lg border bg-card p-6 transition-all duration-200 hover:scale-[1.02] hover:border-primary/40"
            >
              <f.icon className="w-5 h-5 text-primary mb-3" />
              <h3 className="font-semibold text-foreground mb-1">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
