"""Tests for reporting artifact generation."""

import os
import unittest

from kryptos.k4.reporting import generate_candidate_artifacts, write_candidates_csv, write_candidates_json


class TestReportingArtifacts(unittest.TestCase):
    def setUp(self):
        self.out_dir = 'reports_test'
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        self.candidates = [
            {
                'text': 'SAMPLETEXT',
                'score': 10.0,
                'source': 'test',
                'key': [[1, 2], [3, 4]],
            },
            {
                'text': 'OTHERTEXT',
                'score': 5.0,
                'source': 'test2',
            },
        ]

    def tearDown(self):
        # Clean up created files
        for fname in ['k4_candidates.json', 'k4_candidates.csv']:
            path = os.path.join(self.out_dir, fname)
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(self.out_dir):
            try:
                os.rmdir(self.out_dir)
            except OSError:
                pass

    def test_write_candidates_json(self):
        path = write_candidates_json(
            'stage',
            'K4',
            'ABCDEF',
            self.candidates,
            output_path=os.path.join(self.out_dir, 'k4_candidates.json'),
        )
        self.assertTrue(os.path.exists(path))

    def test_write_candidates_csv(self):
        path = write_candidates_csv(
            self.candidates,
            output_path=os.path.join(self.out_dir, 'k4_candidates.csv'),
        )
        self.assertTrue(os.path.exists(path))

    def test_generate_candidate_artifacts(self):
        paths = generate_candidate_artifacts(
            'stage',
            'K4',
            'ABCDEF',
            self.candidates,
            out_dir=self.out_dir,
            write_csv=True,
        )
        self.assertIn('json', paths)
        self.assertIn('csv', paths)
        self.assertTrue(os.path.exists(paths['json']))
        self.assertTrue(os.path.exists(paths['csv']))


if __name__ == '__main__':
    unittest.main()
