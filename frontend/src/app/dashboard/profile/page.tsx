"use client";

import {
  CalendarDays,
  CheckCircle2,
  Eye,
  EyeOff,
  Fingerprint,
  KeyRound,
  LoaderCircle,
  LockKeyhole,
  Mail,
  Pencil,
  Save,
  ShieldCheck,
  TerminalSquare,
  UserRound,
  X,
  XCircle,
} from "lucide-react";
import { FormEvent, useEffect, useId, useState } from "react";
import { clsx } from "clsx";
import { useAuth } from "@/components/providers/AuthProvider";
import type { User } from "@/lib/types";

type NoticeState = { type: "success" | "error"; text: string } | null;

function SectionHeader({
  icon: Icon,
  title,
  subtitle,
  action,
}: {
  icon: React.ElementType;
  title: string;
  subtitle: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-4 flex items-start justify-between gap-4 border-b border-terminal-border pb-3">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded border border-terminal-border bg-terminal-surface">
          <Icon className="h-4 w-4 text-terminal-accent" />
        </div>
        <div className="min-w-0">
          <h2 className="font-mono text-sm font-semibold uppercase tracking-widest text-terminal-text">
            {title}
          </h2>
          <p className="mt-0.5 font-mono text-[10px] text-terminal-muted">
            {subtitle}
          </p>
        </div>
      </div>
      {action}
    </div>
  );
}

function Notice({ notice }: { notice: NoticeState }) {
  if (!notice) return null;

  const Icon = notice.type === "success" ? CheckCircle2 : XCircle;

  return (
    <div
      role={notice.type === "error" ? "alert" : "status"}
      className={clsx(
        "flex items-start gap-2 rounded border px-3 py-2.5 font-mono text-[11px] leading-relaxed",
        notice.type === "success"
          ? "border-terminal-green/30 bg-terminal-green/5 text-terminal-green"
          : "border-terminal-red/30 bg-terminal-red/5 text-terminal-red"
      )}
    >
      <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0" />
      <span>{notice.text}</span>
    </div>
  );
}

function DataRow({
  icon: Icon,
  label,
  value,
  badge,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  badge?: boolean;
}) {
  return (
    <div className="grid gap-2 rounded border border-terminal-border bg-terminal-surface px-3 py-2.5 transition-colors hover:border-terminal-accent/30 sm:grid-cols-[148px_minmax(0,1fr)] sm:items-center">
      <div className="flex items-center gap-2 font-mono text-[10px] font-medium uppercase tracking-wider text-terminal-muted">
        <Icon className="h-3.5 w-3.5" />
        {label}
      </div>
      <div className="min-w-0 font-mono text-xs text-terminal-text">
        {badge ? (
          <span className="inline-flex items-center gap-1.5 rounded border border-terminal-green/30 bg-terminal-green/5 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-terminal-green">
            <span className="h-1.5 w-1.5 rounded-full bg-terminal-green" />
            {value}
          </span>
        ) : (
          <span className="block truncate">{value}</span>
        )}
      </div>
    </div>
  );
}

function PasswordField({
  label,
  value,
  onChange,
  placeholder,
  autoComplete,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  autoComplete: string;
}) {
  const id = useId();
  const [visible, setVisible] = useState(false);

  return (
    <div>
      <label
        htmlFor={id}
        className="mb-1.5 block font-mono text-[10px] font-medium uppercase tracking-wider text-terminal-muted"
      >
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={visible ? "text" : "password"}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          autoComplete={autoComplete}
          placeholder={placeholder}
          required
          className="h-10 w-full rounded border border-terminal-border bg-terminal-bg px-3 pr-10 font-mono text-xs text-terminal-text outline-none transition-colors placeholder:text-terminal-muted/50 hover:border-terminal-muted focus:border-terminal-accent/60"
        />
        <button
          type="button"
          onClick={() => setVisible((current) => !current)}
          aria-label={visible ? `Hide ${label}` : `Show ${label}`}
          className="absolute inset-y-0 right-0 flex w-10 items-center justify-center text-terminal-muted transition-colors hover:text-terminal-accent focus:outline-none focus:text-terminal-accent"
        >
          {visible ? (
            <EyeOff className="h-3.5 w-3.5" />
          ) : (
            <Eye className="h-3.5 w-3.5" />
          )}
        </button>
      </div>
    </div>
  );
}

export default function ProfilePage() {
  const { user, refreshUser, updateProfile, changePassword } = useAuth();
  const [profile, setProfile] = useState<User | null>(null);
  const [fullName, setFullName] = useState("");
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<NoticeState>(null);

  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState<NoticeState>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const freshUser = await refreshUser();
        setProfile(freshUser);
        setFullName(freshUser.fullName || "");
      } catch {
        if (user) {
          setProfile(user);
          setFullName(user.fullName || "");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
    // Mount-only: re-fetching after local edits would overwrite form state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (user && !profile) {
      setProfile(user);
      setFullName(user.fullName || "");
    }
  }, [user, profile]);

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalizedName = fullName.trim();
    if (!normalizedName) {
      setMessage({ type: "error", text: "Display name cannot be empty." });
      return;
    }

    setSaving(true);
    setMessage(null);
    try {
      const data = await updateProfile(normalizedName);
      setProfile(data);
      setFullName(data.fullName || "");
      setMessage({ type: "success", text: "Profile data updated successfully." });
      setEditing(false);
    } catch (error: any) {
      setMessage({
        type: "error",
        text:
          error.response?.data?.message ||
          error.message ||
          "Unable to update profile.",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFullName(profile?.fullName || "");
    setEditing(false);
    setMessage(null);
  };

  const resetPasswordForm = () => {
    setShowPasswordForm(false);
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setPasswordError("");
  };

  const handleChangePassword = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!currentPassword) {
      setPasswordError("Current password is required.");
      return;
    }
    if (newPassword.length < 6) {
      setPasswordError("New password must contain at least 6 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("Password confirmation does not match.");
      return;
    }

    setPasswordError("");
    setPasswordLoading(true);
    setPasswordMessage(null);
    try {
      await changePassword(currentPassword, newPassword);
      resetPasswordForm();
      setPasswordMessage({
        type: "success",
        text: "Password changed. Your account credentials are up to date.",
      });
    } catch (error: any) {
      setPasswordMessage({
        type: "error",
        text:
          error?.response?.data?.message ||
          error?.message ||
          "Unable to change password.",
      });
    } finally {
      setPasswordLoading(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Not available";

    const date = new Date(dateStr);
    if (Number.isNaN(date.getTime())) return "Not available";

    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
    }).format(date);
  };

  const displayName = profile?.fullName || "Unnamed account";
  const initials = (profile?.fullName || profile?.email || "U")
    .split(/\s+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const role = profile?.role?.replace("ROLE_", "") || "USER";
  const userId = profile?.id || "Not available";

  if (loading) {
    return (
      <div
        className="flex min-h-[320px] items-center justify-center font-mono"
        aria-live="polite"
      >
        <div className="flex items-center gap-3 text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
          <LoaderCircle className="h-4 w-4 animate-spin text-terminal-accent" />
          Loading account record
        </div>
      </div>
    );
  }

  return (
    <div
      className="min-h-full font-mono text-terminal-text"
      style={{
        fontFamily:
          "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
      }}
    >
      <header className="mb-6 flex flex-col gap-4 border-b border-terminal-border pb-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-terminal-accent">
            <TerminalSquare className="h-3.5 w-3.5" />
            Account console
          </div>
          <h1 className="font-display text-xl font-bold uppercase tracking-[0.18em] text-terminal-text">
            Profile
          </h1>
          <p className="mt-1 max-w-xl text-[11px] leading-relaxed text-terminal-muted">
            Manage identity metadata and authentication credentials for this
            StockWise account.
          </p>
        </div>
        <div className="flex items-center gap-2 self-start rounded border border-terminal-green/20 bg-terminal-green/5 px-2.5 py-1.5 text-[9px] font-semibold uppercase tracking-widest text-terminal-green sm:self-auto">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-terminal-green" />
          Account active
        </div>
      </header>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-12">
        <aside className="space-y-5 xl:col-span-4">
          <section>
            <SectionHeader
              icon={UserRound}
              title="Identity"
              subtitle="Authenticated account snapshot"
            />
            <div className="relative overflow-hidden rounded border border-terminal-border bg-terminal-surface p-4">
              <div className="pointer-events-none absolute right-0 top-0 h-24 w-24 bg-[linear-gradient(135deg,transparent_48%,rgba(240,180,41,0.08)_49%,rgba(240,180,41,0.08)_51%,transparent_52%)]" />
              <div className="relative flex items-center gap-3">
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded border border-terminal-accent/40 bg-terminal-accent/5 text-lg font-bold tracking-wider text-terminal-accent">
                  {initials}
                </div>
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-terminal-text">
                    {displayName}
                  </p>
                  <p className="mt-1 truncate text-[10px] text-terminal-muted">
                    {profile?.email || "Email unavailable"}
                  </p>
                  <span className="mt-2 inline-flex rounded border border-terminal-border bg-terminal-bg px-1.5 py-0.5 text-[9px] font-medium uppercase tracking-wider text-terminal-accent">
                    {role}
                  </span>
                </div>
              </div>

              <div className="mt-4 border-t border-terminal-border pt-3">
                <div className="flex items-center justify-between gap-3 text-[9px] uppercase tracking-wider">
                  <span className="text-terminal-muted">Account ID</span>
                  <span className="max-w-[65%] truncate text-right text-terminal-text">
                    {userId}
                  </span>
                </div>
                <div className="mt-2 flex items-center justify-between gap-3 text-[9px] uppercase tracking-wider">
                  <span className="text-terminal-muted">Created</span>
                  <span className="text-right text-terminal-text">
                    {formatDate(profile?.createdAt || null)}
                  </span>
                </div>
              </div>
            </div>
          </section>

          <section>
            <SectionHeader
              icon={ShieldCheck}
              title="Security status"
              subtitle="Credential health overview"
            />
            <div className="space-y-1">
              <div className="flex items-center justify-between rounded border border-terminal-border bg-terminal-surface px-3 py-2.5">
                <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-terminal-muted">
                  <Fingerprint className="h-3.5 w-3.5" />
                  Session
                </div>
                <span className="text-[9px] font-semibold uppercase tracking-wider text-terminal-green">
                  Verified
                </span>
              </div>
              <div className="flex items-center justify-between rounded border border-terminal-border bg-terminal-surface px-3 py-2.5">
                <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-terminal-muted">
                  <KeyRound className="h-3.5 w-3.5" />
                  Password
                </div>
                <span className="text-[9px] font-semibold uppercase tracking-wider text-terminal-amber">
                  Managed
                </span>
              </div>
            </div>
          </section>
        </aside>

        <div className="space-y-5 xl:col-span-8">
          <section>
            <SectionHeader
              icon={Fingerprint}
              title="Profile data"
              subtitle="Core identity fields linked to your account"
              action={
                !editing ? (
                  <button
                    type="button"
                    onClick={() => {
                      setEditing(true);
                      setMessage(null);
                    }}
                    className="inline-flex shrink-0 items-center gap-1.5 rounded border border-terminal-accent/40 bg-terminal-accent/5 px-2.5 py-1.5 text-[9px] font-semibold uppercase tracking-widest text-terminal-accent transition-colors hover:bg-terminal-accent/10 focus:outline-none focus:ring-1 focus:ring-terminal-accent/50"
                  >
                    <Pencil className="h-3 w-3" />
                    Edit
                  </button>
                ) : undefined
              }
            />

            <div className="space-y-2">
              <Notice notice={message} />

              {editing ? (
                <form
                  onSubmit={handleSave}
                  className="rounded border border-terminal-accent/30 bg-terminal-surface p-4"
                >
                  <label
                    htmlFor="display-name"
                    className="mb-1.5 block text-[10px] font-medium uppercase tracking-wider text-terminal-muted"
                  >
                    Display name
                  </label>
                  <input
                    id="display-name"
                    type="text"
                    value={fullName}
                    onChange={(event) => setFullName(event.target.value)}
                    autoComplete="name"
                    maxLength={120}
                    autoFocus
                    className="h-10 w-full rounded border border-terminal-border bg-terminal-bg px-3 text-xs text-terminal-text outline-none transition-colors placeholder:text-terminal-muted/50 hover:border-terminal-muted focus:border-terminal-accent/60"
                    placeholder="Enter display name"
                  />
                  <p className="mt-2 text-[9px] leading-relaxed text-terminal-muted">
                    This name is displayed across your dashboard and account
                    activity.
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <button
                      type="submit"
                      disabled={saving || !fullName.trim()}
                      className="inline-flex items-center gap-1.5 rounded border border-terminal-accent/50 bg-terminal-accent/10 px-3 py-2 text-[9px] font-semibold uppercase tracking-widest text-terminal-accent transition-colors hover:bg-terminal-accent/20 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      {saving ? (
                        <LoaderCircle className="h-3 w-3 animate-spin" />
                      ) : (
                        <Save className="h-3 w-3" />
                      )}
                      {saving ? "Saving" : "Save changes"}
                    </button>
                    <button
                      type="button"
                      onClick={handleCancel}
                      disabled={saving}
                      className="inline-flex items-center gap-1.5 rounded border border-terminal-border px-3 py-2 text-[9px] font-semibold uppercase tracking-widest text-terminal-muted transition-colors hover:border-terminal-muted hover:text-terminal-text disabled:opacity-40"
                    >
                      <X className="h-3 w-3" />
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-1">
                  <DataRow
                    icon={UserRound}
                    label="Display name"
                    value={displayName}
                  />
                  <DataRow
                    icon={Mail}
                    label="Email address"
                    value={profile?.email || "Not available"}
                  />
                  <DataRow
                    icon={ShieldCheck}
                    label="Access role"
                    value={role}
                    badge
                  />
                  <DataRow
                    icon={CalendarDays}
                    label="Member since"
                    value={formatDate(profile?.createdAt || null)}
                  />
                </div>
              )}
            </div>
          </section>

          <section>
            <SectionHeader
              icon={LockKeyhole}
              title="Authentication"
              subtitle="Rotate your password without interrupting the active session"
              action={
                !showPasswordForm ? (
                  <button
                    type="button"
                    onClick={() => {
                      setShowPasswordForm(true);
                      setPasswordMessage(null);
                    }}
                    className="inline-flex shrink-0 items-center gap-1.5 rounded border border-terminal-accent/40 bg-terminal-accent/5 px-2.5 py-1.5 text-[9px] font-semibold uppercase tracking-widest text-terminal-accent transition-colors hover:bg-terminal-accent/10 focus:outline-none focus:ring-1 focus:ring-terminal-accent/50"
                  >
                    <KeyRound className="h-3 w-3" />
                    Rotate
                  </button>
                ) : undefined
              }
            />

            <div className="space-y-2">
              <Notice notice={passwordMessage} />

              {showPasswordForm ? (
                <form
                  onSubmit={handleChangePassword}
                  className="rounded border border-terminal-accent/30 bg-terminal-surface p-4"
                >
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="md:col-span-2">
                      <PasswordField
                        label="Current password"
                        value={currentPassword}
                        onChange={setCurrentPassword}
                        autoComplete="current-password"
                        placeholder="Enter current password"
                      />
                    </div>
                    <PasswordField
                      label="New password"
                      value={newPassword}
                      onChange={setNewPassword}
                      autoComplete="new-password"
                      placeholder="Minimum 6 characters"
                    />
                    <PasswordField
                      label="Confirm password"
                      value={confirmPassword}
                      onChange={setConfirmPassword}
                      autoComplete="new-password"
                      placeholder="Repeat new password"
                    />
                  </div>

                  <div className="mt-3 flex items-center justify-between gap-4 border-t border-terminal-border pt-3">
                    <p className="text-[9px] leading-relaxed text-terminal-muted">
                      Use at least 6 characters and avoid reusing an old
                      password.
                    </p>
                    <span
                      className={clsx(
                        "shrink-0 text-[9px] uppercase tracking-wider",
                        newPassword.length >= 6
                          ? "text-terminal-green"
                          : "text-terminal-muted"
                      )}
                    >
                      {Math.min(newPassword.length, 99)} chars
                    </span>
                  </div>

                  {passwordError && (
                    <p
                      role="alert"
                      className="mt-3 flex items-center gap-2 text-[10px] text-terminal-red"
                    >
                      <XCircle className="h-3.5 w-3.5" />
                      {passwordError}
                    </p>
                  )}

                  <div className="mt-4 flex flex-wrap gap-2">
                    <button
                      type="submit"
                      disabled={passwordLoading}
                      className="inline-flex items-center gap-1.5 rounded border border-terminal-accent/50 bg-terminal-accent/10 px-3 py-2 text-[9px] font-semibold uppercase tracking-widest text-terminal-accent transition-colors hover:bg-terminal-accent/20 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      {passwordLoading ? (
                        <LoaderCircle className="h-3 w-3 animate-spin" />
                      ) : (
                        <KeyRound className="h-3 w-3" />
                      )}
                      {passwordLoading ? "Updating" : "Update password"}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        resetPasswordForm();
                        setPasswordMessage(null);
                      }}
                      disabled={passwordLoading}
                      className="inline-flex items-center gap-1.5 rounded border border-terminal-border px-3 py-2 text-[9px] font-semibold uppercase tracking-widest text-terminal-muted transition-colors hover:border-terminal-muted hover:text-terminal-text disabled:opacity-40"
                    >
                      <X className="h-3 w-3" />
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <div className="flex flex-col gap-3 rounded border border-terminal-border bg-terminal-surface px-3 py-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-start gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded border border-terminal-border bg-terminal-bg">
                      <LockKeyhole className="h-4 w-4 text-terminal-muted" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-terminal-text">
                        Password protection enabled
                      </p>
                      <p className="mt-1 text-[10px] leading-relaxed text-terminal-muted">
                        Rotate credentials periodically to keep account access
                        secure.
                      </p>
                    </div>
                  </div>
                  <span className="self-start rounded border border-terminal-green/30 bg-terminal-green/5 px-2 py-1 text-[9px] font-semibold uppercase tracking-wider text-terminal-green sm:self-auto">
                    Protected
                  </span>
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
