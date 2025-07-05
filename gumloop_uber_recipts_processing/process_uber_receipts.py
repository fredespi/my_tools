#!/usr/bin/env python3
"""
Uber Receipt Data Extractor

This script extracts cost, currency, date, and passenger information
from Uber receipt emails stored in JSON format and returns them as separate lists.

The script handles various formats including:
- Different currencies (kr, US$)
- Swedish date formats (converted to ISO format YYYY-MM-DD)
- Special cases like cancellation fees

Usage:
    dates, passengers, costs, currencies = main()
    
Or with custom input file:
    python process_uber_receipts.py [input_file]
    
Default input file: uber_data.json

Returns:
    Tuple of (dates, passenger_names, costs, currencies) as lists
"""

import re
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


def convert_swedish_date_to_iso(date_str: str) -> Optional[str]:
    """
    Convert Swedish date format to ISO format (YYYY-MM-DD)
    
    Args:
        date_str: Date string in Swedish format like "5 juli 2025"
        
    Returns:
        ISO formatted date string like "2025-07-05" or None if conversion fails
    """
    if not date_str:
        return None
    
    # Swedish month mapping
    swedish_months = {
        'januari': '01', 'februari': '02', 'mars': '03', 'april': '04',
        'maj': '05', 'juni': '06', 'juli': '07', 'augusti': '08',
        'september': '09', 'oktober': '10', 'november': '11', 'december': '12'
    }
    
    try:
        # Parse Swedish date format "DD MONTH YYYY"
        parts = date_str.strip().split()
        if len(parts) != 3:
            return None
            
        day = parts[0].zfill(2)  # Pad with zero if needed
        month_swedish = parts[1].lower()
        year = parts[2]
        
        if month_swedish in swedish_months:
            month = swedish_months[month_swedish]
            return f"{year}-{month}-{day}"
        else:
            return None
            
    except Exception:
        return None


def extract_uber_receipt_data(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract cost, currency, date, and passenger from Uber receipt emails.
    
    Args:
        email_data: Dictionary containing email data with 'body' field
        
    Returns:
        Dictionary with extracted 'cost', 'currency', 'date', and 'passenger'
    """
    body = email_data.get('body', '')
    
    # Initialize return values
    cost = None
    currency = None
    date_str = None
    passenger = None
    
    # Extract total cost and currency from the first "Totalt" occurrence
    # This handles both "kr" and "US$" currencies
    total_pattern = r'Totalt\s+([\d\.,]+)\s+([A-Za-z$€£]+)'
    total_match = re.search(total_pattern, body)
    
    if total_match:
        # Replace comma with period for consistent decimal handling
        cost_str = total_match.group(1).replace(',', '.')
        cost = float(cost_str)
        currency = total_match.group(2)
    
    # Extract date - look for date pattern after "Totalt" amount and before "Tack för att du reser"
    # This pattern captures Swedish date formats like "5 juli 2025", "7 februari 2025", etc.
    date_pattern = r'Totalt\s+[\d\.,]+\s+[A-Za-z$€£]+\s+([0-9]{1,2}\s+[a-zA-ZåäöÅÄÖ]+\s+[0-9]{4})'
    date_match = re.search(date_pattern, body)
    
    if date_match:
        date_str = date_match.group(1).strip()
        # Convert to ISO format
        date_str = convert_swedish_date_to_iso(date_str)
    
    # Extract passenger name from "Tack för att du reser, [Name]"
    passenger_pattern = r'Tack för att du reser,\s+([A-Za-zåäöÅÄÖ]+)'
    passenger_match = re.search(passenger_pattern, body)
    
    if passenger_match:
        passenger = passenger_match.group(1).strip()
    
    # Handle special cases like cancellation fees
    is_cancellation = 'Avbokningsavgift' in body
    
    return {
        'email_id': email_data.get('id'),
        'cost': cost,
        'currency': currency,
        'date': date_str,
        'passenger': passenger,
        'is_cancellation': is_cancellation,
        'subject': email_data.get('subject', ''),
        'email_date': email_data.get('date', '')
    }


def parse_uber_data_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse the uber_data.json file which contains multiple email objects
    separated by "Value #N:" headers.
    
    Args:
        file_path: Path to the input JSON file
        
    Returns:
        List of email data dictionaries
    """
    emails = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by "Value #" markers to separate individual emails
        # The first split might not start with "Value #" so we handle that
        parts = re.split(r'\n\nValue #\d+:\n\n', content)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            try:
                # Try to parse as JSON
                if part.startswith('{') and part.endswith('}'):
                    email_data = json.loads(part)
                    emails.append(email_data)
                else:
                    # Handle the first entry which might not have a "Value #" prefix
                    if '{' in part:
                        json_start = part.find('{')
                        json_part = part[json_start:]
                        if json_part.endswith('}'):
                            email_data = json.loads(json_part)
                            emails.append(email_data)
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse JSON in part: {e}")
                continue
                
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    return emails


def function(emails: List[Dict[str, Any]]) -> Tuple[List[str], List[str], List[float], List[str]]:
    """
    Extract Uber receipt data from email objects and return as separate lists.
    
    This is a standalone function that can be copied and used elsewhere.
    It extracts cost, currency, date (ISO format), and passenger information
    from Uber receipt emails.
    
    Args:
        emails: List of email data dictionaries, each containing:
                - 'body': Email body text containing receipt information
                - 'id': Email ID (optional, for error reporting)
    
    Returns:
        Tuple containing (dates, passenger_names, costs, currencies):
        - dates: List of ISO formatted dates (YYYY-MM-DD) or None for cancellations
        - passenger_names: List of passenger names or None for cancellations  
        - costs: List of numerical costs (float)
        - currencies: List of currency codes ('kr', 'US$', etc.)
        
        All lists are guaranteed to have the same length (validated)
    
    Raises:
        ValueError: If extracted lists have inconsistent lengths
    """
    
    def convert_swedish_date_to_iso(date_str: str) -> Optional[str]:
        """Convert Swedish date format to ISO format (YYYY-MM-DD)"""
        if not date_str:
            return None
        
        swedish_months = {
            'januari': '01', 'februari': '02', 'mars': '03', 'april': '04',
            'maj': '05', 'juni': '06', 'juli': '07', 'augusti': '08',
            'september': '09', 'oktober': '10', 'november': '11', 'december': '12'
        }
        
        try:
            parts = date_str.strip().split()
            if len(parts) != 3:
                return None
                
            day = parts[0].zfill(2)
            month_swedish = parts[1].lower()
            year = parts[2]
            
            if month_swedish in swedish_months:
                month = swedish_months[month_swedish]
                return f"{year}-{month}-{day}"
            else:
                return None
        except Exception:
            return None

    def extract_single_receipt(email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from a single email receipt"""
        body = email_data.get('body', '')
        
        # Initialize return values
        cost = None
        currency = None
        date_str = None
        passenger = None
        
        # Extract total cost and currency
        total_pattern = r'Totalt\s+([\d\.,]+)\s+([A-Za-z$€£]+)'
        total_match = re.search(total_pattern, body)
        
        if total_match:
            cost_str = total_match.group(1).replace(',', '.')
            cost = float(cost_str)
            currency = total_match.group(2)
        
        # Extract date
        date_pattern = r'Totalt\s+[\d\.,]+\s+[A-Za-z$€£]+\s+([0-9]{1,2}\s+[a-zA-ZåäöÅÄÖ]+\s+[0-9]{4})'
        date_match = re.search(date_pattern, body)
        
        if date_match:
            date_str = date_match.group(1).strip()
            date_str = convert_swedish_date_to_iso(date_str)
        
        # Extract passenger name
        passenger_pattern = r'Tack för att du reser,\s+([A-Za-zåäöÅÄÖ]+)'
        passenger_match = re.search(passenger_pattern, body)
        
        if passenger_match:
            passenger = passenger_match.group(1).strip()
        
        return {
            'cost': cost,
            'currency': currency,
            'date': date_str,
            'passenger': passenger
        }
    
    # Process all emails
    dates = []
    passenger_names = []
    costs = []
    currencies = []
    
    for email in emails:
        try:
            extracted = extract_single_receipt(email)
            
            # Only include successfully extracted data
            if extracted['cost'] is not None and extracted['currency'] is not None:
                dates.append(extracted['date'])
                passenger_names.append(extracted['passenger'])
                costs.append(extracted['cost'])
                currencies.append(extracted['currency'])
                
        except Exception:
            # Skip failed extractions silently
            continue
    
    # Validation: Ensure all lists have the same length
    list_lengths = [len(dates), len(passenger_names), len(costs), len(currencies)]
    if len(set(list_lengths)) != 1:
        raise ValueError(f"Inconsistent list lengths: dates={len(dates)}, "
                        f"passengers={len(passenger_names)}, costs={len(costs)}, "
                        f"currencies={len(currencies)}")
    
    return dates, passenger_names, costs, currencies


def process_all_emails(emails: List[Dict[str, Any]]) -> Tuple[List[str], List[str], List[float], List[str]]:
    """
    Process all emails and extract Uber receipt data (with verbose output)
    
    Args:
        emails: List of email data dictionaries
        
    Returns:
        Tuple containing (dates, passenger_names, costs, currencies)
        All lists are guaranteed to have the same length (validated)
    """
    dates = []
    passenger_names = []
    costs = []
    currencies = []
    
    for i, email in enumerate(emails, 1):
        try:
            extracted = extract_uber_receipt_data(email)
            
            # Only include successfully extracted data
            if extracted['cost'] is not None and extracted['currency'] is not None:
                dates.append(extracted['date'])  # May be None for cancellations
                passenger_names.append(extracted['passenger'])  # May be None for cancellations
                costs.append(extracted['cost'])
                currencies.append(extracted['currency'])
                
                # Print progress for verification
                print(f"Entry {i}: {extracted['cost']} {extracted['currency']} - "
                      f"{extracted['date']} - {extracted['passenger']}")
            else:
                print(f"Entry {i}: Could not extract data from email {extracted['email_id']}")
                
        except Exception as e:
            print(f"Error processing email {i}: {e}")
            continue
    
    # Validation step: Ensure all lists have the same length
    list_lengths = [len(dates), len(passenger_names), len(costs), len(currencies)]
    if len(set(list_lengths)) != 1:
        raise ValueError(f"Inconsistent list lengths: dates={len(dates)}, "
                        f"passengers={len(passenger_names)}, costs={len(costs)}, "
                        f"currencies={len(currencies)}")
    
    print(f"Validation passed: All lists have {len(costs)} elements")
    
    return dates, passenger_names, costs, currencies


def main():
    """Main function to process Uber receipts"""
    # Default file names
    input_file = "uber_data.json"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    print(f"Processing Uber receipts from: {input_file}")
    print("-" * 50)
    
    # Parse the input file
    emails = parse_uber_data_file(input_file)
    if not emails:
        print("No email data found or could not parse file.")
        return [], [], [], []
    
    print(f"Found {len(emails)} emails to process\n")
    
    # Use the standalone function for extraction
    try:
        dates, passenger_names, costs, currencies = function(emails)
        
        # Print processing results
        print(f"Successfully processed {len(costs)} entries")
        
        # Print summary statistics
        print(f"\nTotal entries processed: {len(costs)}")
        print(f"Data validation: All 4 lists contain {len(costs)} elements")
        
        if costs:
            total_cost_kr = sum(cost for cost, currency in zip(costs, currencies) if currency == 'kr')
            total_cost_usd = sum(cost for cost, currency in zip(costs, currencies) if currency == 'US$')
            
            print(f"Total cost in SEK: {total_cost_kr:.2f} kr")
            if total_cost_usd > 0:
                print(f"Total cost in USD: {total_cost_usd:.2f} US$")
            
            # Count rides per passenger (excluding None values)
            passengers = {}
            for passenger in passenger_names:
                if passenger:
                    passengers[passenger] = passengers.get(passenger, 0) + 1
            
            print("\nRides per passenger:")
            for passenger, count in sorted(passengers.items()):
                print(f"  {passenger}: {count} rides")
        
        return dates, passenger_names, costs, currencies
        
    except ValueError as e:
        print(f"Validation error: {e}")
        return [], [], [], []
    except Exception as e:
        print(f"Error processing emails: {e}")
        return [], [], [], []


if __name__ == "__main__":
    main()
