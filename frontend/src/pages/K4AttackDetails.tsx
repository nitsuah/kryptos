import AttackVectorVisualizer from "../components/AttackVectorVisualizer";
import { AttackVector } from "../api";

interface Props {
  vector: AttackVector;
  onClose: () => void;
}

export default function K4AttackDetails({ vector, onClose }: Props) {
  return (
    <div className="modal-overlay" onClick={onClose} style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(4, 52, 44, 0.8)', display: 'flex',
      alignItems: 'center', justifyContent: 'center', zIndex: 100
    }}>
      <div className="panel" onClick={(e) => e.stopPropagation()} style={{ width: '600px', border: '1px solid var(--accent)', boxShadow: '0 0 10px rgba(29, 158, 117, 0.5)' }}>
        <h2 style={{ color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '10px', marginBottom: '15px', fontSize: '1.2em', letterSpacing: '2px', textShadow: '0 0 8px var(--accent)' }}>{vector.name}</h2>
        <div className="body">
          <p style={{ marginBottom: '8px', fontSize: '1em' }}><strong>Status:</strong> <span style={{ color: vector.status === "Ruled Out" ? 'var(--accent)' : vector.status === "In Progress" ? 'var(--warning)' : 'var(--text)' }}>{vector.status}</span></p>
          {vector.artifact && (
            <p style={{ marginBottom: '15px', fontSize: '1em' }}><strong>Artifact:</strong> <a href={`/artifacts/${vector.artifact}`} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)', textDecoration: 'underline' }}>{vector.artifact}</a></p>
          )}
          {!vector.artifact && (
            <p style={{ marginBottom: '15px', fontSize: '1em' }}><strong>Artifact:</strong> N/A</p>
          )}

          {vector.description && (
            <div style={{
              border: '0.5px dashed var(--border)',
              padding: '12px', /* Increased padding */
              borderRadius: '3px',
              marginBottom: '15px',
              backgroundColor: 'rgba(29, 158, 117, 0.05)',
              color: 'var(--text)',
              fontSize: '0.9em', /* Slightly smaller font size for description */
              lineHeight: '1.5', /* Adjusted line height */
              boxShadow: '0 0 5px rgba(29, 158, 117, 0.2)' /* Subtle glow for description box */
            }}>
              <strong>Description:</strong> {vector.description}
            </div>
          )}
          <AttackVectorVisualizer vector={vector.name} description={vector.description} />
          <button onClick={onClose} style={{ marginTop: '25px', background: 'var(--surface)', color: 'var(--accent)', border: '0.5px solid var(--accent)', padding: '10px 18px', borderRadius: '3px', cursor: 'pointer', float: 'right', fontSize: '0.9em', textTransform: 'uppercase', letterSpacing: '1px' }}>Close</button>

        </div>
      </div>
    </div>
  );
}
