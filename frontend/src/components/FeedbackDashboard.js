import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  MessageSquare, 
  ThumbsUp, 
  ThumbsDown, 
  AlertTriangle,
  TrendingUp,
  Users,
  Clock,
  Send
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const FeedbackDashboard = () => {
  const [feedback, setFeedback] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [newFeedback, setNewFeedback] = useState({
    type: 'correction',
    comment: '',
    decision_id: ''
  });

  useEffect(() => {
    fetchFeedback();
    fetchAnalytics();
  }, []);

  const fetchFeedback = async () => {
    try {
      const response = await axios.get('/api/feedback');
      setFeedback(response.data);
    } catch (error) {
      toast.error('Failed to load feedback');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get('/api/feedback/analytics');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to load analytics');
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    
    if (!newFeedback.comment.trim()) {
      toast.error('Please enter a comment');
      return;
    }

    try {
      await axios.post('/api/feedback', {
        type: newFeedback.type,
        comment: newFeedback.comment,
        decision_id: newFeedback.decision_id || 'general'
      });
      
      setNewFeedback({ type: 'correction', comment: '', decision_id: '' });
      fetchFeedback();
      fetchAnalytics();
      toast.success('Feedback submitted successfully!');
    } catch (error) {
      toast.error('Failed to submit feedback');
    }
  };

  const handleViewFeedback = (feedbackItem) => {
    setSelectedFeedback(feedbackItem);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center space-x-2 mb-8">
        <MessageSquare className="h-8 w-8 text-primary-600" />
        <h1 className="text-3xl font-bold text-gray-900">Feedback Dashboard</h1>
      </div>

      {/* Analytics Overview */}
      {analytics && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          <div className="card">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <MessageSquare className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Total Feedback</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.total_feedback || 0}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <ThumbsUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Correction Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics.correction_rate ? `${(analytics.correction_rate * 100).toFixed(1)}%` : '0%'}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Improvement Requests</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics.feedback_by_type?.improvement || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Decision Changes</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics.decision_changes || 0}
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Submit Feedback */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card mb-8"
      >
        <h3 className="text-lg font-semibold mb-4">Submit Feedback</h3>
        <form onSubmit={handleSubmitFeedback} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Feedback Type</label>
              <select
                value={newFeedback.type}
                onChange={(e) => setNewFeedback(prev => ({ ...prev, type: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="correction">Correction</option>
                <option value="improvement">Improvement</option>
                <option value="bug_report">Bug Report</option>
                <option value="feature_request">Feature Request</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Decision ID (Optional)</label>
              <input
                type="text"
                placeholder="Enter decision ID..."
                value={newFeedback.decision_id}
                onChange={(e) => setNewFeedback(prev => ({ ...prev, decision_id: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Comment</label>
            <textarea
              value={newFeedback.comment}
              onChange={(e) => setNewFeedback(prev => ({ ...prev, comment: e.target.value }))}
              placeholder="Describe your feedback..."
              rows={4}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              className="btn-primary flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
              <span>Submit Feedback</span>
            </button>
          </div>
        </form>
      </motion.div>

      {/* Feedback List */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold mb-4">Recent Feedback</h3>
        
        {feedback.map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-lg transition-shadow duration-200"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-4 mb-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    item.type === 'correction' ? 'bg-red-100 text-red-800' :
                    item.type === 'improvement' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {item.type.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-500">
                    <Clock className="inline h-4 w-4 mr-1" />
                    {new Date(item.timestamp).toLocaleDateString()}
                  </span>
                </div>
                
                <p className="text-gray-700 mb-2">{item.comment}</p>
                
                {item.original_decision && (
                  <div className="text-sm text-gray-600">
                    <span>Original: {item.original_decision}</span>
                    {item.corrected_decision && (
                      <span className="ml-4">→ Corrected: {item.corrected_decision}</span>
                    )}
                  </div>
                )}
              </div>
              
              <button
                onClick={() => handleViewFeedback(item)}
                className="btn-secondary flex items-center space-x-1"
              >
                <MessageSquare className="h-4 w-4" />
                <span>View</span>
              </button>
            </div>
          </motion.div>
        ))}
        
        {feedback.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No feedback submitted yet</p>
          </motion.div>
        )}
      </div>

      {/* Feedback Detail Modal */}
      {selectedFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Feedback Details</h2>
              <button
                onClick={() => setSelectedFeedback(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Type</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  selectedFeedback.type === 'correction' ? 'bg-red-100 text-red-800' :
                  selectedFeedback.type === 'improvement' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {selectedFeedback.type.toUpperCase()}
                </span>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Comment</h3>
                <p className="text-gray-700">{selectedFeedback.comment}</p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Timestamp</h3>
                <p className="text-gray-700">{new Date(selectedFeedback.timestamp).toLocaleString()}</p>
              </div>
              
              {selectedFeedback.user_id && (
                <div>
                  <h3 className="font-semibold mb-2">User ID</h3>
                  <p className="text-gray-700">{selectedFeedback.user_id}</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default FeedbackDashboard;
