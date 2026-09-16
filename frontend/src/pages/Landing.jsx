import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, BarChart3, Target, ArrowRight, Zap } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export function Landing() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    company_name: '',
    industry: '',
    employee_count: '',
    email: '',
    phone: ''
  });

  const handleStartAssessment = (e) => {
    e.preventDefault();
    navigate('/assessment', {
      state: {
        company_profile: {
          company_name: formData.company_name,
          industry: formData.industry,
          employee_count: parseInt(formData.employee_count, 10),
          email: formData.email,
          phone: formData.phone,
          current_digital_tools: [], // to be collected by AI
          main_operational_problems: [] // to be collected by AI
        }
      }
    });
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Exabytes Header */}
      <header className="border-b border-gray-100 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded flex items-center justify-center">
              <span className="text-white font-bold text-lg">E</span>
            </div>
            <span className="text-xl font-semibold text-gray-900 tracking-tight">Exabytes</span>
            <span className="ml-2 text-sm text-gray-500 border-l border-gray-200 pl-2">AI Consultant</span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight mb-6">
              Turn Your Business Challenges Into a <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-blue-400">Digital Transformation Roadmap</span>
            </h1>
            <p className="text-xl text-gray-600 mb-10 leading-relaxed">
              Our AI Consultant analyses your current operations, identifies operational bottlenecks, and recommends the exact digital tools to scale your SME efficiently.
            </p>
            
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
                    className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
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
                    className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
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
                    placeholder="e.g. 25"
                    className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
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
                    className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
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
                    className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
                  />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 pt-2">
                <Button 
                  type="submit"
                  className="text-lg px-8 py-4 bg-primary-600 hover:bg-primary-700 shadow-lg shadow-primary-600/20"
                >
                  Start Assessment
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </div>
            </form>
          </div>
        </div>

        {/* Capabilities Grid */}
        <div className="bg-gray-50 border-t border-gray-100 py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-4 gap-8">
              <Card className="hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-blue-100 text-primary-600 rounded-lg flex items-center justify-center mb-6">
                  <Bot className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Diagnose</h3>
                <p className="text-gray-600">Adaptive AI understands your unique business processes and pain points.</p>
              </Card>

              <Card className="hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-lg flex items-center justify-center mb-6">
                  <BarChart3 className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Quantify</h3>
                <p className="text-gray-600">Measure the exact financial and time impact of your current operational bottlenecks.</p>
              </Card>

              <Card className="hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-red-100 text-red-600 rounded-lg flex items-center justify-center mb-6">
                  <Target className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Prioritise</h3>
                <p className="text-gray-600">Rank operational issues by urgency and overall business impact.</p>
              </Card>

              <Card className="hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-green-100 text-green-600 rounded-lg flex items-center justify-center mb-6">
                  <Zap className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Recommend</h3>
                <p className="text-gray-600">Get matched with specific Exabytes solutions and potential government grants.</p>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
