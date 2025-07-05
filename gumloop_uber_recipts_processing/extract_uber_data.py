#!/usr/bin/env python3
"""
Uber Receipt Data Extractor - Standalone Function

A clean, single function that can be copied into any project to extract
cost, currency, date, and passenger information from Uber receipt emails.

Usage:
    dates, passengers, costs, currencies = extract_uber_data(emails)

Where `emails` is a list of dictionaries, each containing a 'body' field
with the Uber receipt text.
"""

import re
from typing import Dict, Any, List, Optional, Tuple


def extract_uber_data(emails):
    """
    Extract Uber receipt data from email objects and return as separate lists.
    
    This is a standalone function that can be copied and used elsewhere.
    It extracts cost, currency, date (ISO format), and passenger information
    from Uber receipt emails.
    
    Args:
        emails: Can be one of:
               - List of email data dictionaries
               - List of JSON strings representing email data
               - A JSON string representing a list of emails
               - A string containing multiple JSON objects
               Each email should contain a 'body' field with receipt text
    
    Returns:
        Tuple containing (dates, passenger_names, costs, currencies):
        - dates: List of ISO formatted dates (YYYY-MM-DD)
        - passenger_names: List of passenger names
        - costs: List of numerical costs (float)
        - currencies: List of currency codes ('kr', 'US$', etc.)
        
        All lists are guaranteed to have the same length (validated)
    
    Raises:
        ValueError: If extracted lists have inconsistent lengths
    """
    import json  # Import here for standalone function
    import re  # Import here for the nested functions
    
    # Handle case where emails is a string (JSON or text with embedded JSON)
    if isinstance(emails, str):
        parsed_emails = []
        try:
            # Try to parse as a JSON array or object first
            try:
                parsed_emails = json.loads(emails)
                if not isinstance(parsed_emails, list):
                    parsed_emails = [parsed_emails]
            except json.JSONDecodeError:
                # If that fails, split by "Value #n:" markers and parse each part
                parts = re.split(r'\n\nValue #\d+:\n\n', emails)
                
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                        
                    try:
                        if part.startswith('{') and part.endswith('}'):
                            email_data = json.loads(part)
                            parsed_emails.append(email_data)
                        elif '{' in part:
                            json_start = part.find('{')
                            json_part = part[json_start:]
                            if json_part.endswith('}'):
                                email_data = json.loads(json_part)
                                parsed_emails.append(email_data)
                    except json.JSONDecodeError:
                        continue
            
            emails = parsed_emails
        except Exception as e:
            # If all parsing fails, wrap in a more helpful error
            raise ValueError(f"Failed to parse emails data: {str(e)}")
    
    # Inner helper function for date conversion
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

    # Inner helper function to extract data from a single email
    def extract_receipt_from_email(email_data):
        """Extract data from a single email receipt"""
        # Handle JSON string if provided instead of dict
        if isinstance(email_data, str):
            try:
                email_data = json.loads(email_data)
            except json.JSONDecodeError:
                return {'cost': None, 'currency': None, 'date': None, 'passenger': None}
        
        body = email_data.get('body', '')
        
        # Initialize return values
        cost = None
        currency = None
        date_str = None
        passenger = None
        
        # Extract total cost and currency
        # Look for either "Totalt" or "Avbokningsavgift" (cancellation fee)
        total_pattern = r'(Totalt|Avbokningsavgift)\s+([\d\.,]+)\s+([A-Za-z$€£]+)'
        total_match = re.search(total_pattern, body)
        
        if total_match:
            cost_str = total_match.group(2).replace(',', '.')
            cost = float(cost_str)
            currency = total_match.group(3)
        else:
            # Try a more relaxed pattern
            total_pattern2 = r'(\d+[\.,]?\d*)\s*([A-Za-z$€£]+)'
            total_match2 = re.search(total_pattern2, body)
            if total_match2:
                cost_str = total_match2.group(1).replace(',', '.')
                cost = float(cost_str)
                currency = total_match2.group(2)
        
        # Extract date - look after either "Totalt" or "Avbokningsavgift"
        date_pattern = r'(Totalt|Avbokningsavgift)\s+[\d\.,]+\s+[A-Za-z$€£]+\s+(\d{1,2}\s+[a-zA-ZåäöÅÄÖ]+\s+\d{4})'
        date_match = re.search(date_pattern, body)
        
        if date_match:
            date_str = date_match.group(2).strip()
            date_str = convert_swedish_date_to_iso(date_str)
        else:
            # Try a more general pattern to find date anywhere in the text
            general_date_pattern = r'(\d{1,2}\s+[a-zA-ZåäöÅÄÖ]+\s+\d{4})'
            general_date_match = re.search(general_date_pattern, body)
            if general_date_match:
                date_str = general_date_match.group(1).strip()
                date_str = convert_swedish_date_to_iso(date_str)
        
        # Define known family member names - extracted from the real uber_data.json
        family_members = {'Fredrik', 'Viggo', 'Agne', 'Giedre', 'Nadine', 'Leona'}
        
        # First try the most reliable pattern: "Tack för att du reser, X" or "Vi ses en annan gång, X"
        passenger_pattern = r'(Tack för att du reser,|Vi ses en annan gång,)\s+([A-Za-zåäöÅÄÖ]+)'
        passenger_match = re.search(passenger_pattern, body)
        
        if passenger_match:
            candidate_name = passenger_match.group(2).strip()
            # Check if it's a known family member
            if candidate_name in family_members:
                passenger = candidate_name
            else:
                # Unknown name - still use it but could be flagged for review
                passenger = candidate_name
        else:
            # If that fails, try other patterns with the known family member names
            passenger = None
            for name in family_members:
                name_patterns = [
                    fr'Tack\s+{name}!',
                    fr'{name}s\s+(?:resa|tur)',
                    fr'(?:reser|åker|färd|resa).*?,\s+{name}'
                ]
                
                for pattern in name_patterns:
                    if re.search(pattern, body):
                        passenger = name
                        break
                
                if passenger:
                    break
                    
            # If still no match, try other general patterns
            if not passenger:
                general_patterns = [
                    r'Tack\s+([A-Za-zåäöÅÄÖ]+)!',
                    r'(?:reser|åker|färd|resa).*?,\s+([A-Za-zåäöÅÄÖ]+)',
                    r'([A-Za-zåäöÅÄÖ]+)s\s+(?:resa|tur)'
                ]
                
                for pattern in general_patterns:
                    match = re.search(pattern, body)
                    if match:
                        candidate = match.group(1).strip()
                        # Check if the extracted name is in our family members list
                        for member in family_members:
                            if candidate.lower() == member.lower():
                                passenger = member  # Use the canonical spelling
                                break
                        
                        # If not a known family member, use it anyway
                        if not passenger:
                            passenger = candidate
                        break
        
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
            extracted = extract_receipt_from_email(email)
            
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
    
    # Additional validation: Check that attributed rides match total receipts
    total_receipts = len(costs)
    attributed_rides = sum(1 for p in passenger_names if p is not None)
    unattributed_rides = total_receipts - attributed_rides
    
    # Check for unknown names (names not in the predefined family list)
    known_family = {'Fredrik', 'Viggo', 'Agne', 'Giedre', 'Nadine', 'Leona'}
    unknown_names = set()
    for name in passenger_names:
        if name is not None and name not in known_family:
            unknown_names.add(name)
    
    if unattributed_rides > 0:
        # This is a warning, not an error - some rides might not have passenger names
        pass  # Could add logging here if needed
    
    # Validate that we have some data
    if total_receipts == 0:
        raise ValueError("No valid receipts were extracted from the provided data")
    
    # Return extracted data along with metadata about unknown names
    return dates, passenger_names, costs, currencies


# Example usage:
if __name__ == "__main__":
    import json
    import sys
    
    # Sample usage function that demonstrates how to use extract_uber_data
    def demo_extraction(file_path="uber_data.json"):
        print(f"Reading data from: {file_path}")
        
        try:
            # Load emails from a JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Just pass the raw content to extract_uber_data
            # The function will handle JSON parsing internally
            
            # Use the extract_uber_data function directly on the content
            dates, passengers, costs, currencies = extract_uber_data(content)
            
            # Calculate attribution statistics
            total_receipts = len(costs)
            attributed_rides = sum(1 for p in passengers if p is not None)
            unattributed_rides = total_receipts - attributed_rides
            
            # Check for unknown names
            known_family = {'Fredrik', 'Viggo', 'Agne', 'Giedre', 'Nadine', 'Leona'}
            unknown_names = set()
            for name in passengers:
                if name is not None and name not in known_family:
                    unknown_names.add(name)
            
            print(f"Successfully extracted {total_receipts} receipts")
            print(f"Attributed rides: {attributed_rides}, Unattributed: {unattributed_rides}")
            if unknown_names:
                print(f"⚠️  Unknown passenger names found: {', '.join(sorted(unknown_names))}")
            print("\nSample data (first 5 entries):")
            for i in range(min(5, len(costs))):
                print(f"  {dates[i]} | {passengers[i]} | {costs[i]} {currencies[i]}")
                
            # Calculate totals
            total_kr = sum(cost for cost, curr in zip(costs, currencies) if curr == 'kr')
            total_usd = sum(cost for cost, curr in zip(costs, currencies) if curr == 'US$')
            
            print(f"\nTotal in SEK: {total_kr:.2f} kr")
            if total_usd > 0:
                print(f"Total in USD: {total_usd:.2f} US$")
                
            # Count rides by passenger
            passenger_counts = {}
            for p in passengers:
                if p:
                    passenger_counts[p] = passenger_counts.get(p, 0) + 1
                    
            print("\nRides by passenger:")
            for p, count in sorted(passenger_counts.items()):
                print(f"  {p}: {count}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Run the demo if called directly
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path == "-":
            # Read from stdin
            import sys
            content = sys.stdin.read()
            try:
                dates, passengers, costs, currencies = extract_uber_data(content)
                
                # Calculate attribution statistics
                total_receipts = len(costs)
                attributed_rides = sum(1 for p in passengers if p is not None)
                unattributed_rides = total_receipts - attributed_rides
                
                # Check for unknown names
                known_family = {'Fredrik', 'Viggo', 'Agne', 'Giedre', 'Nadine', 'Leona'}
                unknown_names = set()
                for name in passengers:
                    if name is not None and name not in known_family:
                        unknown_names.add(name)
                
                print(f"Successfully extracted {total_receipts} receipts")
                print(f"Attributed rides: {attributed_rides}, Unattributed: {unattributed_rides}")
                if unknown_names:
                    print(f"⚠️  Unknown passenger names found: {', '.join(sorted(unknown_names))}")
                print("\nSample data:")
                for i in range(len(costs)):
                    print(f"  {dates[i]} | {passengers[i]} | {costs[i]} {currencies[i]}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            demo_extraction(file_path)
    else:
        demo_extraction("uber_data.json")
