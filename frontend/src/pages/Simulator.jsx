import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Calculator, TrendingUp, Clock, DollarSign, ArrowRight, Loader2 } from 'lucide-react';
import { api } from '../api/client';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export function Simulator() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [params, setParams] = useState({
    hours_per_week: 20,
    hourly_rate_assumption: 25,
    automation_scenario_pct: 50
  });
  
  const [results, setResults] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [error, setError] = useState(null);

  const runSimulation = async (currentParams) => {
    setIsSimulating(true);
    try {
      const res = await api.simulateImpact(id, currentParams);
      setResults(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to run simulation.");
    } finally {
      setIsSimulating(false);
    }
  };

  // Run initial simulation on load
  useEffect(() => {
    runSimulation(params);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleSliderChange = (e) => {
    const { name, value } = e.target;
    setParams(prev => ({ ...prev, [name]: parseFloat(value) }));
  };

  const applySimulation = () => {
    runSimulation(params);
  };

  const formatCurrency = (val) => new Intl.NumberFormat('en-MY', { style: 'currency', currency: 'MYR' }).format(val);

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Calculator className="w-8 h-8 text-primary-600" />
              Impact Simulator
            </h1>
            <p className="text-gray-500 mt-2">Adjust the assumptions below to dynamically calculate the potential ROI of digital transformation.</p>
          </div>
          <Button size="lg" className="px-8" onClick={() => navigate(`/report/${id}?from=user&return=simulator`)}>
            Generate Detailed Report <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          
          {/* Controls */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Simulation Variables</h2>
            
            <div className="space-y-8">
              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">Hours spent on manual tasks per week</label>
                  <span className="text-primary-700 font-semibold">{params.hours_per_week} hrs</span>
                </div>
                <input 
                  type="range" name="hours_per_week" 
                  min="1" max="100" step="1"
                  value={params.hours_per_week} onChange={handleSliderChange}
                  className="w-full accent-primary-600"
                />
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">Blended hourly cost rate (MYR)</label>
                  <span className="text-primary-700 font-semibold">RM {params.hourly_rate_assumption}</span>
                </div>
                <input 
                  type="range" name="hourly_rate_assumption" 
                  min="10" max="200" step="5"
                  value={params.hourly_rate_assumption} onChange={handleSliderChange}
                  className="w-full accent-primary-600"
                />
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">Target automation %</label>
                  <span className="text-primary-700 font-semibold">{params.automation_scenario_pct}%</span>
                </div>
                <input 
                  type="range" name="automation_scenario_pct" 
                  min="10" max="90" step="5"
                  value={params.automation_scenario_pct} onChange={handleSliderChange}
                  className="w-full accent-primary-600"
                />
              </div>

              <div className="pt-4 border-t border-gray-100">
                <Button onClick={applySimulation} disabled={isSimulating} className="w-full">
                  {isSimulating ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Recalculate Impact'}
                </Button>
                {error && <p className="text-red-500 text-sm mt-2 text-center">{error}</p>}
              </div>
            </div>
          </Card>

          {/* Results */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Estimated Impact</h2>
            <p className="text-sm text-gray-500 italic mb-4">* Estimates only. Not guaranteed savings.</p>
            
            {!results ? (
              <Card className="h-64 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-gray-300 animate-spin" />
              </Card>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                <Card className="bg-red-50 border-red-100">
                  <div className="text-red-600 mb-2"><DollarSign className="w-6 h-6" /></div>
                  <p className="text-sm text-red-800 font-medium mb-1">Annual Opportunity Cost</p>
                  <p className="text-2xl font-bold text-red-900">{formatCurrency(results.annual_opportunity_cost)}</p>
                </Card>

                <Card className="bg-gray-50">
                  <div className="text-gray-500 mb-2"><Clock className="w-6 h-6" /></div>
                  <p className="text-sm text-gray-700 font-medium mb-1">Current Annual Hours</p>
                  <p className="text-2xl font-bold text-gray-900">{results.input_hours_per_week * 52} hrs</p>
                </Card>

                <Card className="bg-green-50 border-green-100 sm:col-span-2">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-green-600">
                      <TrendingUp className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm text-green-800 font-medium mb-1">Estimated Recovered Value / Year</p>
                      <p className="text-3xl font-bold text-green-900">{formatCurrency(results.recovered_value_per_year)}</p>
                      <p className="text-sm text-green-700 mt-1">({results.recovered_hours_per_year} hours saved annually)</p>
                    </div>
                  </div>
                </Card>

              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
