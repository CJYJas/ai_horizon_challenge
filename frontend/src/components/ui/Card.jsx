export function Card({ children, className = '', noPadding = false }) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-100 ${noPadding ? '' : 'p-6'} ${className}`}>
      {children}
    </div>
  );
}
