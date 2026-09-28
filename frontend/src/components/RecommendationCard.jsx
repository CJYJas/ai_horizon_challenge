import { CheckCircle2, ChevronRight, Zap } from 'lucide-react';
import { ExplanationChain } from './ExplanationChain';
import { Badge } from './ui/Badge';

export function RecommendationCard({ recommendation, rationale }) {
  return (
    <div className="relative group rounded-2xl bg-white border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-all duration-300">
      {/* Decorative top border gradient */}
      <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-primary-500 to-blue-500"></div>

      <div className="flex flex-col">
        {/* Top Section: Identity & Deep Dive */}
        <div className="flex flex-col xl:flex-row border-b border-gray-100">
          <div className="xl:w-1/3 p-6 md:p-8 border-b xl:border-b-0 xl:border-r border-gray-100 bg-white flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-6 h-6 text-primary-500 fill-primary-100" />
              <h3 className="text-2xl font-bold text-gray-900 uppercase tracking-tight">
                {recommendation.product_id}
              </h3>
            </div>
            <p className="text-gray-500 font-medium mb-4">
              {recommendation.expected_outcome}
            </p>
            {recommendation.transformation_area && (
              <Badge variant="blue" className="self-start shadow-sm">
                {recommendation.transformation_area}
              </Badge>
            )}
          </div>

          <div className="xl:w-2/3 p-6 md:p-8 bg-gray-50/30">
            {rationale ? (
              <div className="grid md:grid-cols-2 gap-6 h-full">
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col">
                  <h4 className="flex items-center gap-2 text-lg font-bold text-gray-900 mb-3 border-b border-gray-100 pb-3">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                    Why this fits your business
                  </h4>
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {rationale.why_suitable}
                  </p>
                </div>
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col">
                  <h4 className="flex items-center gap-2 text-lg font-bold text-gray-900 mb-3 border-b border-gray-100 pb-3">
                    <ChevronRight className="w-5 h-5 text-primary-500" />
                    How to begin
                  </h4>
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {rationale.implementation_suggestion}
                  </p>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400 text-sm">
                Detailed implementation plan pending
              </div>
            )}
          </div>
        </div>

        {/* Bottom Section: Full Width Logic Chain */}
        <div className="p-6 md:p-8 bg-white">
          {recommendation.explanation ? (
            <ExplanationChain explanation={recommendation.explanation} />
          ) : (
            <div className="bg-gray-50 rounded-xl p-6 border border-gray-100 text-center max-w-3xl mx-auto">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">AI Reasoning</p>
              <p className="text-gray-700 text-sm leading-relaxed italic">"{recommendation.reason}"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
