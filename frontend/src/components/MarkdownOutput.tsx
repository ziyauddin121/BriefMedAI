import React, { useState } from 'react';
import { marked } from 'marked';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface MarkdownOutputProps {
  content: string;
}

export function MarkdownOutput({ content }: MarkdownOutputProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogTerm, setDialogTerm] = useState("");
  const [dialogContent, setDialogContent] = useState("");
  const [dialogLoading, setDialogLoading] = useState(false);

  const processMarkdown = (text: string) => {
    if (!text) return "";
    let processedText = text.replace(/```[a-zA-Z]*\n?/g, '');

    processedText = processedText.replace(
      /(?:\*\*Disclaimer:\*\*|\*Disclaimer:\*|Disclaimer:|Note: Disclaimer:)\s*([\s\S]*?)(?=\n\n|$)/gi,
      '\n\n<div class="disclaimer-alert rounded-md bg-destructive/10 border-l-4 border-destructive p-3 my-4"><strong class="text-destructive font-semibold">DISCLAIMER:</strong> $1</div>\n\n'
    );
    
    processedText = processedText.replace(/\[\[MED\|(.*?)\]\]/gi, "<span class='ner-badge ner-med cursor-pointer inline-flex items-center rounded-md border border-primary/20 bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary transition-colors hover:bg-primary/20'>$1</span>");
    processedText = processedText.replace(/\[\[DIAG\|(.*?)\]\]/gi, "<span class='ner-badge ner-diag cursor-pointer inline-flex items-center rounded-md border border-amber-200 bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-800 transition-colors hover:bg-amber-200'>$1</span>");
    processedText = processedText.replace(/\[\[PROC\|(.*?)\]\]/gi, "<span class='ner-badge ner-proc cursor-pointer inline-flex items-center rounded-md border border-accent/20 bg-accent/10 px-2.5 py-0.5 text-xs font-semibold text-accent transition-colors hover:bg-accent/20'>$1</span>");

    return marked.parse(processedText) as string;
  };

  const handleMarkdownClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    if (target.classList.contains('ner-badge')) {
      openDialog(target.innerText);
    }
  };

  const openDialog = async (term: string) => {
    setDialogOpen(true);
    setDialogTerm(term);
    setDialogContent("");
    setDialogLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/explain_term', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ term })
      });

      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let explanation = "";
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
              explanation = data.content;
              setDialogContent(explanation);
            } else if (data.type === 'error') {
               setDialogContent(`[ERROR]: ${data.message}`);
            }
          } catch (e) {
            console.error("Parse error", e);
          }
        }
      }
    } catch (err: any) {
      setDialogContent(`[NETWORK ERROR]: ${err.message}`);
    } finally {
      setDialogLoading(false);
    }
  };

  return (
    <>
      <div 
        className="prose prose-sm dark:prose-invert max-w-none font-sans text-sm leading-relaxed" 
        onClick={handleMarkdownClick}
        dangerouslySetInnerHTML={{ __html: processMarkdown(content) }} 
      />
      
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md bg-background border border-border">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-foreground">
              {dialogTerm}
              <span className="text-xs text-muted-foreground font-mono font-normal">:: LAYMAN'S TERMS ::</span>
            </DialogTitle>
            <DialogDescription className="text-foreground">
              {dialogLoading ? (
                <span className="animate-pulse">Translating jargon...</span>
              ) : (
                <div dangerouslySetInnerHTML={{ __html: marked.parse(dialogContent) as string }} />
              )}
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </>
  );
}
