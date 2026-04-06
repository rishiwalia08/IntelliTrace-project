import { useEffect, useState } from "react";

import { invoiceApi } from "../services/api";

function getRiskLevel(score) {
  if (score <= 30) {
    return "LOW";
  }
  if (score <= 70) {
    return "MEDIUM";
  }
  return "HIGH";
}

function normalizeInvoice(invoice) {
  const score = Number(invoice?.risk_assessment?.score ?? 0);
  const risk = invoice?.risk_assessment?.risk ?? getRiskLevel(score);

  return {
    ...invoice,
    risk_assessment: {
      score,
      risk,
      reasons: invoice?.risk_assessment?.reasons || ["No risk explanation available yet."],
      flags: {
        cycle: Boolean(invoice?.risk_assessment?.flags?.cycle),
        duplicate: Boolean(invoice?.risk_assessment?.flags?.duplicate),
        velocity: Boolean(invoice?.risk_assessment?.flags?.velocity),
        high_frequency: Boolean(invoice?.risk_assessment?.flags?.high_frequency),
        hub: Boolean(invoice?.risk_assessment?.flags?.hub),
      },
    },
  };
}

function buildAlerts(invoices) {
  const alerts = [];

  invoices.forEach((invoice) => {
    const score = Number(invoice.risk_assessment?.score || 0);
    const risk = invoice.risk_assessment?.risk;
    if (risk === "HIGH") {
      alerts.push({
        id: `${invoice.id}-high-risk`,
        message: `HIGH RISK: ${invoice.invoice_id} (Score: ${score})`,
      });
    }

    if (invoice.risk_assessment?.flags?.cycle) {
      alerts.push({
        id: `${invoice.id}-cycle`,
        message: `CYCLE DETECTED: ${invoice.invoice_id} (${invoice.supplier_id} → ${invoice.buyer_id})`,
      });
    }
  });

  return alerts;
}

function useInvoices() {
  const [invoices, setInvoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    const fetchInvoices = async () => {
      try {
        const response = await invoiceApi.getInvoices();
        if (active) {
          setInvoices((response || []).map(normalizeInvoice));
        }
      } catch (error) {
        setError(error);
        console.error("Failed to load invoices", error);
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    fetchInvoices();

    return () => {
      active = false;
    };
  }, []);

  const alerts = buildAlerts(invoices);

  return { invoices, isLoading, error, alerts };
}

export default useInvoices;
