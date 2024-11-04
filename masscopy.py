#!/usr/bin/python3

import os
import sys
import argparse
import hashlib
import time
import shutil


def list_str(items: str):
    return items.split(",")


def console_log(message: str, message2 = str(""), value = float(0), tp = int(0), value_avaliable = bool(True)) -> None:
    verbosity = args.verbosity.lower()

    # Types
    types = ["EXECUTION", "WARNING", "ERROR", "INFO"]

    # What type is
    msg_type = types[tp]

    # Print acordingly
    if msg_type != "EXECUTION":
        print(f"[{msg_type}] {message}")
        
        if msg_type == "ERROR":
            sys.exit(1)
    else:
        if verbosity == "y":
            print(f"[{msg_type}] {message} -> {message2}: ", end="")
            if value_avaliable:
                print(f"{value:.2f}%")
            else:
                print("Unknown%")


def is_boolean(text: str) -> bool:
    # Check if it's a boolean
    if text in "YyNn":
        return True
    else:
        return False


# Get the hash of a file
def get_hash(file: str, chunk_size: int) -> str:
    hash_func = hashlib.new("sha256")

    with open(file, 'rb') as file:
        while chunk := file.read(chunk_size):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def list_dir(path: str, exclude: list, specific_list: list, is_main: bool) -> list:
    files_list = [] # This will be the list that will return
    
    # Only execute this part if it's not the main proccess or there's no specified files
    if not is_main or (specific_list[0] == "" and len(specific_list) == 1):
        try:
            files = os.listdir(f"{path}")
            
            # Path to each file
            for i in files:
                if i not in exclude:
                    files_list.append(os.path.join(path, i))
        except NotADirectoryError:
            files_list = [path]  
    else:
        # Else, return the specific list ignoring if there's any excluded file.
        for i in specific_list:
            full_path = os.path.join(path, i)

            # Check if the file even exists
            if os.path.exists(full_path):
                files_list.append(full_path)
            else:
                console_log(message=f"Ignoring non-existing file '{full_path}'.", tp=1)

    return files_list


def copy_to(origin: str, dst: str, chunk_size: int, check_integrity: str, exclude: list, specific_list: list, is_main: bool, method: str) -> list:
    files = list_dir(origin, exclude, specific_list, is_main) # Get the list of files

    # No work to do
    if len(files) <= 0:
        return

    output_paths = [] # List of output paths
    hashes = []

    corrupted = []
    stored_corruptions = [] # Where the corrupted files are moved

    try:
        os.makedirs(dst, exist_ok=True) # Create dst folder
    except FileExistsError:
        pass

    # In case dst is a file
    if os.path.isfile(dst):
        raise NotADirectoryError("Target path is a file.")


    for file in files: # Itarate and create output paths
        filename = os.path.split(file)[1] # Just the last part
        output_path = os.path.join(dst, filename)

        # Create if non existing
        if not os.path.exists(output_path):
            if os.path.isfile(file):
                open(output_path, "w+").write("")
            elif os.path.isdir(file):
                os.makedirs(output_path)

        # Get all the hashes of origin folder to check integrity later
        if os.path.isfile(file) and check_integrity == "y":
            hashes.append(get_hash(file, chunk_size))
        
        output_paths.append(output_path)


    index = -1 # Index to each file
    index_nodir = -1 # Index to each non-dir file 
    redo = False # Redo?
    attempts = 0 # Attempts of redoing
    while True:
        if not redo:
            index += 1
            index_nodir += 1
        
        # Ends loop on end of array
        if index >= len(files):
            break

        file = files[index]

        output_path = output_paths[index]

        # Create the file if not exists
        if not os.path.exists(output_path):
            open(output_path, "w+").write("")

        # Recursion if it's a directory so the folder content is also copied
        if os.path.isdir(file):
            copy_to(file, output_path, chunk_size, check_integrity, exclude, specific_list, False, method)
            index_nodir -= 1
            continue

        # Copy the file
        

        # Open the source and destination files in binary mode if method is detailed
        percents = 0
        if method == "detailed":
            console_log(message=file, message2=output_path, value=percents, tp=0, value_avaliable=True)
            with open(file, "rb") as src_file, open(output_path, "wb") as dst_file:
                src_file.seek(0, os.SEEK_END)
                total_size = src_file.tell()
                src_file.seek(0)  # Go back to the start of the file

                copied_size = 0

                while True:
                    chunk = src_file.read(chunk_size)
                    if not chunk:
                        break  # End of file

                    dst_file.write(chunk)
                    copied_size += len(chunk)

                    # Calculate and print the progress
                    percents = (copied_size / total_size) * 100
                    console_log(message=file, message2=output_path, value=percents, tp=0, value_avaliable=True)
        elif method == "system":
            # Use a system call
            console_log(message=file, message2=output_path, value=0, tp=0, value_avaliable=False)
            shutil.copy(file, output_path)

        # Checks integrity
        if check_integrity == "y":
            origin_fileh = hashes[index_nodir]
            dst_hash = get_hash(output_path, chunk_size)

            if origin_fileh != dst_hash:
                attempts += 1

                if attempts <= 3:
                    redo = True
                else:
                    corrupted.append(file)
                    redo = False
            else:
                redo = False

    # Move the corrupted files so user can do something about it
    if len(corrupted) >= 1:
        corrupted_folder = os.path.join(dst, "CORRUPTED_DATA")

        os.makedirs(corrupted_folder, exist_ok=True)
        for file in corrupted:
            filename = os.path.split(file)[1]
            corrupted_newpath = os.path.join(corrupted_folder, filename)
            shutil.move(file, corrupted_folder)
            stored_corruptions.append(corrupted_newpath)

            open(f"{filename}_path.txt", "w+").write(f"{file}")

    return stored_corruptions


def main(args):
    stime = time.time() # Start time
    
    # Chunk sizes needs to be at least 1 byte.
    if args.chunk_size <= 0:
        console_log(message="Chunk size should be at least 1 byte.", tp=2)

    if not is_boolean(args.check_integrity):
        console_log(message="Check integrity check must be y or n.", tp=2)

    if not is_boolean(args.verbosity):
        console_log(message="Verbosity must be y or n.", tp=2)

    if not is_boolean(args.execution_time):
        console_log(message="Execution time must be y or n", tp=2)

    if args.mode.lower() not in ["system", "detailed"]:
        console_log(message="Mode must be 'system' or 'detailed'.", tp=2)

    check_integrity = args.check_integrity.lower()
    execution_time = args.execution_time.lower()

    try:
        damaged = copy_to(args.paths[0], args.paths[1], args.chunk_size, check_integrity, args.exclude, args.specify, True, args.mode)
    except FileNotFoundError:
        console_log(message="No such file or directoroy.", tp=2)
    except NotADirectoryError:
        console_log(message="Target path is a file.", tp=2)

    # Print damaged files if there are any.
    if len(damaged) >= 1:
        console_log(message="Damaged files:", tp=1)
        for i in damaged:
            console_log(message=i, tp=1)
    else:
        console_log(message="All files copied successfully.", tp=3)

    if execution_time == "y":
        etime = time.time() # End of execution time
        run_time = etime - stime # Full execution time

        # Print execution time
        console_log(message=f"Ran in {run_time:.2f}s ({run_time*1000:.2f}ms)", tp=3)


if __name__ ==  '__main__':
    parse = argparse.ArgumentParser(prog="Mass Copy", description="Copy in mass files and directories")
    parse.add_argument("paths", type=str, nargs=2, help="Source and destination paths")
    parse.add_argument("--chunk_size", "-c", type=int, default=67108864, help="Chunk size in bytes") # Chunk size in 
    parse.add_argument("--check_integrity", "-i", type=str, default="y", help="Check for integrity. y to yes, anything else to no.")
    parse.add_argument("--verbosity", "-v", type=str, default="y", help="Defines verbosity")
    parse.add_argument("--execution_time", "-e", default="n", type=str, help="Show execution time")
    parse.add_argument("--exclude", "-x", type=list_str, default="", help="List of files (on source path) separated by ',' to be ignored. (Full path after source's last path.\nEx: Source = /home/user, so exclude would be exclude (/home/user/exclude))")
    parse.add_argument("--specify", "-s", type=list_str, default="", help="Specification of which files on source path will be copied, separated by comma (','). (Full path after source's last path.\nEx: Source = /home/user, so  only 'include/a,include2/b would be copied.'")
    parse.add_argument("--mode", "-m", default="system", type=str, help="Use 'system' for a syscall or 'detailed' for a detailed (but slower) copy method.")
    args = parse.parse_args()

    try:
        main(args)
    except PermissionError:
        console_log(message="Permission denied.", tp=2)
    except (IOError, TypeError):
        console_log(message="No files to be copied.", tp=2)
