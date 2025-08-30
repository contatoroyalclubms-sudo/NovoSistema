import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  TrendingUp, 
  Zap, 
  Globe, 
  Users, 
  Target,
  Cpu,
  Database,
  Signal,
  Cloud,
  Shield,
  Rocket
} from 'lucide-react';

interface RealTimeMetric {
  label: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  color: string;
}

const RealTimeDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<RealTimeMetric[]>([
    { label: 'Throughput', value: 1250, unit: 'msg/min', trend: 'up', color: 'text-green-500' },
    { label: 'Latência', value: 12, unit: 'ms', trend: 'down', color: 'text-blue-500' },
    { label: 'CPU', value: 34, unit: '%', trend: 'stable', color: 'text-yellow-500' },
    { label: 'RAM', value: 2.1, unit: 'GB', trend: 'up', color: 'text-purple-500' },
    { label: 'Rede', value: 89, unit: 'MB/s', trend: 'up', color: 'text-pink-500' },
    { label: 'Storage', value: 156, unit: 'GB', trend: 'stable', color: 'text-indigo-500' }
  ]);

  const [animationKey, setAnimationKey] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => prev.map(metric => ({
        ...metric,
        value: metric.value + (Math.random() - 0.5) * (metric.value * 0.1),
        trend: Math.random() > 0.7 ? (Math.random() > 0.5 ? 'up' : 'down') : metric.trend
      })));
      setAnimationKey(prev => prev + 1);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
      {metrics.map((metric, index) => (
        <div
          key={`${metric.label}-${animationKey}`}
          className="bg-gradient-to-br from-white to-gray-50 backdrop-blur-sm border border-white/20 rounded-xl p-4 shadow-lg hover:shadow-xl transition-all duration-500 group"
          style={{ animationDelay: `${index * 100}ms` }}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg text-white">
              {index === 0 && <Zap className="w-4 h-4" />}
              {index === 1 && <Activity className="w-4 h-4" />}
              {index === 2 && <Cpu className="w-4 h-4" />}
              {index === 3 && <Database className="w-4 h-4" />}
              {index === 4 && <Signal className="w-4 h-4" />}
              {index === 5 && <Cloud className="w-4 h-4" />}
            </div>
            <div className={`w-2 h-2 rounded-full ${
              metric.trend === 'up' ? 'bg-green-400' : 
              metric.trend === 'down' ? 'bg-red-400' : 'bg-yellow-400'
            } animate-pulse`} />
          </div>
          
          <div className="space-y-1">
            <p className="text-xs font-medium text-gray-600">{metric.label}</p>
            <p className={`text-lg font-bold ${metric.color} transition-all duration-300 group-hover:scale-110`}>
              {metric.value.toFixed(metric.label === 'RAM' ? 1 : 0)}
              <span className="text-xs ml-1 opacity-70">{metric.unit}</span>
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

const NeuralVisualization: React.FC = () => {
  const [nodes, setNodes] = useState<Array<{x: number, y: number, active: boolean, id: number}>>([]);

  useEffect(() => {
    // Gerar nós aleatórios
    const newNodes = Array.from({ length: 20 }, (_, i) => ({
      x: Math.random() * 400,
      y: Math.random() * 200,
      active: Math.random() > 0.7,
      id: i
    }));
    setNodes(newNodes);

    const interval = setInterval(() => {
      setNodes(prev => prev.map(node => ({
        ...node,
        active: Math.random() > 0.6
      })));
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 rounded-2xl p-6 overflow-hidden h-64">
      <div className="absolute inset-0 bg-black/20" />
      
      <div className="relative z-10 text-white mb-4">
        <h3 className="text-lg font-bold mb-1">Rede Neural de Notificações</h3>
        <p className="text-sm opacity-80">Processamento em tempo real</p>
      </div>
      
      <svg className="absolute inset-4 w-full h-full" style={{ maxWidth: '400px', maxHeight: '200px' }}>
        {/* Conexões */}
        {nodes.map((node, i) => 
          nodes.slice(i + 1).map((otherNode, j) => (
            <line
              key={`${i}-${j}`}
              x1={node.x}
              y1={node.y}
              x2={otherNode.x}
              y2={otherNode.y}
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="1"
              className={node.active && otherNode.active ? 'animate-pulse' : ''}
            />
          ))
        )}
        
        {/* Nós */}
        {nodes.map(node => (
          <circle
            key={node.id}
            cx={node.x}
            cy={node.y}
            r={node.active ? "6" : "3"}
            fill={node.active ? "#60A5FA" : "rgba(255,255,255,0.3)"}
            className={node.active ? 'animate-pulse' : 'transition-all duration-300'}
          />
        ))}
      </svg>
      
      <div className="absolute bottom-4 right-4 flex items-center gap-2 text-white/70 text-xs">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
        <span>Processando</span>
      </div>
    </div>
  );
};

export { RealTimeDashboard, NeuralVisualization };
