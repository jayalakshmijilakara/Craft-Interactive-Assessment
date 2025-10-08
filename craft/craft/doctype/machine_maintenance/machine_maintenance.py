# Copyright (c) 2025, Craft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, getdate

class MachineMaintenance(Document):
    def before_submit(self):
        if not self.technician:
            frappe.throw(_("Technician is required before submitting Machine Maintenance."))
        
        if self.status != 'Completed' and not self.completion_date:
            frappe.throw('Maintenance must be marked as completed with a completion date before submission.')

    def on_submit(self):
        create_maintenance_journal_entry(self)



def create_maintenance_journal_entry(doc):
    cost = flt(doc.cost)

    if cost <= 0:
        frappe.throw(_("Maintenance cost must be greater than zero to create Journal Entry."))

    company = doc.get("company") or frappe.defaults.get_global_default("company")
    if not company:
        frappe.throw(_("Company not set on Machine Maintenance."))

    company_currency = frappe.db.get_value("Company", company, "default_currency")
    doc_currency = getattr(doc, "currency", None) or company_currency

    rate = 1.0
    if doc_currency != company_currency:
        from frappe.utils import get_exchange_rate
        rate = get_exchange_rate(doc_currency, company_currency, doc.get("completion_date") or nowdate()) or 1.0

    amount_company_currency = flt(cost) * flt(rate)

   
    if amount_company_currency <= 0:
        frappe.throw(_("Invalid converted amount. Please check maintenance cost or exchange rate."))

    maintenance_expense_account = frappe.db.get_value("Company", company, "custom_default_maintenance_expense_account")
    cash_account = frappe.db.get_value("Company", company, "default_cash_account")

    if not maintenance_expense_account or not cash_account:
        frappe.throw(_("Please configure both Maintenance Expense and Cash/Bank accounts in Company."))

    
    if not (flt(amount_company_currency) > 0):
        frappe.throw(_("Journal Entry amount cannot be zero."))

    je = frappe.new_doc("Journal Entry")
    je.company = company
    je.posting_date = doc.get("completion_date") or nowdate()
    je.voucher_type = "Journal Entry"
    je.user_remark = _("Auto JE for Machine Maintenance {0}").format(doc.name)

    je.append("accounts", {
        "account": maintenance_expense_account,
        "debit_in_account_currency": amount_company_currency,
        "credit_in_account_currency": 0
    })
    je.append("accounts", {
        "account": cash_account,
        "debit_in_account_currency": 0,
        "credit_in_account_currency": amount_company_currency
    })


    # print(
    #     f"\n=== DEBUG: Machine Maintenance JE ===\n"
    #     f"Cost: {doc.cost}\n"
    #     f"Amount (Company Currency): {amount_company_currency}\n"
    #     f"Maintenance Account: {maintenance_expense_account}\n"
    #     f"Cash Account: {cash_account}\n"
    #     f"Exchange Rate: {rate}\n"
    #     "====================================\n"
    # )

    je.insert(ignore_permissions=True)
    je.submit()

    

    doc.db_set("journal_entry", je.name)
    frappe.msgprint(_("Journal Entry {0} has been created for Maintenance {1} (Total Amount: {2}).").format(je.name, doc.name, amount_company_currency))

