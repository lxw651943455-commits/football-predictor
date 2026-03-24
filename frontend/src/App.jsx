import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import HomePage from './pages/HomePage';
import PredictPage from './pages/PredictPage';
import AnalysisPage from './pages/AnalysisPage';
import HistoryPage from './pages/HistoryPage';
import TestPage from './pages/TestPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/test" element={<TestPage />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/predict" element={<PredictPage />} />
        <Route path="/analysis/:matchId" element={<AnalysisPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
