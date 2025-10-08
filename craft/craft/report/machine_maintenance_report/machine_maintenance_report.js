frappe.query_reports["Machine Maintenance Report"] = {
    "filters": [
        {
            "fieldname": "machine_name",
            "label": "Machine",
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0
        },
        {
            "fieldname": "technician",
            "label": "Technician",
            "fieldtype": "Link",
            "options": "Employee",
            "reqd": 0
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "consolidated",
            "label": "Consolidated",
            "fieldtype": "Check",
            "default": 0
        },
        {
            "fieldname": "chart_type",
            "label": "Chart Type",
            "fieldtype": "Select",
            "options": ["Pie", "Bar"],
            "default": "Pie"
        }
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (column.fieldname === "status" && data && data.status) {
            let color = "";
            if (data.status === "Overdue") color = "color:#ff4d4d;";
            else if (data.status === "Scheduled") color = "color:#ffe066;";
            else if (data.status === "Completed") color = "color:#33cc33;";
            return `<div style="${color}; padding:4px; border-radius:4px;">${value}</div>`;
        }
        return value;
    }
};
