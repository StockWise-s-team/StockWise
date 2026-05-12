"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { User, Mail, Shield, Calendar } from "lucide-react";
import type { User as UserType } from "@/lib/types";

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserType | null>(null);
  const [fullName, setFullName] = useState("");
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("accessToken");
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
          headers: { "Authorization": `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setProfile(data);
          setFullName(data.fullName || "");
          localStorage.setItem("user", JSON.stringify(data));
        } else {
          setProfile(user);
          setFullName(user?.fullName || "");
        }
      } catch {
        setProfile(user);
        setFullName(user?.fullName || "");
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSave = async () => {
    if (!fullName.trim()) return;
    setSaving(true);
    setMessage(null);
    try {
      const token = localStorage.getItem("accessToken");
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ fullName: fullName.trim() }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || "Failed to update profile");
      }
      const updated = { ...profile, fullName: data.fullName, createdAt: data.createdAt };
      setProfile(updated);
      localStorage.setItem("user", JSON.stringify(updated));
      setMessage({ type: "success", text: "Profile updated successfully!" });
      setEditing(false);
    } catch (err: any) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFullName(profile?.fullName || "");
    setEditing(false);
    setMessage(null);
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
              <User className="h-4 w-4" />
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
    </div>
  );
}
