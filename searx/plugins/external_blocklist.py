# external_blocklist.py
from searx.plugins import Plugin, PluginInfo
from searx import logger, settings as searx_settings
import re

logger = logger.getChild('external_blocklist')

class ExternalBlocklist(Plugin):
    id = "external_blocklist"
    def __init__(self, plg_cfg):
        super().__init__(plg_cfg)
        self.info = PluginInfo(
            id=self.id,
            name="External Blocklist Plugin",
            description="Removes results from domains listed in external text files."
        )
        self.patterns = []

    def init(self, app):
        print("DEBUG: external plugin init called", flush=True)
        # Use the already‑loaded settings
        config = searx_settings.get('EXTERNAL_REMOVE', {})
        print(f"DEBUG: config = {config}", flush=True)
        file_paths = config.get('blocklist_files', [])
        print(f"DEBUG: file_paths = {file_paths}", flush=True)
        if not file_paths:
            logger.warning("EXTERNAL_REMOVE: No blocklist_files found in settings")
            print("DEBUG: returning False because no file_paths", flush=True)
            return False

        total = 0
        for file_path in file_paths:
            print(f"DEBUG: processing {file_path}", flush=True)
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        # Remove leading '*.' if present
                        if line.startswith('*.'):
                            line = line[2:]
                        regex = r'(.*\.)?' + re.escape(line) + r'$'
                        self.patterns.append(re.compile(regex, re.IGNORECASE))
                        total += 1
                logger.info(f"Loaded patterns from {file_path}")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                print(f"DEBUG: error reading {file_path}: {e}", flush=True)
                return False
        logger.info(f"Loaded {total} total patterns.")
        print(f"DEBUG: loaded {total} patterns", flush=True)
        return True

    def on_result(self, request, search, result):
        if not hasattr(result, 'parsed_url') or not result.parsed_url.netloc:
            return True
        for pattern in self.patterns:
            if pattern.search(result.parsed_url.netloc):
                return False
        return True
