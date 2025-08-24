/**
 * Gamification Dashboard Component - Sprint 5
 * Sistema Universal de Gestão de Eventos
 * 
 * Advanced gamification interface with:
 * - Real-time leaderboards
 * - Achievement tracking
 * - Points visualization
 * - Badge showcase
 * - Progress indicators
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Trophy, Award, Zap, Star, Crown, Medal, Target, TrendingUp,
  ChevronUp, ChevronDown, Calendar, Users, Activity, Gift
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface UserProfile {
  user_id: string;
  name: string;
  email: string;
  total_points: number;
  monthly_points: number;
  current_badge: {
    name: string;
    icon: string;
    color: string;
    min_points: number;
  };
  next_badge: {
    name: string;
    icon: string;
    color: string;
    points_needed: number;
  } | null;
  achievements: Array<{
    name: string;
    description: string;
    type: string;
    points: number;
    unlocked_at: string;
  }>;
  activity_stats: {
    total_actions: number;
    avg_points_per_action: number;
    last_activity: string;
  };
}

interface LeaderboardEntry {
  position: number;
  user_id: string;
  name: string;
  email: string;
  total_points: number;
  total_actions: number;
  badge: string;
  badge_icon: string;
  badge_color: string;
  last_activity: string;
  is_current_user: boolean;
}

interface Achievement {
  type: string;
  name: string;
  icon: string;
  points: number;
  is_unlocked: boolean;
  unlocked_at: string | null;
}

const BadgeIcon: React.FC<{ badge: string; className?: string }> = ({ badge, className = "w-8 h-8" }) => {
  const badgeIcons = {
    'bronze': '🥉',
    'silver': '🥈', 
    'gold': '🥇',
    'platinum': '🏆',
    'diamond': '💎'
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <span className="text-2xl">{badgeIcons[badge as keyof typeof badgeIcons] || '🌟'}</span>
    </div>
  );
};

const ProgressBar: React.FC<{ 
  current: number; 
  max: number; 
  color?: string; 
  showLabels?: boolean;
  height?: string;
}> = ({ 
  current, 
  max, 
  color = 'bg-blue-500', 
  showLabels = true,
  height = 'h-3'
}) => {
  const percentage = Math.min((current / max) * 100, 100);

  return (
    <div className="w-full">
      <div className={`w-full ${height} bg-gray-200 rounded-full overflow-hidden`}>
        <motion.div 
          className={`h-full ${color} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </div>
      {showLabels && (
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>{current.toLocaleString()}</span>
          <span>{max.toLocaleString()}</span>
        </div>
      )}
    </div>
  );
};

const AnimatedCounter: React.FC<{ 
  value: number; 
  format?: 'number' | 'points';
  duration?: number;
}> = ({ value, format = 'number', duration = 1 }) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = value;
    const startTime = Date.now();
    const durationMs = duration * 1000;

    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / durationMs, 1);
      
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const current = Math.floor(start + (end - start) * easeOutQuart);
      
      setDisplayValue(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  const formatValue = (val: number) => {
    switch (format) {
      case 'points':
        return `${val.toLocaleString()} pts`;
      default:
        return val.toLocaleString();
    }
  };

  return <span>{formatValue(displayValue)}</span>;
};

const ProfileCard: React.FC<{ profile: UserProfile }> = ({ profile }) => {
  const progressToNext = profile.next_badge 
    ? ((profile.total_points - profile.current_badge.min_points) / 
       (profile.next_badge.points_needed)) * 100
    : 100;

  return (
    <motion.div 
      className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <BadgeIcon badge={profile.current_badge.name} className="w-16 h-16" />
            <motion.div 
              className="absolute -top-1 -right-1 bg-yellow-400 rounded-full p-1"
              animate={{ rotate: [0, -10, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            >
              <Crown className="w-4 h-4 text-yellow-800" />
            </motion.div>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">{profile.name}</h2>
            <p className="text-gray-600 capitalize">{profile.current_badge.name} Badge</p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">
            <AnimatedCounter value={profile.total_points} format="points" />
          </div>
          <p className="text-sm text-gray-600">Pontos totais</p>
        </div>
      </div>

      {profile.next_badge && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Progresso para {profile.next_badge.name}
            </span>
            <span className="text-sm text-gray-600">
              {profile.next_badge.points_needed} pontos restantes
            </span>
          </div>
          <ProgressBar 
            current={profile.total_points - profile.current_badge.min_points}
            max={profile.next_badge.points_needed}
            color="bg-gradient-to-r from-blue-500 to-purple-500"
          />
        </div>
      )}

      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">
            <AnimatedCounter value={profile.monthly_points} />
          </div>
          <p className="text-xs text-gray-600">Este mês</p>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">
            <AnimatedCounter value={profile.achievements.length} />
          </div>
          <p className="text-xs text-gray-600">Conquistas</p>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">
            <AnimatedCounter value={profile.activity_stats.total_actions} />
          </div>
          <p className="text-xs text-gray-600">Ações</p>
        </div>
      </div>
    </motion.div>
  );
};

const LeaderboardTable: React.FC<{ 
  leaderboard: LeaderboardEntry[];
  period: string;
  onPeriodChange: (period: string) => void;
}> = ({ leaderboard, period, onPeriodChange }) => {
  const periods = [
    { value: 'day', label: 'Hoje' },
    { value: 'week', label: 'Semana' },
    { value: 'month', label: 'Mês' },
    { value: 'year', label: 'Ano' },
    { value: 'all', label: 'Todos os tempos' }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Trophy className="w-5 h-5 mr-2 text-yellow-500" />
          Ranking
        </h3>
        
        <select
          value={period}
          onChange={(e) => onPeriodChange(e.target.value)}
          className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {periods.map(p => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
      </div>

      <div className="space-y-3">
        <AnimatePresence>
          {leaderboard.slice(0, 10).map((entry, index) => (
            <motion.div
              key={entry.user_id}
              className={`flex items-center justify-between p-3 rounded-lg ${
                entry.is_current_user 
                  ? 'bg-blue-50 border-2 border-blue-200' 
                  : 'bg-gray-50'
              }`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <div className="flex items-center space-x-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                  entry.position === 1 ? 'bg-yellow-100 text-yellow-800' :
                  entry.position === 2 ? 'bg-gray-100 text-gray-800' :
                  entry.position === 3 ? 'bg-orange-100 text-orange-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {entry.position <= 3 ? (
                    entry.position === 1 ? '🥇' :
                    entry.position === 2 ? '🥈' : '🥉'
                  ) : (
                    entry.position
                  )}
                </div>
                
                <BadgeIcon badge={entry.badge} className="w-6 h-6" />
                
                <div>
                  <div className="font-medium text-gray-900">{entry.name}</div>
                  <div className="text-xs text-gray-600">
                    {entry.total_actions} ações
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="font-bold text-blue-600">
                  {entry.total_points.toLocaleString()} pts
                </div>
                <div className="text-xs text-gray-600">
                  {new Date(entry.last_activity).toLocaleDateString('pt-BR')}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

const AchievementsGrid: React.FC<{ achievements: Achievement[] }> = ({ achievements }) => {
  const [showAll, setShowAll] = useState(false);
  const displayedAchievements = showAll ? achievements : achievements.slice(0, 6);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Award className="w-5 h-5 mr-2 text-purple-500" />
          Conquistas
        </h3>
        
        <div className="text-sm text-gray-600">
          {achievements.filter(a => a.is_unlocked).length} de {achievements.length}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {displayedAchievements.map((achievement, index) => (
          <motion.div
            key={achievement.type}
            className={`p-4 rounded-lg border-2 transition-all ${
              achievement.is_unlocked 
                ? 'bg-green-50 border-green-200' 
                : 'bg-gray-50 border-gray-200 grayscale'
            }`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
          >
            <div className="text-center">
              <div className="text-3xl mb-2">{achievement.icon}</div>
              <h4 className="font-medium text-gray-900 text-sm mb-1">
                {achievement.name}
              </h4>
              <p className="text-xs text-gray-600 mb-2">
                {achievement.points} pontos
              </p>
              {achievement.is_unlocked ? (
                <div className="text-xs text-green-600 font-medium">
                  ✓ Desbloqueada
                </div>
              ) : (
                <div className="text-xs text-gray-400">
                  Bloqueada
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {achievements.length > 6 && (
        <div className="text-center mt-4">
          <button
            onClick={() => setShowAll(!showAll)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            {showAll ? 'Ver menos' : `Ver todas (${achievements.length})`}
          </button>
        </div>
      )}
    </div>
  );
};

const RecentActivity: React.FC<{ activities: any[] }> = ({ activities = [] }) => {
  const mockActivities = [
    { id: 1, type: 'checkin', description: 'Check-in no evento Tech Conference', points: 25, time: '2 horas atrás', icon: '📍' },
    { id: 2, type: 'achievement', description: 'Desbloqueou "Primeira Presença"', points: 50, time: '3 horas atrás', icon: '🏆' },
    { id: 3, type: 'points', description: 'Vendeu produto no PDV', points: 75, time: '1 dia atrás', icon: '💰' },
    { id: 4, type: 'social', description: 'Compartilhou evento nas redes sociais', points: 5, time: '2 dias atrás', icon: '📱' },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
        <Activity className="w-5 h-5 mr-2 text-green-500" />
        Atividade Recente
      </h3>

      <div className="space-y-3">
        {mockActivities.map((activity, index) => (
          <motion.div
            key={activity.id}
            className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <div className="text-2xl">{activity.icon}</div>
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-900">
                {activity.description}
              </div>
              <div className="text-xs text-gray-600">{activity.time}</div>
            </div>
            <div className="text-right">
              <div className="text-sm font-bold text-green-600">
                +{activity.points} pts
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export const GamificationDashboard: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('month');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Buscar perfil do usuário
        const profileResponse = await fetch('/api/v1/gamificacao/my-profile');
        const profileData = await profileResponse.json();
        if (profileData.success) {
          setProfile(profileData.profile);
        }

        // Buscar leaderboard
        const leaderboardResponse = await fetch(`/api/v1/gamificacao/leaderboard?period=${selectedPeriod}`);
        const leaderboardData = await leaderboardResponse.json();
        if (leaderboardData.success) {
          setLeaderboard(leaderboardData.leaderboard);
        }

        // Buscar conquistas
        const achievementsResponse = await fetch('/api/v1/gamificacao/achievements');
        const achievementsData = await achievementsResponse.json();
        if (achievementsData.success) {
          setAchievements(achievementsData.achievements);
        }

        setLoading(false);
      } catch (error) {
        console.error('Erro ao carregar dados de gamificação:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedPeriod]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Sistema de Gamificação
          </h1>
          <p className="text-gray-600">
            Ganhe pontos, desbloqueie conquistas e compete com outros usuários
          </p>
        </div>

        {/* User Profile */}
        {profile && <ProfileCard profile={profile} />}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Leaderboard */}
          <LeaderboardTable
            leaderboard={leaderboard}
            period={selectedPeriod}
            onPeriodChange={setSelectedPeriod}
          />

          {/* Recent Activity */}
          <RecentActivity activities={[]} />
        </div>

        {/* Achievements */}
        <AchievementsGrid achievements={achievements} />
      </div>
    </div>
  );
};

export default GamificationDashboard;