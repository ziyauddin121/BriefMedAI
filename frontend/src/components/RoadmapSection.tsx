import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const phases = [
  {
    title: "Phase 1 — Advanced RAG",
    items: [
      { n: 1, title: "Hybrid Search", desc: "Combine BM25 keyword search with vector similarity for better retrieval." },
      { n: 2, title: "Re-ranking Pipeline", desc: "Add a cross-encoder re-ranker to improve context relevance." },
      { n: 3, title: "Multi-Document Queries", desc: "Compare and contrast findings across multiple uploaded documents." },
      { n: 4, title: "Citation Linking", desc: "Link each summary sentence back to its source chunk for verifiability." },
      { n: 5, title: "Adaptive Chunking", desc: "Use semantic boundaries instead of fixed-size chunks for cleaner retrieval." },
    ],
  },
  {
    title: "Phase 2 — Input Parsing & Data Structuring",
    items: [
      { n: 6, title: "OCR Support", desc: "Handle scanned PDF documents and images using Tesseract or EasyOCR." },
      { n: 7, title: "Table Extraction", desc: "Parse and preserve tabular data from lab reports and prescriptions." },
      { n: 8, title: "FHIR Export", desc: "Export structured summaries to HL7 FHIR format for EHR integration." },
      { n: 9, title: "Multi-Language Input", desc: "Support medical documents in Hindi, Spanish, and other languages." },
    ],
  },
  {
    title: "Phase 3 — Prompt Engineering & LLM Control",
    items: [
      { n: 10, title: "Audience-Adaptive Summaries", desc: "Toggle between clinician-grade and patient-friendly output." },
      { n: 11, title: "Confidence Scoring", desc: "Show model confidence for each extracted entity and finding." },
      { n: 12, title: "Structured JSON Output", desc: "Enforce consistent schema output via LangChain structured generation." },
      { n: 13, title: "Prompt Templates Library", desc: "Pre-built templates for discharge notes, radiology, pathology, etc." },
      { n: 14, title: "Hallucination Detection", desc: "Cross-reference generated claims against source text to flag unsupported statements." },
    ],
  },
  {
    title: "Phase 4 — UX & Agentic Features",
    items: [
      { n: 15, title: "Voice Input", desc: "Dictate medical notes via speech-to-text for hands-free operation." },
      { n: 16, title: "Auto-Suggest Follow-Ups", desc: "AI-generated follow-up questions based on summary content." },
      { n: 17, title: "Document History", desc: "Local storage of past summaries with search and comparison." },
      { n: 18, title: "PDF Report Export", desc: "Generate formatted PDF reports from summaries with hospital branding." },
      { n: 19, title: "Multi-Agent Pipeline", desc: "Specialized agents for NER, summarization, and Q&A working in concert." },
      { n: 20, title: "Plugin Architecture", desc: "Extensible system for adding custom models, tools, and output formats." },
    ],
  },
];

export default function RoadmapSection() {
  const ref = useScrollReveal();
  return (
    <section id="roadmap" className="py-24 px-4">
      <div ref={ref} className="reveal container mx-auto max-w-3xl">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-primary text-center mb-2">
          Roadmap
        </h2>
        <p className="text-2xl sm:text-3xl font-bold text-foreground text-center mb-10">
          20 planned enhancements
        </p>

        <Accordion type="multiple" className="space-y-2">
          {phases.map((phase, pi) => (
            <AccordionItem key={pi} value={`phase-${pi}`} className="border rounded-lg px-4">
              <AccordionTrigger className="text-base font-semibold hover:no-underline">
                {phase.title}
                <Badge variant="secondary" className="ml-auto mr-3 text-xs">
                  {phase.items.length} items
                </Badge>
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-3 pb-2">
                  {phase.items.map((item) => (
                    <div key={item.n} className="flex gap-3 items-start">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center">
                        {item.n}
                      </span>
                      <div>
                        <p className="text-sm font-medium text-foreground">{item.title}</p>
                        <p className="text-xs text-muted-foreground">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}
