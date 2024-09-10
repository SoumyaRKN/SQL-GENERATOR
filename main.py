import os
import pandas as pd

def show_warning():
    """
    Displays a warning or note when the script is run.
    """
    print("WARNING: This script will assist you in performing SQL operations like SELECT, INSERT, UPDATE, DELETE, etc.")
    print("For INSERT and UPDATE, a CSV/Excel file will be used. it will convert CSV/Excel data into SQL statements")
    print("Any empty values, or '-' in the CSV/Excel sheet will be converted to NULL in the SQL queries.")
    print("Make sure you have the correct details before proceeding.")
    print("=========================================================")

def read_input_file(file_path):
    """
    Reads the input file (CSV or Excel) and returns a pandas DataFrame.
    
    :param file_path: The path of the CSV or Excel file.
    :return: A pandas DataFrame containing the file data.
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    # Read the file based on its extension
    if file_extension == '.csv':
        df = pd.read_csv(file_path)
    elif file_extension in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")
    
    return df

def generate_insert_queries(df, table_name):
    """
    Generates SQL INSERT queries from a pandas DataFrame.
    
    :param df: The pandas DataFrame containing the data.
    :param table_name: The table name to be used in the SQL query.
    :return: A string containing the generated SQL query.
    """
    # Extract column names
    columns = df.columns.tolist()

    # Prepare the base insert statement
    base_insert = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES"
    
    # Collect the values for each row
    values_list = []
    for _, row in df.iterrows():
        values = [f"'{str(v)}'" if pd.notna(v) and str(v).strip().lower() not in ['null', '', '-'] else 'NULL' for v in row.tolist()]
        values_list.append(f"({', '.join(values)})")
    
    # Combine the base statement with values
    full_query = f"{base_insert} {', '.join(values_list)};"
    
    return full_query

def generate_update_queries(df, table_name, condition):
    """
    Generates SQL UPDATE queries from a pandas DataFrame.
    
    :param df: The pandas DataFrame containing the data.
    :param table_name: The table name to be used in the SQL query.
    :param condition: The condition to specify which rows to update.
    :return: A string containing the generated SQL queries.
    """
    queries = []
    
    for index, row in df.iterrows():
        set_clause = ', '.join(f"{col} = '{row[col]}'" for col in df.columns if pd.notna(row[col]) and str(row[col]).strip().lower() not in ['null', '', '-'])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition};"
        queries.append(query)
    
    return '\n'.join(queries)

def write_queries_to_file(query, output_file):
    """
    Writes generated SQL queries to a specified output file.
    Creates the directory if it does not exist.
    
    :param query: The SQL query to be written to the file.
    :param output_file: Path to the output file.
    """
    directory = './storage'
    
    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Construct the full path for the output file
    output_file_path = os.path.join(directory, output_file)
    
    # Write the query to the output SQL file
    with open(output_file_path, 'w') as outfile:
        outfile.write(query + "\n\n")
    
    print(f"SQL queries have been written to {output_file_path}")

def get_output_file_name(input_file):
    """
    Generates the output SQL file name based on the input file name.
    
    :param input_file: The path to the input file (CSV or Excel).
    :return: The output file name with .sql extension.
    """
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    return f"{base_name}.sql"

def get_user_selection(options, prompt="Please select an option"):
    """
    Displays options in a dropdown-style and asks the user to select one.
    
    :param options: List of options to display
    :param prompt: The message to display for selection
    :return: The selected option
    """
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        try:
            choice = int(input(f"Enter your choice (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Invalid input, please enter a number.")

if __name__ == '__main__':
    # Show the warning/note when the script is run
    show_warning()
    
    # Define available operations
    operations = [
        "select", "insert", "update", "delete", 
        "create_table", "drop_table", 
        "alter_table", "create_view", "drop_view"
    ]
    
    # Get user input for operation
    operation = get_user_selection(operations, "Choose an SQL operation to perform:")
    while True:
        table_name = input('Enter the table name: ').strip()
        if table_name:
            break
        print("Table name cannot be empty. Please enter a valid table name.")
    
    if operation == 'select':
        columns = input("Enter the columns to select (comma-separated, or * for all): ").strip()
        limit = input("Enter the limit (default is 10): ").strip() or "10"
        offset = input("Enter the offset (default is 0): ").strip() or "0"
        condition = input("Enter any conditions (or leave blank): ").strip()

        # Generate the SELECT query
        sql_query = f"SELECT {', '.join(columns.split(','))} FROM {table_name} WHERE {condition} LIMIT {limit} OFFSET {offset};"
        print(f"Generated SQL Query:\n{sql_query}")

    elif operation in ['insert', 'update']:
        file_path = os.path.realpath(input('Enter full path of the CSV/Excel file: '))
        
        # Read the input file (CSV or Excel)
        df = read_input_file(file_path)
        
        # Generate SQL insert queries
        if operation == 'insert':
            sql_query = generate_insert_queries(df, table_name)
        else:
            # Assuming a simple update where all rows are updated
            condition = input("Enter the condition for updating rows (e.g., WHERE id = 1): ")
            sql_query = generate_update_queries(df, table_name, condition)
        
        # Get the output SQL file name from the input file name
        output_file_path = get_output_file_name(file_path)
        
        # Write the query to the output SQL file
        write_queries_to_file(sql_query, output_file_path)
        
        print(f"SQL queries have been written to {output_file_path}")
    
    elif operation == 'delete':
        condition = input("Enter the condition for DELETE (e.g., id=10): ")

        # Generate the DELETE query
        sql_query = f"DELETE FROM {table_name} WHERE {condition};"
        print(f"Generated SQL Query:\n{sql_query}")
    
    elif operation == 'create_table':
        columns = {}
        while True:
            col_name = input("Enter column name (or type 'done' to finish): ")
            if col_name.lower() == 'done':
                break
            col_type = input(f"Enter data type for {col_name}: ")
            col_default = input(f"Enter default value for {col_name} (or leave blank for none): ")
            col_key = input(f"Is {col_name} a PRIMARY KEY, UNIQUE, or INDEX (leave blank if none): ")
            columns[col_name] = f"{col_type} {col_key} {f'DEFAULT {col_default}' if col_default else ''}"

        # Generate the CREATE TABLE query
        sql_query = f"CREATE TABLE {table_name} ({columns});"
        print(f"Generated SQL Query:\n{sql_query}")
    
    elif operation == 'drop_table':
        # Generate the DROP TABLE query
        sql_query = f"DROP TABLE IF EXISTS {table_name};"
        print(f"Generated SQL Query:\n{sql_query}")

    elif operation == 'alter_table':
        alter_statement = input("Enter the ALTER TABLE statement (e.g., ADD COLUMN age INT): ")

        # Generate the ALTER TABLE query
        sql_query = f"ALTER TABLE {table_name} {alter_statement};"
        print(f"Generated SQL Query:\n{sql_query}")

    elif operation == 'create_view':
        while True:
            view_name = input('Enter the view name: ').strip()
            if view_name:
                break
            print("View name cannot be empty. Please enter a valid view name.")
        select_statement = input("Enter the SELECT statement (e.g., SELECT id, name FROM users): ")

        # Generate the ALTER TABLE query
        sql_query = f"CREATE VIEW {view_name} AS {select_statement};"
        print(f"Generated SQL Query:\n{sql_query}")

    elif operation == 'drop_view':
        while True:
            view_name = input('Enter the view name: ').strip()
            if view_name:
                break
            print("View name cannot be empty. Please enter a valid view name.")

        # Generate the ALTER TABLE query
        sql_query = f"DROP VIEW IF EXISTS {view_name};"
        print(f"Generated SQL Query:\n{sql_query}")

