export interface Team {
    id: number;
    name: string;
    abbreviation: string;
    logo_path: string;
}

export interface Week {
    id: number;
    season: number;
    week_number: number;
    start_date: string;
    end_date: string;
}

export interface Game {
    id: number;
    week_id: number;
    home_team: Team;
    away_team: Team;
    spread: number;
    home_score?: number;
    away_score?: number;
    status: string;
    game_time?: string;
    over_under?: number;
}

export interface Pick {
    id: number;
    user_id: number;
    game_id: number;
    selected_team_id: number;
}

export interface LeaderboardEntry {
    rank: number;
    user_id: number;
    user_name: string;
    profile_picture?: string;
    correct_picks: number;
    total_picks: number;
    win_rate: number;
}
