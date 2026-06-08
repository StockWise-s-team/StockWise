"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { OhlcPoint } from "@/lib/types";

interface OHLCChartProps {
  symbol: string;
  data: OhlcPoint[];
}

const numberFormatter = new Intl.NumberFormat("vi-VN");

export function OHLCChart({ symbol, data }: OHLCChartProps) {
  return (
    <div className="rounded-lg border bg-card p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">{symbol} Price Trend</h3>
          <p className="text-sm text-muted-foreground">
            {data.length > 0
              ? `${data.length} phiên gần nhất`
              : "Chưa có dữ liệu biểu đồ"}
          </p>
        </div>
      </div>

      <div className="h-72">
        {data.length === 0 ? (
          <div className="flex h-full items-center justify-center text-muted-foreground">
            <p>No OHLC data available</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="closeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis
                dataKey="date"
                tickFormatter={(value: string) => value.slice(5)}
                minTickGap={24}
              />
              <YAxis
                tickFormatter={(value: number) => numberFormatter.format(value)}
                domain={["dataMin - 1000", "dataMax + 1000"]}
                width={80}
              />
              <Tooltip
                formatter={(value: number, name: string) => [numberFormatter.format(value), name]}
                labelFormatter={(label: string) => `Ngày: ${label}`}
              />
              <Area
                type="monotone"
                dataKey="close"
                stroke="#2563eb"
                strokeWidth={2}
                fill="url(#closeGradient)"
                activeDot={{ r: 5 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
