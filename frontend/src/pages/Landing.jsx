import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, BarChart3, Target, ArrowRight, Zap, Sparkles, Building2, Play } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

const DEMO_PERSONA = {
  company_name: 'ABC Enterprise',
  industry: 'Retail',
  employee_count: '8',
  email: 'contact@abcenterprise.com',
  phone: '+60 12-345 6789',
  current_digital_tools: ['whatsapp', 'spreadsheet'],
  main_operational_problems: ['Customer orders are tracked across WhatsApp and spreadsheets']
};

export function Landing() {
  const navigate = useNavigate();
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [formData, setFormData] = useState({
    company_name: '',
    industry: '',
    employee_count: '',
    email: '',
    phone: ''
  });

  const handleModeChange = (demo) => {
    setIsDemoMode(demo);
    if (demo) {
      setFormData({
        company_name: DEMO_PERSONA.company_name,
        industry: DEMO_PERSONA.industry,
        employee_count: DEMO_PERSONA.employee_count,
        email: DEMO_PERSONA.email,
        phone: DEMO_PERSONA.phone
      });
    } else {
      setFormData({
        company_name: '',
        industry: '',
        employee_count: '',
        email: '',
        phone: ''
      });
    }
  };

  const handleStartAssessment = (e) => {
    e.preventDefault();
    navigate('/assessment', {
      state: {
        is_demo: isDemoMode,
        company_profile: {
          company_name: formData.company_name,
          industry: formData.industry,
          employee_count: parseInt(formData.employee_count, 10) || 8,
          email: formData.email,
          phone: formData.phone,
          current_digital_tools: isDemoMode ? DEMO_PERSONA.current_digital_tools : [],
          main_operational_problems: isDemoMode ? DEMO_PERSONA.main_operational_problems : []
        }
      }
    });
  };

  const handleDirectDemoLaunch = () => {
    navigate('/assessment', {
      state: {
        is_demo: true,
        company_profile: {
          company_name: DEMO_PERSONA.company_name,
          industry: DEMO_PERSONA.industry,
          employee_count: parseInt(DEMO_PERSONA.employee_count, 10),
          email: DEMO_PERSONA.email,
          phone: DEMO_PERSONA.phone,
          current_digital_tools: DEMO_PERSONA.current_digital_tools,
          main_operational_problems: DEMO_PERSONA.main_operational_problems
        }
      }
    });
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Exabytes Header */}
      <header className="border-b border-gray-100 bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded flex items-center justify-center">
              <span className="text-white font-bold text-lg">E</span>
            </div>
            <span className="text-xl font-semibold text-gray-900 tracking-tight">Exabytes</span>
            <span className="ml-2 text-sm text-gray-500 border-l border-gray-200 pl-2">AI Consultant</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => handleModeChange(!isDemoMode)}
              className={`text-xs px-3 py-1.5 rounded-full font-medium transition-all flex items-center gap-1.5 border ${
                isDemoMode
                  ? 'bg-amber-100 border-amber-300 text-amber-900 shadow-sm'
                  : 'bg-gray-100 hover:bg-gray-200 border-gray-200 text-gray-700'
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-amber-600" />
              {isDemoMode ? 'Demo Mode Active' : 'Enable Demo Mode'}
            </button>

            <button
              type="button"
              onClick={() => navigate('/leads')}
              className="text-xs px-3 py-1.5 rounded-full font-medium bg-gray-100 hover:bg-gray-200 border border-gray-200 text-gray-700 transition-colors flex items-center gap-1.5"
            >
              <BarChart3 className="w-3.5 h-3.5 text-primary-600" />
              Sales Dashboard
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid lg:grid-cols-12 gap-12 items-start">
            
            <div className="lg:col-span-7">
              {/* Demo Mode Banner */}
              {isDemoMode && (
                <div className="mb-6 p-4 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl shadow-sm">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-amber-500 text-white rounded-lg mt-0.5">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-amber-900 text-sm">Controlled Hackathon Demo Mode Active</h3>
                        <span className="text-[11px] bg-amber-200 text-amber-900 px-2 py-0.5 rounded font-mono">docs/mock_flow.md</span>
                      </div>
                      <p className="text-xs text-amber-800 mt-1 leading-relaxed">
                        Canonical Persona: <strong>ABC Enterprise</strong> (Retail • 8 staff). Demonstrates 3-turn interview, causal diagnosis, Freshsales match, SFSME 2.0 grant, and live impact simulation.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight mb-6">
                Turn Your Business Challenges Into a{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-blue-500">
                  Digital Transformation Roadmap
                </span>
              </h1>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                Our AI Consultant analyses your current operations, identifies operational bottlenecks, and recommends the exact digital tools to scale your SME efficiently.
              </p>

              {/* Assessment Mode Switcher */}
              <div className="mb-6 flex p-1 bg-gray-100 rounded-xl max-w-md">
                <button
                  type="button"
                  onClick={() => handleModeChange(false)}
                  className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                    !isDemoMode ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Normal Assessment
                </button>
                <button
                  type="button"
                  onClick={() => handleModeChange(true)}
                  className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-1.5 ${
                    isDemoMode ? 'bg-amber-500 text-white shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Zap className="w-4 h-4" /> Demo Assessment
                </button>
              </div>

              {/* Form */}
              <form onSubmit={handleStartAssessment} className="space-y-4 mb-8">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                    <input
                      type="text"
                      required
                      value={formData.company_name}
                      onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                      placeholder="Enter company name"
                      className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
                    <input
                      type="text"
                      required
                      value={formData.industry}
                      onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                      placeholder="e.g. Retail, F&B, Logistics"
                      className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 text-sm"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Employee Count</label>
                    <input
                      type="number"
                      required
                      min="1"
                      value={formData.employee_count}
                      onChange={(e) => setFormData({ ...formData, employee_count: e.target.value })}
                      placeholder="e.g. 8"
                      className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="name@company.com"
                      className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <input
                      type="tel"
                      required
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="Phone number"
                      className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 text-sm"
                    />
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 pt-2">
                  <Button 
                    type="submit"
                    className={`text-base px-8 py-3.5 shadow-lg ${
                      isDemoMode 
                        ? 'bg-amber-600 hover:bg-amber-700 shadow-amber-600/20 text-white' 
                        : 'bg-primary-600 hover:bg-primary-700 shadow-primary-600/20'
                    }`}
                  >
                    {isDemoMode ? 'Start Demo Assessment' : 'Start Assessment'}
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>

                  {!isDemoMode && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleDirectDemoLaunch}
                      className="border-amber-300 text-amber-700 hover:bg-amber-50"
                    >
                      <Zap className="mr-2 w-4 h-4 text-amber-500" />
                      1-Click Hackathon Demo
                    </Button>
                  )}
                </div>
              </form>
            </div>

            {/* Right Column: Demo Scenario Card */}
            <div className="lg:col-span-5 space-y-6">
              <Card className="border-primary-100 bg-gradient-to-br from-primary-50/50 to-white shadow-sm p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-primary-100 text-primary-600 rounded-lg flex items-center justify-center">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900">Canonical Demo Scenario</h3>
                    <p className="text-xs text-gray-500">ABC Enterprise (Retail, 8 employees)</p>
                  </div>
                </div>

                <div className="space-y-3 text-xs text-gray-600">
                  <div className="flex justify-between py-1.5 border-b border-gray-100">
                    <span className="text-gray-500">Tools</span>
                    <span className="font-semibold text-gray-800">WhatsApp & Spreadsheets</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-100">
                    <span className="text-gray-500">Core Issue</span>
                    <span className="font-semibold text-gray-800">Customer order tracking bottleneck</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-100">
                    <span className="text-gray-500">Manual Hours</span>
                    <span className="font-semibold text-gray-800">20 hrs/week (~RM26,000/yr)</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-100">
                    <span className="text-gray-500">Matched Solution</span>
                    <span className="font-semibold text-primary-700">Freshsales (CRM)</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-100">
                    <span className="text-gray-500">Matched Grant</span>
                    <span className="font-semibold text-green-700">SFSME 2.0 (50% matching)</span>
                  </div>
                </div>

                <div className="mt-5 pt-4 border-t border-gray-200">
                  <Button 
                    onClick={handleDirectDemoLaunch}
                    className="w-full bg-primary-600 hover:bg-primary-700 text-white text-sm py-2.5 flex items-center justify-center gap-2"
                  >
                    <Play className="w-4 h-4 fill-white" /> Launch Live Demo Flow
                  </Button>
                </div>
              </Card>
            </div>

          </div>
        </div>

        {/* Capabilities Grid */}
        <div className="bg-gray-50 border-t border-gray-100 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-4 gap-8">
              <Card className="hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-blue-100 text-primary-600 rounded-lg flex items-center justify-center mb-6">
                  <Bot className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Diagnose</h3>
                <p className="text-gray-600 text-sm">Adaptive AI understands your unique business processes and pain points.</p>
              </Card>

              <Card className="hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-lg flex items-center justify-center mb-6">
                  <BarChart3 className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Quantify</h3>
                <p className="text-gray-600 text-sm">Measure the exact financial and time impact of your current operational bottlenecks.</p>
              </Card>

              <Card className="hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-red-100 text-red-600 rounded-lg flex items-center justify-center mb-6">
                  <Target className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Prioritise</h3>
                <p className="text-gray-600 text-sm">Rank operational issues by urgency and overall business impact.</p>
              </Card>

              <Card className="hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-green-100 text-green-600 rounded-lg flex items-center justify-center mb-6">
                  <Zap className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Recommend</h3>
                <p className="text-gray-600 text-sm">Get matched with specific Exabytes solutions and potential government grants.</p>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
