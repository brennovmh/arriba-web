type Props = {
  status: string | null | undefined;
};

export default function StatusBadge({ status }: Props) {
  return <span className={`status-badge status-${status || "unknown"}`}>{status || "unknown"}</span>;
}
