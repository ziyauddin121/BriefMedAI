import { Activity } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t py-10 px-4">
      <div className="container mx-auto max-w-4xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Activity className="w-4 h-4 text-primary" />
          <span className="font-semibold text-foreground">BriefMed AI</span>
        </div>
        <p className="text-xs text-muted-foreground">Built with privacy in mind. Your data never leaves your machine.</p>
      </div>
    </footer>
  );
}
