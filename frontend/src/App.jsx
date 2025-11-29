import { useState } from 'react';
import axios from 'axios';
import { Upload, Camera, Brain, Layers, Zap, Image as ImageIcon, Loader2 } from 'lucide-react';
import './styles.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError('');
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://127.0.0.1:8000/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError('Connection failed. Please ensure the Backend Server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Intelligent Scene Breakdown</h1>
        <p className="subtitle">Visual Perception • Spatial Logic • Generative Reasoning</p>
      </header>

      {/* Upload Section */}
      <div className="upload-card">
        <input 
          type="file" 
          accept="image/*" 
          onChange={handleFileChange} 
          id="fileInput"
          style={{ display: 'none' }} 
        />
        
        {!preview ? (
          <label htmlFor="fileInput" style={{ width: '100%', cursor: 'pointer' }}>
            <div className="upload-content">
              <Upload size={48} className="icon-large" />
              <h3>Click to Upload Image</h3>
              <p>Supports JPG, PNG, JPEG</p>
            </div>
          </label>
        ) : (
          <div className="preview-section">
            <div className="preview-container">
              <img src={preview} alt="Preview" className="preview-img" />
            </div>
            <div style={{ marginTop: '20px' }}>
              <label htmlFor="fileInput" style={{ color: '#38bdf8', cursor: 'pointer', textDecoration: 'underline' }}>
                Choose a different image
              </label>
            </div>
            
            <button className="analyze-btn" onClick={handleAnalyze} disabled={loading}>
              {loading ? <Loader2 className="loading-spinner" /> : <Zap size={20} />}
              {loading ? 'Processing Scene...' : 'Analyze Scene'}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div style={{ marginTop: '20px', padding: '15px', background: 'rgba(239,68,68,0.2)', border: '1px solid #ef4444', borderRadius: '10px', color: '#fca5a5', textAlign: 'center' }}>
          {error}
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="result-grid">
          
          {/* Left: Annotated Image */}
          <div className="card">
            <div className="card-header">
              <Camera color="#38bdf8" />
              <h3 className="card-title">Computer Vision</h3>
            </div>
            <div className="preview-container" style={{ marginTop: '0' }}>
              <img src={result.image_data} alt="Processed" className="preview-img" />
            </div>
          </div>

          {/* Right: AI Analysis */}
          <div className="card">
            <div className="card-header">
              <Brain color="#38bdf8" />
              <h3 className="card-title">Gemini Interpretation</h3>
            </div>

            <div className="badge-container">
              <span className="badge">Scene: {result.scene_type}</span>
              <span className="badge">Objects: {result.object_count}</span>
            </div>

            <div style={{ marginBottom: '30px' }}>
              <p className="narrative-text">{result.narrative}</p>
            </div>

            <div className="card-header" style={{ borderBottom: 'none', paddingBottom: '5px', marginBottom: '10px' }}>
              <Layers color="#38bdf8" size={18} />
              <h4 style={{ margin: 0, fontSize: '1rem', color: '#cbd5e1' }}>Spatial Logic Engine</h4>
            </div>
            
            <ul className="spatial-list">
              {result.spatial_data.length > 0 ? (
                result.spatial_data.map((item, index) => (
                  <li key={index} className="spatial-item">
                    <span className="bullet">›</span> {item}
                  </li>
                ))
              ) : (
                <li className="spatial-item" style={{ fontStyle: 'italic' }}>
                  No significant spatial relationships detected.
                </li>
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;