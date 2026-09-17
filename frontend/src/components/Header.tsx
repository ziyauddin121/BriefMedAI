import { Activity } from "lucide-react";

const links = [
  { label: "Features", href: "#features" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Demo", href: "#demo" },
  { label: "Tech", href: "#tech" },
  { label: "Roadmap", href: "#roadmap" },
];

export default function Header() {

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-card/80 backdrop-blur-md border-b">
      <div className="container mx-auto flex items-center justify-between h-14 px-4">
        <a href="#" className="flex items-center gap-2 font-bold text-lg tracking-tight text-foreground">
          <Activity className="w-5 h-5 text-primary" />
          BriefMed AI
        </a>
        <nav className="hidden md:flex items-center gap-6">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              {l.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}
