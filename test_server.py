import unittest, time
from utils import load_config
from server import massege_treatment


class MassegeTreatmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self._config = load_config()
        self._dict_ok = {
            "action": self._config['PRESENCE'],
            "time": time.time(),
            "type": "status",
            "user": {
                "account_name": 'Ivan',
                "status": "Yep, I am here!"
            }
        }
        self._dict_not_ok = {
            "action": self._config['PRESENCE'],
            "time": time.time(),
            "type": "status",
            "user": {
                "account_name": 'None',
                "status": "Yep, I am here!"
            }
        }
        self._answer_ok = {"response": '200',
                           "time": time.time(),
                           "alert": "успешное завершение"}
        self._answer_not_ok = {"response": '400',
                              "time": time.time(),
                              "alert": "Неверные данные"}
        self._count_dict_ok = len(self._answer_ok)
        self._count_dict_not_ok = len(self._answer_not_ok)

    def test_answer_ok(self):
        self.assertEqual(massege_treatment(self._dict_ok, self._config), self._answer_ok)

    def test_count_answer_ok(self):
        self.assertEqual(len(massege_treatment(self._dict_ok, self._config)), self._count_dict_ok)

    def test_answer_ok(self):
        self.assertEqual(massege_treatment(self._dict_not_ok, self._config), self._answer_not_ok)

    def test_count_answer_ok(self):
        self.assertEqual(len(massege_treatment(self._dict_not_ok, self._config)), self._count_dict_not_ok)


if __name__ == '__main__':
    unittest.main()
