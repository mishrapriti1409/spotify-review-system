import type { Metadata } from "next";
import "./globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "Spotify Review Discovery Engine",
  description: "RAG-Based Customer Intelligence Platform",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-spotify-black text-white antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
