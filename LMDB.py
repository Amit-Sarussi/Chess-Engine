import lmdb
import zlib  # For compressing FEN strings
import numpy as np # For more efficient packing
from typing import Optional, Tuple

class LMDBWrapper:
    def __init__(self, db_path: str, map_size: int = 20 * 1024**3):
        """Initialize LMDB database."""
        self.env = lmdb.open(db_path, map_size=map_size, writemap=True, map_async=True)

    def _encode_key(self, key: str) -> bytes:
        """Encode key (FEN string) using zlib compression."""
        return zlib.compress(key.encode())

    def _decode_key(self, key_bytes: bytes) -> str:
        """Decode key (FEN string) from compressed bytes."""
        return zlib.decompress(key_bytes).decode()

    def put(self, key: str, value: Tuple[float, int]) -> None:
        """Store a key-value pair where key is FEN and value is (eval, count)."""
        # Use numpy for efficient packing: float32 (eval), uint32 (count)
        packed_value = np.array(value, dtype=[('eval', np.float32), ('count', np.uint32)]).tobytes()
        with self.env.begin(write=True) as txn:
            txn.put(self._encode_key(key), packed_value)

    def put_batch(self, data: dict) -> None:
        """Efficiently store multiple key-value pairs."""
        with self.env.begin(write=True) as txn:
            cursor = txn.cursor()
            # Prepare data for putmulti
            items = []
            for k, v in data.items():
                # Use numpy for efficient packing in batch as well
                packed_value = np.array(v, dtype=[('eval', np.float32), ('count', np.uint32)]).tobytes()
                items.append((self._encode_key(k), packed_value))
            cursor.putmulti(items)

    def get(self, key: str) -> Optional[Tuple[float, int]]:
        """Retrieve a value by key."""
        with self.env.begin() as txn:
            value_bytes = txn.get(self._encode_key(key))
            if value_bytes:
                # Use numpy to unpack
                dtype = np.dtype([('eval', np.float32), ('count', np.uint32)])
                value_array = np.frombuffer(value_bytes, dtype=dtype, count=1)
                return value_array[0]['eval'], value_array[0]['count']
            else:
                return None

    def get_or_default(self, key: str, default: Tuple[float, int]) -> Tuple[float, int]:
        """Retrieve a value by key, or return default if not found."""
        with self.env.begin() as txn:
            value_bytes = txn.get(self._encode_key(key))
            if value_bytes:
                # Use numpy to unpack
                dtype = np.dtype([('eval', np.float32), ('count', np.uint32)])
                value_array = np.frombuffer(value_bytes, dtype=dtype, count=1)
                return value_array[0]['eval'], value_array[0]['count']
            else:
                return default

    def delete(self, key: str) -> bool:
        """Delete a key from the database."""
        with self.env.begin(write=True) as txn:
            return txn.delete(self._encode_key(key))

    def keys(self):
        """List all keys in the database."""
        with self.env.begin() as txn:
            with txn.cursor() as cursor:
                return [self._decode_key(key_bytes) for key_bytes, _ in cursor]

    def values(self):
        """Iterate over all values."""
        with self.env.begin() as txn:
            with txn.cursor() as cursor:
                for _, value_bytes in cursor:
                    dtype = np.dtype([('eval', np.float32), ('count', np.uint32)])
                    value_array = np.frombuffer(value_bytes, dtype=dtype, count=1)
                    yield value_array[0]['eval'], value_array[0]['count']

    def items(self):
        """Iterate over all key-value pairs."""
        with self.env.begin() as txn:
            with txn.cursor() as cursor:
                for key_bytes, value_bytes in cursor:
                    key = self._decode_key(key_bytes)
                    dtype = np.dtype([('eval', np.float32), ('count', np.uint32)])
                    value_array = np.frombuffer(value_bytes, dtype=dtype, count=1)
                    value = value_array[0]['eval'], value_array[0]['count']
                    yield key, value

    def get_available_space(self) -> Tuple[float, float]:
        """Get the total and available space in the database in MB."""
        info = self.env.info()
        stat = self.env.stat()
        page_size = stat["psize"]
        total_pages = info["map_size"] // page_size
        used_pages = info["last_pgno"]
        available_size = (total_pages - used_pages) * page_size
        return info["map_size"] / (1024 ** 2), available_size / (1024 ** 2)

    def close(self):
        """Close the database."""
        self.env.sync()
        self.env.close()