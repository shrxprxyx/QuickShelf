import { UserButton } from "@clerk/nextjs";
import Link from "next/link";
import {
  LayoutDashboard,
  BookOpen,
  ScanLine,
  ClipboardList,
  Wallet,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/books", label: "Books", icon: BookOpen },
  { href: "/scan", label: "Scan", icon: ScanLine },
  { href: "/issues", label: "Issues", icon: ClipboardList },
  { href: "/fines", label: "Fines", icon: Wallet },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-60 shrink-0 border-r bg-muted/30 flex flex-col">
        <div className="px-4 py-5 font-semibold text-lg border-b">
          QuickShelf Admin
        </div>
        <div className="px-4 py-2 text-xs text-muted-foreground border-b">
          Navigation
        </div>
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="px-4 py-4 border-t flex items-center gap-3">
          <UserButton />
          <span className="text-xs text-muted-foreground">Admin</span>
        </div>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}