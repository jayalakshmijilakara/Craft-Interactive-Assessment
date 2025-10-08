# Copyright (c) 2025, Craft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns(filters)
    data = get_data(filters)
    
    chart = get_report_chart(filters)  
    return columns, data, None, chart


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

def get_report_chart(filters):
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

    chart_type = (filters.get("chart_type") or "Pie").lower()

    if chart_type == "pie":
      
        query = f"""
            SELECT status, COUNT(name) AS count
            FROM `tabMachine Maintenance`
            WHERE {where_clause}
            GROUP BY status
        """
        data = frappe.db.sql(query, params, as_dict=True)

        return {
            "data": {
                "labels": [d['status'] for d in data],
                "datasets": [{"values": [d['count'] for d in data]}]
            },
            "type": "pie",
            "title": "Maintenance Status Distribution"
        }

    else:
       
        query = f"""
            SELECT 
                DATE_FORMAT(maintenance_date, '%%Y-%%m-%%d') AS day,
                SUM(cost) AS total_cost
            FROM `tabMachine Maintenance`
            WHERE {where_clause}
            GROUP BY day
            ORDER BY day
        """
        data = frappe.db.sql(query, params, as_dict=True)

        return {
            "data": {
                "labels": [d['day'] for d in data],
                "datasets": [{
                    "name": "Daily Maintenance Cost",
                    "values": [d['total_cost'] for d in data]
                }]
            },
            "type": "bar",
            "title": "Daily Maintenance Cost"
        }
