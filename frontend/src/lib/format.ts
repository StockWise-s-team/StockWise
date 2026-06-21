// Formatting helpers for the paper-trading UI.
// virtualCash defaults to 100,000,000 → the platform trades Vietnamese-market
// stocks, so amounts are formatted as VND.

const vnd = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 0 });
const qtyFmt = new Intl.NumberFormat("vi-VN");

export function formatVnd(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${vnd.format(Math.round(value))} ₫`;
}

// Signed amount for P/L figures (e.g. "+1.250.000 ₫").
export function formatPnl(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${formatVnd(value)}`;
}

export function formatQty(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return qtyFmt.format(value);
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Tailwind text color for a P/L value (up / down / neutral).
export function pnlColor(value: number | null | undefined): string {
  if (value === null || value === undefined || value === 0) return "text-terminal-text";
  return value > 0 ? "text-terminal-green" : "text-terminal-red";
}

// Current date in Asia/Ho_Chi_Minh as YYYY-MM-DD (matches backend LocalDate.parse).
export function toVndYmd(date: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Ho_Chi_Minh" }).format(date);
}
