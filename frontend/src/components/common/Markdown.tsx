import React from "react";

interface MarkdownProps {
  content: string;
}

export function Markdown({ content }: MarkdownProps) {
  if (!content) return null;

  // Split by line
  const lines = content.split("\n");
  const blocks: React.ReactNode[] = [];

  let currentTable: string[][] = [];
  let currentList: string[] = [];

  const flushTable = (key: string) => {
    if (currentTable.length === 0) return;

    // Check if the second row is a table separator (e.g. |---|---|)
    const hasSeparator =
      currentTable[1] &&
      currentTable[1].every((cell) => {
        const val = cell.trim();
        return val.startsWith("---") || val === "";
      });

    const headerRow = hasSeparator ? currentTable[0] : null;
    const bodyRows = hasSeparator ? currentTable.slice(2) : currentTable;

    blocks.push(
      <div key={`table-${key}`} className="my-3 overflow-x-auto rounded border border-terminal-border bg-terminal-surface/30">
        <table className="w-full border-collapse text-left text-xs text-terminal-text">
          {headerRow && (
            <thead>
              <tr className="border-b border-terminal-border bg-terminal-surface/60 font-semibold uppercase tracking-wider">
                {headerRow.map((cell, idx) => (
                  <th key={`th-${idx}`} className="px-3 py-2 border-r border-terminal-border last:border-r-0">
                    {renderInline(cell)}
                  </th>
                ))}
              </tr>
            </thead>
          )}
          <tbody>
            {bodyRows.map((row, rowIdx) => (
              <tr key={`tr-${rowIdx}`} className="border-b border-terminal-border/40 last:border-b-0 hover:bg-terminal-surface/20">
                {row.map((cell, idx) => (
                  <td key={`td-${idx}`} className="px-3 py-2 border-r border-terminal-border/40 last:border-r-0">
                    {renderInline(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
    currentTable = [];
  };

  const flushList = (key: string) => {
    if (currentList.length === 0) return;
    blocks.push(
      <ul key={`list-${key}`} className="my-2 ml-5 list-disc space-y-1 text-xs text-terminal-text">
        {currentList.map((item, idx) => (
          <li key={`li-${idx}`}>{renderInline(item)}</li>
        ))}
      </ul>
    );
    currentList = [];
  };

  const renderInline = (text: string) => {
    const parts: React.ReactNode[] = [];
    let remaining = text.trim();
    let keyIdx = 0;

    while (remaining.length > 0) {
      const boldMatch = remaining.match(/\*\*(.*?)\*\*/);
      const codeMatch = remaining.match(/`(.*?)`/);

      const boldIdx = boldMatch ? remaining.indexOf(boldMatch[0]) : -1;
      const codeIdx = codeMatch ? remaining.indexOf(codeMatch[0]) : -1;

      if (boldIdx !== -1 && (codeIdx === -1 || boldIdx < codeIdx)) {
        if (boldIdx > 0) {
          parts.push(remaining.substring(0, boldIdx));
        }
        parts.push(
          <strong key={`bold-${keyIdx++}`} className="font-semibold text-terminal-accent">
            {boldMatch![1]}
          </strong>
        );
        remaining = remaining.substring(boldIdx + boldMatch![0].length);
      } else if (codeIdx !== -1) {
        if (codeIdx > 0) {
          parts.push(remaining.substring(0, codeIdx));
        }
        parts.push(
          <code key={`code-${keyIdx++}`} className="rounded bg-terminal-surface px-1 py-0.5 font-mono text-[10px] border border-terminal-border text-terminal-amber">
            {codeMatch![1]}
          </code>
        );
        remaining = remaining.substring(codeIdx + codeMatch![0].length);
      } else {
        parts.push(remaining);
        break;
      }
    }

    return parts.length > 0 ? parts : text;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Check if table row (starts and ends with |)
    if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
      flushList(String(i));
      const cells = trimmed
        .split("|")
        .slice(1, -1)
        .map((c) => c.trim());
      currentTable.push(cells);
      continue;
    } else {
      flushTable(String(i));
    }

    // Check if bullet point list item
    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      currentList.push(trimmed.substring(2));
      continue;
    } else if (trimmed.match(/^\d+\.\s/)) {
      currentList.push(trimmed.replace(/^\d+\.\s/, ""));
      continue;
    } else {
      flushList(String(i));
    }

    // Check if heading
    if (trimmed.startsWith("### ")) {
      blocks.push(
        <h4 key={`h3-${i}`} className="mt-4 mb-1.5 text-xs font-bold uppercase tracking-wider text-terminal-accent border-b border-terminal-border/30 pb-0.5">
          {renderInline(trimmed.substring(4))}
        </h4>
      );
    } else if (trimmed.startsWith("## ")) {
      blocks.push(
        <h3 key={`h2-${i}`} className="mt-5 mb-2 text-[13px] font-bold uppercase tracking-wider text-terminal-accent border-b border-terminal-border/50 pb-0.5">
          {renderInline(trimmed.substring(3))}
        </h3>
      );
    } else if (trimmed.startsWith("# ")) {
      blocks.push(
        <h2 key={`h1-${i}`} className="mt-6 mb-2.5 text-sm font-bold uppercase tracking-widest text-terminal-accent border-b border-terminal-border pb-1">
          {renderInline(trimmed.substring(2))}
        </h2>
      );
    } else if (trimmed === "") {
      continue;
    } else {
      // Regular paragraph
      blocks.push(
        <p key={`p-${i}`} className="my-2 text-xs leading-relaxed text-terminal-text">
          {renderInline(line)}
        </p>
      );
    }
  }

  // Flush remaining blocks
  flushTable("end");
  flushList("end");

  return <div className="space-y-1">{blocks}</div>;
}
