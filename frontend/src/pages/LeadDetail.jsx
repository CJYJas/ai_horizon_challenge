import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { ArrowLeft, BrainCircuit, Target, Flame, TrendingUp, AlertTriangle, Lightbulb, Link as LinkIcon, Building2 } from 'lucide-react';
import { api } from '../api/client';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export function LeadDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadLead() {
      try {
        const res = await api.getLeadDetail(id);
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadLead();
  }, [id]);

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  if (!data) return <div className="text-center py-20 text-red-500">Failed to load lead details.</div>;

  const { lead_label, company_profile, diagnosis_data, impact_simulation, lead_score, lead_score_reasons, sales_brief } = data;
  const { top_pain_points, maturity_scores, recommendations } = diagnosis_data;
  
  const mainProblem = top_pain_points[0] || {};
  const mainSolution = recommendations[0] || {};

  const radarData = Object.entries(maturity_scores).map(([key, val]) => ({
    subject: key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
    A: val,
    fullMark: 5
  }));

  const formatCurrency = (val) => new Intl.NumberFormat('en-MY', { style: 'currency', currency: 'MYR' }).format(val);

  return (
    <div className="min-h-screen bg-gray-50 pb-12">
      
      {/* Top Navigation */}
      <div className="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Button variant="ghost" className="pl-0 text-gray-500" onClick={() => navigate('/leads')}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Pipeline
          </Button>
          <div className="flex items-center gap-4">
            <Button variant="secondary" onClick={() => navigate(`/report/${id}`)}>
              View Detailed Report
            </Button>
            <div className="w-px h-6 bg-gray-200"></div>
            <span className="text-sm font-medium text-gray-500">Lead Score</span>
            <div className={`px-4 py-1.5 rounded-full font-bold flex items-center gap-2 ${lead_score >= 80 ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-600'}`}>
              {Math.round(lead_score)} / 100
              {lead_score >= 80 && <Flame className="w-4 h-4" />}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Row 1: Company Profile & Causal Viz */}
        <div className="grid lg:grid-cols-3 gap-8">
          
          <Card className="lg:col-span-1 border-t-4 border-t-primary-600">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center text-primary-600">
                <Building2 className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">{lead_label || company_profile.company_name}</h2>
                <p className="text-gray-500 text-sm">{company_profile.industry} • {company_profile.employee_count} employees</p>
                {(company_profile.email || company_profile.phone) && (
                  <p className="text-gray-400 text-xs mt-1">
                    {company_profile.email} {company_profile.email && company_profile.phone && '|'} {company_profile.phone}
                  </p>
                )}
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Current Tech Stack</p>
                <div className="flex flex-wrap gap-2">
                  {company_profile.current_digital_tools.map((tool, idx) => (
                    <Badge key={idx} variant="gray" className="capitalize">{tool}</Badge>
                  ))}
                </div>
              </div>
              <div className="pt-4 border-t border-gray-100">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Maturity Radar</p>
                <div className="h-48 w-full -ml-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="60%" data={radarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#6B7280', fontSize: 9 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 5]} tick={false} axisLine={false} />
                      <Radar name="Maturity" dataKey="A" stroke="#005B9F" fill="#005B9F" fillOpacity={0.3} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </Card>

          <Card className="lg:col-span-2 bg-gradient-to-br from-white to-primary-50/30">
            <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Target className="w-5 h-5 text-primary-600" /> Causal Opportunity Chain
            </h2>
            
            <div className="relative flex flex-col md:flex-row justify-between items-center h-full pb-8">
              {/* Connector Line */}
              <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-gray-200 -z-10 -translate-y-1/2"></div>
              
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm w-full md:w-1/4 text-center relative z-0 mb-4 md:mb-0">
                <p className="text-xs text-gray-400 font-semibold uppercase mb-2">Root Cause</p>
                <p className="text-sm font-medium text-gray-900">{mainProblem.root_cause}</p>
              </div>
              
              <LinkIcon className="w-5 h-5 text-gray-300 md:hidden" />
              
              <div className="bg-white p-4 rounded-lg border border-red-200 shadow-sm w-full md:w-1/4 text-center relative z-0 mb-4 md:mb-0">
                <p className="text-xs text-red-400 font-semibold uppercase mb-2">Business Impact</p>
                <p className="text-sm font-medium text-red-700">{mainProblem.business_impact}</p>
              </div>

              <LinkIcon className="w-5 h-5 text-gray-300 md:hidden" />

              <div className="bg-primary-600 p-4 rounded-lg shadow-md w-full md:w-1/4 text-center relative z-0 text-white">
                <p className="text-xs text-primary-200 font-semibold uppercase mb-2">Solution</p>
                <p className="text-sm font-bold tracking-wide uppercase">{mainSolution.product_id}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Row 2: Sales Brief */}
        <div className="grid lg:grid-cols-3 gap-8">
          
          <div className="lg:col-span-2 space-y-8">
            <Card>
              <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100">
                <BrainCircuit className="w-6 h-6 text-primary-600" />
                <h2 className="text-xl font-bold text-gray-900">AI Sales Brief</h2>
                <Badge variant="blue" className="ml-auto">Strategist Output</Badge>
              </div>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-2">SME Situation</h3>
                  <p className="text-gray-700 leading-relaxed">
                    {sales_brief.sme_situation_summary || sales_brief.one_line_hook || 'Situation summary will appear after diagnosis is complete.'}
                  </p>
                </div>
                
                <div className="bg-blue-50 p-6 rounded-xl border border-blue-100">
                  <h3 className="text-sm font-bold text-blue-900 uppercase tracking-wider mb-2 flex items-center gap-2">
                    <Lightbulb className="w-4 h-4" /> Suggested Conversation Angle
                  </h3>
                  <p className="text-blue-800 leading-relaxed font-medium">
                    "{sales_brief.suggested_conversation_angle || sales_brief.recommended_approach || 'Focus on the top operational pain point and a quick-win product outcome.'}"
                  </p>
                </div>
              </div>
            </Card>

            {impact_simulation && (
              <Card>
                <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" /> Estimated Financial Impact
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-red-50 rounded-lg border border-red-100">
                    <p className="text-xs font-semibold text-red-600 uppercase mb-1">Opportunity Cost</p>
                    <p className="text-2xl font-bold text-red-900">{formatCurrency(impact_simulation.annual_opportunity_cost)}</p>
                    <p className="text-xs text-red-700 mt-1">per year</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg border border-green-100">
                    <p className="text-xs font-semibold text-green-600 uppercase mb-1">Target ROI / Savings</p>
                    <p className="text-2xl font-bold text-green-900">{formatCurrency(impact_simulation.recovered_value_per_year)}</p>
                    <p className="text-xs text-green-700 mt-1">per year estimated</p>
                  </div>
                </div>
              </Card>
            )}
          </div>

          <div className="space-y-8">
            <Card className="bg-gray-900 text-white">
              <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" /> Why This Lead Matters
              </h2>
              <ul className="space-y-4">
                {(lead_score_reasons.length ? lead_score_reasons : (sales_brief.why_this_lead_is_hot || [])).map((reason, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-sm">
                    <div className="w-6 h-6 rounded-full bg-gray-800 flex items-center justify-center flex-shrink-0 mt-0.5 text-amber-500 font-bold text-xs">
                      {idx + 1}
                    </div>
                    <span className="text-gray-300">{reason}</span>
                  </li>
                ))}
              </ul>
            </Card>

            <Card>
              <h2 className="text-lg font-bold text-gray-900 mb-6">Recommended Approach</h2>
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Primary Solution</p>
                  <Badge variant="blue" className="uppercase text-sm px-3 py-1">{mainSolution.product_id}</Badge>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Expected Outcome</p>
                  <p className="text-gray-900 text-sm font-medium">{mainSolution.expected_outcome}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">AI Reasoning</p>
                  <p className="text-gray-600 text-sm italic">"{mainSolution.reason}"</p>
                </div>
              </div>
            </Card>
          </div>

        </div>

      </div>
    </div>
  );
}
