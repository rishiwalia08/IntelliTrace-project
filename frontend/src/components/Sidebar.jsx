import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Dashboard", to: "/" },
  { label: "Invoices", to: "/" },
  { label: "Graph View", to: "/graph" },
  { label: "Settings", to: "/" },
];

function Sidebar() {
  return (
    <aside className="w-64 border-r border-slate-200 bg-white p-4">
      <h2 className="mb-6 text-xl font-bold text-brand-700">CipherLink</h2>
      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.label}
            to={item.to}
            className={({ isActive }) =>
              `block rounded-md px-3 py-2 text-sm font-medium ${
                isActive
                  ? "bg-brand-600 text-white hover:bg-brand-700"
                  : "text-slate-700 hover:bg-slate-100"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
