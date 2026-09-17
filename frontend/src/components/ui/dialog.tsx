import * as React from "react";

/* ── Overlay ──────────────────────────────────────────────── */
const DialogOverlay = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={[
      "fixed inset-0 z-50 bg-black/50 backdrop-blur-sm",
      "data-[state=open]:animate-in data-[state=closed]:animate-out",
      "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className,
    ]
      .filter(Boolean)
      .join(" ")}
    {...props}
  />
));
DialogOverlay.displayName = "DialogOverlay";

/* ── Context ──────────────────────────────────────────────── */
interface DialogContextValue {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}
const DialogContext = React.createContext<DialogContextValue>({
  open: false,
  onOpenChange: () => {},
});

/* ── Root ─────────────────────────────────────────────────── */
interface DialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

function Dialog({ open = false, onOpenChange = () => {}, children }: DialogProps) {
  return (
    <DialogContext.Provider value={{ open, onOpenChange }}>
      {children}
    </DialogContext.Provider>
  );
}

/* ── Trigger ──────────────────────────────────────────────── */
function DialogTrigger({ children, asChild }: { children: React.ReactNode; asChild?: boolean }) {
  const { onOpenChange } = React.useContext(DialogContext);
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as React.ReactElement<any>, {
      onClick: () => onOpenChange(true),
    });
  }
  return <button onClick={() => onOpenChange(true)}>{children}</button>;
}

/* ── Portal / Content ─────────────────────────────────────── */
interface DialogContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const DialogContent = React.forwardRef<HTMLDivElement, DialogContentProps>(
  ({ className, children, ...props }, ref) => {
    const { open, onOpenChange } = React.useContext(DialogContext);

    // Close on Escape
    React.useEffect(() => {
      if (!open) return;
      const handler = (e: KeyboardEvent) => {
        if (e.key === "Escape") onOpenChange(false);
      };
      document.addEventListener("keydown", handler);
      return () => document.removeEventListener("keydown", handler);
    }, [open, onOpenChange]);

    if (!open) return null;

    return (
      <>
        {/* Overlay */}
        <DialogOverlay onClick={() => onOpenChange(false)} />

        {/* Panel */}
        <div
          ref={ref}
          role="dialog"
          aria-modal="true"
          className={[
            "fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2",
            "w-full max-w-lg rounded-lg border bg-background p-6 shadow-lg",
            "animate-in fade-in-0 zoom-in-95",
            className,
          ]
            .filter(Boolean)
            .join(" ")}
          {...props}
        >
          {/* Close button */}
          <button
            onClick={() => onOpenChange(false)}
            className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 focus:outline-none"
            aria-label="Close"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>

          {children}
        </div>
      </>
    );
  }
);
DialogContent.displayName = "DialogContent";

/* ── Header ───────────────────────────────────────────────── */
function DialogHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={["flex flex-col space-y-1.5 text-center sm:text-left", className]
        .filter(Boolean)
        .join(" ")}
      {...props}
    />
  );
}

/* ── Footer ───────────────────────────────────────────────── */
function DialogFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={[
        "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      {...props}
    />
  );
}

/* ── Title ────────────────────────────────────────────────── */
const DialogTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h2
    ref={ref}
    className={["text-lg font-semibold leading-none tracking-tight", className]
      .filter(Boolean)
      .join(" ")}
    {...props}
  />
));
DialogTitle.displayName = "DialogTitle";

/* ── Description ──────────────────────────────────────────── */
const DialogDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={["text-sm text-muted-foreground mt-2", className]
      .filter(Boolean)
      .join(" ")}
    {...props}
  />
));
DialogDescription.displayName = "DialogDescription";

export {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
};
