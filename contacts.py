import os
import re
from dotenv import load_dotenv
from lib.y360_api.api_script import API360

def add_contacts_from_file():
    contact_file_name = os.environ.get('CONTACT_FILE_NAME')
    if not os.path.exists(contact_file_name):
        full_path = os.path.join(os.path.dirname(__file__), contact_file_name)
        if not os.path.exists(full_path):
            print (f'ERROR! Input file {contact_file_name} not exist!')
            return []
        else:
            contact_file_name = full_path
    
    ### Another way to read file with needed transfromations
    # with open(deps_file_name, 'r') as csvfile:
    #     header = csvfile.readline().split(";")
    #     for line in csvfile:
    #         fields = line.split(";")
    #         entry = {}
    #         for i,value in enumerate(fields):
    #             entry[header[i].strip()] = value.strip()
    #         data.append(entry)
    # print(data)


    data = []
    print_data = []
    full_line = ''
    print('*' * 100)
    print('Data to import')
    print('-' * 100)
    with open(contact_file_name, 'r', encoding='utf-8') as csvfile:
        for line in csvfile:
            if line.startswith(','):
                if len(full_line) > 0:
                    #print(f'Comma count: {full_line.count(",")}, {full_line.count("CN=")} {full_line}')
                    entry = ProcessLine(full_line)
                    if entry:
                        data.append(entry)
                        #print_data.append(full_line)

                full_line = line.strip()
                continue
            else:
                if len(full_line) > 0:
                    full_line += ',' + line.strip()
    if len(full_line) > 0:
        #print(f'Comma count: {full_line.count(",")}, {full_line.count("CN=")} {full_line}')
        entry = ProcessLine(full_line)
        if entry:
            data.append(entry)
            #print_data.append(full_line)
    
    # for line in print_data:
    #     print(line)
    print('-' * 100)
    answer = input("Continue to import? (Y/n): ")
    if answer.upper() in ["Y", "YES"]:
        organization.post_create_contact(data)
        return data
    else:
        return []
    
def ProcessLine(full_line):
    regex = re.compile(
    r"(?i)"  # Case-insensitive matching
    r"(?:[A-Z0-9!#$%&'*+/=?^_`{|}~-]+"  # Unquoted local part
    r"(?:\.[A-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"  # Dot-separated atoms in local part
    r"|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]"  # Quoted strings
    r"|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")"  # Escaped characters in local part
    r"@"  # Separator
    r"[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?"  # Domain name
    r"\.(?:[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?)+"  # Top-level domain and subdomains
    )
    entry= {}
    print_entry = {}
    email_entry = {}
    email_list = []
    phone_entry = {}
    phone_list = []
    part1 = ','.join(full_line.split(",")[0:4])
    part2 = ','.join(full_line.split(",")[4:])
    print_entry['name'] = part1.split(",")[1]
    print_entry['surname'] = part1.split(",")[3]
    print_entry['email'] = re.findall(regex, part2)
    if part1.split(",")[1]:
        entry['firstName'] = part1.split(",")[1]
    else:
        entry['firstName'] = ' '
    if part1.split(",")[3]:
        entry['lastName'] = part1.split(",")[3]
    entry['address'] = ''
    entry['company'] = ''
    entry['department'] = ''
    entry['externalId'] = ''
    entry['middleName'] = ''
    entry['title'] = ''
    email_index = 1
    unique_emails = []      
    for email in re.findall(regex, part2):
        if email not in unique_emails:
            email_entry = {}
            unique_emails.append(email)
            if email_index == 1:
                email_entry['main'] = True
            else:
                email_entry['main'] = False
            email_entry['email'] = email                        
            email_entry['type'] = 'work'                        
            email_list.append(email_entry)
            email_index += 1
    entry['emails'] = email_list.copy()
    phone_entry['phone'] = ''
    phone_entry['main'] = True
    phone_entry['type'] = 'work'
    phone_list.append(phone_entry)
    entry['phones'] = phone_list.copy()
    if len(email_list) > 0 and (part1.split(",")[1] or part1.split(",")[3]) and full_line.count("CN=") == 1:
        #print(entry)
        print(print_entry)
        return entry
    else:
        print(f'Bad or suspicious string: {full_line}')
        return {}
    
def get_all_contacts():
    organization.get_all_contacts(file=True)
    print('-' * 100)
    print('Contacts list was saved to contacts_output.txt file')
    print('-' * 100)

def delete_all_contacts():
    print('-' * 100)
    answer = input("WARNING!!! You selected to DELETE ALL CONTACTS. Continue? (Y/n): ")
    if answer.upper() in ["Y", "YES"]:
        organization.wipe_all_contacts()
    print('-' * 100)

def main_menu():

    while True:
        print(" ")
        print("Select option:")
        print("1. Add contacts from file.")
        print("2. Export existing contacts to file.")
        print("3. Delete all contacts.")
        print("0. Exit")

        choice = input("Enter your choice (0-3): ")

        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            print('\n')
            add_contacts_from_file()
        elif choice == "2":
            get_all_contacts()
        elif choice == "3":
            delete_all_contacts()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    denv_path = os.path.join(os.path.dirname(__file__), '.env')

    if os.path.exists(denv_path):
        load_dotenv(dotenv_path=denv_path,verbose=True, override=True)
    
    organization = API360(os.environ.get('orgId'), os.environ.get('access_token'))
    
    main_menu()