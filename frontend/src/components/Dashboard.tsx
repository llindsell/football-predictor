'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { fetchAPI } from '@/lib/api';
import { Week, Game, Pick } from '@/types';
import GameCard from './GameCard';

export default function Dashboard() {
    const { user, token } = useAuth();

    const [selectedWeek, setSelectedWeek] = useState<Week | null>(null);
    const [games, setGames] = useState<Game[]>([]);
    const [picks, setPicks] = useState<Pick[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadWeeks = async () => {
            try {
                const data = await fetchAPI('/weeks');
                if (data.length > 0) {
                    setSelectedWeek(data[0]); // Default to first week (or current)
                }
            } catch (error) {
                console.error('Failed to load weeks', error);
            }
        };
        loadWeeks();
    }, []);

    useEffect(() => {
        if (!selectedWeek || !token) return;

        const loadData = async () => {
            setLoading(true);
            try {
                const [gamesData, picksData] = await Promise.all([
                    fetchAPI(`/weeks/${selectedWeek.id}/games`),
                    fetchAPI('/picks/me', { headers: { Authorization: `Bearer ${token}` } })
                ]);
                setGames(gamesData);
                setPicks(picksData);
            } catch (error) {
                console.error('Failed to load games/picks', error);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, [selectedWeek, token]);

    const handlePick = async (gameId: number, teamId: number) => {
        if (!token) return;

        const existingPick = picks.find(p => p.game_id === gameId);
        const isSamePick = existingPick?.selected_team_id === teamId;

        // Store previous state for revert
        const previousPicks = [...picks];

        // Optimistic update
        if (isSamePick) {
            // Remove pick
            setPicks(prev => prev.filter(p => p.game_id !== gameId));
        } else {
            // Add/Update pick
            const newPick = { game_id: gameId, selected_team_id: teamId } as Pick;
            setPicks(prev => {
                if (existingPick) {
                    return prev.map(p => p.game_id === gameId ? { ...p, selected_team_id: teamId } : p);
                }
                return [...prev, newPick];
            });
        }

        try {
            if (isSamePick) {
                await fetchAPI(`/picks/${gameId}`, {
                    method: 'DELETE',
                    headers: { Authorization: `Bearer ${token}` },
                });
            } else {
                await fetchAPI('/picks/', {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${token}` },
                    body: JSON.stringify({ game_id: gameId, selected_team_id: teamId }),
                });
            }
        } catch (error) {
            console.error('Failed to update pick', error);
            // Revert to previous state
            setPicks(previousPicks);

            // Show error message to user
            if (error instanceof Error) {
                alert(error.message);
            }
        }
    };

    if (!user) {
        return <div className="p-8">Please login to view picks.</div>;
    }

    return (
        <div className="max-w-md mx-auto pb-20">
            <div className="px-4 mb-4 pt-4">
                {selectedWeek && (
                    <h2 className="inline-block px-4 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-sm font-bold">
                        Week {selectedWeek.week_number}
                    </h2>
                )}
            </div>

            <div className="px-4">
                {loading ? (
                    <div className="text-center py-8">Loading...</div>
                ) : (
                    games.map(game => (
                        <GameCard
                            key={game.id}
                            game={game}
                            currentPick={picks.find(p => p.game_id === game.id)}
                            onPick={handlePick}
                        />
                    ))
                )}
            </div>
        </div>
    );
}
