import React, { useState } from 'react';
import './App.css';

function App() {
  const [age, setAge] = useState('');
  const [keywords, setKeywords] = useState(['', '', '']);
  const [story, setStory] = useState('');
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const data = {
      age,
      keywords
    };

    try {
      const response = await fetch('/generate_story', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      setStory(result.story);
      setImages(result.images);
    } catch (error) {
      console.error('Error generating story:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Generate a Fairy Tale</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          placeholder="Enter age"
          value={age}
          onChange={(e) => setAge(e.target.value)}
        />
        <input
          type="text"
          placeholder="Keyword 1"
          value={keywords[0]}
          onChange={(e) => setKeywords([e.target.value, keywords[1], keywords[2]])}
        />
        <input
          type="text"
          placeholder="Keyword 2"
          value={keywords[1]}
          onChange={(e) => setKeywords([keywords[0], e.target.value, keywords[2]])}
        />
        <input
          type="text"
          placeholder="Keyword 3"
          value={keywords[2]}
          onChange={(e) => setKeywords([keywords[0], keywords[1], e.target.value])}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Story'}
        </button>
      </form>

      {story && (
        <div className="story-container">
          <h2>Story</h2>
          <p>{story}</p>
        </div>
      )}

      {images.length > 0 && (
        <div className="image-grid">
          {images.map((img, index) => (
            <img
              key={index}
              src={`data:image/jpeg;base64,${img}`}
              alt={`Story Image ${index + 1}`}
              className="story-image"
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default App;