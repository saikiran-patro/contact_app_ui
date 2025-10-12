#!/usr/bin/env python3

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Optional

class ContactManager:
    def __init__(self, data_file: str = "contacts.json"):
        self.data_file = data_file
        self.contacts = self.load_contacts()
        self.next_id = self.get_next_id()

    def load_contacts(self) -> List[Dict]:
        """Load contacts from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_contacts(self) -> None:
        """Save contacts to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.contacts, f, indent=2)

    def get_next_id(self) -> int:
        """Get the next available contact ID"""
        if not self.contacts:
            return 1
        return max(contact['id'] for contact in self.contacts) + 1

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) >= 10

    def add_contact(self, name: str, email: str = "", phone: str = "", 
                   address: str = "", company: str = "", notes: str = "") -> Dict:
        """Add a new contact"""
        # Validate email if provided
        if email and not self.validate_email(email):
            raise ValueError("Invalid email format")
        
        # Validate phone if provided
        if phone and not self.validate_phone(phone):
            raise ValueError("Invalid phone number format")
        
        contact = {
            'id': self.next_id,
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'company': company,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.contacts.append(contact)
        self.next_id += 1
        self.save_contacts()
        return contact

    def update_contact(self, contact_id: int, **kwargs) -> Optional[Dict]:
        """Update an existing contact"""
        for contact in self.contacts:
            if contact['id'] == contact_id:
                # Validate email if being updated
                if 'email' in kwargs and kwargs['email']:
                    if not self.validate_email(kwargs['email']):
                        raise ValueError("Invalid email format")
                
                # Validate phone if being updated
                if 'phone' in kwargs and kwargs['phone']:
                    if not self.validate_phone(kwargs['phone']):
                        raise ValueError("Invalid phone number format")
                
                for key, value in kwargs.items():
                    if key in contact:
                        contact[key] = value
                contact['updated_at'] = datetime.now().isoformat()
                self.save_contacts()
                return contact
        return None

    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact"""
        for i, contact in enumerate(self.contacts):
            if contact['id'] == contact_id:
                del self.contacts[i]
                self.save_contacts()
                return True
        return False

    def get_contact(self, contact_id: int) -> Optional[Dict]:
        """Get a specific contact by ID"""
        for contact in self.contacts:
            if contact['id'] == contact_id:
                return contact
        return None

    def list_contacts(self) -> List[Dict]:
        """List all contacts sorted by name"""
        return sorted(self.contacts, key=lambda x: x['name'].lower())

    def search_contacts(self, query: str) -> List[Dict]:
        """Search contacts by name, email, phone, or company"""
        query = query.lower()
        results = []
        
        for contact in self.contacts:
            if (query in contact['name'].lower() or
                query in contact['email'].lower() or
                query in contact['phone'].lower() or
                query in contact['company'].lower() or
                query in contact['notes'].lower()):
                results.append(contact)
        
        return sorted(results, key=lambda x: x['name'].lower())

    def get_stats(self) -> Dict:
        """Get contact statistics"""
        total = len(self.contacts)
        with_email = len([c for c in self.contacts if c['email']])
        with_phone = len([c for c in self.contacts if c['phone']])
        with_company = len([c for c in self.contacts if c['company']])
        
        # Group by first letter of name
        by_letter = {}
        for contact in self.contacts:
            first_letter = contact['name'][0].upper()
            by_letter[first_letter] = by_letter.get(first_letter, 0) + 1
        
        return {
            'total': total,
            'with_email': with_email,
            'with_phone': with_phone,
            'with_company': with_company,
            'by_letter': by_letter
        }

    def export_contacts(self, format_type: str = "json") -> str:
        """Export contacts to different formats"""
        if format_type == "json":
            return json.dumps(self.contacts, indent=2)
        elif format_type == "csv":
            if not self.contacts:
                return "No contacts to export"
            
            # CSV header
            headers = ["ID", "Name", "Email", "Phone", "Company", "Address", "Notes", "Created"]
            csv_lines = [",".join(headers)]
            
            for contact in self.contacts:
                row = [
                    str(contact['id']),
                    f'"{contact["name"]}"',
                    f'"{contact["email"]}"',
                    f'"{contact["phone"]}"',
                    f'"{contact["company"]}"',
                    f'"{contact["address"]}"',
                    f'"{contact["notes"]}"',
                    contact['created_at'][:19]
                ]
                csv_lines.append(",".join(row))
            
            return "\n".join(csv_lines)
        else:
            raise ValueError("Unsupported export format")

def display_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("          CONTACT MANAGER")
    print("="*50)
    print("1. Add Contact")
    print("2. List All Contacts")
    print("3. Search Contacts")
    print("4. Update Contact")
    print("5. Delete Contact")
    print("6. View Contact Details")
    print("7. View Statistics")
    print("8. Export Contacts")
    print("9. Exit")
    print("="*50)

def display_contact(contact: Dict, detailed: bool = False):
    """Display a single contact"""
    if not contact:
        print("Contact not found.")
        return
    
    print(f"\n📋 Contact #{contact['id']}")
    print("-" * 40)
    print(f"👤 Name: {contact['name']}")
    
    if contact['email']:
        print(f"📧 Email: {contact['email']}")
    
    if contact['phone']:
        print(f"📞 Phone: {contact['phone']}")
    
    if contact['company']:
        print(f"🏢 Company: {contact['company']}")
    
    if contact['address']:
        print(f"📍 Address: {contact['address']}")
    
    if contact['notes']:
        print(f"📝 Notes: {contact['notes']}")
    
    if detailed:
        print(f"📅 Created: {contact['created_at'][:19]}")
        print(f"🔄 Updated: {contact['updated_at'][:19]}")

def display_contacts_list(contacts: List[Dict], title: str = "Contacts"):
    """Display a list of contacts"""
    print(f"\n{title}:")
    print("-" * 60)
    
    if not contacts:
        print("No contacts found.")
        return
    
    for contact in contacts:
        email_info = f" | {contact['email']}" if contact['email'] else ""
        phone_info = f" | {contact['phone']}" if contact['phone'] else ""
        company_info = f" | {contact['company']}" if contact['company'] else ""
        
        print(f"#{contact['id']:3d} {contact['name']}{email_info}{phone_info}{company_info}")

def get_contact_input():
    """Get contact input from user"""
    name = input("Enter contact name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return None
    
    email = input("Enter email (optional): ").strip()
    phone = input("Enter phone number (optional): ").strip()
    company = input("Enter company (optional): ").strip()
    address = input("Enter address (optional): ").strip()
    notes = input("Enter notes (optional): ").strip()
    
    return {
        'name': name,
        'email': email,
        'phone': phone,
        'company': company,
        'address': address,
        'notes': notes
    }

def main():
    """Main application loop"""
    print("Welcome to Contact Manager!")
    contact_manager = ContactManager()
    
    while True:
        display_menu()
        
        try:
            choice = input("Enter your choice (1-9): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break
        
        if choice == '1':
            # Add Contact
            contact_data = get_contact_input()
            if contact_data:
                try:
                    contact = contact_manager.add_contact(**contact_data)
                    print(f"\n✅ Contact added successfully! ID: {contact['id']}")
                except ValueError as e:
                    print(f"\n❌ Error: {e}")
        
        elif choice == '2':
            # List All Contacts
            contacts = contact_manager.list_contacts()
            display_contacts_list(contacts, "All Contacts")
        
        elif choice == '3':
            # Search Contacts
            query = input("Enter search query: ").strip()
            if query:
                results = contact_manager.search_contacts(query)
                display_contacts_list(results, f"Search Results for '{query}'")
            else:
                print("Please enter a search query!")
        
        elif choice == '4':
            # Update Contact
            try:
                contact_id = int(input("Enter contact ID to update: "))
                contact = contact_manager.get_contact(contact_id)
                
                if not contact:
                    print("Contact not found!")
                    continue
                
                print(f"\nCurrent contact: {contact['name']}")
                print("What would you like to update?")
                print("1. Name")
                print("2. Email")
                print("3. Phone")
                print("4. Company")
                print("5. Address")
                print("6. Notes")
                
                update_choice = input("Choose field (1-6): ").strip()
                
                try:
                    if update_choice == '1':
                        new_name = input("Enter new name: ").strip()
                        if new_name:
                            contact_manager.update_contact(contact_id, name=new_name)
                            print("✅ Name updated!")
                    
                    elif update_choice == '2':
                        new_email = input("Enter new email: ").strip()
                        contact_manager.update_contact(contact_id, email=new_email)
                        print("✅ Email updated!")
                    
                    elif update_choice == '3':
                        new_phone = input("Enter new phone: ").strip()
                        contact_manager.update_contact(contact_id, phone=new_phone)
                        print("✅ Phone updated!")
                    
                    elif update_choice == '4':
                        new_company = input("Enter new company: ").strip()
                        contact_manager.update_contact(contact_id, company=new_company)
                        print("✅ Company updated!")
                    
                    elif update_choice == '5':
                        new_address = input("Enter new address: ").strip()
                        contact_manager.update_contact(contact_id, address=new_address)
                        print("✅ Address updated!")
                    
                    elif update_choice == '6':
                        new_notes = input("Enter new notes: ").strip()
                        contact_manager.update_contact(contact_id, notes=new_notes)
                        print("✅ Notes updated!")
                    
                    else:
                        print("Invalid choice!")
                        
                except ValueError as e:
                    print(f"❌ Error: {e}")
                    
            except ValueError:
                print("Invalid contact ID!")
        
        elif choice == '5':
            # Delete Contact
            try:
                contact_id = int(input("Enter contact ID to delete: "))
                contact = contact_manager.get_contact(contact_id)
                
                if contact:
                    confirm = input(f"Are you sure you want to delete '{contact['name']}'? (y/N): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        if contact_manager.delete_contact(contact_id):
                            print("✅ Contact deleted successfully!")
                        else:
                            print("❌ Failed to delete contact!")
                    else:
                        print("Deletion cancelled.")
                else:
                    print("❌ Contact not found!")
            except ValueError:
                print("Invalid contact ID!")
        
        elif choice == '6':
            # View Contact Details
            try:
                contact_id = int(input("Enter contact ID: "))
                contact = contact_manager.get_contact(contact_id)
                display_contact(contact, detailed=True)
            except ValueError:
                print("Invalid contact ID!")
        
        elif choice == '7':
            # View Statistics
            stats = contact_manager.get_stats()
            print("\n📊 Contact Statistics:")
            print("-" * 30)
            print(f"Total Contacts: {stats['total']}")
            print(f"With Email: {stats['with_email']}")
            print(f"With Phone: {stats['with_phone']}")
            print(f"With Company: {stats['with_company']}")
            
            if stats['by_letter']:
                print("\nBy First Letter:")
                for letter in sorted(stats['by_letter'].keys()):
                    print(f"  {letter}: {stats['by_letter'][letter]}")
        
        elif choice == '8':
            # Export Contacts
            print("Export formats: json, csv")
            format_type = input("Choose format (json/csv): ").strip().lower()
            
            if format_type in ['json', 'csv']:
                try:
                    export_data = contact_manager.export_contacts(format_type)
                    filename = f"contacts_export.{format_type}"
                    
                    with open(filename, 'w') as f:
                        f.write(export_data)
                    
                    print(f"✅ Contacts exported to {filename}")
                except Exception as e:
                    print(f"❌ Export failed: {e}")
            else:
                print("Invalid format!")
        
        elif choice == '9':
            print("Thank you for using Contact Manager. Goodbye!")
            break
        
        else:
            print("Invalid choice! Please enter 1-9.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
