import React from 'react';

// Mock visualization component for K4 attack surface
export default function AttackVectorGraph({ data }: { data: any[] }) {
  return (
    <div className="panel" style={{ marginTop: '16px' }}>
      <h2>Attack Surface Analysis</h2>
      <div className="body">
        <svg viewBox="0 0 400 200" style={{ width: '100%', height: 'auto' }}>
          {/* Very simple visualization for now */}
          <rect x="20" y="20" width="360" height="160" fill="var(--bg)" stroke="var(--accent)" strokeWidth="1" />
          <text x="200" y="100" textAnchor="middle" fill="var(--text)">Surface Graph Placeholder</text>
        </svg>
      </div>
    </div>
  );
}
