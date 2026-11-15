"""Run Hangman unit tests with a compact, student-friendly summary.

From the project directory:
    python3 run_tests.py       # all tests
    python3 run_tests.py 3     # test 3 only
    python3 run_tests.py 1-5   # tests 1 through 5
"""

import sys
import unittest
from pathlib import Path


class CompactResult(unittest.TestResult):
    """Collect test outcomes without printing exception tracebacks."""

    def __init__(self) -> None:
        super().__init__()
        self.outcomes: list[tuple[str, str]] = []

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        self.outcomes.append((test._testMethodName, "OK"))

    def addFailure(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addFailure(test, err)
        self.outcomes.append((test._testMethodName, "FAIL"))

    def addError(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addError(test, err)
        self.outcomes.append((test._testMethodName, "FAIL"))

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self.outcomes.append((test._testMethodName, "SKIP"))


def main() -> int:
    if len(sys.argv) > 2:
        print("Usage: python3 run_tests.py [number | start-end]")
        return 2

    selected: set[int] | None = None
    if len(sys.argv) == 2:
        sChoice: str = sys.argv[1]
        try:
            if "-" in sChoice:
                sStart, sEnd = sChoice.split("-")
                iStart: int = int(sStart)
                iEnd: int = int(sEnd)
                if iStart > iEnd:
                    raise ValueError
                selected = set(range(iStart, iEnd + 1))
            else:
                selected = {int(sChoice)}
        except ValueError:
            print("Specify a test number (3) or range (1-5).")
            return 2
        if not selected or min(selected) < 1 or max(selected) > 14:
            print("Test numbers must be between 1 and 14.")
            return 2

    oRoot: Path = Path(__file__).resolve().parent
    oLoader: unittest.TestLoader = unittest.TestLoader()
    oSuite: unittest.TestSuite = oLoader.discover(
        start_dir=str(oRoot / "tests"), pattern="test_hangman.py"
    )

    def gather(oTests: unittest.TestSuite):
        for oTest in oTests:
            if isinstance(oTest, unittest.TestSuite):
                yield from gather(oTest)
            else:
                yield oTest

    lTests = list(gather(oSuite))
    if selected is not None:
        lTests = [oTest for oTest in lTests
                  if int(oTest._testMethodName.split("_")[1]) in selected]

    oResult: CompactResult = CompactResult()
    unittest.TestSuite(lTests).run(oResult)

    print("Hangman Unit Tests")
    print("-----------------------------")
    for sName, sStatus in oResult.outcomes:
        lParts: list[str] = sName.split("_", 2)
        print(f"{lParts[1]} {lParts[2]:<23} {sStatus}")
    print()
    iPassed: int = sum(sStatus == "OK" for _, sStatus in oResult.outcomes)
    iFailed: int = sum(sStatus == "FAIL" for _, sStatus in oResult.outcomes)
    print(f"{iPassed} passed, {iFailed} failed")
    return 0 if oResult.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
