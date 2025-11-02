// Files view component - browse and download files

import { useState, useEffect } from 'react';
import api from '../services/api';
import { formatTimestamp } from '../utils/time';

export default function FilesView() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const loadFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getFiles('default', filterType);
      setFiles(data.files || []);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load files:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (fileId) => {
    if (!confirm('Delete this file?')) return;

    try {
      setDeletingId(fileId);
      setError(null);
      await api.deleteFile(fileId);
      await loadFiles();
    } catch (err) {
      setError(err.message);
      console.error('Failed to delete file:', err);
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownload = (fileId, filename) => {
    const url = api.getFileUrl(fileId);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
  };

  useEffect(() => {
    loadFiles();
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadFiles, 10000);
    return () => clearInterval(interval);
  }, [filterType]);

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const fileTypes = [...new Set(files.map(f => f.file_type).filter(Boolean))];

  if (loading && files.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400">Loading files...</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">📁 Files</h2>
        <p className="text-gray-400 text-sm">Browse and download stored files</p>
      </div>

      {/* Filter */}
      {fileTypes.length > 0 && (
        <div className="mb-4 flex gap-2">
          <button
            onClick={() => setFilterType(null)}
            className={`px-3 py-1 rounded text-sm ${
              filterType === null
                ? 'bg-blue-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            All
          </button>
          {fileTypes.map(type => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1 rounded text-sm ${
                filterType === type
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-4 p-4 bg-red-900/30 border border-red-500 rounded">
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {/* Files List */}
      <div className="flex-1 overflow-y-auto">
        {files.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400">No files yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {files.map(file => (
              <div
                key={file.id}
                className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-lg truncate">
                        {file.filename}
                      </h3>
                      {file.file_type && (
                        <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-xs rounded">
                          {file.file_type}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-400 space-y-1">
                      <div className="flex items-center gap-4">
                        <span>{file.content_type}</span>
                        <span>{formatFileSize(file.size_bytes)}</span>
                        <span
                          className="cursor-help"
                          title={new Date(file.created_at).toLocaleString()}
                        >
                          {formatTimestamp(file.created_at)}
                        </span>
                      </div>
                      {file.metadata && Object.keys(file.metadata).length > 0 && (
                        <div className="text-xs text-gray-500">
                          {file.metadata.text_preview && (
                            <span>Preview: {file.metadata.text_preview}</span>
                          )}
                          {file.metadata.voice_id && (
                            <span className="ml-3">Voice: {file.metadata.voice_id}</span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {/* Play button for audio */}
                    {file.content_type.startsWith('audio/') && (
                      <audio
                        controls
                        preload="none"
                        className="h-10"
                        src={api.getFileUrl(file.id)}
                      />
                    )}

                    {/* Download button */}
                    <button
                      onClick={() => handleDownload(file.id, file.filename)}
                      className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors"
                      title="Download"
                    >
                      ⬇️
                    </button>

                    {/* Delete button */}
                    <button
                      onClick={() => handleDelete(file.id)}
                      disabled={deletingId === file.id}
                      className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded transition-colors disabled:opacity-50"
                      title="Delete"
                    >
                      {deletingId === file.id ? '...' : '🗑️'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div className="mt-4 pt-4 border-t border-gray-700 text-sm text-gray-400">
        {files.length} file{files.length !== 1 ? 's' : ''} total
        {filterType && ` • Filtered by: ${filterType}`}
      </div>
    </div>
  );
}
