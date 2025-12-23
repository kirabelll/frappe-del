#!/bin/bash

# Sales Invoice Complete Deletion Script
# This script provides multiple methods to delete all sales invoices

echo "Sales Invoice Deletion Methods"
echo "=============================="
echo "1. Python Script (Recommended - handles all edge cases)"
echo "2. Direct Database (Fastest - requires database access)"
echo "3. Bench Console (Interactive)"
echo ""

read -p "Choose method (1-3): " method

case $method in
    1)
        echo "Running Python deletion script..."
        bench --site frappe.com console < delete_all_sales_invoices.py
        ;;
    2)
        echo "WARNING: This will directly modify the database!"
        read -p "Enter your database name: " db_name
        read -p "Enter your database user: " db_user
        read -s -p "Enter your database password: " db_pass
        echo ""
        
        # Create backup first
        echo "Creating backup..."
        mysqldump -u $db_user -p$db_pass $db_name > backup_before_deletion_$(date +%Y%m%d_%H%M%S).sql
        
        # Run deletion
        echo "Running database cleanup..."
        mysql -u $db_user -p$db_pass $db_name < direct_database_cleanup.sql
        ;;
    3)
        echo "Opening bench console..."
        echo "Copy and paste the following commands:"
        echo ""
        echo "import frappe"
        echo "exec(open('delete_all_sales_invoices.py').read())"
        echo ""
        bench --site frappe.com console
        ;;
    *)
        echo "Invalid option"
        ;;
esac