'use client';

import { useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

export default function LogoutPage() {
    const { logout } = useAuth();
    const router = useRouter();

    useEffect(() => {
        logout();
        router.push('/');
    }, [logout, router]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <p className="text-gray-600 dark:text-gray-400">Logging out...</p>
            </div>
        </div>
    );
}
