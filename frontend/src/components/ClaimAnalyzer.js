import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Home, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  FileText,
  Brain,
  TrendingUp,
  Eye,
  Download,
  MessageSquare,
  RefreshCw
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

const ClaimAnalyzer = () => {
  const [query, setQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [showReasoningTree, setShowReasoningTree] = useState(false);

  const handleAnalyze = async () => {
    if (!query.trim()) {
      toast.error('Please enter a claim description');
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await axios.post('/api/analyze', {
        query: query
      });
      
      setAnalysisResult(response.data);
      toast.success('Analysis completed successfully!');
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setAnalysisResult(null);
    setShowReasoningTree(false);
  };

  const handleOverride = async (newDecision) => {
    if (!analysisResult) return;
    
    try {
      await axios.post('/api/feedback', {
        original_decision: analysisResult,
        corrected_decision: newDecision,
        feedback_type: 'correction',
        user_comment: 'Manual override by user',
        user_id: 'web_user'
      });
      
      setAnalysisResult(prev => ({
        ...prev,
        decision: newDecision,
        override_reason: 'Manual correction by user'
      }));
      
      toast.success('Decision overridden successfully!');
    } catch (error) {
      toast.error('Failed to override decision');
    }
  };

  const handleExportAudit = async () => {
    if (!analysisResult) return;
    
    try {
      const response = await axios.post('/api/audit/export', {
        decision_data: analysisResult
      });
      
      // Create download link
      const blob = new Blob([JSON.stringify(response.data, null, 2)], {
        type: 'application/json'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_report_${Date.now()}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
      
      toast.success('Audit report exported!');
    } catch (error) {
      toast.error('Failed to export audit report');
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex justify-center space-x-4 mb-8">
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing}
          className="btn-primary flex items-center space-x-2"
        >
          {isAnalyzing ? (
            <RefreshCw className="h-5 w-5 animate-spin" />
          ) : (
            <Search className="h-5 w-5" />
          )}
          <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Claim'}</span>
        </button>
        
        <button
          onClick={handleClear}
          className="btn-secondary flex items-center space-x-2"
        >
          <Home className="h-5 w-5" />
          <span>Clear Form</span>
        </button>
      </div>

      {/* Input Section */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Claim Description</h2>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe the insurance claim in natural language... (e.g., 'I'm a 45-year-old male who needs cataract surgery in Pune. My policy is 24 months old.')"
          className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      {/* Analysis Results */}
      {analysisResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="card"
        >
          <div className="flex items-center space-x-2 mb-6">
            <TrendingUp className="h-6 w-6 text-primary-600" />
            <h2 className="text-xl font-semibold">Analysis Results</h2>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-medium text-gray-700 mb-2">Decision</h3>
              <div className={`inline-block px-4 py-2 rounded-full text-lg font-semibold ${
                analysisResult.decision === 'approved' 
                  ? 'status-approved' 
                  : 'status-rejected'
              }`}>
                {analysisResult.decision?.toUpperCase()}
              </div>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <span className="text-2xl">₹</span>
              </div>
              <h3 className="font-medium text-gray-700 mb-2">Coverage Amount</h3>
              <div className="text-2xl font-bold text-gray-900">
                ₹{analysisResult.amount?.toLocaleString() || '0'}
              </div>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-medium text-gray-700 mb-2">Claim Type</h3>
              <div className="inline-block px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-sm font-medium">
                {analysisResult.query_data?.procedure || 'surgery'}
              </div>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <AlertTriangle className="h-6 w-6 text-orange-600" />
              </div>
              <h3 className="font-medium text-gray-700 mb-2">Accident Status</h3>
              <div className="inline-block px-3 py-1 rounded-full bg-orange-100 text-orange-800 text-sm font-medium">
                {analysisResult.query_data?.accident ? 'Accident' : 'Non-Accident'}
              </div>
            </div>
          </div>

          {/* Justification */}
          <div className="mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <Brain className="h-5 w-5 text-primary-600" />
              <h3 className="font-semibold">Justification</h3>
            </div>
            <p className="text-gray-700 leading-relaxed">
              {analysisResult.justification || 'No justification available.'}
            </p>
          </div>

          {/* Waiting Period Status */}
          <div className="mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <Clock className="h-5 w-5 text-primary-600" />
              <h3 className="font-semibold">Waiting Period Status</h3>
            </div>
            <p className="text-gray-700 leading-relaxed">
              {analysisResult.reasoning_breakdown || 'Waiting period analysis not available.'}
            </p>
          </div>

          {/* Relevant Clauses */}
          <div className="mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <FileText className="h-5 w-5 text-primary-600" />
              <h3 className="font-semibold">Relevant Clauses</h3>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              {analysisResult.retrieved_chunks ? (
                <ul className="space-y-2">
                  {analysisResult.retrieved_chunks.slice(0, 3).map((chunk, index) => (
                    <li key={index} className="text-sm text-gray-700">
                      • {chunk.substring(0, 150)}...
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No relevant clauses found.</p>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4 pt-6 border-t border-gray-200">
            <button
              onClick={() => setShowReasoningTree(!showReasoningTree)}
              className="btn-secondary flex items-center space-x-2"
            >
              <Eye className="h-4 w-4" />
              <span>{showReasoningTree ? 'Hide' : 'Show'} Reasoning Tree</span>
            </button>
            
            <button
              onClick={() => handleOverride(analysisResult.decision === 'approved' ? 'rejected' : 'approved')}
              className="btn-secondary flex items-center space-x-2"
            >
              <MessageSquare className="h-4 w-4" />
              <span>Override Decision</span>
            </button>
            
            <button
              onClick={handleExportAudit}
              className="btn-secondary flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Export Audit</span>
            </button>
          </div>

          {/* Reasoning Tree */}
          {showReasoningTree && analysisResult.reasoning_tree && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-6 p-4 bg-gray-50 rounded-lg"
            >
              <h4 className="font-semibold mb-3">Reasoning Tree</h4>
              <div className="space-y-2 text-sm">
                {analysisResult.reasoning_tree.steps?.map((step, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className={`w-2 h-2 rounded-full ${
                      step.status ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                    <span className="text-gray-700">{step.title}: {step.description}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default ClaimAnalyzer;
