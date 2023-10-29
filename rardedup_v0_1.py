import os
import rarfile
import hashlib
from tqdm import tqdm
import subprocess
import tempfile

def calculate_hash(file_path):
    BUF_SIZE = 65536
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read(BUF_SIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BUF_SIZE)
            yield
    return hasher.hexdigest()

def hash_files_in_rar(rar_path, temp_dir):
    file_hashes = {}
    with rarfile.RarFile(rar_path, 'r') as rf:
        file_list = [f for f in rf.infolist() if not f.isdir()]
        total_size = sum(f.file_size for f in file_list)
        progress = tqdm(total=100, desc=f"Hashing files in {os.path.basename(rar_path)}",
                        unit='%', dynamic_ncols=True)
        for i, f in enumerate(file_list, start=1):
            extracted_path = os.path.join(temp_dir, f.filename)
            rf.extract(f, temp_dir)
            hash_gen = calculate_hash(extracted_path)
            try:
                while True:
                    next(hash_gen)
                    progress.update((f.file_size / total_size) * 100 / 2)  # Update by half of the per-file progress
            except StopIteration as e:
                file_hash = e.value
            file_hashes[f.filename] = file_hash
            progress.update((f.file_size / total_size) * 100 / 2)  # Complete the other half of the per-file progress
            os.remove(extracted_path)
        progress.close()
    return file_hashes

def rardedup(rar1_path, rar2_path, temp_dir):
    print(f"Using temp dir: {temp_dir}")
    # print(f"Hashing files in {rar1_path} ...")
    rar1_hashes = hash_files_in_rar(rar1_path, temp_dir)
    # print(f"Hashing files in {rar2_path} ...")
    rar2_hashes = hash_files_in_rar(rar2_path, temp_dir)

    duplicates = [filename for filename, filehash in rar2_hashes.items() if rar1_hashes.get(filename) == filehash]
    if duplicates:
        print("Found duplicates. Deleting from RAR 2...")
        with tempfile.NamedTemporaryFile(mode='w+t', delete=False) as tf:
            tf.write('\n'.join(duplicates))
            tf_name = tf.name
        subprocess.run(["WinRAR", "d", rar2_path, f"@{tf_name}"], check=True)
        os.remove(tf_name)
        print("Duplicates removed.")
    else:
        print("No duplicates found.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Deduplicate files between two RAR archives.')
    parser.add_argument('rar1', help='Path to the first RAR file')
    parser.add_argument('rar2', help='Path to the second RAR file')
    parser.add_argument('--temp-dir', help='Temporary directory for extraction',
                        default=tempfile.gettempdir())
    args = parser.parse_args()

    if not os.path.exists(args.temp_dir):
        os.makedirs(args.temp_dir)
    
    rardedup(args.rar1, args.rar2, args.temp_dir)

if __name__ == "__main__":
    main()
