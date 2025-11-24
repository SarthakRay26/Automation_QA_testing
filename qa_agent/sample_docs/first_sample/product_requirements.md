# E-Commerce Checkout Feature Requirements

## Overview
The checkout page allows users to complete their purchase by entering payment and shipping information.

## Features

### 1. Discount Code Functionality
- Users can enter discount codes in the checkout form
- Valid codes: SAVE10, SAVE15, SAVE20
- SAVE10: 10% off total price
- SAVE15: 15% off total price
- SAVE20: 20% off total price
- Invalid codes should display error message: "Invalid discount code"

### 2. Payment Information
- Users must provide:
  - Credit card number (16 digits)
  - Expiration date (MM/YY format)
  - CVV (3 digits)
  - Cardholder name

### 3. Shipping Information
- Required fields:
  - Full name
  - Street address
  - City
  - State/Province
  - Postal code
  - Country

### 4. Order Summary
- Display:
  - Item list with prices
  - Subtotal
  - Discount amount (if applicable)
  - Shipping cost
  - Tax
  - Grand total

## Validation Rules
- All fields marked with * are required
- Email must be in valid format
- Credit card must pass Luhn algorithm
- Postal code must match selected country format
- Phone number must be 10 digits minimum

## Error Handling
- Display field-specific error messages
- Highlight invalid fields in red
- Prevent form submission if validation fails
- Show loading spinner during payment processing

## Success Criteria
- Successful payment shows confirmation page
- Order number is generated and displayed
- Confirmation email is sent to user
- Payment amount matches displayed total
