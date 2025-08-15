import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Download, 
  Search, 
  Calendar,
  Filter,
  Eye,
  Printer
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuditReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    decision: 'all',
    search: ''
  });

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await axios.get('/api/audit/reports');
      setReports(response.data);
    } catch (error) {
      toast.error('Failed to load audit reports');
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = async (reportId) => {
    try {
      const response = await axios.get(`/api/audit/export/${reportId}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit_report_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Report exported successfully!');
    } catch (error) {
      toast.error('Failed to export report');
    }
  };

  const handleViewReport = (report) => {
    setSelectedReport(report);
  };

  const filteredReports = reports.filter(report => {
    if (filters.search && !report.query.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }
    if (filters.decision !== 'all' && report.decision !== filters.decision) {
      return false;
    }
    if (filters.dateFrom && new Date(report.timestamp) < new Date(filters.dateFrom)) {
      return false;
    }
    if (filters.dateTo && new Date(report.timestamp) > new Date(filters.dateTo)) {
      return false;
    }
    return true;
  });

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
        <FileText className="h-8 w-8 text-primary-600" />
        <h1 className="text-3xl font-bold text-gray-900">Audit Reports</h1>
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card mb-8"
      >
        <div className="flex items-center space-x-2 mb-4">
          <Filter className="h-5 w-5 text-primary-600" />
          <h3 className="font-semibold">Filters</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search reports..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Decision</label>
            <select
              value={filters.decision}
              onChange={(e) => setFilters(prev => ({ ...prev, decision: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Decisions</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
      </motion.div>

      {/* Reports List */}
      <div className="space-y-4">
        {filteredReports.map((report, index) => (
          <motion.div
            key={report.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-lg transition-shadow duration-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-4 mb-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    report.decision === 'approved' ? 'status-approved' : 'status-rejected'
                  }`}>
                    {report.decision.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-500">
                    <Calendar className="inline h-4 w-4 mr-1" />
                    {new Date(report.timestamp).toLocaleDateString()}
                  </span>
                </div>
                
                <h3 className="font-semibold text-gray-900 mb-2">
                  {report.query.substring(0, 100)}...
                </h3>
                
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span>Amount: ₹{report.amount?.toLocaleString() || '0'}</span>
                  <span>Confidence: {(report.confidence_score * 100).toFixed(1)}%</span>
                  <span>Chunks: {report.retrieved_chunks?.length || 0}</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleViewReport(report)}
                  className="btn-secondary flex items-center space-x-1"
                >
                  <Eye className="h-4 w-4" />
                  <span>View</span>
                </button>
                
                <button
                  onClick={() => handleExportReport(report.id)}
                  className="btn-secondary flex items-center space-x-1"
                >
                  <Download className="h-4 w-4" />
                  <span>Export</span>
                </button>
              </div>
            </div>
          </motion.div>
        ))}
        
        {filteredReports.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No audit reports found</p>
          </motion.div>
        )}
      </div>

      {/* Report Detail Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Audit Report Details</h2>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">Query</h3>
                <p className="text-gray-700">{selectedReport.query}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h3 className="font-semibold mb-2">Decision</h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    selectedReport.decision === 'approved' ? 'status-approved' : 'status-rejected'
                  }`}>
                    {selectedReport.decision.toUpperCase()}
                  </span>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2">Amount</h3>
                  <p className="text-2xl font-bold">₹{selectedReport.amount?.toLocaleString() || '0'}</p>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2">Confidence</h3>
                  <p className="text-2xl font-bold">{(selectedReport.confidence_score * 100).toFixed(1)}%</p>
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Justification</h3>
                <p className="text-gray-700">{selectedReport.justification}</p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Relevant Clauses</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  {selectedReport.retrieved_chunks?.map((chunk, index) => (
                    <div key={index} className="mb-2 text-sm text-gray-700">
                      • {chunk}
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex justify-end space-x-4 pt-6 border-t">
                <button
                  onClick={() => handleExportReport(selectedReport.id)}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Download className="h-4 w-4" />
                  <span>Export PDF</span>
                </button>
                
                <button
                  onClick={() => window.print()}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Printer className="h-4 w-4" />
                  <span>Print</span>
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default AuditReports;
