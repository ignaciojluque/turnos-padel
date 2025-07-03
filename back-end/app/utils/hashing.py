import hashlib

def hash_archivo(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()
