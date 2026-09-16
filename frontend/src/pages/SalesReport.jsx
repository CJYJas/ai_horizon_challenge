import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, BrainCircuit, CheckCircle2, FileSearch, Lightbulb, MessageCircle, ShieldQuestion, Target } from 'lucide-react';
import { api } from '../api/client';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

const List = ({ items, icon: Icon = CheckCircle2 }) => (
  <ul className="space-y-3">{(items || []).map((item, index) => <li key={index} className="flex gap-3 text-sm text-gray-700"><Icon className="w-4 h-4 mt-0.5 shrink-0 text-primary-600" />{item}</li>)}</ul>
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
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <main className="max-w-6xl mx-auto space-y-7">
        <div className="flex justify-between items-center">
          <Button variant="ghost" onClick={() => navigate(`/leads/${id}`)}><ArrowLeft className="w-4 h-4 mr-2" />Back to lead</Button>
          <Badge variant="blue">Sales-only playbook</Badge>
        </div>
        <header className="bg-primary-900 text-white rounded-2xl p-8">
          <p className="text-primary-200 text-sm mb-2">Consultative sales playbook</p>
          <h1 className="text-3xl font-bold">{profile.company_name || data.lead_label}</h1>
          <p className="mt-2 text-primary-100">{profile.industry} · {profile.employee_count} employees · {profile.email} · {profile.phone}</p>
          <p className="mt-5 text-lg max-w-3xl">{playbook.situation_summary || report.sales_brief?.sme_situation_summary}</p>
        </header>

        <div className="grid lg:grid-cols-2 gap-6">
          <Card>
            <h2 className="font-bold text-lg mb-4 flex gap-2 items-center"><FileSearch className="w-5 h-5 text-primary-600" />Evidence and opportunity</h2>
            {(diagnosis.top_pain_points || []).map((point) => <div key={point.problem} className="mb-5 last:mb-0"><p className="font-semibold text-gray-900">{point.problem}</p><p className="text-sm text-gray-600 mt-1">Cause: {point.root_cause}</p><div className="mt-3 space-y-2">{point.evidence.map((evidence, index) => <p key={index} className="rounded bg-gray-50 p-2 text-sm italic text-gray-700">“{evidence}”</p>)}</div></div>)}
          </Card>
          <Card>
            <h2 className="font-bold text-lg mb-4 flex gap-2 items-center"><Lightbulb className="w-5 h-5 text-primary-600" />Product fit and implementation</h2>
            <div className="space-y-6">{(report.product_rationales || []).map((item) => <div key={item.product_id} className="border-l-4 border-primary-500 pl-4"><h3 className="font-bold uppercase">{item.product_id}</h3><p className="mt-2 text-sm text-gray-700">{item.why_suitable}</p><p className="mt-3 text-xs font-semibold uppercase text-gray-500">Relevant capabilities</p><List items={item.relevant_capabilities} /><p className="mt-3 text-xs font-semibold uppercase text-gray-500">How to start</p><p className="text-sm text-gray-700">{item.implementation_suggestion}</p>{item.prerequisites?.length > 0 && <><p className="mt-3 text-xs font-semibold uppercase text-gray-500">Prerequisites</p><List items={item.prerequisites} /></>}</div>)}</div>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card><h2 className="font-bold mb-4 flex gap-2 items-center"><ShieldQuestion className="w-5 h-5 text-primary-600" />Discovery questions</h2><List items={playbook.discovery_questions} icon={MessageCircle} /></Card>
          <Card><h2 className="font-bold mb-4 flex gap-2 items-center"><BrainCircuit className="w-5 h-5 text-primary-600" />Talk track</h2><List items={playbook.talk_track} /></Card>
          <Card><h2 className="font-bold mb-4 flex gap-2 items-center"><Target className="w-5 h-5 text-primary-600" />Next actions</h2><List items={playbook.next_actions} /></Card>
        </div>
        <Card>
          <h2 className="font-bold text-lg mb-4">Likely objections and suggested responses</h2>
          <div className="grid md:grid-cols-2 gap-4">{(playbook.likely_objections || []).map((objection, index) => <div key={objection} className="rounded-xl bg-amber-50 border border-amber-100 p-4"><p className="font-medium text-amber-900">“{objection}”</p><p className="mt-2 text-sm text-gray-700">{playbook.objection_responses?.[index] || 'Validate the concern and agree a low-risk first step.'}</p></div>)}</div>
        </Card>
      </main>
    </div>
  );
}
