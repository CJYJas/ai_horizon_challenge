export function ProgressBar({ value, max = 5, colorClass = "bg-primary-500", className = "" }) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2.5 ${className}`}>
      <div 
        className={`h-2.5 rounded-full ${colorClass} transition-all duration-500`} 
        style={{ width: `${percentage}%` }}
      ></div>
    </div>
  );
}
