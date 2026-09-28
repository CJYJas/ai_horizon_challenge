import { Link as LinkIcon, Network, Cpu, ShieldCheck } from 'lucide-react';

export function ExplanationChain({ explanation }) {
  if (!explanation) return null;
  
  const steps = [
    { 
      label: 'Assessment Evidence', 
      value: explanation.evidence?.join(', ') || 'Observed signals',
      icon: Network,
      color: 'text-purple-500',
      bg: 'bg-purple-100'
    },
    { 
      label: 'Identified Problem', 
      value: explanation.problem,
      icon: ShieldCheck,
      color: 'text-rose-500',
      bg: 'bg-rose-100'
    },
    { 
      label: 'Recommended Solution', 
      value: explanation.product_id?.toUpperCase(),
      icon: Cpu,
      color: 'text-blue-500',
      bg: 'bg-blue-100'
    }
  ];
  
  if (explanation.programme_name) {
    steps.push({ 
      label: 'Potential Gov Support', 
      value: explanation.programme_name,
      icon: LinkIcon,
      color: 'text-amber-500',
      bg: 'bg-amber-100'
    });
  }

  return (
    <div className="bg-gray-50/50 rounded-xl p-6 border border-gray-100 shadow-sm">
      <h4 className="text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-6 flex items-center gap-2">
        <LinkIcon className="w-3.5 h-3.5" /> Recommendation Logic Chain
      </h4>
      
      <div className={`grid grid-cols-1 md:grid-cols-2 ${steps.length === 4 ? 'lg:grid-cols-4' : 'lg:grid-cols-3'} gap-4 lg:gap-6 relative`}>
        {steps.map((step, idx) => (
          <div key={idx} className="relative flex flex-col items-center text-center gap-4 group">
            {idx < steps.length - 1 && (
              <div className="hidden lg:block absolute top-5 left-[50%] w-full h-0.5 bg-gradient-to-r from-gray-200 to-transparent z-0"></div>
            )}
            <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-gray-50 bg-white shadow-sm shrink-0 z-10">
              <step.icon className={`w-4 h-4 ${step.color}`} />
            </div>
            
            <div className="w-full h-full p-4 rounded-xl bg-white border border-gray-100 shadow-sm transition-all hover:shadow-md hover:border-gray-200 flex flex-col items-center">
              <span className={`inline-block text-[10px] uppercase font-bold tracking-wider mb-3 px-2.5 py-1 rounded-md ${step.bg} ${step.color}`}>
                {step.label}
              </span>
              <p className="text-sm font-medium text-gray-800 leading-relaxed">
                {step.value}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 pt-5 border-t border-gray-200/60 flex flex-col items-center text-center">
        <span className="text-[10px] uppercase text-primary-500 font-bold tracking-widest mb-2 bg-primary-50 px-3 py-1 rounded-full">
          AI Reason
        </span>
        <p className="text-sm text-gray-600 font-medium max-w-lg italic">
          "{explanation.reason}"
        </p>
      </div>
    </div>
  );
}
