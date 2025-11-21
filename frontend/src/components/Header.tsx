'use client';

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';

export default function Header() {
    const { user } = useAuth();
    const pathname = usePathname();

    const NavLink = ({ href, children }: { href: string, children: React.ReactNode }) => (
        <Link
            href={href}
            className={clsx(
                "text-sm font-medium transition-colors hover:text-blue-600",
                pathname === href ? "text-blue-600" : "text-gray-600 dark:text-gray-400"
            )}
        >
            {children}
        </Link>
    );

    return (
        <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
            <div className="max-w-md mx-auto p-4 flex justify-between items-center">
                <Link href="/" className="text-xl font-bold">Predictor</Link>

                <nav className="flex items-center gap-4">
                    <NavLink href="/">Picks</NavLink>
                    <NavLink href="/leaderboard">Leaderboard</NavLink>

                    {!user && (
                        <Link href="/login" className="text-blue-600 font-medium text-sm">Login</Link>
                    )}
                </nav>
            </div>
        </header>
    );
}
