import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, BrainCircuit, CheckCircle2, FileSearch, Lightbulb, MessageCircle, ShieldQuestion, Target } from 'lucide-react';
import { api } from '../api/client';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

const List = ({ items, icon: Icon = CheckCircle2 }) => (
  <ul className="space-y-4">
    {(items || []).map((item, index) => (
      <li key={index} className="flex gap-3 text-sm text-gray-700 leading-relaxed">
        <Icon className="w-4 h-4 mt-0.5 shrink-0 text-primary-600" />
        {item}
      </li>
    ))}
  </ul>
);

export function SalesReport() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getSalesReport(id).then(setData).catch(() => setError('This sales playbook is not ready yet.')).finally(() => {});
  }, [id]);

  if (error) return <div className="min-h-screen flex items-center justify-center text-red-600">{error}</div>;
  if (!data) return <div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" /></div>;

  const { company_profile: profile, diagnosis_data: diagnosis, report } = data;
  const playbook = report.sales_playbook || {};

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="sticky top-0 z-20 bg-white/95 backdrop-blur border-b border-gray-200">
        <div className="max-w-screen-2xl mx-auto px-6 lg:px-10 py-4 flex justify-between items-center">
          <Button variant="ghost" onClick={() => navigate(`/leads/${id}`)}>
            <ArrowLeft className="w-4 h-4 mr-2" />Back to lead
          </Button>
          <Badge variant="blue">Sales-only playbook</Badge>
        </div>
      </div>

      <main className="max-w-screen-2xl mx-auto px-6 lg:px-10 py-8 lg:py-10 space-y-8">
        <header className="bg-primary-900 text-white rounded-3xl px-8 lg:px-12 py-10 lg:py-12 flex flex-col xl:flex-row justify-between xl:items-start gap-8 shadow-md">
          <div className="max-w-3xl">
            <p className="text-primary-200 text-sm font-bold uppercase tracking-widest mb-3">Consultative sales playbook</p>
            <h1 className="text-4xl lg:text-5xl font-bold mb-6 leading-tight">{profile.company_name || data.lead_label}</h1>
            <p className="text-lg leading-relaxed text-primary-100">{playbook.situation_summary || report.sales_brief?.sme_situation_summary}</p>
          </div>
          <div className="flex flex-col sm:flex-row xl:flex-col gap-3 min-w-[280px]">
            <div className="bg-primary-800/40 backdrop-blur px-5 py-3.5 rounded-xl border border-primary-700/50 flex justify-between items-center gap-4">
              <span className="text-primary-300 text-sm font-medium">Industry</span>
              <span className="font-semibold text-white text-right">{profile.industry}</span>
            </div>
            <div className="bg-primary-800/40 backdrop-blur px-5 py-3.5 rounded-xl border border-primary-700/50 flex justify-between items-center gap-4">
              <span className="text-primary-300 text-sm font-medium">Employees</span>
              <span className="font-semibold text-white text-right">{profile.employee_count}</span>
            </div>
            <div className="bg-primary-800/40 backdrop-blur px-5 py-3.5 rounded-xl border border-primary-700/50 flex flex-col gap-1">
              <span className="text-primary-300 text-sm font-medium">Contact</span>
              <span className="font-semibold text-white text-sm break-all">{profile.email || '—'}</span>
              <span className="font-semibold text-white text-sm">{profile.phone || '—'}</span>
            </div>
          </div>
        </header>

        <div className="flex flex-col gap-8">
          <Card className="p-8 lg:p-10">
            <h2 className="font-bold text-2xl mb-8 flex gap-3 items-center">
              <FileSearch className="w-6 h-6 text-primary-600" />Evidence and opportunity
            </h2>
            <div className="flex flex-col gap-6">
              {(diagnosis.top_pain_points || []).map((point) => (
                <div key={point.problem} className="rounded-2xl border border-gray-200 bg-white shadow-sm flex flex-col lg:flex-row gap-6 p-6 md:p-8 hover:shadow-md transition-all">
                  <div className="lg:w-1/3">
                    <p className="font-bold text-gray-900 text-xl mb-2">{point.problem}</p>
                    <p className="text-sm text-gray-600 leading-relaxed"><span className="font-semibold text-gray-800">Cause:</span> {point.root_cause}</p>
                  </div>
                  <div className="lg:w-2/3 bg-gray-50 p-6 rounded-xl border border-gray-100">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Supporting Evidence</p>
                    <div className="grid gap-3">
                      {point.evidence.map((evidence, index) => (
                        <p key={index} className="rounded-xl bg-white p-4 text-sm italic text-gray-700 border border-gray-100 shadow-sm">“{evidence}”</p>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
          
          <Card className="p-8 lg:p-10">
            <h2 className="font-bold text-2xl mb-8 flex gap-3 items-center">
              <Lightbulb className="w-6 h-6 text-primary-600" />Product fit and implementation
            </h2>
            <div className="grid md:grid-cols-2 gap-8">
              {(report.product_rationales || []).map((item) => (
                <div key={item.product_id} className="border border-primary-100 bg-primary-50/30 rounded-2xl p-6 md:p-8 shadow-sm">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="w-2 h-8 bg-primary-500 rounded-full"></span>
                    <h3 className="font-bold uppercase text-xl text-primary-900">{item.product_id}</h3>
                  </div>
                  <p className="mb-6 text-sm text-gray-700 leading-relaxed font-medium">{item.why_suitable}</p>
                  
                  <div className="bg-white rounded-xl p-5 border border-primary-100 shadow-sm mb-6">
                    <p className="text-xs font-semibold uppercase text-gray-500 tracking-widest mb-3">Relevant capabilities</p>
                    <List items={item.relevant_capabilities} />
                  </div>
                  
                  <div className="bg-white rounded-xl p-5 border border-primary-100 shadow-sm">
                    <p className="text-xs font-semibold uppercase text-gray-500 tracking-widest mb-3">How to start</p>
                    <p className="text-sm text-gray-700 leading-relaxed">{item.implementation_suggestion}</p>
                    {item.prerequisites?.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-100">
                        <p className="text-xs font-semibold uppercase text-gray-500 tracking-widest mb-3">Prerequisites</p>
                        <List items={item.prerequisites} />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          <Card className="p-8">
            <h2 className="font-bold text-lg mb-5 flex gap-2 items-center">
              <ShieldQuestion className="w-5 h-5 text-primary-600" />Discovery questions
            </h2>
            <List items={playbook.discovery_questions} icon={MessageCircle} />
          </Card>
          <Card className="p-8">
            <h2 className="font-bold text-lg mb-5 flex gap-2 items-center">
              <BrainCircuit className="w-5 h-5 text-primary-600" />Talk track
            </h2>
            <List items={playbook.talk_track} />
          </Card>
          <Card className="p-8">
            <h2 className="font-bold text-lg mb-5 flex gap-2 items-center">
              <Target className="w-5 h-5 text-primary-600" />Next actions
            </h2>
            <List items={playbook.next_actions} />
          </Card>
        </div>

        <Card className="p-8 lg:p-10">
          <h2 className="font-bold text-xl mb-6">Likely objections and suggested responses</h2>
          <div className="grid lg:grid-cols-2 gap-5">
            {(playbook.likely_objections || []).map((objection, index) => (
              <div key={objection} className="rounded-2xl bg-amber-50 border border-amber-100 p-5">
                <p className="font-medium text-amber-900">“{objection}”</p>
                <p className="mt-3 text-sm text-gray-700 leading-relaxed">{playbook.objection_responses?.[index] || 'Validate the concern and agree a low-risk first step.'}</p>
              </div>
            ))}
          </div>
        </Card>
      </main>
    </div>
  );
}
