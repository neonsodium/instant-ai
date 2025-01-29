import os


def count_python_lines(directory):
    total_lines = 0
    file_count = 0

    # Traverse the directory and its subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Check for Python files
                file_count += 1
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        line_count = len(lines)
                        total_lines += line_count
                        print(f"{file}: {line_count} lines")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    print(f"\nTotal Python files: {file_count}")
    print(f"Total lines of code: {total_lines}")


# Example: Replace with the directory you want to scan
directory_to_scan = "./"  # Current directory
count_python_lines(directory_to_scan)
