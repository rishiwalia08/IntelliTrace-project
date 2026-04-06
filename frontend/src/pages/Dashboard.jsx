import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import AlertPanel from "../components/AlertPanel";
import InvoiceTable from "../components/InvoiceTable";
import useInvoices from "../hooks/useInvoices";
import { formatCurrency } from "../utils/formatters";

function Dashboard() {
  const { invoices, isLoading, alerts } = useInvoices();

  const highRiskCount = invoices.filter((invoice) => invoice.risk_assessment?.risk === "HIGH").length;
  const mediumRiskCount = invoices.filter((invoice) => invoice.risk_assessment?.risk === "MEDIUM").length;
  const totalExposure = invoices.reduce((sum, invoice) => sum + Number(invoice.amount), 0);

  const chartData = [
    { label: "Low", count: invoices.filter((invoice) => invoice.risk_assessment?.risk === "LOW").length },
    { label: "Medium", count: mediumRiskCount },
    { label: "High", count: highRiskCount },
  ];

  const cardBaseClass = "rounded-xl bg-white p-4 shadow-sm";

  return (
    <div className="space-y-6">
      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className={cardBaseClass}>
          <p className="text-sm text-slate-500">Total Invoices</p>
          <p className="mt-2 text-2xl font-semibold">{invoices.length}</p>
        </div>

        <div className={`${cardBaseClass} border-l-4 border-red-500`}>
          <p className="text-sm text-slate-500">High Risk Invoices</p>
          <p className="mt-2 text-2xl font-semibold text-red-600">{highRiskCount}</p>
        </div>

        <div className={`${cardBaseClass} border-l-4 border-amber-500`}>
          <p className="text-sm text-slate-500">Medium Risk Invoices</p>
          <p className="mt-2 text-2xl font-semibold text-amber-600">{mediumRiskCount}</p>
        </div>

        <div className={`${cardBaseClass} border-l-4 border-emerald-500`}>
          <p className="text-sm text-slate-500">Fraud Alerts Triggered</p>
          <p className="mt-2 text-2xl font-semibold text-emerald-600">{alerts.length}</p>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-xl bg-white p-4 shadow-sm lg:col-span-2">
          <h3 className="mb-3 text-base font-semibold text-slate-900">Risk Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="label" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Financing Exposure</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{formatCurrency(totalExposure)}</p>
          <p className="mt-2 text-xs text-slate-500">
            Exposure aggregates all supplier invoices currently visible in the network feed.
          </p>
        </div>
      </section>

      <AlertPanel alerts={alerts} />
      <InvoiceTable invoices={invoices} isLoading={isLoading} />
    </div>
  );
}

export default Dashboard;
