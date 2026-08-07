import Link from "next/link";

export function Footer() {
  return (
    <footer className="relative mt-12 mb-8">
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-border-subtle to-transparent" />
        <div className="container mx-auto px-6 py-12 flex flex-col md:flex-row items-center justify-between text-sm text-text-secondary gap-4">
          <div>&copy; {new Date().getFullYear()} Truth Check AI. All rights reserved.</div>
          <div className="flex gap-8">
            <Link href="/privacy" className="hover:text-white transition-colors relative group">
              Privacy
            </Link>
            <Link href="/terms" className="hover:text-white transition-colors relative group">
              Terms
            </Link>
            <Link href="/contact" className="hover:text-white transition-colors relative group">
              Contact
            </Link>
            <Link href="/team" className="hover:text-white transition-colors relative group">
              Team
            </Link>
          </div>
        </div>
    </footer>
  );
}
