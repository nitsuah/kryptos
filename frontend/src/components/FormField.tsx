export default function FormField({
  label,
  children,
  style
}: {
  label: string;
  children: React.ReactNode;
  style?: React.CSSProperties
}) {
  return (
    <div className="field" style={style}>
      <label>{label}</label>
      {children}
    </div>
  );
}
