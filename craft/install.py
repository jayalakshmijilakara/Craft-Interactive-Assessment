import frappe

def after_install():
    # Create Maintenance Expense Account
    if not frappe.db.exists("Account", {"account_name": "Maintenance Expense Account"}):
        maintenance_account = frappe.get_doc({
            "doctype": "Account",
            "account_name": "Maintenance Expense Account",
            "account_type": "Expense Account",
            "root_type": "Expense",
            "company": get_default_company(),
            "is_group": 0
        })
        maintenance_account.insert(ignore_permissions=True)
    else:
        maintenance_account = frappe.get_doc("Account", {"account_name": "Maintenance Expense Account"})

    # Create Cash/Bank Account
    if not frappe.db.exists("Account", {"account_name": "Cash/Bank Account"}):
        cash_account = frappe.get_doc({
            "doctype": "Account",
            "account_name": "Cash/Bank Account",
            "account_type": "Cash",
            "root_type": "Asset",
            "company": get_default_company(),
            "is_group": 0
        })
        cash_account.insert(ignore_permissions=True)
    else:
        cash_account = frappe.get_doc("Account", {"account_name": "Cash/Bank Account"})

    # Assign to Company Doctype
    company = frappe.get_doc("Company", get_default_company())
    company.custom_default_maintenance_expense_account = maintenance_account.name
    company.default_cash_account = cash_account.name
    company.save(ignore_permissions=True)

    frappe.db.commit()
    frappe.logger().info("Default accounts created and linked to Company")

def get_default_company():
    """Return the first company or default one"""
    company = frappe.db.get_default("company")
    if not company:
        company = frappe.db.get_value("Company", {}, "name")
    return company
