import argparse
import json
import sys
from pymemcache.client.base import Client as MemcacheClient
import logging

from thoughts.core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def dump_memcache():
    """
    Connects to Memcached and dumps all keys and their values.
    Note: This uses commands that are not recommended for production environments.
    """
    logger.info(f"Connecting to Memcached at {settings.MEMCACHED_HOST}:{settings.MEMCACHED_PORT}")
    client = MemcacheClient((settings.MEMCACHED_HOST, settings.MEMCACHED_PORT))
    
    all_items = {}
    try:
        # This is a bit of a hack, as pymemcache doesn't directly support this.
        # We need to talk to the server directly.
        # This is NOT guaranteed to get all keys, especially on a busy server.
        # It's a debugging tool.
        
        # Get all slab IDs
        logger.info("Fetching slab statistics...")
        slab_stats = client.stats('items')
        slab_ids = set()
        if slab_stats:
            # The key format is like 'items:1:number'
            for key, _ in slab_stats.items():
                parts = key.decode().split(':')
                if len(parts) > 1 and parts[1].isdigit():
                    slab_ids.add(parts[1])
        logger.info(f"Found slab IDs: {slab_ids or 'None'}")

        # For each slab, get all keys
        all_keys = []
        if slab_ids:
            logger.info("Fetching keys from slabs...")
            for slab_id in slab_ids:
                # The '0' means get all keys for this slab
                key_stats = client.stats('cachedump', slab_id, '0')
                if key_stats:
                    all_keys.extend([key.decode() for key, _ in key_stats.items()])
            logger.info(f"Found a total of {len(all_keys)} keys.")
        
        # Get values for all keys
        if all_keys:
            logger.info("Fetching values for all keys...")
            # Note: get_many returns a dict of keys that were found.
            values = client.get_many(all_keys)
            
            # Decode values for printing
            for key, value in values.items():
                try:
                    # Try to decode as UTF-8, otherwise show bytes
                    all_items[key] = value.decode()
                except (UnicodeDecodeError, AttributeError):
                    all_items[key] = str(value)

        logger.info("Dumping all found items to stdout.")
        json.dump(all_items, sys.stdout, indent=4)
        
    except Exception:
        logger.error("Error connecting to or reading from Memcached.", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dump all keys and values from Memcached to JSON format.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.parse_args() # No arguments needed for this script
    
    dump_memcache() 