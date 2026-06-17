import json
import time


def main() -> None:
    print("mock autoresearch experiment starting")
    for step in range(3):
        time.sleep(0.05)
        print(f"step={step} loss={2.0 - step * 0.2}")
    print(json.dumps({"metrics": {"val_bpb": 1.2345, "loss": 1.6, "tokens": 128}}))


if __name__ == "__main__":
    main()
