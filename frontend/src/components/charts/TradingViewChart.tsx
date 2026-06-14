"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  ColorType,
  IChartApi,
  CandlestickData,
  HistogramData,
  CandlestickSeries,
  HistogramSeries,
} from "lightweight-charts";
import type { OhlcPoint } from "@/lib/types";

interface TradingViewChartProps {
  symbol: string;
  data: OhlcPoint[];
}

export default function TradingViewChart({ symbol, data }: TradingViewChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<any>(null);
  const volumeSeriesRef = useRef<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 1. Initialize the Chart with dark theme matching StockWise palette
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#1e2329" }, // --surface-card-dark
        textColor: "#eaecef", // --body
        fontSize: 12,
        fontFamily: "Inter, sans-serif",
      },
      grid: {
        vertLines: { color: "#2b3139" }, // --hairline-on-dark
        horzLines: { color: "#2b3139" },
      },
      crosshair: {
        mode: 0, // Normal crosshair
        vertLine: {
          color: "#707a8a", // --muted
          width: 1,
          style: 3, // dashed
          labelBackgroundColor: "#2b3139",
        },
        horzLine: {
          color: "#707a8a",
          width: 1,
          style: 3,
          labelBackgroundColor: "#2b3139",
        },
      },
      timeScale: {
        borderColor: "#2b3139",
        timeVisible: false,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: "#2b3139",
        autoScale: true,
      },
      width: chartContainerRef.current.clientWidth,
      height: 350,
    });

    chartRef.current = chart;

    // 2. Add Candlestick Series using v5 addSeries API
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#0ecb81", // --trading-up
      downColor: "#f6465d", // --trading-down
      borderVisible: false,
      wickUpColor: "#0ecb81",
      wickDownColor: "#f6465d",
    });
    candlestickSeriesRef.current = candlestickSeries;

    // 3. Add Volume Series (Histogram) rendered as overlay at the bottom using v5 addSeries API
    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: {
        type: "volume",
      },
      priceScaleId: "", // Overlay over the main pane
    });
    
    // Configure volume pane height and overlay style
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.75, // Volume occupies bottom 25% of the chart
        bottom: 0,
      },
    });
    volumeSeriesRef.current = volumeSeries;

    // 4. Handle auto-resizing
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    // Clean up on unmount
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, []);

  // Update data when props change
  useEffect(() => {
    if (!candlestickSeriesRef.current || !volumeSeriesRef.current || !data) return;

    // Sort data chronologically (lightweight-charts requires sorted time values)
    const sortedData = [...data].sort((a, b) => a.date.localeCompare(b.date));

    // Convert data to lightweight-charts specifications
    const candleData: CandlestickData[] = sortedData.map((d) => ({
      time: d.date,
      open: Number(d.open),
      high: Number(d.high),
      low: Number(d.low),
      close: Number(d.close),
    }));

    const volData: HistogramData[] = sortedData.map((d) => {
      const isUp = Number(d.close) >= Number(d.open);
      return {
        time: d.date,
        value: Number(d.volume),
        color: isUp ? "rgba(14, 203, 129, 0.35)" : "rgba(246, 70, 93, 0.35)", // Semi-transparent up/down color
      };
    });

    candlestickSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volData);

    // Fit content inside the viewport
    chartRef.current?.timeScale().fitContent();
  }, [data]);

  return (
    <div className="rounded-lg border border-hairline-on-dark bg-surface-card-dark p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-body">{symbol} Interactive Candlestick Chart</h3>
          <p className="text-sm text-muted">
            {data.length > 0
              ? `Hiển thị ${data.length} phiên giao dịch gần nhất (Dữ liệu thời gian thực)`
              : "Đang tải dữ liệu biểu đồ..."}
          </p>
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full relative" style={{ height: "350px" }} />
    </div>
  );
}
