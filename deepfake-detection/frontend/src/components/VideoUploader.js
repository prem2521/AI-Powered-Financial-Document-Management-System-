import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

const VideoUploader = () => {
  const [file, setFile] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, success, error
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
      // Reset state
      setTaskId(null);
      setStatus('idle');
      setResult(null);
      setErrorMsg('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setStatus('uploading');
      const res = await axios.post(`${API_URL}/upload-video`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setTaskId(res.data.task_id);

      // Start analysis immediately after upload
      await axios.post(`${API_URL}/analyze/${res.data.task_id}`);
      setStatus('processing');
    } catch (err) {
      setStatus('error');
      setErrorMsg(err.response?.data?.detail || err.message);
    }
  };

  // Poll for results
  useEffect(() => {
    let interval;
    if (status === 'processing' && taskId) {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_URL}/result/${taskId}`);
          if (res.data.status === 'success') {
            setResult(res.data);
            setStatus('success');
            clearInterval(interval);
          } else if (res.data.status === 'error') {
            setStatus('error');
            setErrorMsg(res.data.message);
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 3000); // poll every 3 seconds
    }
    return () => clearInterval(interval);
  }, [status, taskId]);

  return (
    <div style={styles.container}>
      <div style={styles.uploadSection}>
        <input
          type="file"
          accept="video/mp4,video/avi,video/quicktime"
          onChange={handleFileChange}
          style={styles.fileInput}
        />
        <button
          onClick={handleUpload}
          disabled={!file || status === 'uploading' || status === 'processing'}
          style={styles.button}
        >
          {status === 'uploading' ? 'Uploading...' : 'Analyze Video'}
        </button>
      </div>

      {status === 'processing' && (
        <div style={styles.loader}>
          <h3>Analyzing Video...</h3>
          <p>This may take a few moments depending on the video length.</p>
        </div>
      )}

      {status === 'error' && (
        <div style={styles.errorBox}>
          <strong>Error: </strong> {errorMsg}
        </div>
      )}

      {status === 'success' && result && (
        <div style={styles.resultsContainer}>
          <div style={{...styles.resultHeader, backgroundColor: result.result === 'Deepfake Detected' ? '#ffebee' : '#e8f5e9'}}>
            <h2>{result.result}</h2>
            <p>Confidence: {(result.confidence * 100).toFixed(2)}%</p>
          </div>

          <h3>Frame Analysis ({result.frames_analyzed} frames)</h3>
          <div style={styles.framesGrid}>
            {result.frame_details.map((frame, idx) => (
              <div key={idx} style={styles.frameCard}>
                <p style={styles.frameTime}>Time: {frame.time_sec.toFixed(2)}s</p>
                <div style={styles.imageComparison}>
                  <div>
                    <p style={styles.imgLabel}>Extracted Face</p>
                    <img src={`data:image/jpeg;base64,${frame.face_image_b64}`} alt="Face" style={styles.img} />
                  </div>
                  <div>
                    <p style={styles.imgLabel}>Grad-CAM Heatmap</p>
                    <img src={`data:image/jpeg;base64,${frame.heatmap_b64}`} alt="Heatmap" style={styles.img} />
                  </div>
                </div>
                <div style={styles.framePrediction}>
                  <span>{frame.is_fake ? '🛑 Fake' : '✅ Real'}</span>
                  <span style={{float: 'right'}}>{(frame.fake_probability * 100).toFixed(1)}% Fake Prob</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
  },
  uploadSection: {
    display: 'flex',
    justifyContent: 'center',
    gap: '20px',
    marginBottom: '30px'
  },
  fileInput: {
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px'
  },
  button: {
    padding: '10px 20px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  loader: {
    textAlign: 'center',
    padding: '40px'
  },
  errorBox: {
    padding: '15px',
    backgroundColor: '#f8d7da',
    color: '#721c24',
    borderRadius: '4px',
    marginBottom: '20px'
  },
  resultsContainer: {
    marginTop: '30px'
  },
  resultHeader: {
    padding: '20px',
    borderRadius: '8px',
    textAlign: 'center',
    marginBottom: '30px'
  },
  framesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px'
  },
  frameCard: {
    border: '1px solid #eee',
    borderRadius: '8px',
    padding: '15px',
    backgroundColor: '#fafafa'
  },
  frameTime: {
    fontWeight: 'bold',
    marginBottom: '10px'
  },
  imageComparison: {
    display: 'flex',
    gap: '10px',
    marginBottom: '10px'
  },
  img: {
    width: '100%',
    borderRadius: '4px'
  },
  imgLabel: {
    fontSize: '12px',
    textAlign: 'center',
    margin: '0 0 5px 0',
    color: '#666'
  },
  framePrediction: {
    marginTop: '10px',
    padding: '10px',
    backgroundColor: '#fff',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '14px',
    fontWeight: 'bold'
  }
};

export default VideoUploader;
