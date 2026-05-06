import type { Metadata } from "next";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "StockWise - AI Stock Analysis",
  description: "AI-powered stock analysis and portfolio management platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
