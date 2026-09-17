import { Button } from "@/components/ui/button";
import { FileText } from "lucide-react";

export default function HeroSection() {
  return (
    <section className="relative pt-32 pb-24 px-4">
      <div className="container mx-auto max-w-4xl text-center">
        {/* Scan icon */}
        <div className="mx-auto w-20 h-24 mb-8 relative">
          <FileText className="w-20 h-24 text-border" strokeWidth={1} />
          <div className="absolute left-0 right-0 h-[2px] bg-primary/80 animate-pulse-scan" />
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-foreground leading-[1.1]">
          BriefMed AI
        </h1>
        <p className="mt-2 text-lg sm:text-xl text-primary font-semibold tracking-wide">
          Intelligent Medical Document Analysis
        </p>
        <p className="mt-4 max-w-2xl mx-auto text-muted-foreground text-base sm:text-lg leading-relaxed">
          Privacy-first summarization powered by a local LLM. No cloud dependency, no API keys,
          no login required. Your medical data never leaves your machine.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Button asChild size="lg" className="rounded-full px-8">
            <a href="#demo">Try the Demo</a>
          </Button>
          <Button asChild variant="outline" size="lg" className="rounded-full px-8">
            <a href="#roadmap">View Roadmap</a>
          </Button>
        </div>
      </div>
    </section>
  );
}
