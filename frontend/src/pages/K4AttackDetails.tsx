import AttackVectorVisualizer from "../components/AttackVectorVisualizer";
import { AttackVector } from "../api";

interface Props {
  vector: AttackVector;
  onClose: () => void;
}

export default function K4AttackDetails({ vector, onClose }: Props) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="panel modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>{vector.name}</h2>
        <div className="body">
          <p>
            <strong>Status:</strong>{" "}
            <span
              className={`status-${vector.status
                .toLowerCase()
                .replace(/\s+/g, "-")}`}
            >
              {vector.status}
            </span>
          </p>
          <p>
            <strong>Artifact:</strong>{" "}
            {vector.artifact ? (
              <a
                href={`/artifacts/${vector.artifact}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                {vector.artifact}
              </a>
            ) : (
              "N/A"
            )}
          </p>

          {vector.description && (
            <div className="description-box">{vector.description}</div>
          )}
          <AttackVectorVisualizer
            vector={vector.name}
            description={vector.description}
          />
          <div className="modal-footer">
            <button onClick={onClose}>Close</button>
          </div>
        </div>
      </div>
    </div>
  );
}
