import React from 'react';

const RepoSelector = ({
  repositories,
  selectedRepo,
  setSelectedRepo,
  loadRepositories,
  isLoading
}) => (
  <div className="section">
    <h2 className="section-title">🎯 Select Repository for Upload</h2>
    <div className="input-group">
      <select
        value={selectedRepo}
        onChange={e => setSelectedRepo(e.target.value)}
        className="select"
        disabled={isLoading}
      >
        <option value="">Select a repository...</option>
        {repositories.map((repo) => (
          <option key={repo.id} value={repo.id}>
            {repo.name} (ID: {repo.id})
          </option>
        ))}
      </select>
      <button 
        onClick={loadRepositories}
        className="btn btn-secondary"
        disabled={isLoading}
      >
        {isLoading ? 'Loading...' : 'Refresh'}
      </button>
    </div>
  </div>
);

export default RepoSelector;
