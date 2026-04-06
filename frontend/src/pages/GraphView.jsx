import GraphView from "../components/GraphView";
import useInvoices from "../hooks/useInvoices";

function GraphViewPage() {
  const { invoices, isLoading } = useInvoices();

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Supply Chain Relationship Graph</h2>
        <p className="text-sm text-slate-500">
          Red links indicate cycle-like relationship patterns that may represent carousel fraud.
        </p>
      </div>

      {isLoading ? (
        <div className="rounded-xl bg-white p-6 text-sm text-slate-500 shadow-sm">
          Loading transaction graph...
        </div>
      ) : (
        <GraphView invoices={invoices} />
      )}
    </div>
  );
}

export default GraphViewPage;
