import { UserButton } from "@clerk/nextjs";
import Link from "next/link";

const navItems = [
  { href: "/browse", label: "Browse" },
  { href: "/my-books", label: "My Books" },
  { href: "/reservations", label: "Reservations" },
];

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <div className="max-w-5xl mx-auto flex items-center justify-between px-6 py-4">
          <span className="font-semibold text-lg">📚 Smart Library</span>
          <nav className="flex items-center gap-6">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                {item.label}
              </Link>
            ))}
            <UserButton />
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-8">{children}</main>
    </div>
  );
}