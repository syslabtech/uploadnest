import React from 'react';

const FileUpload = ({
  handleFileSelect,
  selectedRepo,
  isUploading,
  uploadProgress
}) => (
  <div className="section">
    <h2 className="section-title">📤 Upload File</h2>
    <div className="upload-area">
      <input
        type="file"
        onChange={handleFileSelect}
        disabled={!selectedRepo || isUploading}
        className="file-input"
        id="file-upload"
      />
      <label htmlFor="file-upload" className={`file-label ${(!selectedRepo || isUploading) ? 'disabled' : ''}`}>
        {isUploading ? '⏳ Uploading...' : '📎 Choose File to Upload'}
      </label>
      {isUploading && uploadProgress.fileName && (
        <div className="progress-section">
          <div className="progress-info">
            <div className="progress-text">
              📁 {uploadProgress.fileName}
            </div>
            <div className="progress-stats">
              Chunk {uploadProgress.current}/{uploadProgress.total} ({uploadProgress.percentage}%)
            </div>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${uploadProgress.percentage}%` }}
            />
          </div>
        </div>
      )}
    </div>
  </div>
);

export default FileUpload;
