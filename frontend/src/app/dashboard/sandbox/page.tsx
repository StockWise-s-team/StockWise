"use client";

import { useMemo, useState } from "react";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  CircleDollarSign,
  Clock3,
  FlaskConical,
  RotateCcw,
  ShieldCheck,
  WalletCards,
} from "lucide-react";
import { clsx } from "clsx";

type Side = "BUY" | "SELL";
type OrderType = "MARKET" | "LIMIT";

type Market = {
  symbol: string;
  name: string;
  price: number;
  change: number;
  bid: number;
  ask: number;
  volume: string;
};

type Position = {
  symbol: string;
  quantity: number;
  avgPrice: number;
};

type Order = {
  id: number;
  symbol: string;
  side: Side;
  quantity: number;
  price: number;
  type: OrderType;
  time: string;
};

const markets: Market[] = [
  {
    symbol: "AAPL",
    name: "Apple Inc.",
    price: 198.42,
    change: 1.84,
    bid: 198.39,
    ask: 198.45,
    volume: "42.8M",
  },
  {
    symbol: "NVDA",
    name: "NVIDIA Corp.",
    price: 141.72,
    change: 3.12,
    bid: 141.68,
    ask: 141.76,
    volume: "289.4M",
  },
  {
    symbol: "MSFT",
    name: "Microsoft Corp.",
    price: 448.37,
    change: -0.63,
    bid: 448.31,
    ask: 448.42,
    volume: "18.2M",
  },
  {
    symbol: "TSLA",
    name: "Tesla Inc.",
    price: 352.56,
    change: -2.17,
    bid: 352.49,
    ask: 352.63,
    volume: "91.7M",
  },
];

const initialPositions: Position[] = [
  { symbol: "AAPL", quantity: 12, avgPrice: 184.2 },
  { symbol: "NVDA", quantity: 8, avgPrice: 128.6 },
  { symbol: "MSFT", quantity: 3, avgPrice: 421.15 },
];

const initialOrders: Order[] = [
  {
    id: 3,
    symbol: "NVDA",
    side: "BUY",
    quantity: 4,
    price: 138.24,
    type: "LIMIT",
    time: "10:42:08",
  },
  {
    id: 2,
    symbol: "AAPL",
    side: "SELL",
    quantity: 2,
    price: 196.81,
    type: "MARKET",
    time: "09:58:31",
  },
  {
    id: 1,
    symbol: "MSFT",
    side: "BUY",
    quantity: 3,
    price: 421.15,
    type: "MARKET",
    time: "09:31:12",
  },
];

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

function SectionHeader({
  icon: Icon,
  title,
  subtitle,
}: {
  icon: React.ElementType;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="mb-4 flex items-center gap-3 border-b border-terminal-border pb-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
        <Icon className="h-4 w-4 text-terminal-accent" />
      </div>
      <div className="min-w-0">
        <h2 className="font-mono text-sm font-semibold uppercase tracking-widest text-terminal-text">
          {title}
        </h2>
        <p className="truncate font-mono text-[10px] text-terminal-muted">
          {subtitle}
        </p>
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  detail,
  tone = "default",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "default" | "positive";
}) {
  return (
    <div className="border-l border-terminal-border pl-3 first:border-l-0 first:pl-0 sm:pl-4">
      <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-terminal-muted">
        {label}
      </p>
      <p
        className={clsx(
          "mt-1 font-mono text-sm font-semibold tabular-nums",
          tone === "positive" ? "text-terminal-green" : "text-terminal-text"
        )}
      >
        {value}
      </p>
      <p className="mt-0.5 font-mono text-[9px] text-terminal-muted">
        {detail}
      </p>
    </div>
  );
}

export default function SandboxPage() {
  const [selectedSymbol, setSelectedSymbol] = useState("AAPL");
  const [side, setSide] = useState<Side>("BUY");
  const [orderType, setOrderType] = useState<OrderType>("MARKET");
  const [quantity, setQuantity] = useState(5);
  const [limitPrice, setLimitPrice] = useState(markets[0].price);
  const [buyingPower, setBuyingPower] = useState(25_000);
  const [positions, setPositions] = useState(initialPositions);
  const [orders, setOrders] = useState(initialOrders);
  const [message, setMessage] = useState(
    "Sandbox ready. Orders execute against simulated quotes."
  );
  const [messageTone, setMessageTone] = useState<"neutral" | "success" | "error">(
    "neutral"
  );

  const market =
    markets.find((item) => item.symbol === selectedSymbol) ?? markets[0];
  const executionPrice = orderType === "MARKET" ? market.price : limitPrice;
  const estimatedValue = executionPrice * Math.max(quantity, 0);
  const currentPosition = positions.find(
    (position) => position.symbol === selectedSymbol
  );

  const marketValue = useMemo(
    () =>
      positions.reduce((total, position) => {
        const quote = markets.find((item) => item.symbol === position.symbol);
        return total + position.quantity * (quote?.price ?? position.avgPrice);
      }, 0),
    [positions]
  );

  const dayPnl = useMemo(
    () =>
      positions.reduce((total, position) => {
        const quote = markets.find((item) => item.symbol === position.symbol);
        if (!quote) return total;
        const previousClose = quote.price / (1 + quote.change / 100);
        return total + (quote.price - previousClose) * position.quantity;
      }, 0),
    [positions]
  );

  const selectMarket = (item: Market) => {
    setSelectedSymbol(item.symbol);
    setLimitPrice(item.price);
    setMessage(`${item.symbol} quote loaded at ${currency.format(item.price)}.`);
    setMessageTone("neutral");
  };

  const resetSandbox = () => {
    setSelectedSymbol("AAPL");
    setSide("BUY");
    setOrderType("MARKET");
    setQuantity(5);
    setLimitPrice(markets[0].price);
    setBuyingPower(25_000);
    setPositions(initialPositions);
    setOrders(initialOrders);
    setMessage("Sandbox reset to the opening paper account snapshot.");
    setMessageTone("neutral");
  };

  const placeOrder = () => {
    if (!Number.isFinite(quantity) || quantity < 1) {
      setMessage("Quantity must be at least 1 share.");
      setMessageTone("error");
      return;
    }

    if (!Number.isFinite(executionPrice) || executionPrice <= 0) {
      setMessage("Enter a valid limit price.");
      setMessageTone("error");
      return;
    }

    if (side === "BUY" && estimatedValue > buyingPower) {
      setMessage(
        `Insufficient buying power. Required ${currency.format(estimatedValue)}.`
      );
      setMessageTone("error");
      return;
    }

    if (side === "SELL" && (currentPosition?.quantity ?? 0) < quantity) {
      setMessage(
        `Cannot sell ${quantity} shares. Current position: ${
          currentPosition?.quantity ?? 0
        }.`
      );
      setMessageTone("error");
      return;
    }

    setBuyingPower((current) =>
      side === "BUY" ? current - estimatedValue : current + estimatedValue
    );

    setPositions((current) => {
      const existing = current.find(
        (position) => position.symbol === selectedSymbol
      );

      if (side === "BUY") {
        if (!existing) {
          return [
            ...current,
            {
              symbol: selectedSymbol,
              quantity,
              avgPrice: executionPrice,
            },
          ];
        }

        const nextQuantity = existing.quantity + quantity;
        const nextAverage =
          (existing.quantity * existing.avgPrice + estimatedValue) /
          nextQuantity;
        return current.map((position) =>
          position.symbol === selectedSymbol
            ? {
                ...position,
                quantity: nextQuantity,
                avgPrice: nextAverage,
              }
            : position
        );
      }

      if (!existing || existing.quantity === quantity) {
        return current.filter(
          (position) => position.symbol !== selectedSymbol
        );
      }

      return current.map((position) =>
        position.symbol === selectedSymbol
          ? { ...position, quantity: position.quantity - quantity }
          : position
      );
    });

    const order: Order = {
      id: Date.now(),
      symbol: selectedSymbol,
      side,
      quantity,
      price: executionPrice,
      type: orderType,
      time: new Date().toLocaleTimeString("en-US", { hour12: false }),
    };

    setOrders((current) => [order, ...current].slice(0, 8));
    setMessage(
      `${side} ${quantity} ${selectedSymbol} filled at ${currency.format(
        executionPrice
      )}.`
    );
    setMessageTone("success");
  };

  return (
    <div
      className="min-h-full bg-terminal-bg font-mono text-terminal-text"
      style={{
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
      }}
    >
      <header className="mb-5 flex flex-col gap-4 border-b border-terminal-border pb-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-terminal-accent">
            <FlaskConical className="h-3.5 w-3.5" />
            Paper environment / live simulation
          </div>
          <h1 className="font-display text-xl font-bold uppercase tracking-[0.14em] text-terminal-text">
            Trading Sandbox
          </h1>
          <p className="mt-1 max-w-2xl font-mono text-[10px] leading-relaxed text-terminal-muted">
            Test order decisions against simulated market data. No real capital
            is used and every fill can be reset.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 rounded border border-terminal-green/30 bg-terminal-green/5 px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-terminal-green">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-terminal-green" />
            Market feed online
          </span>
          <button
            type="button"
            onClick={resetSandbox}
            className="inline-flex items-center gap-1.5 rounded border border-terminal-border px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-terminal-muted transition-colors hover:border-terminal-accent/40 hover:text-terminal-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-terminal-accent/40"
          >
            <RotateCcw className="h-3 w-3" />
            Reset
          </button>
        </div>
      </header>

      <section
        aria-label="Paper account summary"
        className="mb-5 grid grid-cols-2 gap-x-3 gap-y-4 border-b border-terminal-border pb-5 sm:grid-cols-4 sm:gap-x-4"
      >
        <Metric
          label="Net liquidation"
          value={currency.format(buyingPower + marketValue)}
          detail="Paper account"
        />
        <Metric
          label="Buying power"
          value={currency.format(buyingPower)}
          detail="Cash available"
        />
        <Metric
          label="Market value"
          value={currency.format(marketValue)}
          detail={`${positions.length} open positions`}
        />
        <Metric
          label="Day P&L"
          value={`+${currency.format(dayPnl)}`}
          detail="+1.34% today"
          tone="positive"
        />
      </section>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-12">
        <div className="space-y-5 xl:col-span-5">
          <section>
            <SectionHeader
              icon={Activity}
              title="Market Watch"
              subtitle="Select an instrument for the order ticket"
            />
            <div className="space-y-1">
              {markets.map((item) => {
                const selected = item.symbol === selectedSymbol;
                const positive = item.change >= 0;
                return (
                  <button
                    type="button"
                    key={item.symbol}
                    onClick={() => selectMarket(item)}
                    className={clsx(
                      "grid w-full grid-cols-[1fr_auto_auto] items-center gap-3 rounded border px-3 py-2.5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-terminal-accent/40",
                      selected
                        ? "border-terminal-accent/50 bg-terminal-accent/5"
                        : "border-terminal-border bg-terminal-surface hover:border-terminal-accent/30"
                    )}
                  >
                    <span className="min-w-0">
                      <span
                        className={clsx(
                          "block text-xs font-bold tracking-wider",
                          selected
                            ? "text-terminal-accent"
                            : "text-terminal-text"
                        )}
                      >
                        {item.symbol}
                      </span>
                      <span className="block truncate text-[9px] text-terminal-muted">
                        {item.name}
                      </span>
                    </span>
                    <span className="text-right">
                      <span className="block text-xs font-semibold tabular-nums text-terminal-text">
                        {currency.format(item.price)}
                      </span>
                      <span className="block text-[9px] text-terminal-muted">
                        Vol {item.volume}
                      </span>
                    </span>
                    <span
                      className={clsx(
                        "inline-flex min-w-[58px] items-center justify-end gap-1 text-[10px] font-semibold tabular-nums",
                        positive ? "text-terminal-green" : "text-terminal-red"
                      )}
                    >
                      {positive ? (
                        <ArrowUpRight className="h-3 w-3" />
                      ) : (
                        <ArrowDownRight className="h-3 w-3" />
                      )}
                      {positive ? "+" : ""}
                      {item.change.toFixed(2)}%
                    </span>
                  </button>
                );
              })}
            </div>
          </section>

          <section>
            <SectionHeader
              icon={BarChart3}
              title="Quote Snapshot"
              subtitle={`${market.symbol} consolidated simulated quote`}
            />
            <div className="grid grid-cols-3 gap-2">
              {[
                { label: "Bid", value: market.bid },
                { label: "Last", value: market.price },
                { label: "Ask", value: market.ask },
              ].map((quote) => (
                <div
                  key={quote.label}
                  className="rounded border border-terminal-border bg-terminal-surface px-2 py-2 text-center"
                >
                  <p className="text-[9px] uppercase tracking-wider text-terminal-muted">
                    {quote.label}
                  </p>
                  <p className="mt-1 text-xs font-semibold tabular-nums text-terminal-text">
                    {quote.value.toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <div className="space-y-5 xl:col-span-7">
          <section>
            <SectionHeader
              icon={CircleDollarSign}
              title="Order Ticket"
              subtitle={`Route a simulated order for ${market.symbol}`}
            />

            <div className="rounded border border-terminal-border bg-terminal-surface p-3 sm:p-4">
              <div className="mb-4 grid grid-cols-2 gap-1 rounded border border-terminal-border bg-terminal-bg p-1">
                {(["BUY", "SELL"] as Side[]).map((item) => (
                  <button
                    type="button"
                    key={item}
                    onClick={() => setSide(item)}
                    className={clsx(
                      "rounded border py-2 text-[10px] font-semibold uppercase tracking-[0.18em] transition-colors focus-visible:outline-none focus-visible:ring-2",
                      side === item && item === "BUY"
                        ? "border-terminal-green/40 bg-terminal-green/10 text-terminal-green focus-visible:ring-terminal-green/40"
                        : side === item && item === "SELL"
                          ? "border-terminal-red/40 bg-terminal-red/10 text-terminal-red focus-visible:ring-terminal-red/40"
                          : "border-transparent text-terminal-muted hover:text-terminal-text focus-visible:ring-terminal-accent/40"
                    )}
                  >
                    {item}
                  </button>
                ))}
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="order-type"
                    className="mb-1.5 block text-[9px] uppercase tracking-[0.16em] text-terminal-muted"
                  >
                    Order type
                  </label>
                  <select
                    id="order-type"
                    value={orderType}
                    onChange={(event) =>
                      setOrderType(event.target.value as OrderType)
                    }
                    className="h-9 w-full rounded border border-terminal-border bg-terminal-bg px-2.5 text-xs text-terminal-text outline-none transition-colors focus:border-terminal-accent/60"
                  >
                    <option value="MARKET">Market</option>
                    <option value="LIMIT">Limit</option>
                  </select>
                </div>
                <div>
                  <label
                    htmlFor="quantity"
                    className="mb-1.5 block text-[9px] uppercase tracking-[0.16em] text-terminal-muted"
                  >
                    Quantity
                  </label>
                  <div className="relative">
                    <input
                      id="quantity"
                      type="number"
                      min={1}
                      step={1}
                      value={quantity}
                      onChange={(event) =>
                        setQuantity(Number(event.target.value))
                      }
                      className="h-9 w-full rounded border border-terminal-border bg-terminal-bg px-2.5 pr-14 text-xs tabular-nums text-terminal-text outline-none transition-colors focus:border-terminal-accent/60"
                    />
                    <span className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-[9px] uppercase text-terminal-muted">
                      Shares
                    </span>
                  </div>
                </div>
                <div>
                  <label
                    htmlFor="limit-price"
                    className="mb-1.5 block text-[9px] uppercase tracking-[0.16em] text-terminal-muted"
                  >
                    Limit price
                  </label>
                  <div className="relative">
                    <span className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-terminal-muted">
                      $
                    </span>
                    <input
                      id="limit-price"
                      type="number"
                      min={0.01}
                      step={0.01}
                      value={limitPrice}
                      disabled={orderType === "MARKET"}
                      onChange={(event) =>
                        setLimitPrice(Number(event.target.value))
                      }
                      className="h-9 w-full rounded border border-terminal-border bg-terminal-bg px-6 text-xs tabular-nums text-terminal-text outline-none transition-colors focus:border-terminal-accent/60 disabled:cursor-not-allowed disabled:opacity-40"
                    />
                  </div>
                </div>
                <div>
                  <span className="mb-1.5 block text-[9px] uppercase tracking-[0.16em] text-terminal-muted">
                    Current position
                  </span>
                  <div className="flex h-9 items-center justify-between rounded border border-terminal-border bg-terminal-bg px-2.5">
                    <span className="text-xs font-semibold text-terminal-text">
                      {currentPosition?.quantity ?? 0} shares
                    </span>
                    <span className="text-[9px] text-terminal-muted">
                      {currentPosition
                        ? `AVG ${currentPosition.avgPrice.toFixed(2)}`
                        : "NO POSITION"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="my-4 border-t border-terminal-border" />

              <div className="mb-3 flex items-end justify-between">
                <div>
                  <p className="text-[9px] uppercase tracking-[0.16em] text-terminal-muted">
                    Estimated value
                  </p>
                  <p className="mt-1 text-base font-semibold tabular-nums text-terminal-text">
                    {currency.format(
                      Number.isFinite(estimatedValue) ? estimatedValue : 0
                    )}
                  </p>
                </div>
                <div className="text-right text-[9px] leading-relaxed text-terminal-muted">
                  <p>Commission $0.00</p>
                  <p>Simulated fill only</p>
                </div>
              </div>

              <button
                type="button"
                onClick={placeOrder}
                className={clsx(
                  "flex w-full items-center justify-center gap-2 rounded border px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.18em] transition-colors focus-visible:outline-none focus-visible:ring-2",
                  side === "BUY"
                    ? "border-terminal-green/50 bg-terminal-green/10 text-terminal-green hover:bg-terminal-green/20 focus-visible:ring-terminal-green/40"
                    : "border-terminal-red/50 bg-terminal-red/10 text-terminal-red hover:bg-terminal-red/20 focus-visible:ring-terminal-red/40"
                )}
              >
                {side === "BUY" ? (
                  <ArrowUpRight className="h-3.5 w-3.5" />
                ) : (
                  <ArrowDownRight className="h-3.5 w-3.5" />
                )}
                Review &amp; place {side.toLowerCase()} order
              </button>
            </div>

            <div
              role="status"
              aria-live="polite"
              className={clsx(
                "mt-2 flex items-center gap-2 rounded border px-2.5 py-2 text-[10px]",
                messageTone === "success" &&
                  "border-terminal-green/20 bg-terminal-green/5 text-terminal-green",
                messageTone === "error" &&
                  "border-terminal-red/20 bg-terminal-red/5 text-terminal-red",
                messageTone === "neutral" &&
                  "border-terminal-border bg-terminal-surface text-terminal-muted"
              )}
            >
              {messageTone === "success" ? (
                <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
              ) : (
                <ShieldCheck className="h-3.5 w-3.5 shrink-0" />
              )}
              {message}
            </div>
          </section>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-1 gap-5 xl:grid-cols-12">
        <section className="xl:col-span-7">
          <SectionHeader
            icon={WalletCards}
            title="Open Positions"
            subtitle="Mark-to-market paper holdings"
          />
          <div className="overflow-x-auto">
            <div className="min-w-[620px]">
              <div className="grid grid-cols-[1.3fr_.8fr_1fr_1fr_1fr] gap-3 border-b border-terminal-border px-3 pb-2 text-[9px] uppercase tracking-wider text-terminal-muted">
                <span>Instrument</span>
                <span className="text-right">Qty</span>
                <span className="text-right">Avg price</span>
                <span className="text-right">Market value</span>
                <span className="text-right">Unrealized</span>
              </div>
              <div className="mt-1 space-y-1">
                {positions.map((position) => {
                  const quote = markets.find(
                    (item) => item.symbol === position.symbol
                  );
                  const price = quote?.price ?? position.avgPrice;
                  const pnl = (price - position.avgPrice) * position.quantity;
                  return (
                    <button
                      type="button"
                      key={position.symbol}
                      onClick={() => {
                        if (quote) selectMarket(quote);
                      }}
                      className="grid w-full grid-cols-[1.3fr_.8fr_1fr_1fr_1fr] items-center gap-3 rounded border border-terminal-border bg-terminal-surface px-3 py-2.5 text-left transition-colors hover:border-terminal-accent/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-terminal-accent/40"
                    >
                      <span>
                        <span className="block text-xs font-bold text-terminal-text">
                          {position.symbol}
                        </span>
                        <span className="text-[9px] text-terminal-muted">
                          {quote?.name ?? "Paper asset"}
                        </span>
                      </span>
                      <span className="text-right text-xs tabular-nums text-terminal-text">
                        {position.quantity}
                      </span>
                      <span className="text-right text-xs tabular-nums text-terminal-muted">
                        {currency.format(position.avgPrice)}
                      </span>
                      <span className="text-right text-xs tabular-nums text-terminal-text">
                        {currency.format(price * position.quantity)}
                      </span>
                      <span
                        className={clsx(
                          "text-right text-xs font-semibold tabular-nums",
                          pnl >= 0
                            ? "text-terminal-green"
                            : "text-terminal-red"
                        )}
                      >
                        {pnl >= 0 ? "+" : ""}
                        {currency.format(pnl)}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        <section className="xl:col-span-5">
          <SectionHeader
            icon={Clock3}
            title="Order Log"
            subtitle="Most recent simulated fills"
          />
          <div className="space-y-1">
            {orders.map((order) => (
              <div
                key={order.id}
                className="grid grid-cols-[auto_1fr_auto] items-center gap-3 rounded border border-terminal-border bg-terminal-surface px-3 py-2.5"
              >
                <span
                  className={clsx(
                    "rounded border px-1.5 py-0.5 text-[9px] font-semibold",
                    order.side === "BUY"
                      ? "border-terminal-green/30 bg-terminal-green/5 text-terminal-green"
                      : "border-terminal-red/30 bg-terminal-red/5 text-terminal-red"
                  )}
                >
                  {order.side}
                </span>
                <span>
                  <span className="block text-xs font-semibold text-terminal-text">
                    {order.quantity} {order.symbol}
                  </span>
                  <span className="text-[9px] text-terminal-muted">
                    {order.type} / {order.time}
                  </span>
                </span>
                <span className="text-right text-xs font-semibold tabular-nums text-terminal-text">
                  {currency.format(order.price)}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
