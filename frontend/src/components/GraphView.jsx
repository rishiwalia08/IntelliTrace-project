import { useMemo } from "react";
import ForceGraph2D from "react-force-graph-2d";

function hasPath(adjacency, start, target, visited = new Set()) {
  if (start === target) {
    return true;
  }

  visited.add(start);
  const nextNodes = adjacency.get(start) || [];

  for (const next of nextNodes) {
    if (!visited.has(next) && hasPath(adjacency, next, target, visited)) {
      return true;
    }
  }

  return false;
}

function GraphView({ invoices }) {
  const graphData = useMemo(() => {
    const nodeSet = new Set();
    const links = invoices.map((invoice, index) => {
      nodeSet.add(invoice.supplier_id);
      nodeSet.add(invoice.buyer_id);

      return {
        id: `${invoice.id}-${index}`,
        source: invoice.supplier_id,
        target: invoice.buyer_id,
        invoiceId: invoice.invoice_id,
        amount: invoice.amount,
      };
    });

    const adjacency = new Map();
    links.forEach((link) => {
      const list = adjacency.get(link.source) || [];
      list.push(link.target);
      adjacency.set(link.source, list);
    });

    const cycleEdges = new Set();
    links.forEach((link) => {
      const nextNodes = (adjacency.get(link.target) || []).filter((node) => node !== link.source);
      for (const candidate of nextNodes) {
        if (hasPath(adjacency, candidate, link.source)) {
          cycleEdges.add(link.id);
          break;
        }
      }
    });

    const nodes = [...nodeSet].map((id) => ({ id }));
    return { nodes, links, cycleEdges };
  }, [invoices]);

  return (
    <div className="h-[620px] w-full overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <ForceGraph2D
        graphData={{ nodes: graphData.nodes, links: graphData.links }}
        nodeLabel={(node) => `Entity: ${node.id}`}
        linkLabel={(link) => `Invoice ${link.invoiceId} | ${link.source} → ${link.target}`}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.id;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = "#2563eb";
          ctx.beginPath();
          ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
          ctx.fill();
          ctx.fillStyle = "#0f172a";
          ctx.fillText(label, node.x + 8, node.y + 4);
        }}
        linkColor={(link) => (graphData.cycleEdges.has(link.id) ? "#dc2626" : "#94a3b8")}
        linkWidth={(link) => (graphData.cycleEdges.has(link.id) ? 2.5 : 1.2)}
        cooldownTicks={80}
      />
    </div>
  );
}

export default GraphView;
