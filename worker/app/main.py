from app.job_manager.manager import WorkerManager


def main() -> None:
    manager = WorkerManager()
    manager.run_forever()


if __name__ == "__main__":
    main()
