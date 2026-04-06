function Header() {
  return (
    <header className="border-b border-slate-200 bg-white px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">SCF Fraud Control Center</h1>
          <p className="text-sm text-slate-500">Monitor invoice authenticity, tier risk and financing exposure</p>
        </div>
        <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
          System Status: Healthy
        </span>
      </div>
    </header>
  );
}

export default Header;
