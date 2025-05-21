import json
import os
from datetime import datetime
from time import sleep
from collections import defaultdict
import curses

file_name = "data.json"
os.system("cls" if os.name == "nt" else "clear")

category_name = "categories.json"

def load_event_themes():
    with open(category_name, "r") as file:
        data = json.load(file)
        return data["categories"]

event_theme_options = load_event_themes()

def format_event_date(event_date):
    return datetime.strptime(event_date, "%a %b %d %Y").strftime("%m/%d/%Y")

def validate_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        return dt.strftime("%a %b %d %Y")
    except ValueError:
        return None


def load_bills():
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except:
        return {"bills":[]}

def save_bills(bills):
    try:
        with open(file_name, "w") as file:
            json.dump(bills, file, indent=4)
    except:
        print("Failed to save.")

def group_paid_bills_by_theme(bills):
    grouped_totals = defaultdict(float)
    longest_name = max(len(bill['event_theme']) for bill in bills['bills'])

    for bill in bills['bills']:
        if bill["paid"] == 1:
            grouped_totals[bill["event_theme"]] += bill["amount"]

    print("\033[1;32mTotal Amount for Paid Bills:\033[0m\n")
    for theme, total in grouped_totals.items():
        print(f"{theme.ljust(longest_name)}: ${total:.2f}")

def view_bills(bills):
    os.system("cls" if os.name == "nt" else "clear")
    bills_list = sorted(bills["bills"], key=lambda bill: datetime.strptime(bill["event_date"], "%a %b %d %Y"), reverse=True)

    if not bills_list:
        print('\033[1;32mNo Bills to display!\033[0m')
        input("\nPress Enter to return to the menu...")
    else:
        print("\033[1;32mYour bills:\033[0m\n")

        longest_name = max(len(bill["event_theme"]) for bill in bills_list)

        for bill in bills_list:
            status = "[Paid]" if bill["paid"] == 1 else "      "
            print(f"- {format_event_date(bill['event_date'])} - {bill['event_theme'].ljust(longest_name)} {status} ${bill['amount']}")

        input("\nPress Enter to return to the menu...")
        os.system("cls" if os.name == "nt" else "clear")

def view_unpaid_bills(bills):
    os.system("cls" if os.name == "nt" else "clear")
    bills_list = sorted(bills["bills"], key=lambda bill: datetime.strptime(bill["event_date"], "%a %b %d %Y"), reverse=True)

    if len(bills_list) == 0:
        print('\033[1;32mNo Bills to display!\033[0m')
        input("\nPress Enter to return to the menu...")
    else:
        print("\033[1;32mYour UNPAID bills:\033[0m\n")
        
        longest_name = max(len(bill['event_theme']) for bill in bills_list)

        for idx, bill in enumerate(bills_list):
            if bill['paid'] != 1:
                status = "✅" if bill['paid'] == 1 else ""
                print(f"{idx + 1}. {format_event_date(bill['event_date'])} - {bill['event_theme'].ljust(longest_name)} {status} ${bill['amount']}")

def add_bills(bills):
    os.system("cls" if os.name == "nt" else "clear")
    print("\033[1;32m💰 Add a New Bill 💳\033[0m\n")
    
    while True:
        event_date_input = input("Enter the event date (MM/DD/YYYY): ").strip()
        event_date = validate_date(event_date_input)
        if event_date:
            break
        print("Invalid date format. Please enter a valid date in MM/DD/YYYY format.")

    print("\nSelect an event theme:")
    for idx, option in enumerate(event_theme_options, start=1):
        print(f"{idx}. {option}")
    
    while True:
        try:
            theme_choice = int(input("\nEnter the number corresponding to the event theme: "))
            if 1 <= theme_choice <= len(event_theme_options):
                event_theme = event_theme_options[theme_choice - 1]
                break
            print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Enter a valid number.")

    paid = int(input("Is the bill paid? (1 for Yes, 0 for No): ").strip())
    amount = float(input("Enter the amount: ").strip())

    icons = {
        "Rent": "fas fa-home",
        "Car Insurance": "fas fa-bolt",
        "Internet": "fas fa-network-wired",
        "Groceries": "fas fa-shopping-cart"
    }
    icon = icons.get(event_theme, "fas fa-file-invoice")

    new_bill = {
        "event_date": event_date,
        "event_theme": event_theme,
        "paid": paid,
        "amount": amount,
        "icon": icon
    }

    bills["bills"].append(new_bill)

    try:
        with open(file_name, "w") as file:
            json.dump(bills, file, indent=4)
        print("\nBill added successfully!")
    except:
        print("Failed to save the bill.")

    input("\nPress Enter to return to the menu...")
    os.system("cls" if os.name == "nt" else "clear")

def delete_bills(bills):
    os.system("cls" if os.name == "nt" else "clear")
    print("\033[1;32m Delete a Bill\033[0m")

    if not bills["bills"]:
        print("No bills to delete.")
        input("\nPress Enter to return to the menu...")
        os.system("cls" if os.name == "nt" else "clear")
        return

    indexed_bills = sorted(
        [(idx, bill) for idx, bill in enumerate(bills["bills"])],
        key=lambda item: datetime.strptime(item[1]["event_date"], "%a %b %d %Y"),
        reverse=True
    )

    longest_name = max(len(bill["event_theme"]) for _, bill in indexed_bills)

    print("\nSelect a bill to delete:\n")
    for display_idx, (original_idx, bill) in enumerate(indexed_bills, start=1):
        status = "[Paid]" if bill["paid"] == 1 else "      "
        print(f"{display_idx}. {format_event_date(bill['event_date'])} - {bill['event_theme'].ljust(longest_name)} {status} ${bill['amount']}")

    while True:
        try:
            choice = input("\nEnter the number of the bill to delete (or 'b' to go back): ").strip()
            if choice.lower() == "b":
                print("Returning to main menu...")
                os.system("cls" if os.name == "nt" else "clear")
                return

            bill_index = int(choice) - 1
            if 0 <= bill_index < len(indexed_bills):
                original_idx = indexed_bills[bill_index][0]  # Get original index before sorting
                del bills["bills"][original_idx]  # Remove the correct bill from the original list

                with open(file_name, "w") as file:
                    json.dump(bills, file, indent=4)

                print("\nBill deleted successfully!")
                break
            else:
                print("Invalid selection. Please choose a valid bill number.")
        except ValueError:
            print("Enter a valid number.")

    input("\nPress Enter to return to the menu...")
    os.system("cls" if os.name == "nt" else "clear")

def search_bills(bills):
    os.system("cls" if os.name == "nt" else "clear")
    print("\033[1;32m🔍 Search Bills\033[0m\n")

    search_term = input("Enter an event date, theme, amount, or payment status to search: ").strip().lower()

    matching_bills = [
        bill for bill in bills["bills"]
        if search_term in bill["event_date"].lower()
        or search_term in bill["event_theme"].lower()
        or search_term in str(bill["amount"]).lower()
        or search_term in ("paid" if bill["paid"] else "unpaid")
    ]

    if not matching_bills:
        print("\nNo bills found matching your search.")
        input("\nPress Enter to return to the menu...")
        return

    print("\n\033[1;34mMatching Bills:\033[0m\n")
    for idx, bill in enumerate(matching_bills, start=1):
        print(f"{idx}. {bill['event_theme']} - ${bill['amount']} ({'Paid' if bill['paid'] else 'Unpaid'})")

    # Let user select a bill or go back
    while True:
        choice = input("\nEnter the number of the bill you want to see details of, or 'b' to go back: ").strip()

        if choice.lower() == 'b':
            print("Returning to the main menu...")
            os.system("cls" if os.name == "nt" else "clear")
            return  

        try:
            choice = int(choice)
            if 1 <= choice <= len(matching_bills):
                selected_bill = matching_bills[choice - 1]
                print("\n\033[1;32mBill Details:\033[0m")
                print(f"Date: {selected_bill['event_date']}")
                print(f"Name: {selected_bill['event_theme']}")
                print(f"Amount: ${selected_bill['amount']}")
                print(f"Paid: {'Yes' if selected_bill['paid'] else 'No'}")
                input("\nPress Enter to return to the menu...")
                os.system("cls" if os.name == "nt" else "clear")
                return  
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Enter a valid number or 'b' to go back.")

def pay_bills(bills):
    unpaid_bills = sorted(
        [(idx, bill) for idx, bill in enumerate(bills["bills"]) if bill["paid"] != 1],
        key=lambda item: datetime.strptime(item[1]["event_date"], "%a %b %d %Y"), reverse=True
    )

    if not unpaid_bills:
        print("\033[1;32mNo unpaid bills to pay!\033[0m")
        input("\nPress Enter to return to the menu...")
        return

    print("\033[1;32mSelect a bill to mark as paid:\033[0m\n")
    for display_idx, (original_idx, bill) in enumerate(unpaid_bills, start=1):
        print(f"{display_idx}. {format_event_date(bill['event_date'])} - {bill['event_theme']}")

    while True:
        user_input = input("\nEnter the task number to mark as paid (or 'b' to go back): ").strip()

        if user_input.lower() == "b":
            os.system("cls" if os.name == "nt" else "clear")
            return

        try:
            task_number = int(user_input)
            if 1 <= task_number <= len(unpaid_bills):
                original_idx = unpaid_bills[task_number - 1][0]
                bills["bills"][original_idx]["paid"] = 1
                save_bills(bills)
                print("Bills marked as paid.")
                return
            else:
                print("Invalid bill number. Please choose a valid number from the list.")

        except ValueError:
            print("Enter a valid number.")

def welcome_screen(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    height, width = stdscr.getmaxyx()
    message = "💰🇱🇺💰  Welcome to Bill Manager! 🚀🔥💳"
    prompt = "Press Enter to continue..."
    bottom = "made by Robin te Hofstee"
    stdscr.addstr(height // 2 - 1, (width - len(message)) // 2, message)
    stdscr.addstr(height // 2 + 1, (width - len(prompt)) // 2, prompt)
    stdscr.addstr(height // 2 + 10, (width - len(bottom)) // 2, bottom)
    stdscr.refresh()
    stdscr.getch()

def exit_screen(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    height, width = stdscr.getmaxyx()
    message = "👋 Thanks for using the program! 🚀"
    prompt = "Press any key to exit..."
    stdscr.addstr(height // 2 - 1, (width - len(message)) // 2, message)
    stdscr.addstr(height // 2 + 1, (width - len(prompt)) // 2, prompt)
    stdscr.refresh()
    stdscr.getch()

def main():
    bills = load_bills()
    
    while True:
        print("\033[1;32mBill Manager\033[0m\n")
        print("1. View Bills\n2. View Unpaid Bills\n3. Add Bills\n4. Pay Bills\n5. Delete Bills\n6. Grouped Bills\n7. Search Bills\nq. Exit\n")
        choice = input("Enter Your Choice: ").strip()

        if choice == "1":
            view_bills(bills)
        elif choice == "2":
            view_unpaid_bills(bills)
            input("\nPress Enter to return to the menu...")
            os.system("cls" if os.name == "nt" else "clear")
        elif choice == "3":
            os.system("cls" if os.name == "nt" else "clear")
            add_bills(bills)
        elif choice == "4":
            os.system("cls" if os.name == "nt" else "clear")
            pay_bills(bills)
        elif choice == "5":
            delete_bills(bills)
        elif choice == "6":
            os.system("cls" if os.name == "nt" else "clear")
            group_paid_bills_by_theme(bills)
            input("\nPress Enter to return to the menu...")
            os.system("cls" if os.name == "nt" else "clear")
        elif choice == "7":
            search_bills(bills)
        elif choice == "q":
            os.system("cls" if os.name == "nt" else "clear")
           # curses.wrapper(exit_screen)
            break
        else:
            print("Invalid choice. Please try again")
            sleep(1)
            os.system("cls" if os.name == "nt" else "clear")


curses.wrapper(welcome_screen)
main()