import React, { useState, useEffect } from 'react';
import './App.css';
import LoginForm from './components/LoginForm';
import RepoSelector from './components/RepoSelector';
import FileUpload from './components/FileUpload';
import FilesTable from './components/FilesTable';

const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [repositories, setRepositories] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState('');
  const [newRepoName, setNewRepoName] = useState('');
  const [uploadProgress, setUploadProgress] = useState({});
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginUsername, setLoginUsername] = useState('admin');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [filesPerPage] = useState(8);
  const [filteredFiles, setFilteredFiles] = useState([]);

  // Generate unique upload ID
  const generateUploadId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  // Basic Auth login
  const handleLogin = async (e) => {
    e.preventDefault();
    if (isLoading) return;
    setLoginError('');
    if (!loginUsername.trim() || !loginPassword.trim()) {
      setLoginError('Username and password are required');
      return;
    }
    setIsLoading(true);
    try {
      const authString = btoa(loginUsername + ':' + loginPassword);
      const response = await fetch(`${API_BASE_URL}/api/`, {
        headers: {
          'Authorization': 'Basic ' + authString
        }
      });
      if (response.ok) {
        setIsAuthenticated(true);
        sessionStorage.setItem('auth', authString);
      } else {
        setIsAuthenticated(false);
        setLoginError('Invalid username or password');
        sessionStorage.removeItem('auth');
      }
    } catch (err) {
      setIsAuthenticated(false);
      setLoginError('Server error');
      sessionStorage.removeItem('auth');
    }
    setIsLoading(false);
  };

  // On mount, always restore username and password from sessionStorage if present
  useEffect(() => {
    const savedAuth = sessionStorage.getItem('auth');
    if (savedAuth) {
      fetch(`${API_BASE_URL}/api/`, {
        headers: { 'Authorization': 'Basic ' + savedAuth }
      })
        .then(res => {
          if (res.ok) {
            setIsAuthenticated(true);
            const [savedUser, savedPass] = atob(savedAuth).split(':');
            setLoginUsername(savedUser);
            setLoginPassword(savedPass);
          } else {
            setIsAuthenticated(false);
            sessionStorage.removeItem('auth');
          }
        })
        .catch(() => {
          setIsAuthenticated(false);
          sessionStorage.removeItem('auth');
        });
    }
  }, []);

  // On page refresh, clear session if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      sessionStorage.removeItem('auth');
    }
  }, [isAuthenticated]);

  // Wrap all API calls to include basic auth if authenticated
  const fetchWithAuth = async (url, options = {}) => {
    const headers = options.headers || {};
    // Always use the latest credentials from sessionStorage
    const savedAuth = sessionStorage.getItem('auth');
    if (savedAuth) {
      headers['Authorization'] = 'Basic ' + savedAuth;
    }
    return fetch(url, { ...options, headers });
  };

  // Create new repository
  const createRepository = async () => {
    if (!newRepoName.trim()) {
      setMessage('Please enter a repository name');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('repo_name', newRepoName);

      const response = await fetchWithAuth(`${API_BASE_URL}/api/gitlab/create-repository`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      if (data.success) {
        setMessage(`Repository "${newRepoName}" created successfully!`);
        setNewRepoName('');
        await loadRepositories(); // Refresh list
      } else {
        setMessage(`Error creating repository: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      setMessage(`Error creating repository: ${error.message}`);
    }
    setIsLoading(false);
  };

  // Load repositories
  const loadRepositories = async () => {
    setIsLoading(true);
    try {
      console.log('Loading repositories...');
      const response = await fetchWithAuth(`${API_BASE_URL}/api/gitlab/repositories`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Repositories data:', data);
      
      if (data.success && Array.isArray(data.repositories)) {
        setRepositories(data.repositories);
        console.log('Set repositories state:', data.repositories);
      } else {
        setRepositories([]);
        console.warn('Invalid repository data structure:', data);
      }
    } catch (error) {
      console.error('Error loading repositories:', error);
      setMessage(`Error loading repositories: ${error.message}`);
      setRepositories([]);
    }
    setIsLoading(false);
  };

  // Load uploaded files
  const loadUploadedFiles = async () => {
    try {
      console.log('Loading uploaded files...');
      const response = await fetchWithAuth(`${API_BASE_URL}/api/files`);
      if (!response.ok) {
        console.error('API /api/files failed:', response.status, response.statusText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Raw uploaded files from backend:', data);
      const filesArray = Array.isArray(data) ? data : [];
      setUploadedFiles(filesArray);
      console.log('Set uploaded files state:', filesArray);
    } catch (error) {
      console.error('Error loading files:', error);
      setMessage(`Error loading files: ${error.message}`);
    }
  };

  // Upload file in chunks
  const uploadFile = async (file, projectId) => {
    if (!file || !projectId) {
      setMessage('Please select a file and repository');
      return;
    }

    const uploadId = generateUploadId();
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    
    setIsUploading(true);
    setUploadProgress({ current: 0, total: totalChunks, fileName: file.name });

    try {
      for (let chunkNumber = 0; chunkNumber < totalChunks; chunkNumber++) {
        const start = chunkNumber * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const chunk = file.slice(start, end);

        const formData = new FormData();
        formData.append('file', chunk);
        formData.append('chunk_number', chunkNumber);
        formData.append('total_chunks', totalChunks);
        formData.append('file_name', file.name);
        formData.append('upload_id', uploadId);

        const response = await fetchWithAuth(
          `${API_BASE_URL}/api/gitlab/upload-chunk/${projectId}`,
          {
            method: 'POST',
            body: formData
          }
        );

        const data = await response.json();

        setUploadProgress({
          current: chunkNumber + 1,
          total: totalChunks,
          fileName: file.name,
          percentage: Math.round(((chunkNumber + 1) / totalChunks) * 100)
        });

        if (data.success && chunkNumber === totalChunks - 1) {
          setMessage(`File "${file.name}" uploaded successfully! PostgreSQL Doc ID: ${data.postgres_doc_id}`);
          // Refresh files list after successful upload
          setTimeout(() => {
            loadUploadedFiles();
          }, 1000); // Small delay to ensure backend has processed the metadata
        }
      }
    } catch (error) {
      setMessage(`Upload error: ${error.message}`);
    } finally {
      setIsUploading(false);
      setUploadProgress({});
    }
  };

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && selectedRepo) {
      uploadFile(file, selectedRepo);
    }
  };

  // Load data on component mount and when authenticated changes
  useEffect(() => {
    if (isAuthenticated) {
      loadRepositories();
      loadUploadedFiles();
    }
  }, [isAuthenticated]);

  // Reset selectedRepo and filteredFiles if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      setSelectedRepo('');
      setFilteredFiles([]);
    }
  }, [isAuthenticated]);

  // Filter files by selected repo
  useEffect(() => {
    if (selectedRepo) {
      setFilteredFiles(uploadedFiles.filter(f => String(f.gitlab_repo_id) === String(selectedRepo)));
      setCurrentPage(1);
    } else {
      setFilteredFiles([]);
    }
  }, [selectedRepo, uploadedFiles]);

  // Paging logic
  const indexOfLastFile = currentPage * filesPerPage;
  const indexOfFirstFile = indexOfLastFile - filesPerPage;
  const currentFiles = filteredFiles.slice(indexOfFirstFile, indexOfLastFile);
  const totalPages = Math.ceil(filteredFiles.length / filesPerPage);

  // Logout handler
  const handleLogout = () => {
    setIsAuthenticated(false);
    setLoginUsername('admin');
    setLoginPassword('');
    sessionStorage.removeItem('auth');
    setMessage(''); // Do not show 'Logged out successfully' on forced logout
  };

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    // Clear any lingering messages on failed login
    if (message) setMessage('');
    return (
      <LoginForm
        loginUsername={loginUsername}
        setLoginUsername={setLoginUsername}
        loginPassword={loginPassword}
        setLoginPassword={setLoginPassword}
        handleLogin={handleLogin}
        loginError={loginError}
        isLoading={isLoading}
      />
    );
  }

  return (
    <div className="app">
      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 10 }}>
          <button className="btn btn-secondary" onClick={handleLogout} style={{ minWidth: 100 }}>
            Logout
          </button>
        </div>
        <div className="section">
          <h2 className="section-title">📁 Create New Repository</h2>
          <div className="input-group">
            <input
              type="text"
              value={newRepoName}
              onChange={(e) => setNewRepoName(e.target.value)}
              placeholder="Enter repository name"
              className="input"
              disabled={isLoading}
            />
            <button 
              onClick={createRepository}
              className="btn btn-primary"
              disabled={isLoading || !newRepoName.trim()}
            >
              {isLoading ? 'Creating...' : 'Create Repository'}
            </button>
          </div>
        </div>
        <RepoSelector
          repositories={repositories}
          selectedRepo={selectedRepo}
          setSelectedRepo={setSelectedRepo}
          loadRepositories={loadRepositories}
          isLoading={isLoading}
        />
        <FileUpload
          handleFileSelect={handleFileSelect}
          selectedRepo={selectedRepo}
          isUploading={isUploading}
          uploadProgress={uploadProgress}
        />
        <FilesTable
          selectedRepo={selectedRepo}
          filteredFiles={filteredFiles}
          currentFiles={currentFiles}
          formatFileSize={formatFileSize}
          formatDate={formatDate}
          currentPage={currentPage}
          totalPages={totalPages}
          setCurrentPage={setCurrentPage}
        />
        {/* Status Messages */}
        {message && (
          <div className={`message ${message.includes('Error') || message.includes('error') ? 'error' : 'success'}`}>
            {message}
            <button 
              className="message-close"
              onClick={() => setMessage('')}
            >
              ×
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;