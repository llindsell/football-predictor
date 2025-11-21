'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Users, Trophy, User as UserIcon, LogIn } from 'lucide-react';
import clsx from 'clsx';
import { useAuth } from '@/context/AuthContext';

export default function BottomNav() {
    const pathname = usePathname();
    const { user } = useAuth();

    const NavItem = ({ href, icon: Icon, label }: { href: string, icon: any, label: string }) => {
        const isActive = pathname === href;
        return (
            <Link
                href={href}
                className={clsx(
                    "flex flex-col items-center justify-center w-full h-full space-y-1",
                    isActive ? "text-blue-600 dark:text-blue-400" : "text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                )}
            >
                <Icon size={24} strokeWidth={isActive ? 2.5 : 2} />
                <span className="text-[10px] font-medium">{label}</span>
            </Link>
        );
    };

    return (
        <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 h-16 z-50 pb-safe">
            <div className="max-w-md mx-auto h-full flex items-center justify-around px-2">
                <NavItem href="/" icon={Home} label="Picks" />
                <NavItem href="/compare" icon={Users} label="Compare" />
                <NavItem href="/leaderboard" icon={Trophy} label="Leaderboard" />

                {user ? (
                    <div className="flex flex-col items-center justify-center w-full h-full space-y-1 text-gray-500 dark:text-gray-400">
                        {user.profile_picture ? (
                            <img src={user.profile_picture} alt="Profile" className="w-6 h-6 rounded-full" />
                        ) : (
                            <UserIcon size={24} />
                        )}
                        <span className="text-[10px] font-medium">Profile</span>
                    </div>
                ) : (
                    <NavItem href="/login" icon={LogIn} label="Login" />
                )}
            </div>
        </div>
    );
}
