function AlertPanel({ alerts }) {
  return (
    <section className="rounded-xl bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900">Fraud Alerts</h3>
        <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
          {alerts.length} Active
        </span>
      </div>

      <div className="space-y-2">
        {alerts.length === 0 ? (
          <p className="text-sm text-slate-500">No active alerts in the current stream.</p>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className="rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-sm text-red-700"
            >
              [ALERT] {alert.message}
            </div>
          ))
        )}
      </div>
    </section>
  );
}

export default AlertPanel;
