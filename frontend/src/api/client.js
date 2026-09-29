import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  getDemoCase: async () => {
    const res = await client.get('/demo/case');
    return res.data;
  },

  createDemoAssessment: async (profile) => {
    const res = await client.post('/demo/assessments', profile ? { company_profile: profile } : {});
    return res.data;
  },

  createAssessment: async (profile) => {
    const res = await client.post('/assessments', { company_profile: profile });
    return res.data;
  },
  
  submitAnswer: async (id, answer, questionText, questionTopic) => {
    const endpoint = id && id.startsWith('demo-') ? `/demo/assessments/${id}/answers` : `/assessments/${id}/answers`;
    const res = await client.post(endpoint, { answer, question_text: questionText, question_topic: questionTopic });
    return res.data;
  },

  
  getDiagnosis: async (id) => {
    const res = await client.get(`/assessments/${id}/diagnosis`);
    return res.data;
  },
  
  simulateImpact: async (id, payload) => {
    const res = await client.post(`/assessments/${id}/impact-simulation`, payload);
    return res.data;
  },
  
  getReport: async (id) => {
    const res = await client.get(`/assessments/${id}/report`);
    return res.data;
  },
  
  getLeads: async () => {
    const res = await client.get('/leads');
    return res.data;
  },
  
  getLeadDetail: async (id) => {
    const res = await client.get(`/leads/${id}`);
    return res.data;
  },
  getSalesReport: async (id) => {
    const res = await client.get(`/leads/${id}/sales-report`);
    return res.data;
  }
};
