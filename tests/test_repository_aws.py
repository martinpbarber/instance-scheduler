import context
import unittest
import logging

import repository.aws

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class RepositoryTestCase(unittest.TestCase):
    """
    Unit tests for repository.aws

    TODO: Add additional tests using AWS API mocks
    """

    def test_create(self):
        '''
            Create an AWS repository object
        '''
        repo = repository.aws.EC2()
        self.assertTrue(repo)

if __name__ == '__main__':
    unittest.main()
