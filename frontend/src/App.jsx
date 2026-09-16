import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Landing } from './pages/Landing';
import { Assessment } from './pages/Assessment';
import { Diagnosis } from './pages/Diagnosis';
import { Simulator } from './pages/Simulator';
import { Roadmap } from './pages/Roadmap';
import { Report } from './pages/Report';
import { SalesDashboard } from './pages/SalesDashboard';
import { LeadDetail } from './pages/LeadDetail';
import { SalesReport } from './pages/SalesReport';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/assessment" element={<Assessment />} />
        <Route path="/diagnosis/:id" element={<Diagnosis />} />
        <Route path="/simulator/:id" element={<Simulator />} />
        <Route path="/roadmap/:id" element={<Roadmap />} />
        <Route path="/report/:id" element={<Report />} />
        <Route path="/brief-report/:id" element={<Report />} />
        <Route path="/leads" element={<SalesDashboard />} />
        <Route path="/leads/:id" element={<LeadDetail />} />
        <Route path="/leads/:id/sales-report" element={<SalesReport />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
