import context
import unittest

import provider.aws

class ProviderTestCase(unittest.TestCase):
    """
    Unit tests for provider.aws

    TODO: Add additional tests using AWS API mocks
    """

    def test_create_provider(self):
        '''
            Create an AWS provider object
        '''
        id = 'us-east-1' + ':' + 'i-12345678901234567'
        pro = provider.aws.EC2(id)
        self.assertTrue(pro)

if __name__ == '__main__':
    unittest.main()
