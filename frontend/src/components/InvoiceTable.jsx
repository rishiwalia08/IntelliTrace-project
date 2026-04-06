import { useMemo, useState } from "react";

import RiskBadge from "./RiskBadge";
import { formatCurrency } from "../utils/formatters";

function InvoiceTable({ invoices, isLoading }) {
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [sortDirection, setSortDirection] = useState("desc");

  const sortedInvoices = useMemo(() => {
    const copy = [...invoices];
    copy.sort((a, b) => {
      const scoreA = Number(a.risk_assessment?.score || 0);
      const scoreB = Number(b.risk_assessment?.score || 0);
      return sortDirection === "desc" ? scoreB - scoreA : scoreA - scoreB;
    });
    return copy;
  }, [invoices, sortDirection]);

  const toggleSort = () => {
    setSortDirection((prev) => (prev === "desc" ? "asc" : "desc"));
  };

  return (
    <section className="grid gap-4 lg:grid-cols-3">
      <div className="overflow-hidden rounded-xl bg-white shadow-sm lg:col-span-2">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h3 className="text-base font-semibold text-slate-900">Invoice Intelligence Table</h3>
          <button
            onClick={toggleSort}
            className="rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
          >
            Sort Risk {sortDirection === "desc" ? "↓" : "↑"}
          </button>
        </div>

        {isLoading ? (
          <p className="p-4 text-sm text-slate-500">Loading invoice stream...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500">
                <tr>
                  <th className="px-4 py-3">Invoice ID</th>
                  <th className="px-4 py-3">Supplier → Buyer</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Risk Score</th>
                  <th className="px-4 py-3">Risk Level</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {sortedInvoices.map((invoice) => {
                  const risk = invoice.risk_assessment || { score: 0, risk: "LOW", reasons: [] };
                  const isHigh = risk.risk === "HIGH";

                  return (
                    <tr
                      key={invoice.id}
                      onClick={() => setSelectedInvoice(invoice)}
                      className={`cursor-pointer border-b border-slate-100 ${
                        isHigh ? "bg-red-50 hover:bg-red-100" : "hover:bg-slate-50"
                      }`}
                    >
                      <td className="px-4 py-3 font-semibold text-slate-900">{invoice.invoice_id}</td>
                      <td className="px-4 py-3 text-slate-700">
                        {invoice.supplier_id} → {invoice.buyer_id}
                      </td>
                      <td className="px-4 py-3 text-slate-700">{formatCurrency(invoice.amount)}</td>
                      <td className="px-4 py-3 font-semibold text-slate-900">{risk.score}</td>
                      <td className="px-4 py-3">
                        <RiskBadge level={risk.risk} />
                      </td>
                      <td className="px-4 py-3 text-slate-600">{invoice.status || "RECEIVED"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <aside className="rounded-xl bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-base font-semibold text-slate-900">Invoice Detail Panel</h3>
        {!selectedInvoice ? (
          <p className="text-sm text-slate-500">Select an invoice row to view fraud intelligence details.</p>
        ) : (
          <div className="space-y-3 text-sm">
            <div>
              <p className="text-slate-500">Invoice</p>
              <p className="font-medium text-slate-900">{selectedInvoice.invoice_id}</p>
            </div>
            <div>
              <p className="text-slate-500">Flow</p>
              <p className="font-medium text-slate-900">
                {selectedInvoice.supplier_id} → {selectedInvoice.buyer_id}
              </p>
            </div>
            <div>
              <p className="text-slate-500">Amount</p>
              <p className="font-medium text-slate-900">{formatCurrency(selectedInvoice.amount)}</p>
            </div>
            <div className="border-t border-slate-100 pt-3">
              <p className="text-slate-500">Risk score</p>
              <p className="text-lg font-bold text-slate-900">
                {selectedInvoice.risk_assessment?.score || 0}
              </p>
            </div>
            <div>
              <p className="mb-1 text-slate-500">Reasons:</p>
              <ul className="list-disc space-y-1 pl-5 text-slate-700">
                {(selectedInvoice.risk_assessment?.reasons || ["No risk explanation available yet."]).map(
                  (reason, idx) => (
                    <li key={`${selectedInvoice.id}-reason-${idx}`}>{reason}</li>
                  )
                )}
              </ul>
            </div>
          </div>
        )}
      </aside>
    </section>
  );
}

export default InvoiceTable;
