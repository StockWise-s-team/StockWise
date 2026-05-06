import type { Holding } from "@/lib/types";

const mockHoldings: Holding[] = [
  { symbol: "AAPL", quantity: 10, avgPrice: 175.5 },
  { symbol: "GOOGL", quantity: 5, avgPrice: 140.2 },
];

export default function PortfolioPage() {
  return (
    <div>
      <h1 className="mb-4 text-3xl font-bold">Portfolio</h1>
      <div className="rounded-lg border bg-card shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left font-medium">Symbol</th>
                <th className="px-4 py-3 text-right font-medium">Quantity</th>
                <th className="px-4 py-3 text-right font-medium">
                  Avg Price
                </th>
                <th className="px-4 py-3 text-right font-medium">Value</th>
              </tr>
            </thead>
            <tbody>
              {mockHoldings.map((h) => (
                <tr key={h.symbol} className="border-b">
                  <td className="px-4 py-3 font-medium">{h.symbol}</td>
                  <td className="px-4 py-3 text-right">{h.quantity}</td>
                  <td className="px-4 py-3 text-right">
                    ${h.avgPrice.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    ${(h.quantity * h.avgPrice).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
