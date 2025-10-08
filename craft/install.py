import frappe

def after_install():
    company_name = get_default_company()
    company = frappe.get_doc("Company", company_name)
    abbr = company.abbr 

    expense_parent = frappe.db.get_value(
        "Account",
        {"company": company_name, "root_type": "Expense", "is_group": 1},
        "name"
    )
    cash_parent = frappe.db.get_value(
        "Account",
        {"company": company_name, "root_type": "Asset", "is_group": 1},
        "name"
    )

    if not expense_parent:
        frappe.throw(f"No Expense parent account found for company {company_name}")

    if not cash_parent:
        frappe.throw(f"No Asset parent account found for company {company_name}")

    # --- Maintenance Expense Account ---
    maint_acc_name = f"Maintenance Expense Account - {abbr}"
    if not frappe.db.exists("Account", {"name": maint_acc_name, "company": company_name}):
        maintenance_account = frappe.get_doc({
            "doctype": "Account",
            "account_name": "Maintenance Expense Account",
            "parent_account": expense_parent,
            "account_type": "Expense Account",
            "root_type": "Expense",
            "company": company_name,
            "is_group": 0
        })
        maintenance_account.insert(ignore_permissions=True)
    else:
        maintenance_account = frappe.get_doc("Account", maint_acc_name)

    # --- Cash/Bank Account ---
    cash_acc_name = f"Cash/Bank Account - {abbr}"
    if not frappe.db.exists("Account", {"name": cash_acc_name, "company": company_name}):
        cash_account = frappe.get_doc({
            "doctype": "Account",
            "account_name": "Cash/Bank Account",
            "parent_account": cash_parent,
            "account_type": "Cash",
            "root_type": "Asset",
            "company": company_name,
            "is_group": 0
        })
        cash_account.insert(ignore_permissions=True)
    else:
        cash_account = frappe.get_doc("Account", cash_acc_name)

    company.custom_default_maintenance_expense_account = maintenance_account.name
    company.default_cash_account = cash_account.name
    company.save(ignore_permissions=True)

    frappe.db.commit()
    frappe.logger().info(f"Accounts created and linked for {company_name}")

def get_default_company():
    """Return the default company name"""
    company = frappe.db.get_default("company")
    if not company:
        company = frappe.db.get_value("Company", {}, "name")
    return company
