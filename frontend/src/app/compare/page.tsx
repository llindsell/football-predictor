'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { fetchAPI } from '@/lib/api';
import { Week, Game, Pick, User } from '@/types';
import ComparisonCard from '@/components/ComparisonCard';

export default function ComparePage() {
    const { user, token } = useAuth();

    const [selectedWeek, setSelectedWeek] = useState<Week | null>(null);
    const [usersWithPicks, setUsersWithPicks] = useState<User[]>([]);
    const [selectedOpponentId, setSelectedOpponentId] = useState<number | null>(null);

    const [games, setGames] = useState<Game[]>([]);
    const [myPicks, setMyPicks] = useState<Pick[]>([]);
    const [theirPicks, setTheirPicks] = useState<Pick[]>([]);
    const [loading, setLoading] = useState(true);

    // Load weeks
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

    // Load users when week changes
    useEffect(() => {
        if (!selectedWeek || !token) return;

        const loadUsers = async () => {
            try {
                const data: User[] = await fetchAPI(`/picks/week/${selectedWeek.id}/users`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsersWithPicks(data);

                // Default to first user that isn't me, or just first user
                if (data.length > 0 && !selectedOpponentId) {
                    const opponent = data.find(u => u.id !== user?.id) || data[0];
                    if (opponent) setSelectedOpponentId(opponent.id);
                }
            } catch (error) {
                console.error('Failed to load users', error);
            }
        };
        loadUsers();
    }, [selectedWeek, token, user]);

    // Load comparison data
    useEffect(() => {
        if (!selectedWeek || !token || !selectedOpponentId) return;

        const loadData = async () => {
            setLoading(true);
            try {
                const [gamesData, myPicksData, theirPicksData] = await Promise.all([
                    fetchAPI(`/weeks/${selectedWeek.id}/games`),
                    fetchAPI('/picks/me', { headers: { Authorization: `Bearer ${token}` } }),
                    fetchAPI(`/picks/user/${selectedOpponentId}`, { headers: { Authorization: `Bearer ${token}` } })
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
    }, [selectedWeek, token, selectedOpponentId]);

    if (!user) return <div className="p-8">Please login.</div>;

    const selectedOpponent = usersWithPicks.find(u => u.id === selectedOpponentId);

    return (
        <main className="max-w-md mx-auto pb-20">
            <div className="p-4">
                <div className="flex justify-between items-center mb-6">
                    {selectedWeek && (
                        <h2 className="inline-block px-4 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-sm font-bold">
                            Week {selectedWeek.week_number}
                        </h2>
                    )}

                    <select
                        className="p-2 rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm"
                        value={selectedOpponentId || ''}
                        onChange={(e) => setSelectedOpponentId(Number(e.target.value))}
                    >
                        <option value="" disabled>Select Opponent</option>
                        {usersWithPicks.map(u => (
                            <option key={u.id} value={u.id}>
                                {u.name.split(' ')[0]} {u.id === user.id ? '(You)' : ''}
                            </option>
                        ))}
                    </select>
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
                            theirName={selectedOpponent ? selectedOpponent.name.split(' ')[0] : 'Opponent'}
                        />
                    ))
                )}

                {!loading && games.length === 0 && (
                    <div className="text-center py-8 text-gray-500">No games found for this week.</div>
                )}
            </div>
        </main>
    );
}
