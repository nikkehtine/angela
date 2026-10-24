from watchfiles import run_process


def main():
    run_process(".", target="uv run main.py", target_type="command")


if __name__ == "__main__":
    main()
