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
      <div className="panel" onClick={(e) => e.stopPropagation()} style={{ width: '600px' }}>
        <h2>{vector.name}</h2>
        <div className="body">
          <p><strong>Status:</strong> {vector.status}</p>
          <p><strong>Artifact:</strong> <a href={`/artifacts/${vector.artifact}`}>{vector.artifact}</a></p>
          <AttackVectorVisualizer vector={vector.name} description={vector.description} />
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
