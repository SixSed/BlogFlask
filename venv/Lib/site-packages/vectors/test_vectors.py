from vectors import Vector, GridCrawler, Direction

import unittest


class TestVectors(unittest.TestCase):
    def test_adding_vectors(self):
        values_list = [
            ((1, 16), (12, 8), (13, 24)),
            ((-15, 16), (15, -16), (0, 0)),
        ]
        for values in values_list:
            vec1, vec2, exp = values
            result = Vector(vec1) + Vector(vec2)
            self.assertIsInstance(result, Vector)
            self.assertEqual(result, Vector(exp))

    def test_subtracting_vectors(self):
        values_list = [
            ((1, 16), (12, 8), (-11, 8)),
            ((-15, 16), (15, -16), (-30, 32)),
            ((1, 2), (1, 2), (0, 0)),
        ]
        for values in values_list:
            vec1, vec2, exp = values
            result = Vector(vec1) - Vector(vec2)
            self.assertIsInstance(result, Vector)
            self.assertEqual(result, Vector(exp))

    def test_distance(self):
        values_list = [
            ((0, 0), (3, 4), 5),
            ((0, 0), (3, -4), 5),
            ((15, -16), (15, -16), 0),
        ]
        for values in values_list:
            vec1, vec2, exp = values
            result = Vector(vec1).distance(Vector(vec2))
            self.assertEqual(result, exp)

    def test_multiplication(self):
        values_list = [
            ((0, 0), 5, (0, 0)),
            ((1, 0), 3, (3, 0)),
            ((1, -2), 7, (7, -14)),
        ]
        for values in values_list:
            vec1, number, exp = values
            result = Vector(vec1) * number
            self.assertIsInstance(result, Vector)
            self.assertEqual(result, Vector(exp))


class TestGridCrawler(unittest.TestCase):
    def test_crawler(self):
        crawler = GridCrawler(Vector((0, 0)), Direction.UP.value)
        self.assertEqual(crawler.location, Vector((0, 0)))
        crawler.go_ahead()
        self.assertEqual(crawler.location, Vector((0, 1)))
        crawler.turn_back()
        crawler.go_ahead()
        self.assertEqual(crawler.location, Vector((0, 0)))

        crawler.turn_right()
        self.assertEqual(crawler.location, Vector((0, 0)))
        crawler.go_ahead()
        self.assertEqual(crawler.location, Vector((-1, 0)))


if __name__ == "__main__":
    unittest.main()
