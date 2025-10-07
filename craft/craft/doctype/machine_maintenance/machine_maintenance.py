# Copyright (c) 2025, Craft and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class MachineMaintenance(Document):
# 	pass




# machine_maintenance.py
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, getdate

class MachineMaintenance(Document):
   

    def before_submit(self):
        if not self.technician:
            frappe.throw(_("Technician is required before submitting Machine Maintenance."))

    def on_submit(self):
        create_maintenance_journal_entry(self)

def create_maintenance_journal_entry(doc):
    """
    Creates and submits a Journal Entry for the maintenance cost.
    - Debits: Maintenance Expense account
    - Credits: Cash/Bank account
    - Converts doc.cost from doc.currency -> company currency if needed
    """
    # Skip if zero cost
    if flt(doc.cost) <= 0:
        frappe.log_error(_("Maintenance cost is zero; skipping JE creation for {0}").format(doc.name), "Machine Maintenance: zero cost")
        return

    # Prevent duplicate JE creation
    if getattr(doc, "journal_entry", None):
        frappe.log("Journal Entry already exists for {0}: {1}".format(doc.name, doc.journal_entry))
        return

    # Resolve company
    company = doc.get("company") or frappe.defaults.get_global_default("company")
    if not company:
        frappe.throw(_("Company not set on Machine Maintenance and no default company found."))

    # company currency
    company_currency = frappe.db.get_value("Company", company, "default_currency") or frappe.db.get_value("Global Defaults", "Global Defaults", "default_currency")
    # doc currency (if present on the document), else assume company currency
    doc_currency = getattr(doc, "currency", None) or company_currency

    # Determine exchange rate (doc_currency -> company_currency)
    rate = 1.0
    if doc_currency and company_currency and doc_currency != company_currency:
        # try frappe util
        try:
            from frappe.utils import get_exchange_rate
            rate = get_exchange_rate(doc_currency, company_currency, doc.get("completion_date") or nowdate()) or 1.0
        except Exception:
            # fallback: Currency Exchange table
            rate = frappe.db.get_value("Currency Exchange",
                                       {"from_currency": doc_currency, "to_currency": company_currency},
                                       "exchange_rate") or 1.0

    # amount in company currency
    amount_company_currency = flt(doc.cost) * flt(rate)

    # get account names: first from Company, then fallback to single Settings doctype 'Machine Maintenance Settings'
    maintenance_expense_account = frappe.db.get_value("Company", company, "custom_default_maintenance_expense_account")
    cash_account = frappe.db.get_value("Company", company, "default_cash_account")

    if not maintenance_expense_account or not cash_account:
        # fallback to Machine Maintenance Settings single doctype
        maintenance_expense_account = maintenance_expense_account 
        cash_account = cash_account 

    if not maintenance_expense_account or not cash_account:
        frappe.throw(_("Please configure Maintenance Expense and Cash/Bank accounts either in Company"))

    # Build Journal Entry
    je = frappe.new_doc("Journal Entry")
    je.company = company
    je.posting_date = doc.get("completion_date") or nowdate()
    je.title = _("Maintenance: {0}").format(doc.name)
    je.voucher_type = "Journal Entry"
    je.set_posting_time = 1
    je.user_remark = _("Auto JE for Machine Maintenance {0}").format(doc.name)

    # Debit - Maintenance Expense
    je.append("accounts", {
        "account": maintenance_expense_account,
        "debit": amount_company_currency,
        "credit": 0.0
    })

    # Credit - Cash/Bank
    je.append("accounts", {
        "account": cash_account,
        "debit": 0.0,
        "credit": amount_company_currency
    })

    try:
        je.insert(ignore_permissions=True)
        je.submit()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Machine Maintenance: JE Creation Failed")
        frappe.throw(_("Failed to create Journal Entry for {0}: {1}").format(doc.name, e))

    doc.db_set("journal_entry", je.name)
    frappe.msgprint(_("Journal Entry {0} created for maintenance {1} (Amount: {2} {3})").format(je.name, doc.name, amount_company_currency, company_currency))
