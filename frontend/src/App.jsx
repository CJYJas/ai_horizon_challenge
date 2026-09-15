import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function Home() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Home (Landing Page)</h1>
      <nav className="mt-4 flex gap-4">
        <Link to="/assessment" className="text-blue-500">Start Assessment</Link>
        <Link to="/results" className="text-blue-500">View Results</Link>
        <Link to="/sales" className="text-blue-500">Sales Dashboard</Link>
      </nav>
    </div>
  );
}

function Assessment() {
  return <div className="p-8"><h1 className="text-2xl font-bold">Assessment Flow Placeholder</h1></div>;
}

function Results() {
  return <div className="p-8"><h1 className="text-2xl font-bold">Results / Report Placeholder</h1></div>;
}

function Sales() {
  return <div className="p-8"><h1 className="text-2xl font-bold">Sales Dashboard Placeholder</h1></div>;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/assessment" element={<Assessment />} />
        <Route path="/results" element={<Results />} />
        <Route path="/sales" element={<Sales />} />
      </Routes>
    </Router>
  )
}

export default App
