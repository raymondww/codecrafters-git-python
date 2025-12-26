import sys
import os
import zlib
import hashlib
import time


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

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
    elif command == 'hash-object': 
        text_file = sys. argv[3]
        with open(text_file, "rb") as f:
            content = f.read()
        
        header = f"blob {len(content)}\0". encode('utf-8')
        store = header + content
        
        # Calculate SHA-1 hash on the UNCOMPRESSED data
        sha1_hash = hashlib.sha1(store).hexdigest()
        print(sha1_hash)
        # If -w flag is present, write to .git/objects
        if '-w' in sys. argv:
            # Split hash:  first 2 chars = folder, rest = filename
            folder = sha1_hash[:2]
            file_name = sha1_hash[2:]
            
            # Create directory path
            dir_path = os.path.join(".git", "objects", folder)
            file_path = os.path.join(dir_path, file_name)
            
            # Create directory if it doesn't exist
            os.makedirs(dir_path, exist_ok=True)
            
            # Compress the data (header + content)
            compressed_data = zlib.compress(store)
            
            # Write the compressed data to file
            with open(file_path, 'wb') as f:
                f.write(compressed_data)
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
    elif command == 'write-tree':
        def write_blob(file_path):
            """Write a blob object and return its SHA-1 hash"""
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Create blob object:  "blob <size>\0<content>"
            blob_data = f"blob {len(content)}". encode() + b'\x00' + content
            
            # Calculate SHA-1 hash
            sha1_hash = hashlib.sha1(blob_data).hexdigest()
            
            # Write to .git/objects
            folder = sha1_hash[:2]
            file_name = sha1_hash[2:]
            dir_path = os.path.join(".git", "objects", folder)
            os.makedirs(dir_path, exist_ok=True)
            
            file_path_git = os.path.join(dir_path, file_name)
            with open(file_path_git, 'wb') as f:
                f.write(zlib.compress(blob_data))
            
            return sha1_hash
        
        def write_tree(directory='.'):
            """Write a tree object and return its SHA-1 hash"""
            entries = []
            
            # Read all files and directories
            for item in os.listdir(directory):
                # Ignore . git directory
                if item == '.git':
                    continue
                
                item_path = os.path.join(directory, item)
                
                if os.path. isfile(item_path):
                    # Create blob for file
                    sha1_hash = write_blob(item_path)
                    mode = '100644'
                    entries.append((mode, item, sha1_hash))
                elif os.path.isdir(item_path):
                    # Recursively create tree for directory
                    sha1_hash = write_tree(item_path)
                    mode = '40000'
                    entries.append((mode, item, sha1_hash))
            
            # Sort entries alphabetically by name
            entries. sort(key=lambda x: x[1])
            
            # Build tree content
            tree_content = b''
            for mode, name, sha1_hash in entries:
                tree_content += mode.encode() + b' ' + name.encode() + b'\x00'
                tree_content += bytes.fromhex(sha1_hash)
            
            # Create tree object:  "tree <size>\0<content>"
            tree_data = f"tree {len(tree_content)}".encode() + b'\x00' + tree_content
            
            # Calculate SHA-1 hash
            sha1_hash = hashlib.sha1(tree_data).hexdigest()
            
            # Write to .git/objects
            folder = sha1_hash[:2]
            file_name = sha1_hash[2:]
            dir_path = os.path.join(".git", "objects", folder)
            os.makedirs(dir_path, exist_ok=True)
            
            file_path_git = os.path.join(dir_path, file_name)
            with open(file_path_git, 'wb') as f:
                f.write(zlib. compress(tree_data))
            
            return sha1_hash
        
        # Write the tree and print the hash
        tree_hash = write_tree()
        print(tree_hash)
    elif command == 'commit-tree':    
        # Parse arguments
        tree_sha = sys.argv[2]
        parent_sha = sys.argv[4]  # After -p flag
        message = sys.argv[6]  # After -m flag
        
        # Get current timestamp
        timestamp = int(time.time())
        timezone = '+0000'
        
        # Hardcoded author/committer info
        author_name = 'John Doe'
        author_email = 'john@example.com'
        
        # Build commit content
        commit_content = f"tree {tree_sha}\n"
        commit_content += f"parent {parent_sha}\n"
        commit_content += f"author {author_name} <{author_email}> {timestamp} {timezone}\n"
        commit_content += f"committer {author_name} <{author_email}> {timestamp} {timezone}\n"
        commit_content += f"\n{message}\n"
        
        # Create commit object:  "commit <size>\0<content>"
        commit_data = f"commit {len(commit_content)}".encode() + b'\x00' + commit_content. encode()
        
        # Calculate SHA-1 hash
        sha1_hash = hashlib.sha1(commit_data).hexdigest()
        
        # Write to .git/objects
        folder = sha1_hash[:2]
        file_name = sha1_hash[2:]
        dir_path = os.path.join(".git", "objects", folder)
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(zlib.compress(commit_data))
        
        # Print the commit SHA
        print(sha1_hash)

    else:
        raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
