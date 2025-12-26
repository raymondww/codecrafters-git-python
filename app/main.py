import sys
import os
import zlib
import hashlib
import stat


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the code below to pass the first stage
    
    command = sys.argv[1]
    # init command for initializing a git repository
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    # cat-file command for reading a git object
    elif command == 'cat-file': 
        hash_value = sys. argv[3]
        folder = hash_value[:2]
        file_name = hash_value[2:]
        path = os.path.join(".git", "objects", folder, file_name)
        
        if not os.path.exists(path):
            print(f"Error: Object {hash_value} not found")
            sys.exit(1)
        with open(path, "rb") as f:
            compressed_data = f.read()
            decompressed_data = zlib.decompress(compressed_data)
            decode_value = decompressed_data.decode('utf-8')
            # The content is after the first null character, split and strip it to remove newline
            content = decode_value.split('\0', 1)[1]
            print(content, end='')
    elif command == 'ls-tree': 
        # Parse arguments
        if len(sys.argv) == 4:
            option = sys.argv[2]
            sha1_hash = sys. argv[3]
        else:  
            option = None
            sha1_hash = sys.argv[2]
        
        folder = sha1_hash[:2]
        file_name = sha1_hash[2:]
        dir_path = os.path.join(".git", "objects", folder)
        file_path = os.path.join(dir_path, file_name)

        # Read and decompress
        with open(file_path, "rb") as f:
            compressed = f.read()
            decompressed = zlib.decompress(compressed)
        
        # Parse header:  "blob 11\0content" or "tree 234\0..."
        null_index = decompressed.index(b'\x00')
        header = decompressed[:null_index].decode('utf-8')
        content = decompressed[null_index + 1:]
        
        entries = []
        pos = 0

        while pos < len(content):
            # Find the null byte that separates filename from SHA-1
            null_pos = content. index(b'\x00', pos)
            
            # Extract mode and filename
            entry_start = content[pos:null_pos]
            
            # Extract the 20-byte SHA-1 hash after the null byte
            sha1 = content[null_pos + 1:null_pos + 21]
            
            # Combine and store
            entries.append((entry_start, sha1))
            
            # Move to next entry (after the 20-byte SHA-1)
            pos = null_pos + 21

        # Print the entries
        for entry_start, sha1 in entries: 
            header = entry_start. decode('utf-8')
            mode, filename = header.split(' ')
            
            if option == '--name-only': 
                print(filename)
            else:
                # Determine object type based on mode
                if mode == '40000': 
                    obj_type = 'tree'
                else:
                    obj_type = 'blob'
                
                print(f"{mode. zfill(6)} {obj_type} {sha1.hex()}\t{filename}")

    else:
        raise RuntimeError(f"Unknown command #{command}")
    


if __name__ == "__main__":
    main()
