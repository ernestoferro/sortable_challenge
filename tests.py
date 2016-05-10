from unittest import TestCase
from text_processing import standardize_text, normalize_text, tokenize_field


class TextProcessingTestCase(TestCase):
    def test_standarize(self):
        self.assertEqual(standardize_text('cybershot'), 'cybershot')
        self.assertEqual(standardize_text('cyber shot'), 'cyber shot')
        self.assertEqual(standardize_text('cyber-shot'), 'cyber-shot')
        self.assertEqual(standardize_text('cybershot[]'), 'cybershot')
        self.assertEqual(standardize_text('a.b 1.123'), 'a.b 1.123')
        self.assertEqual(standardize_text('a_b/c,d'), 'a b c d')

    def test_normalize(self):
        self.assertEqual(normalize_text('cyber-shot'), 'cyber-shot cybershot cyber shot')
        #should behave like standarize when no dash is found
        self.assertEqual(normalize_text('cybershot'), 'cybershot')
        self.assertEqual(normalize_text('cyber shot'), 'cyber shot')
        self.assertEqual(normalize_text('cybershot[]'), 'cybershot')
        self.assertEqual(normalize_text('a.b 1.123'), 'a.b 1.123')
        self.assertEqual(normalize_text('a_b/c,d'), 'a b c d')

    def test_tokenize(self):
        self.assertEqual(tokenize_field('cyber-shot'), {'cyber-shot', 'cybershot', 'cyber shot'})
        self.assertEqual(tokenize_field('a b'), {'a b', 'ab'})
        self.assertEqual(tokenize_field('a-b'), {'a b', 'a-b', 'ab'})
        self.assertEqual(tokenize_field('a b x-y'), {
            'a b x y', 'abx-y', 'a b x-y', 'a b xy',
        })
        self.assertEqual(tokenize_field('sony dsc-123'), {
            'sony dsc-123', 'sonydsc-123', 'sony dsc123', 'sony dsc 123'
        })
