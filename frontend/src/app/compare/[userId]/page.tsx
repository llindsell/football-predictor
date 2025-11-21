'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { fetchAPI } from '@/lib/api';
import { Week, Game, Pick } from '@/types';
import ComparisonCard from '@/components/ComparisonCard';
import { useParams } from 'next/navigation';

export default function ComparisonPage() {
    const { user, token } = useAuth();
    const params = useParams();
    const targetUserId = Number(params.userId);

    const [weeks, setWeeks] = useState<Week[]>([]);
    const [selectedWeek, setSelectedWeek] = useState<Week | null>(null);
    const [games, setGames] = useState<Game[]>([]);
    const [myPicks, setMyPicks] = useState<Pick[]>([]);
    const [theirPicks, setTheirPicks] = useState<Pick[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadWeeks = async () => {
            try {
                const data = await fetchAPI('/weeks');
                setWeeks(data);
                if (data.length > 0) {
                    setSelectedWeek(data[0]);
                }
            } catch (error) {
                console.error('Failed to load weeks', error);
            }
        };
        loadWeeks();
    }, []);

    useEffect(() => {
        if (!selectedWeek || !token || !targetUserId) return;

        const loadData = async () => {
            setLoading(true);
            try {
                const [gamesData, myPicksData, theirPicksData] = await Promise.all([
                    fetchAPI(`/weeks/${selectedWeek.id}/games`),
                    fetchAPI('/picks/me', { headers: { Authorization: `Bearer ${token}` } }),
                    fetchAPI(`/picks/user/${targetUserId}`, { headers: { Authorization: `Bearer ${token}` } })
                ]);
                setGames(gamesData);
                setMyPicks(myPicksData);
                setTheirPicks(theirPicksData);
            } catch (error) {
                console.error('Failed to load comparison data', error);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, [selectedWeek, token, targetUserId]);

    if (!user) return <div className="p-8">Please login.</div>;

    return (
        <main className="max-w-md mx-auto pb-20">
            <div className="p-4">
                <h1 className="text-xl font-bold mb-4">Comparison</h1>

                <div className="flex overflow-x-auto gap-2 no-scrollbar mb-6">
                    {weeks.map(week => (
                        <button
                            key={week.id}
                            onClick={() => setSelectedWeek(week)}
                            className={`px-4 py-2 rounded-full whitespace-nowrap text-sm font-medium transition-colors ${selectedWeek?.id === week.id
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                                }`}
                        >
                            Week {week.week_number}
                        </button>
                    ))}
                </div>

                {loading ? (
                    <div className="text-center py-8">Loading...</div>
                ) : (
                    games.map(game => (
                        <ComparisonCard
                            key={game.id}
                            game={game}
                            myPick={myPicks.find(p => p.game_id === game.id)}
                            theirPick={theirPicks.find(p => p.game_id === game.id)}
                            theirName={`User ${targetUserId}`} // Ideally fetch user name too
                        />
                    ))
                )}
            </div>
        </main>
    );
}
