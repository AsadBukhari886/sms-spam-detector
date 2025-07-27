import React, { useState } from 'react';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze.');
      setResult(null);
      return;
    }

    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok. Is the backend running?');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('Failed to analyze. Please ensure the backend server is running and reachable.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>AI & Spam Detector</h1>
        <p>Check if a message is spam and detect AI-generated content.</p>
      </header>

      <div className="analyzer">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter SMS message or any text here..."
          rows="6"
        />
        <button onClick={handleAnalyze} disabled={isLoading}>
          {isLoading ? 'Analyzing...' : 'Analyze Text'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {result && (
        <div className="results-container">
          <h2>Analysis Results</h2>
          <div className="result-card spam-card">
            <h3>SMS Spam Detection</h3>
            <p className={result.spam_detection.result === 'Spam' ? 'spam' : 'not-spam'}>
              {result.spam_detection.result}
            </p>
          </div>
          <div className="result-card ai-card">
            <h3>AI Content Detection</h3>
            {typeof result.ai_detection.percentage === 'number' ? (
              <p>
                This message is likely{' '}
                <span className="ai-percentage">{result.ai_detection.percentage}%</span>{' '}
                written by AI.
              </p>
            ) : (
              <p className="error-text">
                AI Score: {result.ai_detection.percentage}
              </p>
            )}
          </div>
        </div>
      )}

      <footer className="footer">
        <p>Built with FastAPI, React, and Groq</p>
      </footer>
    </div>
  );
}

export default App;
