import React from "react";
import { clsx } from "clsx";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
}

export function Button({
  className,
  variant = "default",
  size = "md",
  ...props
}: ButtonProps) {
  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center rounded border font-mono font-semibold uppercase tracking-wider transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-terminal-accent/50 disabled:pointer-events-none disabled:opacity-40",
        {
          "border-terminal-accent/40 bg-terminal-accent/10 text-terminal-accent hover:bg-terminal-accent/20":
            variant === "default",
          "border-terminal-border bg-transparent text-terminal-muted hover:border-terminal-accent/40 hover:text-terminal-accent":
            variant === "outline",
          "border-transparent bg-transparent text-terminal-muted hover:text-terminal-text":
            variant === "ghost",
        },
        {
          "h-8 px-2.5 text-[10px]": size === "sm",
          "h-10 px-3 text-xs": size === "md",
          "h-11 px-4 text-sm": size === "lg",
        },
        className
      )}
      {...props}
    />
  );
}
