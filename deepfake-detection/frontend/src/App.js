import React from 'react';
import VideoUploader from './components/VideoUploader';

function App() {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ color: '#2c3e50' }}>Deepfake Detection System</h1>
        <p style={{ color: '#7f8c8d' }}>Upload a video to analyze it for AI manipulation</p>
      </header>

      <main>
        <VideoUploader />
      </main>
    </div>
  );
}

export default App;
