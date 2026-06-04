"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import { User as UserIcon, Mail, Shield, Calendar, Lock } from "lucide-react";
import type { User } from "@/lib/types";

export default function ProfilePage() {
  const { user, refreshUser, updateProfile, changePassword } = useAuth();
  const [profile, setProfile] = useState<User | null>(null);
  const [fullName, setFullName] = useState("");
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    // Run once on mount: refresh user data from server and seed local state.
    // We do NOT include `user` in deps to avoid re-running (and overwriting
    // local edits) every time the AuthProvider context user object changes.
    const fetchProfile = async () => {
      try {
        // refreshUser() returns the fresh User so we don't read the stale closure.
        const freshUser = await refreshUser();
        setProfile(freshUser);
        setFullName(freshUser.fullName || "");
      } catch {
        // Network error or token expired — fall back to whatever is in context
        if (user) {
          setProfile(user);
          setFullName(user.fullName || "");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // mount-only: intentionally omit `user` to avoid resetting after save

  // Seed local form state if mount effect falls back (no refreshUser response)
  // and context user loads later.
  useEffect(() => {
    if (user && !profile) {
      setProfile(user);
      setFullName(user.fullName || "");
    }
  }, [user, profile]);

  const handleSave = async () => {
    if (!fullName.trim()) return;
    setSaving(true);
    setMessage(null);
    try {
      const data = await updateProfile(fullName.trim());
      setProfile(data);
      setMessage({ type: "success", text: "Profile updated successfully!" });
      setEditing(false);
    } catch (err: any) {
      setMessage({ type: "error", text: err.response?.data?.message || err.message || "Failed to update profile" });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFullName(profile?.fullName || "");
    setEditing(false);
    setMessage(null);
  };

  const handleChangePassword = async () => {
    if (newPassword.length < 6) {
      setPasswordError("New password must be at least 6 characters");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match");
      return;
    }
    setPasswordError("");
    setPasswordLoading(true);
    setPasswordMessage(null);
    try {
      await changePassword(currentPassword, newPassword);
      setPasswordMessage({ type: "success", text: "Password changed successfully!" });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setShowPasswordForm(false);
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || "Failed to change password";
      setPasswordMessage({ type: "error", text: msg });
    } finally {
      setPasswordLoading(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <svg className="h-8 w-8 animate-spin text-[#FCD535]" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <h1 className="mb-6 text-3xl font-bold text-[#eaecef]">My Profile</h1>

      {message && (
        <div
          className={`mb-4 rounded-lg px-4 py-3 text-sm font-medium ${
            message.type === "success"
              ? "border border-[#0ecb81]/30 bg-[#0ecb81]/10 text-[#0ecb81]"
              : "border border-[#f6465d]/30 bg-[#f6465d]/10 text-[#f6465d]"
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Profile Card */}
      <div className="rounded-xl border border-[#2b3139] bg-[#1e2329] p-6 shadow-sm">
        {/* Avatar */}
        <div className="mb-6 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#2b3139] text-2xl font-bold text-[#FCD535]">
            {profile?.fullName
              ? profile.fullName.charAt(0).toUpperCase()
              : profile?.email?.charAt(0).toUpperCase() || "U"}
          </div>
          <div>
            <div className="text-xl font-semibold text-[#eaecef]">
              {profile?.fullName || "Set your display name"}
            </div>
            <div className="text-sm text-[#707a8a]">{profile?.email}</div>
          </div>
        </div>

        {/* Info Fields */}
        <div className="space-y-4">
          {/* Full Name */}
          <div className="flex flex-col gap-2">
            <label className="flex items-center gap-2 text-sm font-medium text-[#929aa5]">
              <UserIcon className="h-4 w-4" />
              Display Name
            </label>
            {editing ? (
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="h-10 rounded-md border border-[#2b3139] bg-[#0b0e11] px-4 text-sm text-[#eaecef] transition-colors focus:border-[#FCD535] focus:outline-none focus:ring-2 focus:ring-[#FCD535]/20"
                placeholder="Enter your display name"
              />
            ) : (
              <div className="rounded-md border border-[#2b3139] bg-[#0b0e11] px-4 py-2.5 text-sm text-[#eaecef]">
                {profile?.fullName || "Not set"}
              </div>
            )}
          </div>

          {/* Email */}
          <div className="flex flex-col gap-2">
            <label className="flex items-center gap-2 text-sm font-medium text-[#929aa5]">
              <Mail className="h-4 w-4" />
              Email
            </label>
            <div className="rounded-md border border-[#2b3139] bg-[#0b0e11] px-4 py-2.5 text-sm text-[#eaecef]">
              {profile?.email || "—"}
            </div>
          </div>

          {/* Role */}
          <div className="flex flex-col gap-2">
            <label className="flex items-center gap-2 text-sm font-medium text-[#929aa5]">
              <Shield className="h-4 w-4" />
              Role
            </label>
            <div className="rounded-md border border-[#2b3139] bg-[#0b0e11] px-4 py-2.5 text-sm text-[#eaecef]">
              {profile?.role?.replace("ROLE_", "") || "—"}
            </div>
          </div>

          {/* Created At */}
          <div className="flex flex-col gap-2">
            <label className="flex items-center gap-2 text-sm font-medium text-[#929aa5]">
              <Calendar className="h-4 w-4" />
              Member Since
            </label>
            <div className="rounded-md border border-[#2b3139] bg-[#0b0e11] px-4 py-2.5 text-sm text-[#eaecef]">
              {formatDate(profile?.createdAt || null)}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 flex gap-3">
          {editing ? (
            <>
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex h-10 items-center justify-center rounded-md bg-[#FCD535] px-6 text-sm font-semibold text-[#181a20] shadow-lg shadow-[#FCD535]/20 transition-colors hover:bg-[#f0b90b] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {saving ? (
                  <span className="flex items-center gap-2">
                    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Saving...
                  </span>
                ) : (
                  "Save Changes"
                )}
              </button>
              <button
                onClick={handleCancel}
                className="flex h-10 items-center justify-center rounded-md border border-[#2b3139] bg-transparent px-6 text-sm font-medium text-[#929aa5] transition-colors hover:border-[#3b82f6] hover:text-[#3b82f6]"
              >
                Cancel
              </button>
            </>
          ) : (
            <button
              onClick={() => setEditing(true)}
              className="flex h-10 items-center justify-center rounded-md border border-[#FCD535] bg-transparent px-6 text-sm font-semibold text-[#FCD535] transition-colors hover:bg-[#FCD535]/10"
            >
              Edit Profile
            </button>
          )}
        </div>
      </div>

      {/* Change Password Card */}
      <div className="mt-6 rounded-xl border border-[#2b3139] bg-[#1e2329] p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-[#FCD535]" />
            <h2 className="text-lg font-semibold text-[#eaecef]">Change Password</h2>
          </div>
          {!showPasswordForm && (
            <button
              onClick={() => setShowPasswordForm(true)}
              className="text-sm text-[#FCD535] transition-colors hover:text-[#f0b90b]"
            >
              Change password
            </button>
          )}
        </div>

        {passwordMessage && (
          <div
            className={`mb-4 rounded-lg px-4 py-3 text-sm font-medium ${
              passwordMessage.type === "success"
                ? "border border-[#0ecb81]/30 bg-[#0ecb81]/10 text-[#0ecb81]"
                : "border border-[#f6465d]/30 bg-[#f6465d]/10 text-[#f6465d]"
            }`}
          >
            {passwordMessage.text}
          </div>
        )}

        {showPasswordForm && (
          <div className="space-y-4">
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-[#929aa5]">Current Password</label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="h-10 rounded-md border border-[#2b3139] bg-[#0b0e11] px-4 text-sm text-[#eaecef] transition-colors focus:border-[#FCD535] focus:outline-none focus:ring-2 focus:ring-[#FCD535]/20"
                placeholder="Enter current password"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-[#929aa5]">New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="h-10 rounded-md border border-[#2b3139] bg-[#0b0e11] px-4 text-sm text-[#eaecef] transition-colors focus:border-[#FCD535] focus:outline-none focus:ring-2 focus:ring-[#FCD535]/20"
                placeholder="Enter new password (min 6 characters)"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-[#929aa5]">Confirm New Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="h-10 rounded-md border border-[#2b3139] bg-[#0b0e11] px-4 text-sm text-[#eaecef] transition-colors focus:border-[#FCD535] focus:outline-none focus:ring-2 focus:ring-[#FCD535]/20"
                placeholder="Confirm new password"
              />
            </div>
            {passwordError && (
              <p className="text-sm text-[#f6465d]">{passwordError}</p>
            )}
            <div className="flex gap-3 pt-2">
              <button
                onClick={handleChangePassword}
                disabled={passwordLoading}
                className="flex h-10 items-center justify-center rounded-md bg-[#FCD535] px-6 text-sm font-semibold text-[#181a20] shadow-lg shadow-[#FCD535]/20 transition-colors hover:bg-[#f0b90b] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {passwordLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Changing...
                  </span>
                ) : (
                  "Change Password"
                )}
              </button>
              <button
                onClick={() => {
                  setShowPasswordForm(false);
                  setCurrentPassword("");
                  setNewPassword("");
                  setConfirmPassword("");
                  setPasswordError("");
                  setPasswordMessage(null);
                }}
                className="flex h-10 items-center justify-center rounded-md border border-[#2b3139] bg-transparent px-6 text-sm font-medium text-[#929aa5] transition-colors hover:border-[#3b82f6] hover:text-[#3b82f6]"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {!showPasswordForm && (
          <p className="text-sm text-[#707a8a]">
            Keep your account secure by regularly updating your password.
          </p>
        )}
      </div>
    </div>
  );
}
