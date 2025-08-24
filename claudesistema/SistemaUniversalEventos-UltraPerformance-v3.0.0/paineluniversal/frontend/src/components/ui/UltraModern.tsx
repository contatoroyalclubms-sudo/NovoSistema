// Design System Ultra-Moderno - Componentes Base
import React from 'react';
import { cn } from '../../lib/utils';
import { gradients, glassVariants } from '../../lib/design-constants';

// Interface para propriedades base
interface BaseProps {
  className?: string;
  children?: React.ReactNode;
}

// Botão Ultra-Moderno
interface UltraButtonProps extends BaseProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'quantum';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  glow?: boolean;
  shimmer?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}

export const UltraButton: React.FC<UltraButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  glow = false,
  shimmer = false,
  onClick,
  disabled = false,
  ...props
}) => {
  const baseClasses = "relative overflow-hidden font-semibold transition-all duration-300 transform";
  
  const variants = {
    primary: "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-2xl",
    secondary: "bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white shadow-2xl",
    ghost: "backdrop-blur-xl bg-white/10 border border-white/20 text-white hover:bg-white/20",
    quantum: "bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:via-purple-500 hover:to-pink-500 text-white shadow-2xl"
  };

  const sizes = {
    sm: "px-4 py-2 text-sm rounded-lg",
    md: "px-6 py-3 text-base rounded-xl",
    lg: "px-8 py-4 text-lg rounded-2xl",
    xl: "px-10 py-5 text-xl rounded-2xl"
  };

  const glowClass = glow ? "hover:shadow-[0_0_30px_rgba(139,92,246,0.4)] hover:scale-105" : "hover:scale-105";
  const shimmerClass = shimmer ? "animate-shimmer" : "";

  return (
    <button
      className={cn(
        baseClasses,
        variants[variant],
        sizes[size],
        glowClass,
        shimmerClass,
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {shimmer && (
        <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
      )}
      <span className="relative z-10">{children}</span>
    </button>
  );
};

// Card Ultra-Moderno
interface UltraCardProps extends BaseProps {
  variant?: 'glass' | 'solid' | 'gradient' | 'neural';
  hover?: boolean;
  glow?: boolean;
}

export const UltraCard: React.FC<UltraCardProps> = ({
  children,
  className,
  variant = 'glass',
  hover = true,
  glow = false,
  ...props
}) => {
  const baseClasses = "rounded-3xl p-6 transition-all duration-500";
  
  const variants = {
    glass: "backdrop-blur-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20",
    solid: "bg-gray-900 border border-gray-800",
    gradient: "bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-cyan-500/20 border border-white/20",
    neural: "backdrop-blur-3xl bg-black/30 border border-purple-500/30"
  };

  const hoverClass = hover ? "hover:bg-white/[0.12] hover:transform hover:scale-[1.02]" : "";
  const glowClass = glow ? "hover:shadow-[0_0_40px_rgba(139,92,246,0.3)]" : "";

  return (
    <div
      className={cn(
        baseClasses,
        variants[variant],
        hoverClass,
        glowClass,
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

// Badge Ultra-Moderno
interface UltraBadgeProps extends BaseProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  pulse?: boolean;
}

export const UltraBadge: React.FC<UltraBadgeProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  pulse = false,
  ...props
}) => {
  const baseClasses = "inline-flex items-center font-semibold transition-all duration-300";
  
  const variants = {
    primary: "bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 text-purple-300",
    secondary: "bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30 text-blue-300",
    success: "bg-gradient-to-r from-emerald-500/20 to-green-500/20 border border-emerald-500/30 text-emerald-300",
    warning: "bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 text-yellow-300",
    danger: "bg-gradient-to-r from-red-500/20 to-rose-500/20 border border-red-500/30 text-red-300"
  };

  const sizes = {
    sm: "px-3 py-1 text-xs rounded-full",
    md: "px-4 py-2 text-sm rounded-full",
    lg: "px-6 py-3 text-base rounded-full"
  };

  const pulseClass = pulse ? "animate-pulse" : "";

  return (
    <span
      className={cn(
        baseClasses,
        variants[variant],
        sizes[size],
        pulseClass,
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

// Título com Gradiente
interface GradientTitleProps extends BaseProps {
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  glow?: boolean;
}

export const GradientTitle: React.FC<GradientTitleProps> = ({
  children,
  className,
  level = 1,
  glow = false,
  ...props
}) => {
  const Tag = `h${level}` as keyof JSX.IntrinsicElements;
  
  const sizes = {
    1: "text-6xl lg:text-7xl",
    2: "text-5xl lg:text-6xl",
    3: "text-4xl lg:text-5xl",
    4: "text-3xl lg:text-4xl",
    5: "text-2xl lg:text-3xl",
    6: "text-xl lg:text-2xl"
  };

  const glowClass = glow ? "drop-shadow-[0_0_30px_rgba(139,92,246,0.5)]" : "";

  return (
    <Tag
      className={cn(
        sizes[level],
        "font-black bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent",
        glowClass,
        className
      )}
      {...props}
    >
      {children}
    </Tag>
  );
};

// Container com efeito Neural
interface NeuralContainerProps extends BaseProps {
  particles?: boolean;
  intensity?: 'low' | 'medium' | 'high';
}

export const NeuralContainer: React.FC<NeuralContainerProps> = ({
  children,
  className,
  particles = true,
  intensity = 'medium',
  ...props
}) => {
  const intensityMap = {
    low: 30,
    medium: 60,
    high: 100
  };

  return (
    <div className={cn("relative overflow-hidden", className)} {...props}>
      {/* Background Neural */}
      <div className="fixed inset-0 z-0">
        <div 
          className="absolute inset-0 opacity-50"
          style={{
            background: `
              radial-gradient(circle at 25% 25%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 75% 75%, rgba(236, 72, 153, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 30%)
            `
          }}
        />
        
        {/* Partículas Animadas */}
        {particles && (
          <div className="absolute inset-0">
            {[...Array(intensityMap[intensity])].map((_, i) => (
              <div
                key={i}
                className="absolute animate-particle"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDuration: `${5 + Math.random() * 10}s`,
                  animationDelay: `${Math.random() * 5}s`
                }}
              >
                <div 
                  className="w-1 h-1 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full opacity-60"
                  style={{ boxShadow: '0 0 10px currentColor' }}
                />
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};

// Input Ultra-Moderno
interface UltraInputProps {
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  type?: string;
  className?: string;
  icon?: React.ReactNode;
  glow?: boolean;
}

export const UltraInput: React.FC<UltraInputProps> = ({
  placeholder,
  value,
  onChange,
  type = "text",
  className,
  icon,
  glow = false,
  ...props
}) => {
  const glowClass = glow ? "focus:shadow-[0_0_30px_rgba(139,92,246,0.3)]" : "";

  return (
    <div className="relative">
      {icon && (
        <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">
          {icon}
        </div>
      )}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        className={cn(
          "w-full backdrop-blur-xl bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500/50 transition-all duration-300",
          icon && "pl-12",
          glowClass,
          className
        )}
        {...props}
      />
    </div>
  );
};

// Loading Spinner Quântico
interface QuantumSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const QuantumSpinner: React.FC<QuantumSpinnerProps> = ({
  size = 'md',
  className
}) => {
  const sizes = {
    sm: "w-6 h-6",
    md: "w-8 h-8",
    lg: "w-12 h-12"
  };

  return (
    <div className={cn("relative", sizes[size], className)}>
      <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-purple-500 border-r-pink-500 animate-spin"></div>
      <div className="absolute inset-1 rounded-full border-2 border-transparent border-t-cyan-500 border-l-blue-500 animate-spin animate-reverse"></div>
      <div className="absolute inset-2 rounded-full border-2 border-transparent border-b-purple-500 border-r-pink-500 animate-spin"></div>
    </div>
  );
};

// Tooltip Ultra-Moderno
interface UltraTooltipProps extends BaseProps {
  content: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export const UltraTooltip: React.FC<UltraTooltipProps> = ({
  children,
  content,
  position = 'top',
  className
}) => {
  const [show, setShow] = React.useState(false);

  const positions = {
    top: "bottom-full left-1/2 transform -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 transform -translate-x-1/2 mt-2",
    left: "right-full top-1/2 transform -translate-y-1/2 mr-2",
    right: "left-full top-1/2 transform -translate-y-1/2 ml-2"
  };

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      {children}
      {show && (
        <div className={cn(
          "absolute z-50 px-3 py-2 text-sm text-white backdrop-blur-xl bg-black/80 border border-white/20 rounded-lg whitespace-nowrap transition-all duration-200",
          positions[position],
          className
        )}>
          {content}
        </div>
      )}
    </div>
  );
};

export default {
  UltraButton,
  UltraCard,
  UltraBadge,
  GradientTitle,
  NeuralContainer,
  UltraInput,
  QuantumSpinner,
  UltraTooltip,
  gradients,
  glassVariants
};
