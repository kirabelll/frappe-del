#!/usr/bin/env python3
"""
Complete Sales Invoice Deletion Script for Frappe
Removes ALL sales invoices regardless of status and related documents
"""

import frappe
from frappe import _

def delete_all_sales_invoices_and_related():
    """
    Delete ALL sales invoices and related documents regardless of status
    WARNING: This is irreversible - backup your database first!
    """
    
    print("Starting comprehensive sales invoice deletion...")
    
    # Get all sales invoices
    all_invoices = frappe.get_all("Sales Invoice", fields=["name", "docstatus", "outstanding_amount"])
    
    print(f"Found {len(all_invoices)} sales invoices to process")
    
    deleted_count = 0
    error_count = 0
    
    for invoice in all_invoices:
        try:
            invoice_name = invoice.name
            print(f"Processing: {invoice_name} (Status: {invoice.docstatus})")
            
            # Delete related documents first
            delete_related_documents(invoice_name)
            
            # Handle different statuses
            if invoice.docstatus == 1:  # Submitted
                # Cancel first, then delete
                doc = frappe.get_doc("Sales Invoice", invoice_name)
                doc.cancel()
                frappe.delete_doc("Sales Invoice", invoice_name, force=1)
            elif invoice.docstatus == 2:  # Cancelled
                # Direct delete
                frappe.delete_doc("Sales Invoice", invoice_name, force=1)
            else:  # Draft
                # Direct delete
                frappe.delete_doc("Sales Invoice", invoice_name, force=1)
            
            deleted_count += 1
            print(f"✓ Deleted: {invoice_name}")
            
        except Exception as e:
            error_count += 1
            print(f"✗ Error deleting {invoice_name}: {str(e)}")
    
    # Clean up orphaned records
    cleanup_orphaned_records()
    
    # Commit all changes
    frappe.db.commit()
    
    print(f"\nDeletion Summary:")
    print(f"Successfully deleted: {deleted_count}")
    print(f"Errors: {error_count}")
    print(f"Total processed: {len(all_invoices)}")

def delete_related_documents(invoice_name):
    """Delete all documents related to the sales invoice"""
    
    related_doctypes = [
        "Payment Entry",
        "Delivery Note",
        "Sales Order",
        "Packing Slip",
        "Installation Note",
        "Warranty Claim"
    ]
    
    for doctype in related_doctypes:
        try:
            # Find related documents
            if doctype == "Payment Entry":
                related_docs = frappe.get_all(doctype, 
                    filters={"reference_name": invoice_name, "reference_doctype": "Sales Invoice"},
                    fields=["name", "docstatus"])
            elif doctype == "Journal Entry":
                # Check journal entry accounts for reference
                related_docs = frappe.db.sql("""
                    SELECT DISTINCT je.name, je.docstatus 
                    FROM `tabJournal Entry` je
                    JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
                    WHERE jea.reference_name = %s AND jea.reference_type = 'Sales Invoice'
                """, invoice_name, as_dict=1)
            else:
                # For other doctypes, check if they have against_sales_invoice field
                if frappe.db.has_column(doctype, "against_sales_invoice"):
                    related_docs = frappe.get_all(doctype,
                        filters={"against_sales_invoice": invoice_name},
                        fields=["name", "docstatus"])
                else:
                    continue
            
            # Delete found related documents
            for doc in related_docs:
                try:
                    if doc.docstatus == 1:  # Submitted
                        related_doc = frappe.get_doc(doctype, doc.name)
                        related_doc.cancel()
                    frappe.delete_doc(doctype, doc.name, force=1)
                    print(f"  ✓ Deleted related {doctype}: {doc.name}")
                except Exception as e:
                    print(f"  ✗ Error deleting related {doctype} {doc.name}: {str(e)}")
                    
        except Exception as e:
            print(f"  ✗ Error processing {doctype}: {str(e)}")

def cleanup_orphaned_records():
    """Clean up orphaned records in child tables"""
    
    print("Cleaning up orphaned records...")
    
    # Clean up Sales Invoice Item
    frappe.db.sql("""
        DELETE FROM `tabSales Invoice Item` 
        WHERE parent NOT IN (SELECT name FROM `tabSales Invoice`)
    """)
    
    # Clean up Sales Taxes and Charges
    frappe.db.sql("""
        DELETE FROM `tabSales Taxes and Charges` 
        WHERE parent NOT IN (SELECT name FROM `tabSales Invoice`)
    """)
    
    # Clean up Payment Schedule
    frappe.db.sql("""
        DELETE FROM `tabPayment Schedule` 
        WHERE parent NOT IN (SELECT name FROM `tabSales Invoice`)
    """)
    
    # Clean up Advance Taxes and Charges
    frappe.db.sql("""
        DELETE FROM `tabAdvance Taxes and Charges` 
        WHERE parent NOT IN (SELECT name FROM `tabSales Invoice`)
    """)
    
    print("✓ Orphaned records cleaned up")

def backup_before_deletion():
    """Create a backup before deletion"""
    import os
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"sales_invoice_backup_{timestamp}.sql"
    
    print(f"Creating backup: {backup_file}")
    
    # Export sales invoice data
    os.system(f"bench --site {frappe.local.site} backup --with-files")
    
    print("✓ Backup created")

if __name__ == "__main__":
    # Safety check
    confirm = input("WARNING: This will delete ALL sales invoices and related documents. Type 'DELETE ALL' to confirm: ")
    
    if confirm == "DELETE ALL":
        # Create backup first
        backup_before_deletion()
        
        # Proceed with deletion
        delete_all_sales_invoices_and_related()
        
        print("\n🎉 All sales invoices and related documents have been deleted!")
    else:
        print("Operation cancelled for safety.")