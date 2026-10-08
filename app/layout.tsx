import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Generated URL to APK & AAB Platform",
  description: "Enterprise-grade web platform converting web apps into production Android APK & AAB packages.",
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "https://generated.business.web.id"),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
        {children}
      </body>
    </html>
  );
}
