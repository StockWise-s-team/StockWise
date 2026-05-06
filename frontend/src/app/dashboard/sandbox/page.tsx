"use client";

import { useState } from "react";

export default function SandboxPage() {
  const [symbol, setSymbol] = useState("");
  const [quantity, setQuantity] = useState(1);

  const handleBuy = () => {};

  const handleSell = () => {};

  return (
    <div>
      <h1 className="mb-4 text-3xl font-bold">Paper Trading Sandbox</h1>
      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold">Place a Trade</h2>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label htmlFor="symbol" className="block text-sm font-medium">
              Symbol
            </label>
            <input
              id="symbol"
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              className="mt-1 w-32 rounded-md border px-3 py-2 text-sm"
              placeholder="AAPL"
            />
          </div>
          <div>
            <label htmlFor="quantity" className="block text-sm font-medium">
              Quantity
            </label>
            <input
              id="quantity"
              type="number"
              min={1}
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              className="mt-1 w-24 rounded-md border px-3 py-2 text-sm"
            />
          </div>
          <button
            onClick={handleBuy}
            className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
          >
            Buy
          </button>
          <button
            onClick={handleSell}
            className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Sell
          </button>
        </div>
      </div>
    </div>
  );
}
