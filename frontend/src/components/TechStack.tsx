import { Badge } from "@/components/ui/badge";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const sections = [
  {
    label: "Backend",
    items: ["Python", "Flask"],
  },
  {
    label: "AI / ML",
    items: ["LangChain", "Ollama", "Qwen2.5-3B", "ChromaDB"],
  },
  {
    label: "Frontend",
    items: ["React", "Vite", "Tailwind CSS", "TypeScript"],
  },
];

const architectureSteps = [
  {
    step: "1. Document Ingestion",
    desc: "PDFs are parsed via PyPDF2; raw text is accepted directly. Content is split into semantic chunks.",
  },
  {
    step: "2. Embedding & Retrieval",
    desc: "Chunks are embedded and stored in ChromaDB. On query, relevant chunks are retrieved using similarity search (RAG pattern).",
  },
  {
    step: "3. LLM Generation",
    desc: "Retrieved context is passed to Qwen2.5-3B via Ollama. The model generates structured markdown with NER entities, urgency levels, and clinical timelines.",
  },
  {
    step: "4. Streaming Response",
    desc: "Output is streamed in real-time to the React frontend with terminal log visibility.",
  },
];

const privacyPoints = [
  {
    title: "Zero Cloud Dependency.",
    desc: "The entire pipeline — model, embeddings, vector store — runs on your local machine.",
  },
  {
    title: "No API Keys Required.",
    desc: "Ollama serves the model locally. No OpenAI, no third-party services.",
  },
  {
    title: "No Login or Accounts.",
    desc: "Open the app and use it. No telemetry, no tracking, no data collection.",
  },
  {
    title: "HIPAA-Friendly by Design.",
    desc: "Patient data never leaves the host environment. Ideal for clinical and research settings.",
  },
];

export default function TechStack() {
  const ref = useScrollReveal();
  return (
    <section id="tech" className="py-24 px-4 bg-secondary/30">
      <div ref={ref} className="reveal container mx-auto max-w-3xl space-y-14">
        <div className="text-center">
          <h2 className="text-sm font-semibold uppercase tracking-widest text-primary mb-2">
            Technology
          </h2>
          <p className="text-2xl sm:text-3xl font-bold text-foreground">
            Built with modern tools
          </p>
        </div>

        {/* Stack */}
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-4">Stack</h3>
          <div className="space-y-4">
            {sections.map((sec) => (
              <div key={sec.label}>
                <p className="text-xs uppercase tracking-widest text-muted-foreground mb-2">
                  {sec.label}
                </p>
                <div className="flex flex-wrap gap-2">
                  {sec.items.map((item) => (
                    <Badge key={item} variant="outline" className="text-sm py-1.5 px-4">
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Architecture */}
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-4">Architecture</h3>
          <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground space-y-3 leading-relaxed">
            {architectureSteps.map((s) => (
              <p key={s.step}>
                <strong className="text-foreground">{s.step}:</strong> {s.desc}
              </p>
            ))}
          </div>
        </div>

        {/* Privacy */}
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-4">Privacy</h3>
          <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground space-y-3 leading-relaxed">
            {privacyPoints.map((p) => (
              <p key={p.title}>
                <strong className="text-foreground">{p.title}</strong> {p.desc}
              </p>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
