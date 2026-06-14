"use client";

import { useEffect, useState } from "react";
import { Settings, Check, RefreshCw, Radio, Sliders } from "lucide-react";
import { userSelectionsApi, trackedSymbolsApi } from "@/lib/api";
import type { UserNewsSource } from "@/lib/types";
import {
  TerminalSectionHeader,
  TerminalButton,
  TerminalNotice,
  TerminalSkeletonRows,
} from "@/components/ui";

export default function SettingsPage() {
  const [globalSymbols, setGlobalSymbols] = useState<string[]>([]);
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [newsSources, setNewsSources] = useState<UserNewsSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingSymbols, setSavingSymbols] = useState(false);
  const [savingSources, setSavingSources] = useState(false);
  const [symbolsNotice, setSymbolsNotice] = useState<{ tone: "success" | "danger"; msg: string } | null>(null);
  const [sourcesNotice, setSourcesNotice] = useState<{ tone: "success" | "danger"; msg: string } | null>(null);

  useEffect(() => {
    async function loadSettings() {
      try {
        setLoading(true);
        const [gSymbols, uSymbols, uSources] = await Promise.all([
          trackedSymbolsApi.list(),
          userSelectionsApi.listSymbols(),
          userSelectionsApi.listNewsSources(),
        ]);
        setGlobalSymbols(gSymbols);
        setSelectedSymbols(uSymbols);
        setNewsSources(uSources);
      } catch (err) {
        setSymbolsNotice({ tone: "danger", msg: "Unable to load settings from server." });
      } finally {
        setLoading(false);
      }
    }
    void loadSettings();
  }, []);

  const handleSymbolToggle = (symbol: string) => {
    setSelectedSymbols((prev) =>
      prev.includes(symbol) ? prev.filter((s) => s !== symbol) : [...prev, symbol]
    );
  };

  const handleSourceToggle = (id: string) => {
    setNewsSources((prev) =>
      prev.map((src) => (src.id === id ? { ...src, isSelected: !src.isSelected } : src))
    );
  };

  const saveSymbols = async () => {
    setSavingSymbols(true);
    setSymbolsNotice(null);
    try {
      await userSelectionsApi.updateSymbols(selectedSymbols);
      setSymbolsNotice({ tone: "success", msg: "Watchlist preferences saved successfully." });
      setTimeout(() => setSymbolsNotice(null), 3000);
    } catch {
      setSymbolsNotice({ tone: "danger", msg: "Failed to save watchlist preferences." });
    } finally {
      setSavingSymbols(false);
    }
  };

  const saveNewsSources = async () => {
    setSavingSources(true);
    setSourcesNotice(null);
    try {
      const activeIds = newsSources.filter((src) => src.isSelected).map((src) => src.id);
      await userSelectionsApi.updateNewsSources(activeIds);
      setSourcesNotice({ tone: "success", msg: "News source visibility preferences saved." });
      setTimeout(() => setSourcesNotice(null), 3000);
    } catch {
      setSourcesNotice({ tone: "danger", msg: "Failed to save news source preferences." });
    } finally {
      setSavingSources(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <header className="border-b border-terminal-border pb-4">
          <h1 className="font-display text-xl font-bold uppercase tracking-[0.18em] text-terminal-accent">
            System Settings
          </h1>
        </header>
        <TerminalSkeletonRows rows={5} />
      </div>
    );
  }

  return (
    <div className="min-h-full space-y-6 font-mono text-terminal-text">
      <header className="border-b border-terminal-border pb-4">
        <div className="mb-2 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-terminal-accent animate-pulse" />
          User Dashboard Preferences
        </div>
        <h1 className="font-display text-xl font-bold uppercase tracking-[0.18em] text-terminal-accent">
          Preferences & Controls
        </h1>
        <p className="mt-1 max-w-2xl text-xs leading-relaxed text-terminal-muted">
          Customize your workspace experience. Filter the dashboard watch list and control news sources fed into the AI Advisor.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Watchlist Symbols Preferences */}
        <section className="rounded border border-terminal-border bg-terminal-surface p-4 space-y-4">
          <TerminalSectionHeader
            icon={Sliders}
            title="My Watchlist"
            subtitle="Select symbols to track on your dashboard"
          />

          {symbolsNotice && (
            <TerminalNotice tone={symbolsNotice.tone}>
              {symbolsNotice.msg}
            </TerminalNotice>
          )}

          {globalSymbols.length === 0 ? (
            <p className="text-xs text-terminal-muted italic">No system symbols available.</p>
          ) : (
            <div className="grid grid-cols-2 gap-2 max-h-[250px] overflow-y-auto pr-1">
              {globalSymbols.map((symbol) => {
                const isChecked = selectedSymbols.includes(symbol);
                return (
                  <button
                    key={symbol}
                    onClick={() => handleSymbolToggle(symbol)}
                    className={`flex items-center justify-between rounded border px-3 py-2 text-xs transition-colors text-left ${
                      isChecked
                        ? "border-terminal-accent bg-terminal-accent/5 text-terminal-accent"
                        : "border-terminal-border bg-terminal-bg text-terminal-muted hover:border-terminal-muted/40 hover:text-terminal-text"
                    }`}
                  >
                    <span>{symbol}</span>
                    {isChecked && <Check className="h-3.5 w-3.5" />}
                  </button>
                );
              })}
            </div>
          )}

          <div className="pt-2 border-t border-terminal-border/50 flex justify-end">
            <TerminalButton
              onClick={saveSymbols}
              disabled={savingSymbols}
              tone="accent"
              className="w-full sm:w-auto"
            >
              {savingSymbols ? (
                <>
                  <RefreshCw className="h-3 w-3 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Watchlist"
              )}
            </TerminalButton>
          </div>
        </section>

        {/* News Sources Visibility Preferences */}
        <section className="rounded border border-terminal-border bg-terminal-surface p-4 space-y-4">
          <TerminalSectionHeader
            icon={Radio}
            title="News Toggles"
            subtitle="Subscribe or unsubscribe to active news feeds"
          />

          {sourcesNotice && (
            <TerminalNotice tone={sourcesNotice.tone}>
              {sourcesNotice.msg}
            </TerminalNotice>
          )}

          {newsSources.length === 0 ? (
            <p className="text-xs text-terminal-muted italic">No news sources available.</p>
          ) : (
            <div className="space-y-2 max-h-[250px] overflow-y-auto pr-1">
              {newsSources.map((src) => {
                // If globally inactive, show indicator that it's disabled globally
                const isGloballyActive = src.isActive;
                return (
                  <button
                    key={src.id}
                    onClick={() => isGloballyActive && handleSourceToggle(src.id)}
                    disabled={!isGloballyActive}
                    className={`flex items-center justify-between rounded border w-full px-3 py-2.5 text-xs transition-colors text-left ${
                      !isGloballyActive
                        ? "border-terminal-border/40 bg-terminal-bg/50 text-terminal-muted/50 cursor-not-allowed"
                        : src.isSelected
                        ? "border-terminal-green bg-terminal-green/5 text-terminal-green"
                        : "border-terminal-border bg-terminal-bg text-terminal-muted hover:border-terminal-muted/40 hover:text-terminal-text"
                    }`}
                  >
                    <div className="min-w-0">
                      <span className="font-semibold block truncate">{src.name}</span>
                      <span className="text-[10px] block truncate text-terminal-muted">
                        {!isGloballyActive ? "Offline (Disabled by Admin)" : src.baseUrl}
                      </span>
                    </div>
                    {isGloballyActive && src.isSelected && (
                      <Check className="h-3.5 w-3.5 shrink-0" />
                    )}
                  </button>
                );
              })}
            </div>
          )}

          <div className="pt-2 border-t border-terminal-border/50 flex justify-end">
            <TerminalButton
              onClick={saveNewsSources}
              disabled={savingSources}
              tone="success"
              className="w-full sm:w-auto"
            >
              {savingSources ? (
                <>
                  <RefreshCw className="h-3 w-3 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save News Sources"
              )}
            </TerminalButton>
          </div>
        </section>
      </div>
    </div>
  );
}
