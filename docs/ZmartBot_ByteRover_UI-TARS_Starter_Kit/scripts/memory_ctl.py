#!/usr/bin/env python3
import subprocess, sys

CMD_UP = ["docker", "compose", "-f", "services/memory-gateway/compose.memory.yml", "up", "-d"]
CMD_DOWN = ["docker", "compose", "-f", "services/memory-gateway/compose.memory.yml", "down"]

def main():
    if len(sys.argv) < 2:
        print("Usage: memory_ctl.py [start|stop|status]")
        sys.exit(1)
    action = sys.argv[1]
    if action == "start":
        subprocess.check_call(CMD_UP)
    elif action == "stop":
        subprocess.check_call(CMD_DOWN)
    elif action == "status":
        subprocess.check_call(["curl", "-fsS", "http://127.0.0.1:8295/health"])
    else:
        print("Unknown action")
        sys.exit(2)

if __name__ == "__main__":
    main()
