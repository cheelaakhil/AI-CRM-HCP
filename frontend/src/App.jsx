/**
 * App — Root component with Navbar + LogInteraction page.
 */
import React from 'react';
import Navbar from './components/Navbar/Navbar';
import LogInteraction from './pages/LogInteraction';

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <div className="page-title-bar">
        <h3>Log Interaction</h3>
        <span className="breadcrumb">Dashboard &gt; Log Interaction</span>
      </div>
      <div className="main-content">
        <LogInteraction />
      </div>
    </div>
  );
}

export default App;
