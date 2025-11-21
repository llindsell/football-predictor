'use client';

import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/context/AuthContext';
import { fetchAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const { login } = useAuth();
    const router = useRouter();

    const handleSuccess = async (credentialResponse: any) => {
        try {
            const res = await fetchAPI('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ credential: credentialResponse.credential }),
            });

            login(res.access_token, res.user);
            router.push('/');
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    return (
        <div className="flex min-h-screen flex-col items-center justify-center p-24">
            <h1 className="text-4xl font-bold mb-8">Login</h1>
            <GoogleLogin
                onSuccess={handleSuccess}
                onError={() => {
                    console.log('Login Failed');
                }}
            />
        </div>
    );
}
