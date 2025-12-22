import sys
import os
import zlib

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
        path = os. path.join(".git", "objects", folder, file_name)
        
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
    else:
        raise RuntimeError(f"Unknown command #{command}")
    


if __name__ == "__main__":
    main()
