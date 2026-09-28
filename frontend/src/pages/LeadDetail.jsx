import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, BrainCircuit, Target, Flame, TrendingUp, AlertTriangle, Lightbulb, Building2 } from 'lucide-react';
import { api } from '../api/client';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { MaturityChart } from '../components/MaturityChart';
import { RecommendationCard } from '../components/RecommendationCard';

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

  const { lead_label, company_profile, diagnosis_data, impact_simulation, lead_score, lead_score_reasons, sales_brief, report } = data;
  const { top_pain_points, maturity_scores, recommendations } = diagnosis_data;

  const mainProblem = top_pain_points[0] || {};
  const mainSolution = recommendations[0] || {};

  const formatCurrency = (val) => new Intl.NumberFormat('en-MY', { style: 'currency', currency: 'MYR' }).format(val);

  return (
    <div className="min-h-screen bg-gray-50 pb-12">

      {/* Top Navigation */}
      <div className="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4 sticky top-0 z-10">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between">
          <Button variant="ghost" className="pl-0 text-gray-500" onClick={() => navigate('/leads')}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Pipeline
          </Button>
          <div className="flex items-center gap-4">
            <Button variant="outline" className="border-gray-200" onClick={() => navigate(`/report/${id}?from=sales`)}>
              View Client Report
            </Button>
            <Button variant="secondary" onClick={() => navigate(`/leads/${id}/sales-report`)}>
              Open Sales Playbook
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

      <div className="max-w-screen-2xl mx-auto px-6 lg:px-10 py-8 lg:py-10 space-y-8">

        {/* Row 1: Company Profile & Causal Viz */}
        <div className="grid lg:grid-cols-3 gap-8">

          <Card className="lg:col-span-1 border-t-4 border-t-primary-600 p-8">
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
                {(() => {
                  const labels = {
                    digital_presence: 'Digital Presence',
                    productivity: 'Productivity',
                    customer_management: 'Customer Management',
                    data_security: 'Data & Security',
                    ai_readiness: 'AI Readiness',
                  };
                  let minScore = Infinity;
                  let biggestGap = 'Digital Presence';
                  if (maturity_scores) {
                    for (const [key, score] of Object.entries(maturity_scores)) {
                      if (score < minScore) {
                        minScore = score;
                        biggestGap = labels[key] || key;
                      }
                    }
                  }
                  return (
                    <div className="mb-6 bg-amber-50/50 p-4 rounded-xl border border-amber-100/50">
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Diagnostic Insight</p>
                      <p className="text-gray-500 text-xs mb-1">Biggest digital gap:</p>
                      <div className="flex items-center gap-1.5 mb-2">
                        <AlertTriangle className="w-4 h-4 text-amber-500" />
                        <span className="text-sm font-bold text-amber-500">{biggestGap}</span>
                      </div>
                      <p className="text-gray-500 text-xs leading-relaxed">
                        {diagnosis_data.maturity_gap_explanation || "Addressing this area will yield the highest immediate ROI for this lead."}
                      </p>
                    </div>
                  );
                })()}

                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 text-center">Digital Maturity Index</p>
                <MaturityChart scores={maturity_scores} compact />
              </div>
            </div>
          </Card>

          <Card className="lg:col-span-2 bg-gradient-to-br from-white to-primary-50/30 overflow-hidden p-8">
            <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Target className="w-5 h-5 text-primary-600" /> Causal Opportunity Chain
            </h2>

            <div className="grid sm:grid-cols-2 xl:grid-cols-6 gap-4">
              <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-center text-center min-h-[120px]">
                <p className="text-[10px] text-gray-400 font-semibold uppercase mb-2">1. Client</p>
                <p className="text-sm font-medium text-gray-900">{lead_label || company_profile.company_name}</p>
              </div>
              <div className="bg-white p-5 rounded-xl border border-red-200 shadow-sm flex flex-col justify-center text-center min-h-[120px]">
                <p className="text-[10px] text-red-400 font-semibold uppercase mb-2">2. Identified Problem</p>
                <p className="text-sm font-medium text-red-700" title={mainProblem.problem}>{mainProblem.problem}</p>
              </div>
              <div className="bg-primary-600 p-5 rounded-xl shadow-md flex flex-col justify-center text-center min-h-[120px] text-white">
                <p className="text-[10px] text-primary-200 font-semibold uppercase mb-2">3. Solution</p>
                <p className="text-sm font-bold tracking-wide uppercase">{mainSolution.product_id}</p>
              </div>
              <div className="bg-white p-5 rounded-xl border border-green-200 shadow-sm flex flex-col justify-center text-center min-h-[120px]">
                <p className="text-[10px] text-green-500 font-semibold uppercase mb-2">4. Gov Support</p>
                <p className="text-sm font-medium text-green-700">
                  {diagnosis_data.government_support?.length ? diagnosis_data.government_support[0].support_id.replace('_', ' ') : 'None Identified'}
                </p>
              </div>
              <div className="bg-white p-5 rounded-xl border border-amber-200 shadow-sm flex flex-col justify-center text-center min-h-[120px]">
                <p className="text-[10px] text-amber-500 font-semibold uppercase mb-2">5. Impact</p>
                <p className="text-sm font-medium text-amber-700">
                  {impact_simulation ? formatCurrency(impact_simulation.recovered_value_per_year) : 'Pending calculation'}
                </p>
              </div>
              <div className="bg-gray-800 p-5 rounded-xl shadow-sm flex flex-col justify-center text-center min-h-[120px]">
                <p className="text-[10px] text-gray-400 font-semibold uppercase mb-2">6. Next Action</p>
                <p className="text-sm font-medium text-white">Review Playbook</p>
              </div>
            </div>
          </Card>
        </div>        {/* Row 2: Sales Brief & Impact */}
        <div className="grid lg:grid-cols-2 gap-8">
          <Card className="p-8">
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

          <div className="space-y-8">
            {impact_simulation && (
              <Card className="p-8">
                <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" /> Estimated Financial Impact
                </h2>
                <div className="flex flex-col rounded-2xl overflow-hidden border border-gray-200 shadow-sm">
                  <div className="bg-gradient-to-br from-red-50 to-white p-6 border-b border-gray-200">
                    <p className="text-xs font-semibold text-red-600 uppercase tracking-widest mb-2">Opportunity Cost</p>
                    <p className="text-3xl font-bold text-red-900">{formatCurrency(impact_simulation.annual_opportunity_cost)}</p>
                    <p className="text-xs text-red-700 mt-1">per year</p>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-white p-6">
                    <p className="text-xs font-semibold text-green-600 uppercase tracking-widest mb-2">Target ROI / Savings</p>
                    <p className="text-3xl font-bold text-green-900">{formatCurrency(impact_simulation.recovered_value_per_year)}</p>
                    <p className="text-xs text-green-700 mt-1">per year estimated</p>
                  </div>
                </div>
              </Card>
            )}

            <Card className="bg-gray-900 text-white p-8">
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
          </div>
        </div>

        {/* Full-width Recommendation Card */}
        <div className="bg-transparent mt-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <BrainCircuit className="w-6 h-6 text-primary-600" /> Recommended Approach
          </h2>
          <RecommendationCard
            recommendation={mainSolution}
            rationale={report?.product_rationales?.find((r) => r.product_id === mainSolution.product_id)}
          />
        </div>

        {/* Row 3: Government Support */}
        {diagnosis_data.government_support && diagnosis_data.government_support.length > 0 && (
          <div className="mt-8">
            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <Building2 className="w-6 h-6 text-primary-600" /> Potential Government Support
              </h2>
              <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
                {diagnosis_data.government_support.map((gov, idx) => (
                  <div key={idx} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold text-gray-900 text-lg uppercase">{gov.programme || gov.support_id.replace('_', ' ')}</h3>
                        {gov.agency && <p className="text-sm text-gray-500">{gov.agency}</p>}
                      </div>
                      <Badge variant="amber" className="whitespace-nowrap">Potentially eligible</Badge>
                    </div>

                    <div className="space-y-3 mt-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700 block">Why it is relevant:</span>
                        <span className="text-gray-600 capitalize">Matches transformation need: {gov.linked_transformation}</span>
                      </div>
                      {gov.coverage && (
                        <div>
                          <span className="font-medium text-gray-700 block">Coverage / Amount:</span>
                          <span className="text-gray-600">{gov.coverage} {gov.maximum_amount ? `(Up to ${gov.maximum_amount})` : ''}</span>
                        </div>
                      )}
                      {(gov.matched_conditions?.length > 0 || gov.pending_conditions?.length > 0) && (
                        <div>
                          <span className="font-medium text-gray-700 block mb-1">Conditions summary:</span>
                          <ul className="space-y-1">
                            {gov.matched_conditions?.map((c, i) => (
                              <li key={`m-${i}`} className="text-xs text-green-700 flex items-start gap-1">
                                <span className="font-bold">✓</span> <span className="line-clamp-2" title={c}>{c}</span>
                              </li>
                            ))}
                            {gov.pending_conditions?.map((c, i) => (
                              <li key={`p-${i}`} className="text-xs text-amber-700 flex items-start gap-1">
                                <span className="font-bold">?</span> <span className="line-clamp-2" title={c}>(To be confirmed) {c}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {gov.status && (
                        <div>
                          <span className="font-medium text-gray-700 block">Status:</span>
                          <span className="text-gray-600 capitalize">{gov.status}</span>
                        </div>
                      )}
                    </div>

                    {gov.source_url && (
                      <div className="mt-5 pt-4 border-t border-gray-100">
                        <a
                          href={gov.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary-700 bg-primary-50 hover:bg-primary-100 transition-colors w-full"
                        >
                          View Official Programme
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

      </div>
    </div>
  );
}
