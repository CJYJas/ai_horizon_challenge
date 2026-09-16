import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { Activity, AlertTriangle, ArrowRight, Target, Shield, Users, Zap, Briefcase } from 'lucide-react';
import { api } from '../api/client';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { ProgressBar } from '../components/ui/ProgressBar';
import { Button } from '../components/ui/Button';

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

  const { top_pain_points, maturity_scores } = data;

  const radarData = [
    { subject: 'Digital Presence', A: maturity_scores.digital_presence, fullMark: 5 },
    { subject: 'Productivity', A: maturity_scores.productivity, fullMark: 5 },
    { subject: 'Customer Mgt', A: maturity_scores.customer_management, fullMark: 5 },
    { subject: 'Data & Security', A: maturity_scores.data_security, fullMark: 5 },
    { subject: 'AI Readiness', A: maturity_scores.ai_readiness, fullMark: 5 },
  ];

  const maturityIcons = {
    digital_presence: <Target className="w-5 h-5 text-blue-500" />,
    productivity: <Zap className="w-5 h-5 text-amber-500" />,
    customer_management: <Users className="w-5 h-5 text-green-500" />,
    data_security: <Shield className="w-5 h-5 text-red-500" />,
    ai_readiness: <Activity className="w-5 h-5 text-purple-500" />
  };

  const formatKey = (key) => key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Your Business Diagnosis</h1>
            <p className="text-gray-500 mt-2">Based on your operational assessment, here are the identified bottlenecks and your digital maturity profile.</p>
          </div>
          <Button onClick={() => navigate(`/simulator/${id}`)}>
            View Impact Simulation <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* Left Column: Pain Points */}
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" /> Key Pain Points
            </h2>
            
            {top_pain_points.map((pt, idx) => (
              <Card key={idx} className="relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
                <div className="mb-4 flex flex-wrap gap-2">
                  <Badge variant="red">Urgency: {pt.urgency}</Badge>
                  <Badge variant="amber">Priority {pt.priority_rank}</Badge>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{pt.problem}</h3>
                
                <div className="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-100">
                  <p className="text-sm font-medium text-gray-700 mb-1">Root Cause</p>
                  <p className="text-gray-600 text-sm">{pt.root_cause}</p>
                </div>
                
                <div className="flex items-center gap-3 bg-red-50 text-red-900 p-4 rounded-lg">
                  <Briefcase className="w-5 h-5 text-red-600" />
                  <div>
                    <p className="text-sm font-semibold">Business Impact</p>
                    <p className="text-sm">{pt.business_impact}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Right Column: Digital Maturity */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary-600" /> Digital Maturity
            </h2>
            
            <Card>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#4B5563', fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 5]} tick={false} axisLine={false} />
                    <Radar name="Maturity" dataKey="A" stroke="#005B9F" fill="#005B9F" fillOpacity={0.3} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              <div className="mt-6 space-y-4">
                {Object.entries(maturity_scores).map(([key, val]) => (
                  <div key={key}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-gray-700 flex items-center gap-2">
                        {maturityIcons[key] || <Target className="w-4 h-4" />}
                        {formatKey(key)}
                      </span>
                      <span className="font-semibold text-primary-700">{val}/5</span>
                    </div>
                    <ProgressBar value={val} max={5} />
                  </div>
                ))}
              </div>
            </Card>
          </div>

        </div>
      </div>
    </div>
  );
}
