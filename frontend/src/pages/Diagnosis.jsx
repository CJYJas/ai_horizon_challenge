import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Activity, AlertTriangle, ArrowRight, Target, Shield, Users, Zap, Briefcase, ChevronDown, Package, Search, BarChart3, ArrowDown, TrendingUp } from 'lucide-react';
import { api } from '../api/client';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { MaturityChart } from '../components/MaturityChart';

export function Diagnosis() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDiagnosis() {
      try {
        const res = await api.getDiagnosis(id);
        setData(res);
      } catch (err) {
        console.error(err);
        setError("Failed to load diagnosis results.");
      } finally {
        setLoading(false);
      }
    }
    loadDiagnosis();
  }, [id]);

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  if (error) return <div className="text-center text-red-500 py-20">{error}</div>;
  if (!data) return null;

  const { top_pain_points, maturity_scores, recommendations } = data;

  // Find biggest gap
  let biggestGap = { name: '', score: 5 };
  Object.entries(maturity_scores).forEach(([key, val]) => {
    if (val < biggestGap.score) {
      biggestGap = { name: key.replace('_', ' '), score: val };
    }
  });

  const getRecommendation = (problem) => {
    return recommendations.find(r => r.linked_pain_point === problem) || null;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex justify-between items-end border-b border-gray-200 pb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Diagnostic Intelligence</h1>
            <p className="text-gray-500 mt-2 text-lg">Causal analysis mapping your assessment to actionable transformations.</p>
          </div>
          <Button onClick={() => navigate(`/simulator/${id}`)}>
            View Financial Impact <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 items-start">
          
          {/* Left Column: Causal Diagnostic Chains (Focus) */}
          <div className="lg:col-span-2 space-y-8">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Search className="w-5 h-5 text-primary-600" /> Causal Diagnostic Findings
            </h2>
            
            {top_pain_points.map((pt, idx) => {
              const rec = getRecommendation(pt.problem);
              
              return (
                <div key={idx} className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                  <div className="bg-gray-50 px-6 py-4 border-b border-gray-100 flex justify-between items-center">
                    <Badge variant="red" className="uppercase font-bold">Priority {pt.priority_rank}</Badge>
                    <span className="text-sm text-gray-500 font-medium">Diagnostic Chain #{idx + 1}</span>
                  </div>
                  
                  <div className="p-8">
                    <div className="relative">
                      {/* Vertical line connecting nodes */}
                      <div className="absolute left-6 top-10 bottom-10 w-0.5 bg-gray-200 -z-10"></div>
                      
                      {/* Node 1: Evidence */}
                      <div className="flex gap-6 mb-8 relative z-0">
                        <div className="w-12 h-12 bg-white border-2 border-gray-200 rounded-full flex items-center justify-center flex-shrink-0 text-gray-500 shadow-sm">
                          <BarChart3 className="w-5 h-5" />
                        </div>
                        <div className="pt-2">
                          <h4 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">1. Assessment Evidence</h4>
                          <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                            <p className="text-gray-700 italic">"{pt.evidence.join('", "')}"</p>
                          </div>
                        </div>
                      </div>

                      {/* Node 2: Problem */}
                      <div className="flex gap-6 mb-8 relative z-0">
                        <div className="w-12 h-12 bg-white border-2 border-amber-200 rounded-full flex items-center justify-center flex-shrink-0 text-amber-500 shadow-sm">
                          <AlertTriangle className="w-5 h-5" />
                        </div>
                        <div className="pt-2 w-full">
                          <h4 className="text-sm font-bold text-amber-500 uppercase tracking-wider mb-2">2. Operational Problem</h4>
                          <div className="bg-amber-50/50 p-4 rounded-xl border border-amber-100">
                            <p className="text-gray-900 font-medium text-lg">{pt.problem}</p>
                          </div>
                        </div>
                      </div>

                      {/* Node 3: Root Cause */}
                      <div className="flex gap-6 mb-8 relative z-0">
                        <div className="w-12 h-12 bg-white border-2 border-gray-300 rounded-full flex items-center justify-center flex-shrink-0 text-gray-600 shadow-sm">
                          <Search className="w-5 h-5" />
                        </div>
                        <div className="pt-2 w-full">
                          <h4 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">3. Root Cause Analysis</h4>
                          <p className="text-gray-800 leading-relaxed bg-white p-4 rounded-xl border border-gray-200 shadow-sm">{pt.root_cause}</p>
                        </div>
                      </div>

                      {/* Node 4: Impact */}
                      <div className="flex gap-6 mb-8 relative z-0">
                        <div className="w-12 h-12 bg-red-100 border-2 border-red-200 rounded-full flex items-center justify-center flex-shrink-0 text-red-600 shadow-sm">
                          <TrendingUp className="w-5 h-5" />
                        </div>
                        <div className="pt-2 w-full">
                          <h4 className="text-sm font-bold text-red-500 uppercase tracking-wider mb-2">4. Business Impact</h4>
                          <div className="bg-red-50 p-4 rounded-xl border border-red-100">
                            <p className="text-red-900 font-semibold">{pt.business_impact}</p>
                          </div>
                        </div>
                      </div>

                      {/* Node 5: Transformation Area */}
                      {rec && (
                        <div className="flex gap-6 mb-8 relative z-0">
                          <div className="w-12 h-12 bg-blue-50 border-2 border-blue-200 rounded-full flex items-center justify-center flex-shrink-0 text-blue-600 shadow-sm">
                            <Activity className="w-5 h-5" />
                          </div>
                          <div className="pt-2 w-full">
                            <h4 className="text-sm font-bold text-blue-500 uppercase tracking-wider mb-2">5. Target Transformation Area</h4>
                            <p className="text-blue-900 font-semibold text-lg capitalize">{rec.transformation_area || 'Digital Solution'}</p>
                          </div>
                        </div>
                      )}

                      {/* Node 6: Solution */}
                      {rec && (
                        <div className="flex gap-6 relative z-0">
                          <div className="w-12 h-12 bg-primary-600 border-2 border-primary-700 rounded-full flex items-center justify-center flex-shrink-0 text-white shadow-md">
                            <Package className="w-5 h-5" />
                          </div>
                          <div className="pt-2 w-full">
                            <h4 className="text-sm font-bold text-primary-600 uppercase tracking-wider mb-2">6. Recommended Exabytes Solution</h4>
                            <div className="bg-primary-50 p-5 rounded-xl border border-primary-200 shadow-sm">
                              <p className="text-primary-900 font-bold text-xl uppercase mb-2">{rec.product_id}</p>
                              <p className="text-primary-800 text-sm">{rec.expected_outcome}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Column: Maturity Radar (Secondary) */}
          <div className="space-y-6">
            
            {/* Insight Card */}
            <Card className="bg-gray-900 border-gray-800 text-white">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Diagnostic Insight</h3>
              <p className="text-gray-300 mb-2">Your biggest digital gap is</p>
              <p className="text-2xl font-bold text-amber-400 capitalize flex items-center gap-2">
                <AlertTriangle className="w-6 h-6" /> {biggestGap.name}
              </p>
              <p className="text-gray-400 mt-4 text-sm leading-relaxed">
                Addressing this area will yield the highest immediate ROI for your transformation journey.
              </p>
            </Card>

            {/* Radar Chart */}
            <Card>
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-6 text-center">Digital Maturity Index</h3>
              
              <MaturityChart scores={maturity_scores} />
            </Card>
            
          </div>

        </div>
      </div>
    </div>
  );
}
