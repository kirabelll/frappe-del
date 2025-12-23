-- Direct Database Cleanup for Sales Invoices
-- WARNING: This will permanently delete ALL sales invoices and related data
-- BACKUP YOUR DATABASE BEFORE RUNNING THIS!

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- Delete Payment Entry References
DELETE FROM `tabPayment Entry Reference` 
WHERE reference_doctype = 'Sales Invoice';

-- Delete Payment Entries related to Sales Invoices
DELETE pe FROM `tabPayment Entry` pe
JOIN `tabPayment Entry Reference` per ON pe.name = per.parent
WHERE per.reference_doctype = 'Sales Invoice';


DELETE FROM `tabJournal Entry Account` 
WHERE reference_type = 'Sales Invoice';

-- Delete Journal Entries that only had Sales Invoice references
DELETE je FROM `tabJournal Entry` je
LEFT JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
WHERE jea.parent IS NULL;

-- Delete Delivery Notes linked to Sales Invoices
DELETE FROM `tabDelivery Note Item` 
WHERE against_sales_invoice IN (SELECT name FROM `tabSales Invoice`);

DELETE FROM `tabDelivery Note` 
WHERE name IN (
    SELECT DISTINCT parent FROM `tabDelivery Note Item` 
    WHERE against_sales_invoice IS NOT NULL
);

-- Delete Sales Invoice child tables
DELETE FROM `tabSales Invoice Item`;
DELETE FROM `tabSales Taxes and Charges` WHERE parenttype = 'Sales Invoice';
DELETE FROM `tabPayment Schedule` WHERE parenttype = 'Sales Invoice';
DELETE FROM `tabAdvance Taxes and Charges` WHERE parenttype = 'Sales Invoice';
DELETE FROM `tabSales Invoice Advance` WHERE parenttype = 'Sales Invoice';
DELETE FROM `tabSales Invoice Payment` WHERE parenttype = 'Sales Invoice';
DELETE FROM `tabPacked Item` WHERE parenttype = 'Sales Invoice';

-- Delete GL Entries for Sales Invoices
DELETE FROM `tabGL Entry` WHERE voucher_type = 'Sales Invoice';

-- Delete Stock Ledger Entries for Sales Invoices
DELETE FROM `tabStock Ledger Entry` WHERE voucher_type = 'Sales Invoice';

-- Delete Serial No entries
DELETE FROM `tabSerial No` WHERE warehouse IS NULL OR warehouse = '';

-- Delete Batch entries that might be orphaned
DELETE FROM `tabBatch` WHERE name NOT IN (
    SELECT DISTINCT batch_no FROM `tabStock Ledger Entry` WHERE batch_no IS NOT NULL
);

-- Finally, delete all Sales Invoices
DELETE FROM `tabSales Invoice`;

-- Clean up any remaining references in other tables
UPDATE `tabSales Order` SET per_billed = 0, billing_status = 'Not Billed' WHERE per_billed > 0;
UPDATE `tabDelivery Note` SET per_billed = 0, billing_status = 'Not Billed' WHERE per_billed > 0;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Reset naming series counter (optional)
DELETE FROM `tabSeries` WHERE name LIKE 'SINV%';

SELECT 'All Sales Invoices and related documents have been deleted!' as Result;