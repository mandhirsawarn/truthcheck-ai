import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
const inter = Inter({
subsets: ["latin"],
variable: "--font-inter",
});
export const metadata: Metadata = {
title: "TruthCheck",
description: "Premium forensic analysis platform for detecting synthetic video.",
};
export default function RootLayout({
children,
}: Readonly<{
children: React.ReactNode;
}>) {
return (
<html lang="en" className={`${inter.variable} dark`}>
<body className="font-sans bg-bg-primary text-text-primary antialiased min-h-screen flex flex-col relative overflow-x-hidden selection:bg-accent selection:text-white">
<div className="fixed inset-0 z-[-1] pointer-events-none aurora-bg" />
<div className="fixed inset-0 z-[-1] pointer-events-none bg-[url('/noise.png')] opacity-20 mix-blend-overlay" />
<Providers>
<Header />
<main className="flex-grow flex flex-col relative z-10">
{children}
</main>
<Footer />
</Providers>
</body>
</html>
);
}
