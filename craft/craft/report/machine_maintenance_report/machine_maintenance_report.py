# Copyright (c) 2025, Craft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data, None, None, get_report_summary(filters)


def get_columns(filters):
    if filters.get('consolidated'):
        return [
            {"fieldname": "machine_name", "label": "Machine Name", "fieldtype": "Data", "width": 200},
            {"fieldname": "maintenance_date", "label": "Maintenance Date", "fieldtype": "Date", "width": 180},
            {"fieldname": "cost", "label": "Total Cost", "fieldtype": "Currency", "width": 160},
        ]
    else:
        return [
            {"fieldname": "name", "label": "ID", "fieldtype": "Data", "width": 150},
            {"fieldname": "machine_name", "label": "Machine Name", "fieldtype": "Data", "width": 200},
            {"fieldname": "maintenance_date", "label": "Maintenance Date", "fieldtype": "Date", "width": 180},
            {"fieldname": "technician", "label": "Technician", "fieldtype": "Link", "options": "Employee", "width": 150},
            {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 130},
            {"fieldname": "cost", "label": "Total Cost", "fieldtype": "Currency", "width": 160},
        ]


def get_data(filters):
    conditions = []
    params = {}

    if filters.get('machine_name'):
        conditions.append("machine_name = %(machine_name)s")
        params['machine_name'] = filters.get('machine_name')
    if filters.get('technician'):
        conditions.append("technician = %(technician)s")
        params['technician'] = filters.get('technician')
    if filters.get('from_date'):
        conditions.append("maintenance_date >= %(from_date)s")
        params['from_date'] = filters.get('from_date')
    if filters.get('to_date'):
        conditions.append("maintenance_date <= %(to_date)s")
        params['to_date'] = filters.get('to_date')

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    if filters.get('consolidated'):
        query = f"""
            SELECT 
                machine_name,
                MIN(maintenance_date) AS maintenance_date,
                SUM(cost) AS cost
            FROM `tabMachine Maintenance`
            WHERE {where_clause}
            GROUP BY machine_name
            ORDER BY SUM(cost) DESC
        """
    else:
        query = f"""
            SELECT 
                name,
                machine_name,
                maintenance_date,
                technician,
                status,
                cost
            FROM `tabMachine Maintenance`
            WHERE {where_clause}
            ORDER BY maintenance_date DESC
        """

    return frappe.db.sql(query, params, as_dict=True)


def get_report_summary(filters):
    if filters.get('consolidated'):
        return
    else:

        conditions = []
        params = {}

        if filters.get('machine_name'):
            conditions.append("machine_name = %(machine_name)s")
            params['machine_name'] = filters.get('machine_name')
        if filters.get('technician'):
            conditions.append("technician = %(technician)s")
            params['technician'] = filters.get('technician')
        if filters.get('from_date'):
            conditions.append("maintenance_date >= %(from_date)s")
            params['from_date'] = filters.get('from_date')
        if filters.get('to_date'):
            conditions.append("maintenance_date <= %(to_date)s")
            params['to_date'] = filters.get('to_date')

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        summary_query = f"""
            SELECT 
                status, COUNT(name) AS count
            FROM `tabMachine Maintenance`
            WHERE {where_clause}
            GROUP BY status
        """

        result = frappe.db.sql(summary_query, params, as_dict=True)
        status_counts = {r['status']: r['count'] for r in result}

        return [
            {
                "label": "Scheduled",
                "value": status_counts.get("Scheduled", 0),
                "indicator": "orange"
            },
            {
                "label": "Completed",
                "value": status_counts.get("Completed", 0),
                "indicator": "green"
            },
            {
                "label": "Overdue",
                "value": status_counts.get("Overdue", 0),
                "indicator": "red"
            }
        ]
