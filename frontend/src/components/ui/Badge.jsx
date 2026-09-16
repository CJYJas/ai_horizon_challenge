export function Badge({ children, variant = 'gray', className = '' }) {
  const variants = {
    gray: "bg-gray-100 text-gray-700",
    blue: "bg-blue-50 text-primary-700 ring-1 ring-inset ring-primary-600/20",
    green: "bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20",
    amber: "bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-600/20",
    red: "bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20"
  };
  
  return (
    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
}
