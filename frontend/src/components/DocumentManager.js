import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FolderOpen, 
  Upload, 
  FileText, 
  Trash2,
  Eye,
  Plus,
  Search,
  Filter
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const DocumentManager = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [filters, setFilters] = useState({
    type: 'all',
    search: ''
  });

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('/api/documents');
      setDocuments(response.data);
    } catch (error) {
      toast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files.length) return;

    setUploading(true);
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', 'base_policy'); // Default type
      formData.append('name', file.name);

      try {
        await axios.post('/api/documents/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        toast.success(`Uploaded ${file.name}`);
      } catch (error) {
        toast.error(`Failed to upload ${file.name}`);
      }
    }
    
    setUploading(false);
    fetchDocuments();
  };

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await axios.delete(`/api/documents/${docId}`);
      toast.success('Document deleted successfully');
      fetchDocuments();
    } catch (error) {
      toast.error('Failed to delete document');
    }
  };

  const handleViewDocument = (document) => {
    setSelectedDocument(document);
  };

  const filteredDocuments = documents.filter(doc => {
    if (filters.search && !doc.name.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }
    if (filters.type !== 'all' && doc.type !== filters.type) {
      return false;
    }
    return true;
  });

  const documentTypes = [
    { value: 'base_policy', label: 'Base Policy', color: 'bg-blue-100 text-blue-800' },
    { value: 'rider', label: 'Rider', color: 'bg-green-100 text-green-800' },
    { value: 'amendment', label: 'Amendment', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'email', label: 'Email', color: 'bg-purple-100 text-purple-800' },
  ];

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
        <FolderOpen className="h-8 w-8 text-primary-600" />
        <h1 className="text-3xl font-bold text-gray-900">Document Manager</h1>
      </div>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card mb-8"
      >
        <div className="flex items-center space-x-2 mb-4">
          <Upload className="h-5 w-5 text-primary-600" />
          <h3 className="font-semibold">Upload Documents</h3>
        </div>
        
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <input
            type="file"
            multiple
            accept=".pdf,.doc,.docx"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer flex flex-col items-center space-y-4"
          >
            <Upload className="h-12 w-12 text-gray-400" />
            <div>
              <p className="text-lg font-medium text-gray-900">
                {uploading ? 'Uploading...' : 'Click to upload documents'}
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF, DOC, DOCX files
              </p>
            </div>
          </label>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card mb-8"
      >
        <div className="flex items-center space-x-2 mb-4">
          <Filter className="h-5 w-5 text-primary-600" />
          <h3 className="font-semibold">Filters</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search documents..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
            <select
              value={filters.type}
              onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              {documentTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>
        </div>
      </motion.div>

      {/* Documents List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Documents ({filteredDocuments.length})</h3>
          <button
            onClick={() => document.getElementById('file-upload').click()}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Add Document</span>
          </button>
        </div>
        
        {filteredDocuments.map((doc, index) => {
          const docType = documentTypes.find(type => type.value === doc.type);
          
          return (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card hover:shadow-lg transition-shadow duration-200"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <FileText className="h-6 w-6 text-gray-600" />
                  </div>
                  
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{doc.name}</h4>
                    <div className="flex items-center space-x-4 mt-1">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${docType?.color || 'bg-gray-100 text-gray-800'}`}>
                        {docType?.label || doc.type}
                      </span>
                      <span className="text-sm text-gray-500">
                        {doc.chunk_count || 0} chunks
                      </span>
                      <span className="text-sm text-gray-500">
                        {new Date(doc.uploaded_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleViewDocument(doc)}
                    className="btn-secondary flex items-center space-x-1"
                  >
                    <Eye className="h-4 w-4" />
                    <span>View</span>
                  </button>
                  
                  <button
                    onClick={() => handleDeleteDocument(doc.id)}
                    className="btn-secondary flex items-center space-x-1 text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}
        
        {filteredDocuments.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <FolderOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No documents found</p>
          </motion.div>
        )}
      </div>

      {/* Document Detail Modal */}
      {selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Document Details</h2>
              <button
                onClick={() => setSelectedDocument(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Name</h3>
                <p className="text-gray-700">{selectedDocument.name}</p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Type</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  documentTypes.find(t => t.value === selectedDocument.type)?.color || 'bg-gray-100 text-gray-800'
                }`}>
                  {documentTypes.find(t => t.value === selectedDocument.type)?.label || selectedDocument.type}
                </span>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Chunks</h3>
                <p className="text-gray-700">{selectedDocument.chunk_count || 0} text chunks</p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Uploaded</h3>
                <p className="text-gray-700">{new Date(selectedDocument.uploaded_at).toLocaleString()}</p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">File Path</h3>
                <p className="text-gray-700 text-sm">{selectedDocument.file_path}</p>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default DocumentManager;
