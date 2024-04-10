import shlex
import json
import subprocess
from src.utils.logger import logger, Log
from src.base.code import LogType
from typing import Any


async def shell(cmd, dir: str, job=None, env: Any = None):
    log = 'Run cmd ' + cmd
    await Log(LogType.INFO, log, job.id)
    try:
        output = subprocess.run(shlex.split(cmd), cwd=dir,
                                capture_output=True, text=True, env=env)
        return output.stdout, output.stderr
    except subprocess.CalledProcessError as e:
        if e.output.startswith('error:'):
            error = json.loads(e.output[7:])
            logger.error(f"{error['code']}:{error['message']}")
