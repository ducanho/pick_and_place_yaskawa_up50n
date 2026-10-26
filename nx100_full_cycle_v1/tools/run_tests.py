"""Run from project root: python -m tools.run_tests"""
import json
import logging
import time
import unittest
import sys
from settings import owned


def main():
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    logging.disable(logging.CRITICAL)
    start=time.monotonic()
    suite=unittest.defaultTestLoader.discover(str(owned('tests')))
    report=owned('docs/test_output.txt')
    with report.open('w',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    summary=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                 skipped=len(result.skipped),seconds=round(time.monotonic()-start,2),passed=result.wasSuccessful())
    owned('docs/test_result.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary))
    if not result.wasSuccessful():
        print(report.read_text(encoding='utf-8'))
        raise SystemExit(1)


if __name__=='__main__':
    main()
