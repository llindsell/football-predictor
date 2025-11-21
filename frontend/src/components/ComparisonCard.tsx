import { Game, Pick, Team } from '@/types';
import Image from 'next/image';
import clsx from 'clsx';

interface ComparisonCardProps {
    game: Game;
    myPick?: Pick;
    theirPick?: Pick;
    theirName: string;
}

export default function ComparisonCard({ game, myPick, theirPick, theirName }: ComparisonCardProps) {
    const TeamDisplay = ({ team, isPicked, label }: { team: Team, isPicked: boolean, label: string }) => (
        <div className={clsx(
            "flex flex-col items-center p-2 rounded-lg border-2 w-full",
            isPicked
                ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                : "border-transparent opacity-50"
        )}>
            <div className="relative w-8 h-8 mb-1">
                <Image
                    src={team.logo_path}
                    alt={team.name}
                    fill
                    className="object-contain"
                />
            </div>
            <span className="font-bold text-xs text-center">{team.abbreviation.toUpperCase()}</span>
            {isPicked && <span className="text-[10px] text-blue-600 font-medium">{label}</span>}
        </div>
    );

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4 mb-4">
            <div className="text-xs text-center text-gray-500 mb-2">
                {game.away_team.name} @ {game.home_team.name}
            </div>

            <div className="grid grid-cols-2 gap-4">
                {/* My Pick Column */}
                <div className="flex flex-col items-center border-r border-gray-100 dark:border-gray-700 pr-4">
                    <span className="text-xs font-medium mb-2 text-gray-500">You</span>
                    {myPick ? (
                        <TeamDisplay
                            team={myPick.selected_team_id === game.home_team.id ? game.home_team : game.away_team}
                            isPicked={true}
                            label="Picked"
                        />
                    ) : (
                        <span className="text-xs text-gray-400 italic">No pick</span>
                    )}
                </div>

                {/* Their Pick Column */}
                <div className="flex flex-col items-center pl-4">
                    <span className="text-xs font-medium mb-2 text-gray-500">{theirName}</span>
                    {theirPick ? (
                        <TeamDisplay
                            team={theirPick.selected_team_id === game.home_team.id ? game.home_team : game.away_team}
                            isPicked={true}
                            label="Picked"
                        />
                    ) : (
                        <span className="text-xs text-gray-400 italic">No pick</span>
                    )}
                </div>
            </div>
        </div>
    );
}
