"""R5.33 full discovery with the explicit frozen B02 acceptance exclusion."""

import json
import sys
import unittest

from benchmark.semantic.verify_binding_r5_32 import cases


def main():
    suite = unittest.defaultTestLoader.discover('benchmark/harness')
    excluded = []
    for test in cases(suite):
        if test.id().startswith('test_phase5e.') and test._testMethodName == 'test_read_only_validation_of_both_continuation_states':
            excluded.append(test.id())
            def skip():
                raise unittest.SkipTest('R5.33 prohibits frozen B02 acceptance')
            setattr(test, test._testMethodName, skip)
    if len(excluded) != 1:
        raise ValueError('historical frozen-acceptance exclusion drift')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'discovered': result.testsRun, 'skipped': len(result.skipped),
                      'failures': len(result.failures), 'errors': len(result.errors),
                      'frozen_acceptance_excluded': excluded}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
