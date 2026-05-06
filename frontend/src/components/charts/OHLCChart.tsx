"use client";

import React from "react";
import type { OHLCV } from "@/lib/types";

interface OHLCChartProps {
  data: OHLCV[];
}

export function OHLCChart({ data }: OHLCChartProps) {
  return (
    <div className="rounded-lg border bg-card p-4 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">
        {data.length > 0 ? data[0].symbol : "OHLC"} Chart
      </h3>
      <div className="flex h-64 items-center justify-center text-muted-foreground">
        {data.length === 0 ? (
          <p>No data available</p>
        ) : (
          <div className="text-center">
            <p>Chart placeholder</p>
            <p className="text-xs">{data.length} data points loaded</p>
          </div>
        )}
      </div>
    </div>
  );
}
