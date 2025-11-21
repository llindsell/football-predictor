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


    const [selectedWeek, setSelectedWeek] = useState<Week | null>(null);
    const [games, setGames] = useState<Game[]>([]);
    const [myPicks, setMyPicks] = useState<Pick[]>([]);
    const [theirPicks, setTheirPicks] = useState<Pick[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadWeeks = async () => {
            try {
                const data = await fetchAPI('/weeks');
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

                <div className="mb-6">
                    {selectedWeek && (
                        <h2 className="text-xl font-bold text-gray-800 dark:text-white">
                            Week {selectedWeek.week_number}
                        </h2>
                    )}
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
