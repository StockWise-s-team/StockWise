"use client";

import { useMemo, useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import { usePortfolio } from "@/hooks/usePortfolio";
import { portfolioGateway } from "@/lib/portfolio/gateway";
import { validateOrderForm } from "@/lib/portfolio/orderValidation";
import { extractErrorMessage } from "@/lib/apiError";
import { formatVnd, formatQty } from "@/lib/format";
import type { OrderResult, OrderSide } from "@/lib/types";

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

  // Holding for the typed symbol — used to surface how many shares are sellable.
  const heldQty = useMemo(() => {
    const s = symbol.trim().toUpperCase();
    return data?.holdings.find((h) => h.symbol === s)?.quantity ?? 0;
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
      const res = await portfolioGateway.placeOrder({
        symbol: symbol.trim().toUpperCase(),
        type: side,
        quantity: Number(quantity),
        price: price === "" ? undefined : Number(price),
      });
      setResult(res);
      await reload();
    } catch (e) {
      setError(extractErrorMessage(e, "Đặt lệnh thất bại."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold text-body">Paper Trading Sandbox</h1>

      <div className="rounded-lg border border-hairline-on-dark bg-surface-card-dark p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-body">Đặt lệnh</h2>
          <span className="text-sm text-muted-strong">
            Tiền ảo: <span className="text-body">{formatVnd(data?.account.virtualCash)}</span>
          </span>
        </div>

        {/* BUY / SELL toggle */}
        <div className="mb-5 grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => setSide("BUY")}
            className={`h-10 rounded-md text-sm font-semibold transition-colors ${
              side === "BUY"
                ? "bg-trading-up text-canvas-dark"
                : "border border-hairline-on-dark text-muted-strong hover:text-body"
            }`}
          >
            Mua (BUY)
          </button>
          <button
            type="button"
            onClick={() => setSide("SELL")}
            className={`h-10 rounded-md text-sm font-semibold transition-colors ${
              side === "SELL"
                ? "bg-trading-down text-on-dark"
                : "border border-hairline-on-dark text-muted-strong hover:text-body"
            }`}
          >
            Bán (SELL)
          </button>
        </div>

        <div className="space-y-4">
          <Field label="Mã cổ phiếu">
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="VD: FPT"
              className={inputClass}
            />
            {side === "SELL" && symbol.trim() && (
              <p className="mt-1 text-xs text-muted">Đang giữ: {formatQty(heldQty)} cổ phiếu</p>
            )}
          </Field>

          <Field label="Số lượng">
            <input
              type="number"
              min={1}
              step={1}
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className={inputClass}
            />
          </Field>

          <Field label="Giá đặt (limit) — để trống nếu dùng giá mặc định">
            <input
              type="number"
              min={0}
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder="VD: 100000"
              className={inputClass}
            />
          </Field>

          <button
            onClick={handleSubmit}
            disabled={submitting || !user}
            className={`h-11 w-full rounded-md text-sm font-semibold transition-colors disabled:opacity-50 ${
              side === "BUY"
                ? "bg-trading-up text-canvas-dark hover:opacity-90"
                : "bg-trading-down text-on-dark hover:opacity-90"
            }`}
          >
            {submitting ? "Đang gửi…" : side === "BUY" ? "Đặt lệnh mua" : "Đặt lệnh bán"}
          </button>
        </div>

        {error && (
          <div className="mt-4 rounded-md border border-trading-down/30 bg-trading-down/10 px-4 py-3 text-sm text-trading-down">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-4 rounded-md border border-trading-up/30 bg-trading-up/10 px-4 py-3 text-sm text-trading-up">
            <p className="font-medium">{result.message}</p>
            <p className="mt-1 text-xs text-muted-strong">
              Trạng thái: {result.status} · Mã lệnh: {result.order_id}
            </p>
            <p className="mt-1 text-xs text-muted">
              Lệnh sẽ khớp khi có giá thị trường phù hợp. Danh mục cập nhật sau khi khớp.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

const inputClass =
  "h-10 w-full rounded-md border border-hairline-on-dark bg-canvas-dark px-3 text-sm text-body transition-colors focus:border-primary focus:outline-none";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-muted-strong">{label}</label>
      {children}
    </div>
  );
}
