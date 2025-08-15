import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import Navbar from './components/Navbar';
import ClaimAnalyzer from './components/ClaimAnalyzer';
import Analytics from './components/Analytics';
import AuditReports from './components/AuditReports';
import FeedbackDashboard from './components/FeedbackDashboard';
import DocumentManager from './components/DocumentManager';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      <Navbar />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="container mx-auto px-4 py-8"
      >
        <Routes>
          <Route path="/" element={<ClaimAnalyzer />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/audit" element={<AuditReports />} />
          <Route path="/feedback" element={<FeedbackDashboard />} />
          <Route path="/documents" element={<DocumentManager />} />
        </Routes>
      </motion.div>
    </div>
  );
}

export default App;
