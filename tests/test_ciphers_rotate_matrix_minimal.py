"""Test rotate_matrix_right_90 on 1x1 matrix."""
import unittest
from src.ciphers import rotate_matrix_right_90

class TestCiphersRotateMatrixMinimal(unittest.TestCase):
    def test_rotate_single_cell(self):
        self.assertEqual(rotate_matrix_right_90([["A"]]), [["A"]])

if __name__ == '__main__':
    unittest.main()
