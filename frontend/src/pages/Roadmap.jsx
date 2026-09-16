import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Map, ArrowRight, CheckCircle2, Landmark, Package, Building2 } from 'lucide-react';
import { api } from '../api/client';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

export function Roadmap() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.getDiagnosis(id);
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  if (!data) return null;

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-12">
        
        <div className="flex justify-between items-end border-b border-gray-200 pb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Map className="w-8 h-8 text-primary-600" />
              Transformation Roadmap
            </h1>
            <p className="text-gray-500 mt-2">Your step-by-step plan to resolve operational bottlenecks.</p>
          </div>
          <Button onClick={() => navigate(`/report/${id}`)}>
            Generate Final Report <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </div>

        {/* Roadmap Steps */}
        <div className="space-y-8">
          <h2 className="text-2xl font-semibold text-gray-900">Recommended Solutions</h2>
          
          <div className="relative border-l-2 border-primary-200 pl-8 ml-4 space-y-12">
            {data.recommendations.map((rec, idx) => {
              // Find the related pain point to show the problem
              const painPoint = data.top_pain_points.find(p => p.problem === rec.linked_pain_point);
              
              return (
                <div key={idx} className="relative">
                  <div className="absolute -left-[41px] top-1 w-8 h-8 bg-primary-100 rounded-full border-4 border-white flex items-center justify-center text-primary-700 font-bold">
                    {idx + 1}
                  </div>
                  
                  <Card className="shadow-sm hover:shadow-md transition-shadow border-primary-100">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <Badge variant="blue" className="mb-2">Priority {painPoint?.priority_rank || idx + 1}</Badge>
                        <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                          <Package className="w-5 h-5 text-primary-600" />
                          {rec.product_id.toUpperCase()}
                        </h3>
                      </div>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <p className="text-sm font-medium text-gray-500 mb-1">Target Problem</p>
                        <p className="text-gray-900">{rec.linked_pain_point}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500 mb-1">Expected Outcome</p>
                        <div className="flex items-start gap-2">
                          <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <p className="text-gray-900">{rec.expected_outcome}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-gray-100 bg-gray-50 -mx-6 -mb-6 p-6 rounded-b-xl">
                      <p className="text-sm text-gray-600 italic">"{rec.reason}"</p>
                    </div>
                  </Card>
                </div>
              );
            })}
          </div>
        </div>

        {/* Government Support */}
        {data.government_support && data.government_support.length > 0 && (
          <div className="pt-8 border-t border-gray-200">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
              <Landmark className="w-6 h-6 text-primary-600" />
              Government Support
            </h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              {data.government_support.map((gov, idx) => (
                <Card key={idx} className="border-green-100 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-green-500"></div>
                  
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="font-bold text-gray-900 text-lg flex items-center gap-2">
                      <Building2 className="w-5 h-5 text-green-600" />
                      {gov.support_id.toUpperCase().replace(/_/g, ' ')}
                    </h3>
                    <Badge variant="amber" className="whitespace-nowrap">Potentially eligible</Badge>
                  </div>
                  
                  <div className="space-y-3 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Matching Transformation:</span>
                      <span className="ml-2 text-gray-600 capitalize">{gov.linked_transformation}</span>
                    </div>
                    <div className="bg-amber-50 p-3 rounded-lg border border-amber-100 text-amber-800 text-xs">
                      <strong>Important:</strong> Eligibility must be confirmed directly with the official agency. This is an automated preliminary match.
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
