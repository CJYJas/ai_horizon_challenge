import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { FileText, Loader2, BrainCircuit, Activity, AlertTriangle, TrendingUp, Package, Building2, Map } from 'lucide-react';
import { api } from '../api/client';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { MaturityChart } from '../components/MaturityChart';
import { RecommendationCard } from '../components/RecommendationCard';

const MATURITY_LABELS = {
  digital_presence: 'Digital Presence',
  productivity: 'Productivity',
  customer_management: 'Customer Management',
  data_security: 'Data & Security',
  ai_readiness: 'AI Readiness',
};

export function Report() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadReport() {
      try {
        let res;
        try {
          res = await api.getReport(id);
        } catch (err) {
          if (err.response?.status === 400) {
            await api.getDiagnosis(id);
            res = await api.getReport(id);
          } else {
            throw err;
          }
        }
        setData(res);
        setError(null);
      } catch (err) {
        console.error(err);
        setError("We couldn't generate the report yet. Complete the assessment and diagnosis first.");
      } finally {
        setLoading(false);
      }
    }
    loadReport();
  }, [id]);

  const formatCurrency = (val) => new Intl.NumberFormat('en-MY', { style: 'currency', currency: 'MYR' }).format(val);
  const returnStep = searchParams.get('return');
  const fromSales = searchParams.get('from') === 'sales';
  const returnPath = fromSales ? '/leads' : returnStep === 'simulator' ? `/simulator/${id}` : returnStep === 'roadmap' ? `/roadmap/${id}` : '/';

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-6 max-w-md text-center">
          <div className="relative">
            <div className="absolute inset-0 bg-primary-100 rounded-full animate-ping opacity-75"></div>
            <div className="relative bg-white p-4 rounded-full shadow-lg">
              <BrainCircuit className="w-8 h-8 text-primary-600 animate-pulse" />
            </div>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">AI Strategist is synthesizing your report...</h2>
            <p className="text-gray-500 mt-2">Analyzing business impact, mapping solutions, and finalizing the transformation roadmap.</p>
          </div>
          <Loader2 className="w-6 h-6 text-primary-600 animate-spin mt-4" />
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4 text-center gap-4">
        <p className="text-red-600 max-w-md">{error || 'Failed to generate report.'}</p>
        <Button onClick={() => navigate(`/diagnosis/${id}`)}>Return to Diagnosis</Button>
      </div>
    );
  }

  const { report, company_profile, diagnosis_data, impact_simulation } = data;
  const { top_pain_points, maturity_scores, recommendations, government_support } = diagnosis_data;

  const executiveSummary =
    report.sme_report_summary?.trim() ||
    (top_pain_points[0]
      ? `Your assessment highlights ${top_pain_points[0].problem}. Recommended next steps focus on ${recommendations[0]?.product_id?.toUpperCase() || 'targeted digital solutions'}.`
      : 'Your transformation report is ready. Review maturity scores and recommendations below.');

  const painExplanations =
    report.pain_point_explanations?.length > 0
      ? report.pain_point_explanations
      : top_pain_points.map((pt) => ({
        problem: pt.problem,
        root_cause_explanation: pt.root_cause,
        why_it_matters: pt.business_impact,
      }));

  const roadmapEntries =
    report.roadmap_narrative && Object.values(report.roadmap_narrative).some((v) => v?.trim())
      ? Object.entries(report.roadmap_narrative)
      : recommendations.map((rec, idx) => [
        `phase_${idx + 1}`,
        `${rec.product_id.toUpperCase()}: ${rec.expected_outcome}`,
      ]);
  const rationales = report.product_rationales || [];

  let biggestGap = 'Digital Presence';
  let minScore = Infinity;
  if (maturity_scores) {
    for (const [key, score] of Object.entries(maturity_scores)) {
      if (score < minScore) {
        minScore = score;
        biggestGap = MATURITY_LABELS[key] || key;
      }
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="sticky top-0 z-20 bg-white/95 backdrop-blur border-b border-gray-200">
        <div className="max-w-screen-2xl mx-auto px-6 lg:px-10 py-4 flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate(returnPath)}>
            {fromSales ? 'Back to dashboard' : 'Back to your journey'}
          </Button>
          <p className="text-sm text-gray-500 hidden sm:block">Digital Transformation Report</p>
        </div>
      </div>

      <div className="max-w-screen-2xl mx-auto px-6 lg:px-10 py-8 lg:py-10 space-y-8">
        <header className="bg-primary-900 text-white rounded-3xl px-8 lg:px-12 py-10 lg:py-12 flex flex-col lg:flex-row justify-between lg:items-center gap-8 shadow-md">
          <div className="max-w-2xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm">
                <span className="text-primary-900 font-black text-xl">E</span>
              </div>
              <span className="text-2xl font-semibold tracking-tight text-white/90">Exabytes</span>
            </div>
            <h1 className="text-4xl lg:text-5xl font-bold mb-4 leading-tight">Digital Transformation Strategy</h1>
            <p className="text-primary-200 text-lg">Executive summary, maturity diagnosis, and implementation roadmap</p>
          </div>
          <div className="flex flex-col sm:flex-row lg:flex-col gap-3 min-w-[280px]">
            <div className="bg-primary-800/40 backdrop-blur px-5 py-3.5 rounded-xl border border-primary-700/50 flex justify-between items-center gap-4">
              <span className="text-primary-300 text-sm font-medium">Industry</span>
              <span className="font-semibold text-white text-right">{company_profile.industry}</span>
            </div>
            <div className="bg-primary-800/40 backdrop-blur px-5 py-3.5 rounded-xl border border-primary-700/50 flex justify-between items-center gap-4">
              <span className="text-primary-300 text-sm font-medium">Employees</span>
              <span className="font-semibold text-white text-right">{company_profile.employee_count}</span>
            </div>
            <div className="bg-primary-800/40 backdrop-blur px-5 py-3.5 rounded-xl border border-primary-700/50 flex flex-col gap-2">
              <span className="text-primary-300 text-sm font-medium">Current Tools</span>
              <span className="font-semibold text-white capitalize leading-snug">{company_profile.current_digital_tools.join(', ')}</span>
            </div>
          </div>
        </header>

        <div className="grid xl:grid-cols-12 gap-8">
          <section className="xl:col-span-7 bg-white rounded-2xl border border-gray-200 p-8 lg:p-10">
            <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-3 mb-6 flex items-center gap-2">
              <FileText className="w-6 h-6 text-primary-600" /> Executive Summary
            </h2>
            <p className="text-gray-700 leading-relaxed text-lg">{executiveSummary}</p>
          </section>

          <section className="xl:col-span-5 bg-white rounded-2xl border border-gray-200 p-8 lg:p-10">
            <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-3 mb-6 flex items-center gap-2">
              <Activity className="w-6 h-6 text-primary-600" /> Digital Maturity
            </h2>
            <div className="bg-amber-50 rounded-xl border border-amber-100 p-5 mb-6">
              <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Diagnostic Insight</p>
              <p className="text-gray-500 mb-2">Your biggest digital gap is</p>
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                <span className="text-xl font-bold text-amber-600">{biggestGap}</span>
              </div>
              <p className="text-gray-600 text-sm">
                {diagnosis_data.maturity_gap_explanation || 'Addressing this area will yield the highest immediate ROI for your transformation journey.'}
              </p>
            </div>
            <MaturityChart scores={maturity_scores} />
          </section>
        </div>

        <section className="bg-white rounded-2xl border border-gray-200 p-8 lg:p-10">
          <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-3 mb-8 flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-primary-600" /> Identified Operational Bottlenecks
          </h2>
          <div className="flex flex-col gap-6">
            {painExplanations.map((exp, idx) => (
              <div key={idx} className="bg-white rounded-2xl p-6 md:p-8 border border-gray-200 flex flex-col lg:flex-row gap-6 items-start shadow-sm hover:shadow-md transition-all">
                <div className="lg:w-1/3 shrink-0">
                  <Badge variant="red" className="mb-4 inline-flex">High Priority</Badge>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{exp.problem}</h3>
                </div>
                <div className="lg:w-2/3 grid sm:grid-cols-2 gap-4 lg:gap-6 w-full">
                  <div className="bg-gray-50/80 p-5 md:p-6 rounded-xl border border-gray-100">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Root Cause</p>
                    <p className="text-gray-800 text-sm leading-relaxed">{exp.root_cause_explanation}</p>
                  </div>
                  <div className="bg-red-50/60 p-5 md:p-6 rounded-xl border border-red-100/60">
                    <p className="text-xs font-semibold text-red-500 uppercase tracking-widest mb-3">Business Impact</p>
                    <p className="text-red-900 font-medium text-sm leading-relaxed">{exp.why_it_matters}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {impact_simulation && (
          <section className="bg-white rounded-2xl border border-gray-200 p-8 lg:p-10">
            <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-3 mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-primary-600" /> ROI & Impact Simulation
            </h2>
            <p className="text-sm text-gray-500 italic mb-6">* Estimates based on user assumptions. Not guaranteed savings.</p>
            <div className="flex flex-col md:flex-row rounded-2xl overflow-hidden border border-gray-200 shadow-sm">
              <div className="flex-1 bg-gradient-to-br from-red-50 to-white p-8 border-b md:border-b-0 md:border-r border-gray-200">
                <p className="text-xs text-red-800 font-bold mb-3 uppercase tracking-widest">Estimated Annual Opportunity Cost</p>
                <p className="text-4xl lg:text-5xl font-bold text-red-600">{formatCurrency(impact_simulation.annual_opportunity_cost)}</p>
              </div>
              <div className="flex-1 bg-gradient-to-br from-green-50 to-white p-8">
                <p className="text-xs text-green-800 font-bold mb-3 uppercase tracking-widest">Target Recovered Value / Year</p>
                <p className="text-4xl lg:text-5xl font-bold text-green-600">{formatCurrency(impact_simulation.recovered_value_per_year)}</p>
              </div>
            </div>
          </section>
        )}

        <section className="bg-white rounded-2xl border border-gray-200 p-8 lg:p-10">
          <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-3 mb-8 flex items-center gap-2">
            <Map className="w-6 h-6 text-primary-600" /> Strategic Roadmap
          </h2>
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
            {roadmapEntries.map(([phase, desc], idx) => (
              <div key={idx} className="rounded-2xl border border-primary-100 bg-primary-50/40 p-6">
                <div className="w-10 h-10 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold mb-4">
                  {idx + 1}
                </div>
                <h3 className="text-lg font-bold text-gray-900 capitalize mb-2">{phase.replace('_', ' ')}</h3>
                <p className="text-gray-700 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-white rounded-2xl border border-gray-200 p-8 lg:p-10">
          <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-3 mb-8 flex items-center gap-2">
            <Package className="w-6 h-6 text-primary-600" /> Recommended Exabytes Solutions
          </h2>
          <div className="flex flex-col gap-8">
            {recommendations.map((rec, idx) => (
              <RecommendationCard
                key={idx}
                recommendation={rec}
                rationale={rationales.find((item) => item.product_id === rec.product_id)}
              />
            ))}
          </div>
        </section>

        {government_support && government_support.length > 0 && (
          <section className="bg-white rounded-2xl border border-gray-200 p-8 lg:p-10">
            <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-3 mb-8 flex items-center gap-2">
              <Building2 className="w-6 h-6 text-primary-600" /> Government Support Opportunities
            </h2>
            <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
              {government_support.map((gov, idx) => (
                <div key={idx} className="bg-amber-50 border border-amber-200 rounded-2xl p-6 flex flex-col">
                  <div className="flex justify-between items-start gap-3 mb-3">
                    <h3 className="font-bold text-gray-900 uppercase">{gov.support_id.replace('_', ' ')}</h3>
                    <Badge variant="amber">Potentially eligible</Badge>
                  </div>
                  <p className="text-sm text-gray-700 mb-3">Matching Transformation: <span className="capitalize font-medium">{gov.linked_transformation}</span></p>
                  <p className="text-xs text-amber-800 bg-amber-100/50 p-3 rounded-xl mb-4">
                    <strong>Important:</strong> Potentially eligible — eligibility must be confirmed directly with the official agency. This is an automated preliminary match.
                  </p>
                  {(gov.matched_conditions?.length > 0 || gov.pending_conditions?.length > 0) && (
                    <div className="mb-4">
                      <span className="font-medium text-gray-700 block mb-1 text-sm">Conditions summary:</span>
                      <ul className="space-y-1">
                        {gov.matched_conditions?.map((c, i) => (
                          <li key={`m-${i}`} className="text-xs text-green-700 flex items-start gap-1">
                            <span className="font-bold mt-0.5">✓</span> <span>{c}</span>
                          </li>
                        ))}
                        {gov.pending_conditions?.map((c, i) => (
                          <li key={`p-${i}`} className="text-xs text-amber-700 flex items-start gap-1">
                            <span className="font-bold mt-0.5">?</span> <span>(To be confirmed) {c}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {gov.source_url && (
                    <div className="mt-auto">
                      <a
                        href={gov.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 transition-colors"
                      >
                        View Official Programme
                      </a>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="bg-primary-50 p-10 rounded-3xl text-center border border-primary-100">
          <h2 className="text-2xl font-bold text-primary-900 mb-3">Thank you for your time!</h2>
          <p className="text-lg text-primary-800 max-w-3xl mx-auto">Our team will contact you shortly to discuss your personalized digital transformation journey.</p>
        </section>
      </div>
    </div>
  );
}
