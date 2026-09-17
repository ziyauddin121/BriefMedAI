import { Upload, Cpu, ClipboardList } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const steps = [
  { icon: Upload, title: "Upload", desc: "Drop a PDF or paste raw medical text into the input panel." },
  { icon: Cpu, title: "Process", desc: "Qwen2.5-3B processes via RAG pipeline with streaming terminal logs." },
  { icon: ClipboardList, title: "Results", desc: "Get a structured summary with urgency levels, NER badges, and chat." },
];

export default function HowItWorks() {
  const ref = useScrollReveal();
  return (
    <section id="how-it-works" className="py-24 px-4 bg-secondary/30">
      <div ref={ref} className="reveal container mx-auto max-w-4xl text-center">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-primary mb-2">
          How It Works
        </h2>
        <p className="text-2xl sm:text-3xl font-bold text-foreground mb-14">
          Three steps to clarity
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* connecting line */}
          <div className="hidden md:block absolute top-10 left-[16.6%] right-[16.6%] h-px bg-border" />
          {steps.map((s, i) => (
            <div key={s.title} className="flex flex-col items-center">
              <div className="w-20 h-20 rounded-full border-2 border-primary/30 bg-card flex items-center justify-center mb-4 relative z-10">
                <s.icon className="w-8 h-8 text-primary" />
              </div>
              <span className="text-xs font-semibold text-primary mb-1">Step {i + 1}</span>
              <h3 className="font-semibold text-foreground">{s.title}</h3>
              <p className="text-sm text-muted-foreground mt-1 max-w-[240px]">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
