import * as React from "react";

/* ── Types ────────────────────────────────────────────────── */
type AccordionType = "single" | "multiple";

interface AccordionContextValue {
  type: AccordionType;
  openItems: string[];
  toggle: (value: string) => void;
}

interface AccordionItemContextValue {
  value: string;
  isOpen: boolean;
}

/* ── Contexts ─────────────────────────────────────────────── */
const AccordionContext = React.createContext<AccordionContextValue>({
  type: "single",
  openItems: [],
  toggle: () => {},
});

const AccordionItemContext = React.createContext<AccordionItemContextValue>({
  value: "",
  isOpen: false,
});

/* ── Root ─────────────────────────────────────────────────── */
interface AccordionProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: AccordionType;
  defaultValue?: string | string[];
  children: React.ReactNode;
}

function Accordion({
  type = "single",
  defaultValue,
  className,
  children,
  ...props
}: AccordionProps) {
  const [openItems, setOpenItems] = React.useState<string[]>(() => {
    if (!defaultValue) return [];
    return Array.isArray(defaultValue) ? defaultValue : [defaultValue];
  });

  const toggle = (value: string) => {
    if (type === "single") {
      setOpenItems((prev) => (prev.includes(value) ? [] : [value]));
    } else {
      setOpenItems((prev) =>
        prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
      );
    }
  };

  return (
    <AccordionContext.Provider value={{ type, openItems, toggle }}>
      <div className={className} {...props}>
        {children}
      </div>
    </AccordionContext.Provider>
  );
}

/* ── Item ─────────────────────────────────────────────────── */
interface AccordionItemProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
  children: React.ReactNode;
}

function AccordionItem({ value, className, children, ...props }: AccordionItemProps) {
  const { openItems } = React.useContext(AccordionContext);
  const isOpen = openItems.includes(value);

  return (
    <AccordionItemContext.Provider value={{ value, isOpen }}>
      <div
        className={["border-b", className].filter(Boolean).join(" ")}
        {...props}
      >
        {children}
      </div>
    </AccordionItemContext.Provider>
  );
}

/* ── Trigger ──────────────────────────────────────────────── */
interface AccordionTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

const AccordionTrigger = React.forwardRef<HTMLButtonElement, AccordionTriggerProps>(
  ({ className, children, ...props }, ref) => {
    const { toggle } = React.useContext(AccordionContext);
    const { value, isOpen } = React.useContext(AccordionItemContext);

    return (
      <button
        ref={ref}
        type="button"
        onClick={() => toggle(value)}
        aria-expanded={isOpen}
        className={[
          "flex w-full items-center justify-between py-4 text-sm font-medium",
          "transition-all hover:underline text-left",
          "[&[data-state=open]>svg]:rotate-180",
          className,
        ]
          .filter(Boolean)
          .join(" ")}
        data-state={isOpen ? "open" : "closed"}
        {...props}
      >
        {children}
        {/* Chevron icon */}
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
          className="shrink-0 transition-transform duration-200"
          style={{ transform: isOpen ? "rotate(180deg)" : "rotate(0deg)" }}
          aria-hidden="true"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
    );
  }
);
AccordionTrigger.displayName = "AccordionTrigger";

/* ── Content ──────────────────────────────────────────────── */
interface AccordionContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const AccordionContent = React.forwardRef<HTMLDivElement, AccordionContentProps>(
  ({ className, children, ...props }, ref) => {
    const { isOpen } = React.useContext(AccordionItemContext);

    return (
      <div
        ref={ref}
        data-state={isOpen ? "open" : "closed"}
        style={{
          overflow: "hidden",
          maxHeight: isOpen ? "2000px" : "0px",
          transition: "max-height 0.3s ease",
        }}
        {...props}
      >
        <div className={["pb-4 pt-0 text-sm", className].filter(Boolean).join(" ")}>
          {children}
        </div>
      </div>
    );
  }
);
AccordionContent.displayName = "AccordionContent";

export { Accordion, AccordionContent, AccordionItem, AccordionTrigger };
