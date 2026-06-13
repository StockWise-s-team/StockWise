import React from "react";
import { clsx } from "clsx";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={clsx(
          "flex h-10 w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 font-mono text-xs text-terminal-text file:border-0 file:bg-transparent file:text-xs file:font-medium placeholder:text-terminal-muted/50 focus-visible:border-terminal-accent/60 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-40",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";
