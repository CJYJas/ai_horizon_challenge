import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bot, ArrowRight, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { api } from '../api/client';

export function Assessment() {
  const navigate = useNavigate();
  const location = useLocation();
  const [step, setStep] = useState('profile'); // 'profile', 'chat', 'loading'
  const [assessmentId, setAssessmentId] = useState(null);
  const [profile] = useState(() => location.state?.company_profile || null);

  // Chat state
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [questionTopic, setQuestionTopic] = useState('tools_workflow');

  useEffect(() => {
    if (!profile) navigate('/', { replace: true });
  }, [navigate, profile]);

  const handleStart = async (e) => {
    e.preventDefault();
    setStep('loading');
    try {
      const res = await api.createAssessment(profile);
      setAssessmentId(res.assessment_id);
      setQuestion(res.initial_question);
      setQuestionTopic(res.initial_question_topic);
      setStep('chat');
    } catch (err) {
      console.error(err);
      setStep('profile');
      alert("Failed to start assessment.");
    }
  };

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();
    if (!answer.trim() || isSubmitting) return;

    const currentAnswer = answer;
    const currentQuestion = question;
    
    setChatHistory(prev => [...prev, { q: currentQuestion, a: currentAnswer }]);
    setAnswer("");
    setIsSubmitting(true);

    try {
      const res = await api.submitAnswer(assessmentId, currentAnswer, currentQuestion, questionTopic);
      
      if (res.is_complete) {
        navigate(`/diagnosis/${assessmentId}`);
      } else {
        setQuestion(res.follow_up_question);
        setQuestionTopic(res.question_topic || 'adaptive');
      }
    } catch (err) {
      console.error(err);
      alert("Analysis failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (step === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
          <p className="text-gray-600">Initializing AI Consultant...</p>
        </div>
      </div>
    );
  }

  if (!profile) return null;

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-primary-100 text-primary-600 rounded-lg flex items-center justify-center">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Smart Assessment</h2>
            <p className="text-gray-500 text-sm">Adaptive diagnostic interview</p>
          </div>
        </div>

        {step === 'profile' && (
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">Company profile received</h3>
            <p className="text-sm text-gray-500 mb-6">We will use these details as context and only ask about your operations.</p>
            <form onSubmit={handleStart} className="space-y-4">
              <dl className="grid sm:grid-cols-2 gap-4 rounded-xl bg-gray-50 p-5 text-sm">
                <div><dt className="text-gray-500">Company</dt><dd className="font-semibold text-gray-900">{profile.company_name}</dd></div>
                <div><dt className="text-gray-500">Industry</dt><dd className="font-semibold text-gray-900">{profile.industry}</dd></div>
                <div><dt className="text-gray-500">Employees</dt><dd className="font-semibold text-gray-900">{profile.employee_count}</dd></div>
                <div><dt className="text-gray-500">Contact</dt><dd className="font-semibold text-gray-900">{profile.email} · {profile.phone}</dd></div>
              </dl>
              <div className="pt-4 flex justify-end">
                <Button type="submit">
                  Begin Analysis
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </div>
            </form>
          </Card>
        )}

        {step === 'chat' && (
          <div className="space-y-6">
            {/* History */}
            {chatHistory.map((item, idx) => (
              <div key={idx} className="space-y-4 opacity-60">
                <Card className="bg-gray-50 border-gray-200">
                  <p className="text-gray-800 font-medium">{item.q}</p>
                </Card>
                <div className="flex justify-end">
                  <Card className="bg-primary-50 border-primary-100 w-3/4">
                    <p className="text-primary-900">{item.a}</p>
                  </Card>
                </div>
              </div>
            ))}

            {/* Current Question */}
            <Card className="border-primary-200 shadow-md shadow-primary-500/5">
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="w-5 h-5 text-primary-600" />
                </div>
                <div className="flex-1">
                  <p className="text-lg font-medium text-gray-900 leading-relaxed mb-6">
                    {question}
                  </p>
                  <form onSubmit={handleSubmitAnswer} className="relative">
                    <textarea
                      value={answer}
                      onChange={e => setAnswer(e.target.value)}
                      placeholder="Type your answer here..."
                      className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[120px] resize-none"
                      disabled={isSubmitting}
                    />
                    <div className="absolute bottom-3 right-3">
                      <Button 
                        type="submit" 
                        disabled={!answer.trim() || isSubmitting}
                        className="py-1.5 px-4"
                      >
                        {isSubmitting ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            Continue
                            <ArrowRight className="ml-2 w-4 h-4" />
                          </>
                        )}
                      </Button>
                    </div>
                  </form>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
