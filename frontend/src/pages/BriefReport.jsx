import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, Loader2, ArrowRight, Download, CheckCircle, BrainCircuit, Activity, AlertTriangle, TrendingUp, DollarSign, Package, Building2, Map } from 'lucide-react';
import { api } from '../api/client';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { ProgressBar } from '../components/ui/ProgressBar';

export function BriefReport() {
  const { id } = useParams();
  const navigate = useNavigate();
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

  const handlePrint = () => {
    window.print();
  };

  const formatCurrency = (val) => new Intl.NumberFormat('en-MY', { style: 'currency', currency: 'MYR' }).format(val);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 no-print">
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
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 no-print px-4 text-center gap-4">
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

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Print Controls */}
        <div className="flex justify-between items-center mb-8 no-print">
          <Button variant="ghost" onClick={() => navigate('/')}>
            Back Home
          </Button>
          <Button variant="primary" onClick={handlePrint}>
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
        </div>

        {/* Report Document */}
        <div className="bg-white shadow-xl rounded-2xl overflow-hidden border border-gray-200">
          
          {/* Header */}
          <div className="bg-primary-900 px-8 py-12 text-white page-break-inside-avoid">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-8 h-8 bg-white rounded flex items-center justify-center">
                <span className="text-primary-900 font-bold text-lg">E</span>
              </div>
              <span className="text-xl font-semibold tracking-tight">Exabytes</span>
            </div>
            <h1 className="text-4xl font-bold mb-4">Digital Transformation Strategy</h1>
            <p className="text-primary-200 text-lg mb-8">Executive Summary & Implementation Roadmap</p>
            
            {/* 2. Company Overview */}
            <div className="bg-primary-800/50 p-6 rounded-xl border border-primary-700/50">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-primary-300 mb-4">Company Overview</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-primary-300 text-sm">Industry</p>
                  <p className="font-semibold">{company_profile.industry}</p>
                </div>
                <div>
                  <p className="text-primary-300 text-sm">Employees</p>
                  <p className="font-semibold">{company_profile.employee_count}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-primary-300 text-sm">Current Tools</p>
                  <p className="font-semibold capitalize">{company_profile.current_digital_tools.join(', ')}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="p-8 space-y-12">
            
            {/* 3. Executive Summary */}
            <section className="page-break-inside-avoid">
              <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-2 mb-6 flex items-center gap-2">
                <FileText className="w-6 h-6 text-primary-600" /> Executive Summary
              </h2>
              <p className="text-gray-700 leading-relaxed text-lg">
                {executiveSummary}
              </p>
            </section>

            {/* 4. Digital Maturity */}
            <section className="page-break-inside-avoid">
              <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-2 mb-6 flex items-center gap-2">
                <Activity className="w-6 h-6 text-primary-600" /> Digital Maturity
              </h2>
              <div className="grid sm:grid-cols-2 gap-x-12 gap-y-6">
                {Object.entries(maturity_scores).map(([key, val]) => (
                  <div key={key}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-gray-700 capitalize">{key.replace('_', ' ')}</span>
                      <span className="font-semibold text-primary-700">{val}/5</span>
                    </div>
                    <ProgressBar value={val} max={5} />
                  </div>
                ))}
              </div>
            </section>

            {/* 5, 6, 7. Key Pain Points, Root Causes, Business Impact */}
            <section className="page-break-before">
              <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-2 mb-6 flex items-center gap-2">
                <AlertTriangle className="w-6 h-6 text-primary-600" /> Identified Operational Bottlenecks
              </h2>
              <div className="grid gap-6">
                {painExplanations.map((exp, idx) => (
                  <div key={idx} className="bg-gray-50 rounded-xl p-6 border border-gray-100 page-break-inside-avoid">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-xl font-bold text-gray-900">{exp.problem}</h3>
                      <Badge variant="red">High Priority</Badge>
                    </div>
                    <p className="text-gray-700 mt-2">{exp.why_it_matters}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* 9 & 12. Transformation Roadmap & Priority Areas */}
            <section className="page-break-before">
              <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-2 mb-6 flex items-center gap-2">
                <Map className="w-6 h-6 text-primary-600" /> Strategic Roadmap
              </h2>
              <div className="space-y-6">
                {roadmapEntries.map(([phase, desc], idx) => (
                  <div key={idx} className="flex gap-4 page-break-inside-avoid">
                    <div className="flex flex-col items-center">
                      <div className="w-10 h-10 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold border-2 border-white shadow-sm z-10">
                        {idx + 1}
                      </div>
                      {idx !== roadmapEntries.length - 1 && (
                        <div className="w-0.5 h-full bg-primary-100 mt-2"></div>
                      )}
                    </div>
                    <div className="pb-6 pt-2">
                      <h3 className="text-lg font-bold text-gray-900 capitalize mb-2">{phase.replace('_', ' ')}</h3>
                      <p className="text-gray-700 leading-relaxed">{desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* 10. Recommended Solutions */}
            <section className="page-break-inside-avoid">
              <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-2 mb-6 flex items-center gap-2">
                <Package className="w-6 h-6 text-primary-600" /> Recommended Exabytes Solutions
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                {recommendations.map((rec, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-xl p-6 bg-white">
                    <h3 className="text-lg font-bold text-gray-900 mb-2 uppercase">{rec.product_id}</h3>
                    <p className="text-sm font-medium text-primary-600 mb-3">{rec.expected_outcome}</p>
                    <p className="text-sm text-gray-600 italic">"{rec.reason}"</p>
                  </div>
                ))}
              </div>
            </section>

            {/* 11. Government Support */}
            {government_support && government_support.length > 0 && (
              <section className="page-break-inside-avoid">
                <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-2 mb-6 flex items-center gap-2">
                  <Building2 className="w-6 h-6 text-primary-600" /> Government Support Opportunities
                </h2>
                <div className="grid gap-4">
                  {government_support.map((gov, idx) => (
                    <div key={idx} className="bg-amber-50 border border-amber-200 rounded-xl p-6">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-bold text-gray-900 uppercase">{gov.support_id.replace('_', ' ')}</h3>
                        <Badge variant="amber">Potentially eligible</Badge>
                      </div>
                      <p className="text-sm text-gray-700 mb-3">Matching Transformation: <span className="capitalize font-medium">{gov.linked_transformation}</span></p>
                      <p className="text-xs text-amber-800 bg-amber-100/50 p-3 rounded">
                        <strong>Important:</strong> Potentially eligible — eligibility must be confirmed directly with the official agency. This is an automated preliminary match.
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            )}

          </div>
        </div>

      </div>
    </div>
  );
}
