"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Banknote, History, Send, ShoppingCart, TrendingDown, TrendingUp, XCircle } from "lucide-react";
import { clsx } from "clsx";
import { useAuth } from "@/components/providers/AuthProvider";
import { usePortfolio } from "@/hooks/usePortfolio";
import { portfolioGateway } from "@/lib/portfolio/gateway";
import { validateOrderForm } from "@/lib/portfolio/orderValidation";
import { extractErrorMessage } from "@/lib/apiError";
import { formatVnd, formatQty, formatDateTime } from "@/lib/format";
import { trackedSymbolsApi } from "@/lib/api";
import type { OrderResult, OrderSide, OrderStatus, PortfolioOrder } from "@/lib/types";
import { MultiSymbolChart } from "@/components/charts/MultiSymbolChart";
import {
  TerminalButton,
  TerminalEmptyState,
  TerminalInput,
  TerminalSelect,
  TerminalMetricCard,
  TerminalNotice,
  TerminalSectionHeader,
  TerminalSkeletonRows,
  TerminalTable,
} from "@/components/ui";
import { Suspense } from "react";

function SandboxContent() {
  const { user } = useAuth();
  const { data, reload } = usePortfolio(user?.id);
  const searchParams = useSearchParams();
  const symbolFromQuery = searchParams.get("symbol") || "";

  const [trackedSymbols, setTrackedSymbols] = useState<string[]>([]);
  const [symbol, setSymbol] = useState("");

  useEffect(() => {
    trackedSymbolsApi.list()
      .then((symbols) => {
        setTrackedSymbols(symbols);
        if (symbolFromQuery && symbols.includes(symbolFromQuery)) {
          setSymbol(symbolFromQuery);
        } else if (symbols.length > 0) {
          setSymbol(symbols[0]);
        }
      })
      .catch(() => {});
  }, [symbolFromQuery]);
  const [side, setSide] = useState<OrderSide>("BUY");
  const [quantity, setQuantity] = useState("100");
  const [price, setPrice] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<OrderResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [orders, setOrders] = useState<PortfolioOrder[]>([]);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [ordersError, setOrdersError] = useState<string | null>(null);
  const [cancelingOrderId, setCancelingOrderId] = useState<string | null>(null);

  const loadOrders = useCallback(async () => {
    if (!user?.id) {
      setOrders([]);
      return;
    }
    setOrdersLoading(true);
    setOrdersError(null);
    try {
      setOrders(await portfolioGateway.getOrders());
    } catch (err) {
      setOrdersError(extractErrorMessage(err, "Order history could not be loaded."));
    } finally {
      setOrdersLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    void loadOrders();
  }, [loadOrders]);

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
      await loadOrders();
    } catch (err) {
      setError(extractErrorMessage(err, "Order placement failed."));
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async (orderId: string) => {
    setError(null);
    setOrdersError(null);
    setCancelingOrderId(orderId);
    try {
      const response = await portfolioGateway.cancelOrder(orderId);
      setResult(response);
      await reload();
      await loadOrders();
    } catch (err) {
      setOrdersError(extractErrorMessage(err, "Order cancellation failed."));
    } finally {
      setCancelingOrderId(null);
    }
  };

  return (
    <div className="min-h-full w-full space-y-5 font-mono text-terminal-text">
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
        {/* Left column — order ticket + account */}
        <section className="xl:col-span-3 space-y-5">
          <TerminalSectionHeader
            icon={Banknote}
            title="Account"
            subtitle="Available buying power"
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <TerminalMetricCard
              label="Virtual cash"
              value={formatVnd(data?.account.virtualCash)}
              tone="accent"
            />
            <TerminalMetricCard
              label="Active symbol"
              value={symbol || "—"}
              tone="default"
            />
          </div>

          <div>
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
          </div>

          <div>
            <TerminalSectionHeader
              icon={Send}
              title="Order ticket"
              subtitle={side === "BUY" ? "Create a buy order" : "Create a sell order"}
            />

            <div className="rounded border border-terminal-border bg-terminal-surface p-4">
              <div className="grid gap-4 md:grid-cols-2">
                <Field label="Symbol">
                  <TerminalSelect
                    value={symbol}
                    onChange={(event) => setSymbol(event.target.value)}
                  >
                    {trackedSymbols.length === 0 && (
                      <option value="">No tracked symbols</option>
                    )}
                    {trackedSymbols.map((sym) => (
                      <option key={sym} value={sym} className="bg-terminal-surface text-terminal-text">
                        {sym}
                      </option>
                    ))}
                  </TerminalSelect>
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
                    {result.status === "PENDING" && (
                      <p className="mt-1 text-[10px] text-terminal-muted">
                        The order will fill when matching market data is available.
                      </p>
                    )}
                  </TerminalNotice>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Right column — chart stays in view while placing orders */}
        <aside className="xl:col-span-7">
          <div className="xl:sticky xl:top-4">
            <MultiSymbolChart
              symbols={trackedSymbols}
              defaultSymbol={symbolFromQuery || symbol}
            />
          </div>
        </aside>
      </div>

      <section>
        <TerminalSectionHeader
          icon={History}
          title="Order history"
          subtitle={`${orders.length} submitted orders`}
          action={
            <TerminalButton onClick={() => void loadOrders()} disabled={ordersLoading || !user} tone="muted">
              Refresh
            </TerminalButton>
          }
        />

        {ordersError && <TerminalNotice tone="danger" className="mb-3">{ordersError}</TerminalNotice>}

        {ordersLoading && orders.length === 0 ? (
          <TerminalSkeletonRows rows={4} />
        ) : orders.length === 0 ? (
          <TerminalEmptyState
            icon={History}
            title="No submitted orders"
            description="Orders placed from this sandbox will appear here."
          />
        ) : (
          <TerminalTable
            headers={[
              { label: "Time" },
              { label: "Symbol" },
              { label: "Side" },
              { label: "Quantity", align: "right" },
              { label: "Limit price", align: "right" },
              { label: "Status" },
              { label: "Action", align: "right" },
            ]}
          >
            {orders.map((order) => (
              <tr
                key={order.id}
                className="border-b border-terminal-border/60 transition-colors hover:bg-terminal-bg"
              >
                <td className="px-3 py-2.5 text-terminal-muted">{formatDateTime(order.createdAt)}</td>
                <td className="px-3 py-2.5 font-semibold text-terminal-accent">{order.symbol}</td>
                <td className="px-3 py-2.5">
                  <span className={order.type === "BUY" ? "text-terminal-green" : "text-terminal-red"}>
                    {order.type}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-right text-terminal-text">{formatQty(order.quantity)}</td>
                <td className="px-3 py-2.5 text-right text-terminal-text">{formatVnd(order.price)}</td>
                <td className="px-3 py-2.5">
                  <OrderStatusBadge status={order.status} />
                </td>
                <td className="px-3 py-2.5 text-right">
                  {order.status === "PENDING" ? (
                    <TerminalButton
                      onClick={() => handleCancel(order.id)}
                      disabled={cancelingOrderId === order.id}
                      tone="danger"
                      size="xs"
                    >
                      <XCircle className="h-3 w-3" />
                      {cancelingOrderId === order.id ? "Canceling" : "Cancel"}
                    </TerminalButton>
                  ) : (
                    <span className="text-terminal-muted">--</span>
                  )}
                </td>
              </tr>
            ))}
          </TerminalTable>
        )}
      </section>
    </div>
  );
}

export default function SandboxPage() {
  return (
    <Suspense fallback={<div className="p-4 font-mono text-sm text-terminal-muted">Loading sandbox...</div>}>
      <SandboxContent />
    </Suspense>
  );
}

function OrderStatusBadge({ status }: { status: OrderStatus }) {
  return (
    <span
      className={clsx(
        "inline-flex rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider",
        status === "PENDING" && "border-terminal-amber/30 bg-terminal-amber/5 text-terminal-amber",
        status === "FILLED" && "border-terminal-green/30 bg-terminal-green/5 text-terminal-green",
        status === "CANCELLED" && "border-terminal-border bg-terminal-bg text-terminal-muted"
      )}
    >
      {status}
    </span>
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
