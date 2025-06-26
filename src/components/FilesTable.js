import React from 'react';

const FilesTable = ({
  selectedRepo,
  filteredFiles,
  currentFiles,
  formatFileSize,
  formatDate,
  currentPage,
  totalPages,
  setCurrentPage
}) => (
  <div className="section">
    <h2 className="section-title">📋 Uploaded Files</h2>
    {selectedRepo ? (
      filteredFiles.length > 0 ? (
        <>
          <table className="files-table">
            <thead>
              <tr>
                <th>File Name</th>
                <th>Size</th>
                <th>Chunks</th>
                <th>Type</th>
                <th>Uploaded</th>
                <th>Status</th>
                <th>Doc ID</th>
              </tr>
            </thead>
            <tbody>
              {currentFiles.map(file => (
                <tr key={file.id}>
                  <td>{file.original_filename}</td>
                  <td>{formatFileSize(file.file_size)}</td>
                  <td>{file.chunk_count}</td>
                  <td>{file.content_type || '-'}</td>
                  <td>{formatDate(file.upload_timestamp)}</td>
                  <td><span className="file-status">{file.status}</span></td>
                  <td><span className="doc-id">{file.id}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="paging">
            <button className="paging-btn" onClick={() => setCurrentPage(p => p - 1)} disabled={currentPage === 1}>Prev</button>
            <span className="paging-info">Page {currentPage} of {totalPages || 1}</span>
            <button className="paging-btn" onClick={() => setCurrentPage(p => p + 1)} disabled={currentPage === totalPages || totalPages === 0}>Next</button>
          </div>
        </>
      ) : (
        <div className="empty-state"><p>📭 No files for this repository</p></div>
      )
    ) : (
      <div className="empty-state"><p>🔎 Select a repository to view its files</p></div>
    )}
  </div>
);

export default FilesTable;
