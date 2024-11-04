import os
import random
import io


def main():
    print("Generating binary files")
    # Prepare to generate sample files
    single_file = "test_files/single_file"
    multiple_files = "test_files/multiple_files"

    folders = [single_file, multiple_files]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # List with byte sizes
    bytes_size = [1024, 1048576, 1073741824]
    
    for f in folders:
        runs = 1

        if f == multiple_files:
            runs = 10

        for size in bytes_size:
            indx = 0
            for r in range(0, runs):
                indx += 1
                size_path = os.path.join(f, f"{size}")
                os.makedirs(size_path, exist_ok=True)
                file = open(os.path.join(size_path, f"{indx}_{size}.bin"), "wb")

                # Write bytes
                divisor = 16
                chunks = int(size/divisor) # Chunk size
                for i in range(0, divisor):
                    try:
                        prct = ((chunks * i) / size) * 100
                    except ZeroDivisionError:
                        prct = 0

                    byte = random.randbytes(chunks) 

                    file.write(byte)
                    print(f"{size} -> {prct:.2f}%")
        
                file.close()


if __name__ == "__main__":
    main()
