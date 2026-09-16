import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, TrendingUp, Flame, ArrowRight, Activity, Search, Filter } from 'lucide-react';
import { api } from '../api/client';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export function SalesDashboard() {
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('all');

  useEffect(() => {
    async function fetchLeads() {
      try {
        const res = await api.getLeads();
        setLeads(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchLeads();
  }, []);

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;

  const totalLeads = leads.length;
  const highPriority = leads.filter(l => l.lead_score >= 80).length;
  const strongLeads = leads.filter(l => l.lead_score >= 50 && l.lead_score < 80).length;
  const avgMaturity = leads.length > 0 ? (leads.reduce((acc, l) => acc + l.overall_maturity, 0) / leads.length).toFixed(1) : 0;
  const visibleLeads = leads.filter((lead) => {
    const query = searchTerm.trim().toLowerCase();
    const matchesSearch = !query || [
      lead.company_name,
      lead.company_industry,
      lead.top_pain_point_problem,
      lead.recommended_transformation,
      lead.email,
      lead.phone,
    ].some((value) => value?.toLowerCase().includes(query));
    return matchesSearch && (priorityFilter === 'all' || String(lead.priority) === priorityFilter);
  });

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex justify-between items-end pb-4 border-b border-gray-200">
          <div>
            <h1 className="text-3xl font-bold text-primary-900 flex items-center gap-3">
              <Users className="w-8 h-8 text-primary-600" />
              Sales Intelligence Dashboard
            </h1>
            <p className="text-gray-500 mt-2">Identify and prioritize high-value transformation leads.</p>
          </div>
          <Button onClick={() => navigate('/')}>
            New Assessment <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </div>

        {/* Lead Overview Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-white border-l-4 border-l-primary-500">
            <p className="text-sm font-medium text-gray-500 mb-1">Total Assessments</p>
            <p className="text-3xl font-bold text-gray-900">{totalLeads}</p>
          </Card>
          <Card className="bg-white border-l-4 border-l-red-500">
            <p className="text-sm font-medium text-gray-500 mb-1">High-Priority Leads</p>
            <p className="text-3xl font-bold text-red-600 flex items-center gap-2">
              {highPriority} <Flame className="w-5 h-5" />
            </p>
          </Card>
          <Card className="bg-white border-l-4 border-l-amber-500">
            <p className="text-sm font-medium text-gray-500 mb-1">Strong Leads</p>
            <p className="text-3xl font-bold text-amber-600">{strongLeads}</p>
          </Card>
          <Card className="bg-white border-l-4 border-l-blue-500">
            <p className="text-sm font-medium text-gray-500 mb-1">Avg. SME Maturity</p>
            <p className="text-3xl font-bold text-blue-600">{avgMaturity} / 5.0</p>
          </Card>
        </div>

        {/* Lead Table */}
        <Card className="p-0 overflow-hidden bg-white">
          <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h2 className="text-lg font-bold text-gray-900">Transformation Pipeline</h2>
            <div className="flex gap-2">
              <div className="relative">
                <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="search"
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder="Search leads..."
                  className="pl-9 pr-4 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
                />
              </div>
              <label className="flex items-center gap-2 px-3 py-1.5 border border-gray-300 rounded-md text-sm bg-white text-gray-600">
                <Filter className="w-4 h-4" />
                <select value={priorityFilter} onChange={(event) => setPriorityFilter(event.target.value)} className="bg-transparent focus:outline-none">
                  <option value="all">All priorities</option>
                  <option value="1">P1</option>
                  <option value="2">P2</option>
                  <option value="3">P3</option>
                </select>
              </label>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  <th className="px-6 py-4">Assessment & Industry</th>
                  <th className="px-6 py-4">Maturity</th>
                  <th className="px-6 py-4">Main Pain Point</th>
                  <th className="px-6 py-4">Priority</th>
                  <th className="px-6 py-4">Lead Score</th>
                  <th className="px-6 py-4">Recommended Solution</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {visibleLeads.map((lead) => (
                  <tr key={lead.assessment_id} className="hover:bg-primary-50/50 transition-colors cursor-pointer group" onClick={() => navigate(`/leads/${lead.assessment_id}`)}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <p className="text-sm font-bold text-gray-900">{lead.company_name}</p>
                      <p className="text-xs text-gray-500 mt-1">{lead.company_industry} &bull; {lead.employee_count} employees</p>
                      {(lead.email || lead.phone) && (
                        <p className="text-xs text-gray-400 mt-1">
                          {lead.email} {lead.email && lead.phone && '|'} {lead.phone}
                        </p>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-500" style={{ width: `${(lead.overall_maturity / 5) * 100}%` }}></div>
                        </div>
                        <span className="text-xs font-medium text-gray-700">{lead.overall_maturity.toFixed(1)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-700 truncate max-w-[200px]" title={lead.top_pain_point_problem}>{lead.top_pain_point_problem || "General Assessment"}</p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={lead.priority === 1 ? 'red' : lead.priority === 2 ? 'amber' : 'gray'}>
                        P{lead.priority}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className={`text-lg font-bold ${lead.lead_score >= 80 ? 'text-red-600' : lead.lead_score >= 50 ? 'text-amber-600' : 'text-gray-500'}`}>
                          {Math.round(lead.lead_score)}
                        </span>
                        {lead.lead_score >= 80 && <Flame className="w-4 h-4 text-red-500" />}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-primary-700 bg-primary-50 px-2 py-1 rounded-md uppercase">
                        {lead.recommended_transformation || "N/A"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors ml-auto" />
                    </td>
                  </tr>
                ))}
                
                {visibleLeads.length === 0 && (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                      <Activity className="w-8 h-8 text-gray-300 mx-auto mb-3" />
                      {leads.length ? 'No leads match the selected filters.' : 'No completed assessments are ready for the pipeline yet.'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>

      </div>
    </div>
  );
}
