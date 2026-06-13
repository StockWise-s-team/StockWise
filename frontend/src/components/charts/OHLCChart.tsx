"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { LineChart } from "lucide-react";
import type { OhlcPoint } from "@/lib/types";
import { TerminalEmptyState, TerminalSectionHeader } from "@/components/ui";

interface OHLCChartProps {
  symbol: string;
  data: OhlcPoint[];
}

const numberFormatter = new Intl.NumberFormat("vi-VN");

export function OHLCChart({ symbol, data }: OHLCChartProps) {
  return (
    <section>
      <TerminalSectionHeader
        icon={LineChart}
        title={`${symbol} Price Trend`}
        subtitle={data.length > 0 ? `${data.length} recent sessions` : "No chart data"}
      />

      <div className="h-72 rounded border border-terminal-border bg-terminal-surface p-3">
        {data.length === 0 ? (
          <TerminalEmptyState icon={LineChart} title="No OHLC data available" />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="closeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f0b429" stopOpacity={0.28} />
                  <stop offset="95%" stopColor="#f0b429" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
              <XAxis
                dataKey="date"
                tickFormatter={(value: string) => value.slice(5)}
                minTickGap={24}
                tick={{ fill: "#5c5c5c", fontSize: 10 }}
                axisLine={{ stroke: "#2a2a2a" }}
                tickLine={{ stroke: "#2a2a2a" }}
              />
              <YAxis
                tickFormatter={(value: number) => numberFormatter.format(value)}
                domain={["dataMin - 1000", "dataMax + 1000"]}
                width={80}
                tick={{ fill: "#5c5c5c", fontSize: 10 }}
                axisLine={{ stroke: "#2a2a2a" }}
                tickLine={{ stroke: "#2a2a2a" }}
              />
              <Tooltip
                formatter={(value: number, name: string) => [
                  numberFormatter.format(value),
                  name,
                ]}
                labelFormatter={(label: string) => `Date: ${label}`}
                contentStyle={{
                  background: "#141414",
                  border: "1px solid #2a2a2a",
                  borderRadius: 4,
                  color: "#d4d4d4",
                  fontFamily: "JetBrains Mono, Fira Code, Consolas, monospace",
                  fontSize: 11,
                }}
                labelStyle={{ color: "#f0b429" }}
              />
              <Area
                type="monotone"
                dataKey="close"
                stroke="#f0b429"
                strokeWidth={2}
                fill="url(#closeGradient)"
                activeDot={{ r: 5 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}
