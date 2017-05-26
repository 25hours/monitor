import os
import sys
if __name__ == "__main__":
    # os.environ.setdefault("DJANDO_SETTINGS_MODULE","monitor.settings")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)
    os.environ.setdefault("DJANDO_SETTINGS_MODULE","monitor.settings")
    from Robb.backends.management import execute_from_command_line
    execute_from_command_line(sys.argv)