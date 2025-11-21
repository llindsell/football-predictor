'use client';

import { useState, useEffect } from 'react';
import { fetchAPI } from '@/lib/api';
import { LeaderboardEntry } from '@/types';

export default function LeaderboardPage() {
    const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadLeaderboard = async () => {
            try {
                const data = await fetchAPI('/leaderboard');
                setLeaderboard(data);
            } catch (error) {
                console.error('Failed to load leaderboard', error);
            } finally {
                setLoading(false);
            }
        };
        loadLeaderboard();
    }, []);

    if (loading) {
        return <div className="p-8 text-center">Loading leaderboard...</div>;
    }

    return (
        <main className="max-w-md mx-auto p-4">
            <h1 className="text-2xl font-bold mb-6">Leaderboard</h1>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-700/50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        <tr>
                            <th className="px-4 py-3">Rank</th>
                            <th className="px-4 py-3">User</th>
                            <th className="px-4 py-3 text-right">Correct</th>
                            <th className="px-4 py-3 text-right">%</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {leaderboard.map((entry) => (
                            <tr key={entry.user_id}>
                                <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">
                                    #{entry.rank}
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center justify-between gap-2">
                                        <div className="flex items-center gap-2">
                                            {entry.profile_picture && (
                                                <img src={entry.profile_picture} alt="" className="w-6 h-6 rounded-full" />
                                            )}
                                            <span className="text-sm font-medium text-gray-900 dark:text-white truncate max-w-[100px]">
                                                {entry.user_name}
                                            </span>
                                        </div>
                                        <a
                                            href={`/compare/${entry.user_id}`}
                                            className="text-xs text-blue-600 hover:underline"
                                        >
                                            Compare
                                        </a>
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-sm text-right text-gray-500 dark:text-gray-400">
                                    {entry.correct_picks}/{entry.total_picks}
                                </td>
                                <td className="px-4 py-3 text-sm text-right font-bold text-gray-900 dark:text-white">
                                    {entry.win_rate}%
                                </td>
                            </tr>
                        ))}
                        {leaderboard.length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                                    No rankings yet. Wait for games to finish!
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </main>
    );
}
