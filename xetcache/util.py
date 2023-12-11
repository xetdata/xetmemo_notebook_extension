import hashlib
import pickle
import os
import subprocess
import fsspec


def hash_anything(x):
    return hashlib.sha256(pickle.dumps(x)).hexdigest()


def file_is_pointer_file(x):
    try:
        if os.path.exists(x):
            with open(x, 'rb') as f:
                rl = f.readline()
                return rl.startswith(b"# xet version 0")
        else:
            return False
    except:
        return False


def materialize_pointer_file(x):
    print(f"Materializing {x}")
    try:
        subprocess.run(["git-xet", "materialize", x], check=True)
        return True
    except Exception as e:
        print(f"Failed to materialize pointer file at {x}. Error {e}")
        return False


def probe_memo(memopath, inputhashstr):
    """
    Locate the memo from the provided input.
    """
    memo_file = inputhashstr + '.pickle'
    full_memo_file = os.path.join(memopath, inputhashstr + '.pickle')
    if full_memo_file.startswith("xet://"):
        try:
            openfile = fsspec.open(full_memo_file, 'rb')
            with openfile as f:
                print(f"Loading from {memo_file}")
                result = pickle.load(f)
                return result
        except:
            return None
    elif os.path.exists(full_memo_file):
        if file_is_pointer_file(full_memo_file):
            materialized = materialize_pointer_file(full_memo_file)
        else:
            materialized = True
        if materialized:
            with open(full_memo_file, 'rb') as f:
                print(f"Loading from {memo_file}")
                result = pickle.load(f)
                return result
    return None


def store_memo(memopath, inputhashstr, store):
    """
    Locate the memo from the provided input.
    """
    memo_file = inputhashstr + '.pickle'
    full_memo_file = os.path.join(memopath, inputhashstr + '.pickle')
    if full_memo_file.startswith("xet://"):
        fs = fsspec.filesystem("xet")
        with fs.transaction:
            openfile = fsspec.open(full_memo_file, 'wb')
            with openfile as f:
                print(f"Writing to {memo_file}")
                pickle.dump(store, f)
    else:
        os.makedirs(memopath, exist_ok=True)
        with open(full_memo_file, 'wb') as f:
            print(f"Writing to {memo_file}")
            pickle.dump(store, f)
        return None