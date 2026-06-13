"use client";

import { useMemo, useState } from "react";
import { Banknote, Send, ShoppingCart, TrendingDown, TrendingUp } from "lucide-react";
import { clsx } from "clsx";
import { useAuth } from "@/components/providers/AuthProvider";
import { usePortfolio } from "@/hooks/usePortfolio";
import { portfolioGateway } from "@/lib/portfolio/gateway";
import { validateOrderForm } from "@/lib/portfolio/orderValidation";
import { extractErrorMessage } from "@/lib/apiError";
import { formatVnd, formatQty } from "@/lib/format";
import type { OrderResult, OrderSide } from "@/lib/types";
import {
  TerminalButton,
  TerminalInput,
  TerminalMetricCard,
  TerminalNotice,
  TerminalSectionHeader,
} from "@/components/ui";

export default function SandboxPage() {
  const { user } = useAuth();
  const { data, reload } = usePortfolio(user?.id);

  const [symbol, setSymbol] = useState("");
  const [side, setSide] = useState<OrderSide>("BUY");
  const [quantity, setQuantity] = useState("100");
  const [price, setPrice] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<OrderResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const heldQty = useMemo(() => {
    const normalizedSymbol = symbol.trim().toUpperCase();
    return data?.holdings.find((holding) => holding.symbol === normalizedSymbol)?.quantity ?? 0;
  }, [data, symbol]);

  const handleSubmit = async () => {
    if (!user?.id) return;
    setResult(null);
    setError(null);

    const validationError = validateOrderForm({
      symbol,
      side,
      quantity,
      price,
      heldQuantity: heldQty,
    });
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    try {
      const response = await portfolioGateway.placeOrder({
        symbol: symbol.trim().toUpperCase(),
        type: side,
        quantity: Number(quantity),
        price: price === "" ? undefined : Number(price),
      });
      setResult(response);
      await reload();
    } catch (err) {
      setError(extractErrorMessage(err, "Order placement failed."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-full max-w-4xl space-y-5 font-mono text-terminal-text">
      <header className="border-b border-terminal-border pb-4">
        <div className="mb-2 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
          <ShoppingCart className="h-3.5 w-3.5 text-terminal-accent" />
          Trading sandbox
        </div>
        <h1 className="font-display text-xl font-bold uppercase tracking-[0.18em] text-terminal-accent">
          Paper Trading
        </h1>
        <p className="mt-1 max-w-2xl text-xs leading-relaxed text-terminal-muted">
          Submit simulated buy and sell orders against the current portfolio account.
        </p>
      </header>

      <div className="grid gap-5 xl:grid-cols-12">
        <aside className="space-y-5 xl:col-span-4">
          <section>
            <TerminalSectionHeader
              icon={Banknote}
              title="Account"
              subtitle="Available buying power"
            />
            <TerminalMetricCard
              label="Virtual cash"
              value={formatVnd(data?.account.virtualCash)}
              tone="accent"
            />
          </section>

          <section>
            <TerminalSectionHeader
              icon={side === "BUY" ? TrendingUp : TrendingDown}
              title="Order mode"
              subtitle="Choose execution side"
            />
            <div className="grid grid-cols-2 gap-2">
              <SideButton
                active={side === "BUY"}
                icon={TrendingUp}
                label="BUY"
                tone="success"
                onClick={() => setSide("BUY")}
              />
              <SideButton
                active={side === "SELL"}
                icon={TrendingDown}
                label="SELL"
                tone="danger"
                onClick={() => setSide("SELL")}
              />
            </div>
          </section>
        </aside>

        <section className="xl:col-span-8">
          <TerminalSectionHeader
            icon={Send}
            title="Order ticket"
            subtitle={side === "BUY" ? "Create a buy order" : "Create a sell order"}
          />

          <div className="rounded border border-terminal-border bg-terminal-surface p-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="Symbol">
                <TerminalInput
                  type="text"
                  value={symbol}
                  onChange={(event) => setSymbol(event.target.value.toUpperCase())}
                  placeholder="FPT"
                  maxLength={10}
                  className="uppercase"
                />
                {side === "SELL" && symbol.trim() && (
                  <p className="mt-1.5 text-[10px] text-terminal-muted">
                    Held quantity: <span className="text-terminal-text">{formatQty(heldQty)}</span>
                  </p>
                )}
              </Field>

              <Field label="Quantity">
                <TerminalInput
                  type="number"
                  min={1}
                  step={1}
                  value={quantity}
                  onChange={(event) => setQuantity(event.target.value)}
                />
              </Field>

              <Field label="Limit price">
                <TerminalInput
                  type="number"
                  min={0}
                  value={price}
                  onChange={(event) => setPrice(event.target.value)}
                  placeholder="Leave empty for default market price"
                />
              </Field>

              <div className="flex items-end">
                <TerminalButton
                  onClick={handleSubmit}
                  disabled={submitting || !user}
                  tone={side === "BUY" ? "success" : "danger"}
                  size="md"
                  className="w-full"
                >
                  <Send className="h-3.5 w-3.5" />
                  {submitting ? "Submitting" : side === "BUY" ? "Place buy order" : "Place sell order"}
                </TerminalButton>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              {error && <TerminalNotice tone="danger">{error}</TerminalNotice>}

              {result && (
                <TerminalNotice tone="success">
                  <p className="font-semibold">{result.message}</p>
                  <p className="mt-1 text-[10px] text-terminal-green/80">
                    Status: {result.status} / Order ID: {result.order_id}
                  </p>
                  <p className="mt-1 text-[10px] text-terminal-muted">
                    The order will fill when matching market data is available.
                  </p>
                </TerminalNotice>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1.5 block text-[10px] font-semibold uppercase tracking-wider text-terminal-muted">
        {label}
      </label>
      {children}
    </div>
  );
}

function SideButton({
  active,
  icon: Icon,
  label,
  tone,
  onClick,
}: {
  active: boolean;
  icon: React.ElementType;
  label: string;
  tone: "success" | "danger";
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        "flex h-16 flex-col items-center justify-center gap-1 rounded border font-mono text-[10px] font-semibold uppercase tracking-widest transition-colors",
        active && tone === "success" && "border-terminal-green/50 bg-terminal-green/10 text-terminal-green",
        active && tone === "danger" && "border-terminal-red/50 bg-terminal-red/10 text-terminal-red",
        !active && "border-terminal-border bg-terminal-surface text-terminal-muted hover:border-terminal-accent/30 hover:text-terminal-text"
      )}
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  );
}
