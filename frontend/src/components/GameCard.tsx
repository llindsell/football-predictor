import { Game, Pick } from '@/types';
import Image from 'next/image';
import clsx from 'clsx';

interface GameCardProps {
    game: Game;
    currentPick?: Pick;
    onPick: (gameId: number, teamId: number) => void;
}

export default function GameCard({ game, currentPick, onPick }: GameCardProps) {
    const isHomePicked = currentPick?.selected_team_id === game.home_team.id;
    const isAwayPicked = currentPick?.selected_team_id === game.away_team.id;

    const TeamButton = ({ team, isPicked, spread }: { team: any, isPicked: boolean, spread?: number }) => (
        <button
            onClick={() => onPick(game.id, team.id)}
            className={clsx(
                "flex flex-col items-center p-4 rounded-lg border-2 transition-all w-full",
                isPicked
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                    : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
            )}
        >
            <div className="relative w-12 h-12 mb-2">
                <Image
                    src={team.logo_path}
                    alt={team.name}
                    fill
                    className="object-contain"
                />
            </div>
            <span className="font-bold text-sm text-center">{team.name}</span>
            {spread !== undefined && (
                <span className="text-xs text-gray-500 mt-1">
                    {spread > 0 ? `+${spread}` : spread}
                </span>
            )}
        </button>
    );

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4 mb-4 relative">
            {game.game_time && (
                <div className="absolute top-2 left-0 right-0 text-center">
                    <span className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">
                        {new Date(game.game_time).toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: 'numeric' })}
                    </span>
                </div>
            )}

            <div className="flex justify-between items-center gap-4 mt-4">
                <TeamButton
                    team={game.away_team}
                    isPicked={isAwayPicked}
                    spread={game.spread > 0 ? -game.spread : -game.spread}
                />

                <div className="flex flex-col items-center text-gray-400 text-sm font-medium">
                    <span>VS</span>
                    {game.over_under && (
                        <span className="text-[10px] mt-1 text-gray-500">
                            O/U {game.over_under}
                        </span>
                    )}
                </div>

                <TeamButton
                    team={game.home_team}
                    isPicked={isHomePicked}
                    spread={game.spread}
                />
            </div>
        </div>
    );
}
