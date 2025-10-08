// Copyright (c) 2025, Craft and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Machine Maintenance", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on('Machine Maintenance', {
    
    // Calculating rate and quantity, then assigning the result to the amount field
    // Assigning the total amount to the cost field

	validate: function(frm) {
		let sum = 0;

		if (Array.isArray(frm.doc.machine_maintenance_part)) {
			frm.doc.machine_maintenance_part.forEach(row => {
				if (row.quantity && row.rate) {
					row.amount = (row.quantity || 1) * (row.rate || 0);
					sum += row.amount;
				}
			});

			frm.set_value('cost', sum);
			frm.refresh_field('machine_maintenance_part');
		}
	},

    // Displaying field based on the document's status

    status: function(frm) {
        toggle_notes_visibility(frm);
    },

    // Adding a button to complete the document, assign the completion date, and submit it
    // If the maintenance date is earlier than today and the status is not 'Completed', mark the document status as overdue

    refresh: function(frm) {
		toggle_notes_visibility(frm);

		if (frm.doc.docstatus === 0 && frm.doc.status !== 'Completed') {
			frm.add_custom_button(__('Mark Completed'), function () {
				frappe.confirm(__('Mark this maintenance as completed?'), function () {
					frm.set_value('status', 'Completed');
					frm.set_value('completion_date', frappe.datetime.get_today());
                    frm.save();
				});
			});
		}

		if (frm.doc.maintenance_date && frm.doc.status !== 'Completed') {
			const mdate = frm.doc.maintenance_date;
			const today = frappe.datetime.get_today();

			if (frappe.datetime.get_diff(today, mdate) > 0 && frm.doc.status !== 'Overdue') {
				frm.set_value('status', 'Overdue');
				frappe.show_alert(__('Status set to Overdue'));
			}
		}
	},

	onload: function(frm) {
        frappe.db.get_single_value('Global Defaults', 'default_company')
            .then(company => {
                frm.set_value('company', company);
            });
    }

});




function toggle_notes_visibility(frm) {
    if(frm.doc.status === 'Scheduled') {
        frm.toggle_display('notes', false);
    } else {
        frm.toggle_display('notes', true);
    }
}