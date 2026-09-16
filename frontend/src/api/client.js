import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  createAssessment: async (profile) => {
    const res = await client.post('/assessments', { company_profile: profile });
    return res.data;
  },
  
  submitAnswer: async (id, answer, questionText, questionTopic) => {
    const res = await client.post(`/assessments/${id}/answers`, { answer, question_text: questionText, question_topic: questionTopic });
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
