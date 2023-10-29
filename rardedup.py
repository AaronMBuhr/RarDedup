import os
import shutil
import subprocess
import sys
import tempfile
from typing import List

# def extract_rar(rar_file_path, temp_dir):
#     """
#     Extracts a RAR file to a temporary directory using the WinRAR command line tool.

#     :param rar_file_path: str, the path to the RAR file
#     :param temp_dir: str, the path to the temporary directory where the files should be extracted
#     """
#     # Ensure the temporary directory exists
#     if not os.path.exists(temp_dir):
#         os.makedirs(temp_dir)

#     # Construct the command to extract the RAR file
#     # Example: "Rar.exe x -y rar_file_path temp_dir"
#     command = ["Rar.exe", "x", "-y", rar_file_path, temp_dir]

#     # Run the command
#     result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

#     # Check if the command executed successfully
#     if result.returncode != 0:
#         print("Error extracting RAR file:")
#         print(result.stderr)
#     else:
#         print("RAR file extracted successfully.")

def extract_rars(rar_file_paths: List[str], temp_dir: str) -> None:
    """
    Extracts multiple RAR files to directories within a temporary directory. Each RAR file is extracted
    to a directory named after the RAR file, excluding the ".rar" extension.

    :param rar_file_paths: list of str, paths to the RAR files
    :param temp_dir: str, path to the temporary directory
    """
    # # Example usage
    # extract_rars(["path/to/your/file1.rar", "path/to/your/file2.rar"], "path/to/temporary/directory")

    # Ensure the temporary directory exists
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for rar_file_path in rar_file_paths:
        # Ensure the RAR file exists
        if not os.path.exists(rar_file_path):
            print(f"Error: The file {rar_file_path} does not exist.")
            continue

        # Get the base name of the RAR file (excluding directory and ".rar" extension)
        base_name = os.path.basename(rar_file_path)
        if base_name.lower().endswith(".rar"):
            base_name = base_name[:-4]

        # Construct the path to the directory where the RAR file will be extracted
        extract_dir = os.path.join(temp_dir, base_name)

        # Ensure the extraction directory exists
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)

        # Construct the command to extract the RAR file
        # Example: "Rar.exe x -y rar_file_path extract_dir"
        command = ["Rar.exe", "x", "-y", rar_file_path, extract_dir]

        # # Run the command
        # result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # # Check if the command executed successfully
        # if result.returncode != 0:
        #     print(f"Error extracting RAR file {rar_file_path}:")
        #     print(result.stderr)
        # else:
        #     print(f"RAR file {rar_file_path} extracted successfully to {extract_dir}.")

        try:
            # Running the command and directly printing the output to the terminal
            subprocess.run(command, check=True)
            print(f"RAR file {rar_file_path} extracted successfully to {extract_dir}.")
        except subprocess.CalledProcessError as e:
            print(f"Error extracting RAR file {rar_file_path}: {e}")



def extract_rars_to_temp_dir(rar_file_paths: List[str]) -> List[str]:
    # # Example usage
    # temp_dirs = extract_rars_to_temp_dir(["path/to/your/file1.rar", "path/to/your/file2.rar"])
    # print("Temporary directories:", temp_dirs)

    # Create the "rardedup" directory inside the system's temporary directory
    rardedup_dir = os.path.join(tempfile.gettempdir(), "rardedup")
    if not os.path.exists(rardedup_dir):
        os.makedirs(rardedup_dir)

    temp_dirs = []
    for rar_file_path in rar_file_paths:
        # Create a temporary directory inside the "rardedup" directory
        temp_dir = tempfile.mkdtemp(dir=rardedup_dir)
        temp_dirs.append(temp_dir)

        # Call the previously defined function to extract the RAR files
        extract_rars([rar_file_path], temp_dir)

    return temp_dirs


def are_files_equal(file1_path: str, file2_path: str, status_message: str) -> bool:
    try:
        with open(file1_path, 'rb') as file1, open(file2_path, 'rb') as file2:
            file1_size = os.path.getsize(file1_path)
            file2_size = os.path.getsize(file2_path)

            if file1_size != file2_size:
                return False

            chunk_size = 1024 * 1024  # 1 MB
            total_read = 0
            while True:
                chunk1 = file1.read(chunk_size)
                chunk2 = file2.read(chunk_size)
                total_read += len(chunk1)

                if not chunk1:
                    print(f"{status_message} 100.00%", end='\r')
                    print()  # Move to the next line after completion
                    return True

                if chunk1 != chunk2:
                    print(f"{status_message} 100.00%", end='\r')
                    print()  # Move to the next line after completion
                    return False

                progress = (total_read / file1_size) * 100
                print(f"{status_message} {progress:.2f}%", end='\r')

    except Exception as e:
        print(f"\nError comparing files: {e}")
        return False


# def find_equal_files(dir1, dir2):
#     # # Example usage
#     # equal_files = find_equal_files("path/to/dir1", "path/to/dir2")
#     # print("Equal files:", equal_files)

#     equal_files = []

#     # Walk through the directory tree starting at dir1
#     for root, _, files in os.walk(dir1):
#         for file in files:
#             # Construct the full path to the file in dir1
#             file_path1 = os.path.join(root, file)
            
#             # Construct the relative path from dir1
#             relative_path = os.path.relpath(file_path1, start=dir1)
            
#             # Construct the corresponding path in dir2
#             file_path2 = os.path.join(dir2, relative_path)
            
#             # Check if the file exists in dir2
#             if os.path.exists(file_path2):
#                 # Compare the two files
#                 if are_files_equal(file_path1, file_path2):
#                     equal_files.append(relative_path)
    
#     return equal_files



def count_files(directory):
    count = 0
    for _, _, files in os.walk(directory):
        count += len(files)
    return count

def find_equal_files(dir1, dir2):
    total_files = count_files(dir1)
    current_file_number = 0

    equal_files = []

    # Walk through the directory tree starting at dir1
    for root, _, files in os.walk(dir1):
        for file in files:
            current_file_number += 1

            # Construct the full path to the file in dir1
            file_path1 = os.path.join(root, file)
            
            # Construct the relative path from dir1
            relative_path = os.path.relpath(file_path1, start=dir1)

            # Construct the status message
            status_message = f"{relative_path} ({current_file_number} / {total_files})"
            
            # # Print initial progress message
            # print(status_message)

            # Construct the corresponding path in dir2
            file_path2 = os.path.join(dir2, relative_path)
            
            # Check if the file exists in dir2
            if os.path.exists(file_path2):
                # Compare the two files
                if are_files_equal(file_path1, file_path2, status_message):
                    equal_files.append(relative_path)
    
    return equal_files


def delete_files_from_rar(rar_file_path: str, files_to_delete: List[str]) -> None:
    # Create a temporary text file
    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    try:
        # Write the list of files to delete to the temporary file
        temp_file.write('\n'.join(files_to_delete))
        temp_file.flush()  # Ensure all data is written to the file
    finally:
        # Ensure the temporary file is closed before running the rar command
        temp_file.close()

    # Construct the command to delete the files from the RAR archive
    cmd = ["rar", "d", rar_file_path, f"@{temp_file.name}"]

    try:
        # Run the command
        subprocess.run(cmd, check=True)
        print(f"Files successfully deleted from {rar_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while deleting files from {rar_file_path}: {e}")
    finally:
        # Delete the temporary file
        os.remove(temp_file.name)
        print(f"Temporary file {temp_file.name} deleted")



def main(args: List[str]) -> int:
    print("Extracting rars...")
    temp_dirs = extract_rars_to_temp_dir([args[1], args[2]])
    print("Finding equal files...")
    equal_files = find_equal_files(temp_dirs[0], temp_dirs[1])
    print("Removing temporary directories...")
    for temp_dir in temp_dirs:
        try:
            shutil.rmtree(temp_dir)
            print(f"Temporary directory {temp_dir} deleted successfully.")
        except OSError as e:
            print(f"Error deleting temporary directory {temp_dir}: {e}")
    print("Deleting files from rar...")
    delete_files_from_rar(args[2], equal_files)
    print(f"Done. {len(equal_files)} files deleted from {args[2]}.")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python rardedup.py <rar1> <rar2>")
        print("<rar1> is the unchanged rar file")
        print("<rar2> is the rar file to be changed")
        sys.exit(1)

    sys.exit(main(sys.argv))
